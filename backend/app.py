import os
import asyncio
import pandas as pd
import discord
from discord.errors import NotFound
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel

class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        def hint_tuples(item):
            if isinstance(item, tuple):
                return {'__tuple__': True, 'items': item}
            if isinstance(item, float):
                if not (abs(item) <= 1.8e308):
                    return str(item)
            return item

        return super(CustomJSONEncoder, self).encode(self.default(hint_tuples(obj)))

    def decode(self, obj):
        def hinted_tuples(item):
            if isinstance(item, dict):
                if '__tuple__' in item:
                    return tuple(item['items'])
                else:
                    return item
            return item

        return super(CustomJSONEncoder, self).decode(obj, object_hook=hinted_tuples)


class DataPath(BaseModel):
    data_path: str
    user_id: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKEN = 'Insert Discord Bot Token Here'

client = discord.Client(intents=discord.Intents.default())

async def start_discord_client():
    await client.start(TOKEN)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_discord_client())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

async def get_username(user_id: int):
    try:
        user = await client.fetch_user(user_id)
        return user.name
    except NotFound:
        return f'Unknown User ({user_id})'

@app.post('/api/messages')
async def process_messages(data: DataPath):
    data_path = data.data_path
    print("test")
    user_id = int(data.user_id)
    messages = []

    for foldername in os.listdir(data_path):
        folder_path = os.path.join(data_path, foldername)

        if not os.path.isdir(folder_path):
            continue

        messages_csv = os.path.join(folder_path, 'messages.csv')
        channel_json = os.path.join(folder_path, 'channel.json')

        if not (os.path.isfile(messages_csv) and os.path.isfile(channel_json)):
            continue

        with open(channel_json, 'r') as file:
            channel_data = json.load(file)

        channel_type = channel_data['type']

        # If the channel type is not DM, skip this folder
        if channel_type != 1:
            continue

        recipients = channel_data['recipients']
        recipient_id = str([r_id for r_id in recipients if r_id != str(user_id)][0])

        df = pd.read_csv(messages_csv)
        print("hello")
        username = await get_username(int(recipient_id))
        print(username)
        for index, row in df.iterrows():
            
            messages.append({
                'user_id': recipient_id,
                'username': username,
                'content': str(row['Contents']),
                'channel_id': foldername
            })
    return messages


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)