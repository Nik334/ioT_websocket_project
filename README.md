# IoT Data Ingestion & Streaming Service

A scalable backend service for managing users, ingesting IoT data, and streaming real-time updates using FastAPI, MongoDB, and WebSockets.

---

## Table of Contents
1. [Setup Instructions](#setup-instructions)
2. [Auth Flow Explanation](#auth-flow-explanation)
3. [API Examples](#api-examples)
4. [WebSocket Examples](#websocket-examples)
5. [Error Handling](#error-handling)
6. [Design Decisions](#design-decisions)

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- MongoDB (local or docker)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ioT_websocket_project
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create `.env` file (optional, defaults work for local development):
```env
MONGODB_URL=mongodb+srv://nikkumar334:hello@ans.y96vfkl.mongodb.net/
DATABASE_NAME=iot_streaming_db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password
```

### 5. Run MongoDB
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7

# Or install locally and run
mongod
```

### 6. Start the Server
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Docker Compose (Alternative)
```bash
docker-compose up -d
```

---

## Frontend Setup (Optional)

The project includes a React frontend for visualization.

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start Development Server
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

### 4. Build for Production
```bash
npm run build
```

---

## Auth Flow Explanation

### 1. Login Flow
```
Client                    Server
  |                         |
  |---- POST /auth/login -->|
  |    {username, password} |
  |<--- {access_token} -----|
  |                         |
```

### 2. Authenticated Request Flow
```
Client                    Server
  |                         |
  |--- GET /users --------->|
  |   Authorization: Bearer |
  |   JWT_TOKEN             |
  |<-- 200 OK [data] ------|
  |                         |
```

### 3. WebSocket Authentication
```
Client                    Server
  |                         |
  |--- WS /ws/ingest?token=JWT_TOKEN |
  |<-- Connection accepted -|
  |                         |
  |--- {iot_data} --------->|
  |<-- {status: stored} ---|
```

---

## API Examples

### Authentication

#### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Users API

#### Get All Users
```bash
curl -X GET http://localhost:8000/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "user_id": "U1001",
    "name": "Test User",
    "status": "active"
  }
]
```

#### Create User
```bash
curl -X POST http://localhost:8000/users \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "joker", "name": "Joker", "status": "active"}'
```

#### Get User
```bash
curl -X GET http://localhost:8000/users/joker \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Update User
```bash
curl -X PUT http://localhost:8000/users/joker \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Joker Updated", "status": "inactive"}'
```

### IoT Data API

#### Ingest IoT Data
```bash
curl -X POST http://localhost:8000/data \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "joker",
    "metric_1": 40.2,
    "metric_2": 150,
    "metric_3": 60,
    "timestamp": 1710000200
  }'
```

**Validation Rules:**
- `metric_1`: 0-100
- `metric_2`: 0-200
- `metric_3`: integer
- `timestamp`: cannot be in the future
- `user_id`: must exist and be "active"

#### Get Latest IoT Data
```bash
curl -X GET http://localhost:8000/users/joker/iot/latest \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "metric_1": 40.2,
  "metric_2": 150.0,
  "metric_3": 60.0,
  "timestamp": 1710000200
}
```

#### Get IoT History
```bash
curl -X GET "http://localhost:8000/users/joker/iot/history?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## WebSocket Examples

### 1. Ingest via WebSocket

**Connection URL:**
```
ws://localhost:8000/ws/ingest?token=YOUR_JWT_TOKEN
```

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ingest?token=YOUR_TOKEN');

ws.onopen = () => {
  console.log('Connected to WebSocket');
  
  // Send IoT data
  ws.send(JSON.stringify({
    user_id: "joker",
    metric_1: 45.2,
    metric_2: 88,
    metric_3: 1,
    timestamp: Math.floor(Date.now() / 1000)
  }));
};

ws.onmessage = (event) => {
  console.log('Response:', JSON.parse(event.data));
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

**Server Response:**
```json
{"status": "stored", "data": {...}}
```

### 2. Subscribe to Real-Time Updates

**Connection URL:**
```
ws://localhost:8000/ws/subscribe?user_id=joker
```

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/subscribe?user_id=joker');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.event === 'NEW_DATA') {
    console.log('New IoT data received:', message.data);
    // Update UI with new data
  }
};
```

**Server Push Message:**
```json
{
  "event": "NEW_DATA",
  "data": {
    "user_id": "joker",
    "metric_1": 45.2,
    "metric_2": 88.0,
    "metric_3": 1.0,
    "timestamp": 1710000200
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid/missing token) |
| 404 | Not Found |
| 409 | Conflict (duplicate user) |
| 422 | Unprocessable Entity (validation failure) |
| 500 | Internal Server Error |

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Common Errors

#### 401 Unauthorized
```json
{"detail": "Not authenticated"}
```

#### 404 Not Found
```json
{"detail": "User joker not found"}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "metric_1"],
      "msg": "ensure value is less than or equal to 100",
      "type": "value_error"
    }
  ]
}
```

#### 400 Bad Request
```json
{"detail": "User joker is not active"}
```

---

## Design Decisions

### 1. FastAPI Framework
- **Why**: Native async/await support for high performance
- **Benefits**: Auto-generated OpenAPI documentation, type validation with Pydantic

### 2. MongoDB Database
- **Why**: Flexible schema for IoT data, excellent time-series support
- **Benefits**: Easy to scale horizontally, efficient for append-heavy workloads
- **Trade-offs**: Not ACID compliant (acceptable for IoT use case)

### 3. JWT Authentication
- **Why**: Stateless, scalable, works well with REST APIs
- **Benefits**: No session storage needed, easy to validate on each request
- **Trade-offs**: Token refresh handling needed

### 4. WebSocket Architecture
- **Why**: Real-time bidirectional communication for IoT updates
- **Implementation**: Custom WebSocketManager for subscription handling
- **Trade-offs**: Requires connection state management

### 5. Data Validation
- **Pydantic Models**: Used for request/response validation
- **Custom Validators**: Added for timestamp future check and metric ranges

### 6. API Design
- **RESTful**: Standard HTTP methods (GET, POST, PUT)
- **Path Design**: `/data` for IoT ingestion, `/users/{id}/iot/*` for data retrieval

### 7. Error Handling Strategy
- **HTTP Exceptions**: FastAPI's built-in HTTPException for clear status codes
- **Validation**: Pydantic model validation with descriptive error messages

---

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # MongoDB connection
│   ├── auth/                # Authentication (JWT, login)
│   ├── routers/             # API endpoints (users, iot)
│   ├── services/            # Business logic (websocket manager)
│   ├── models/              # Pydantic models
│   └── websockets/          # WebSocket endpoints
├── tests/                  # Unit tests
├── frontend/               # React frontend (optional)
├── docker-compose.yml      # Docker compose configuration
├── Dockerfile              # Container build
└── requirements.txt        # Python dependencies
```

---

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Test coverage includes:
- Authentication (login, JWT validation)
- User CRUD operations
- IoT data ingestion and validation
- WebSocket functionality
- Error handling

---

## Future Improvements

- **Redis Pub/Sub**: For scaling WebSocket broadcasting across multiple instances
- **Kafka Integration**: For persistent event streaming
- **Rate Limiting**: API throttling to prevent abuse
- **Analytics**: Aggregations and insights on IoT data
- **Monitoring**: Prometheus + Grafana for observability

---

## License

MIT License