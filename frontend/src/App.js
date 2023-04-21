import React, { useState } from 'react';
import {
  Container,
  Row,
  Col,
  Button,
  InputGroup,
  FormControl,
  ListGroup,
  Spinner,
} from 'react-bootstrap';
import axios from 'axios';
import './App.css';

function App() {
  const [dataPath, setDataPath] = useState('');
  const [userId, setUserId] = useState('');
  const [messages, setMessages] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/messages', {
        data_path: dataPath,
        user_id: userId,
      });
      setMessages(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const uniqueUsers = Array.from(
    new Set(messages.map((message) => message.username))
  );

  const filteredMessages = messages.filter(
    (message) => message.username === selectedUser
  );

  return (
    <div className="App">
      <Container fluid>
        <Row className="my-4">
          <Col>
            <h1>Discord Data Viewer</h1>
          </Col>
        </Row>
        <Row className="my-4">
          <Col>
            <InputGroup>
              <FormControl
                placeholder="Enter the path to your Discord data package"
                value={dataPath}
                onChange={(e) => setDataPath(e.target.value)}
              />
              <FormControl
                placeholder="Enter your user ID"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
              />
              <Button variant="primary" onClick={fetchData}>
                Load Messages
              </Button>
            </InputGroup>
          </Col>
        </Row>
        {loading ? (
          <Row className="my-4">
            <Col className="text-center">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
            </Col>
          </Row>
        ) : (
          <>
            <Row className="my-4">
              <Col>
                <h3>Select a user:</h3>
                <div className="user-bubbles">
                  {uniqueUsers.map((username, index) => (
                    <Button
                      key={index}
                      className="user-bubble"
                      variant={selectedUser === username ? 'primary' : 'outline-primary'}
                      onClick={() => setSelectedUser(username)}
                    >
                      {username}
                    </Button>
                  ))}
                </div>
              </Col>
            </Row>
            {selectedUser && (
              <Row>
                <Col>
                  <h3>Messages with {selectedUser}:</h3>
                  <ListGroup>
                    {filteredMessages.map((message, index) => (
                      <ListGroup.Item key={index}>
                        {message.content}
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                </Col>
              </Row>
            )}
          </>
        )}
      </Container>
    </div>
  );
}

export default App;
