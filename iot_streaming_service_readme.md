# IoT Data Ingestion & Streaming Service

## Objective

Build a generic IoT Data Ingestion and Streaming Service that allows:

-   Creating and managing users
-   Ingesting IoT data for users
-   Fetching historical and latest IoT data
-   Streaming real-time updates via WebSocket
-   Securing APIs and WebSockets using JWT authentication

The service demonstrates modern backend architecture using async APIs
and real-time streaming.

------------------------------------------------------------------------

# Tech Stack

  Technology         Purpose
  ------------------ -------------------------
  Python 3.10+       Backend language
  FastAPI            REST API framework
  MongoDB            Data storage
  WebSockets         Real-time streaming
  JWT                Authentication
  AsyncIO            Asynchronous processing
  Docker             Containerization
  Redis (Optional)   Pub/Sub for scaling
  Pytest             Unit testing

------------------------------------------------------------------------

# System Architecture

Client applications interact with the backend using REST APIs and
WebSockets.

Client\
↓\
FastAPI Backend\
↓\
Authentication (JWT)\
User Service\
IoT Data Service\
WebSocket Manager\
↓\
MongoDB Database

### Data Flow

1.  User authenticates using login API
2.  Client receives JWT token
3.  Client sends IoT data using REST API or WebSocket
4.  Server validates the data
5.  Data is stored in MongoDB
6.  WebSocket subscribers receive real-time updates

------------------------------------------------------------------------

# Authentication

## Login

Endpoint

POST /auth/login

Request

``` json
{
 "username": "admin",
 "password": "password"
}
```

Response

``` json
{
 "access_token": "JWT_TOKEN"
}
```

### Authentication Rules

-   JWT token required for all REST APIs
-   JWT token required for WebSocket connections
-   Unauthorized requests must be rejected

Example header:

Authorization: Bearer JWT_TOKEN

------------------------------------------------------------------------

# User Management APIs

## Create User

POST /users

``` json
{
 "user_id": "U1001",
 "name": "Test User",
 "status": "active"
}
```

## Update User

PUT /users/{user_id}

``` json
{
 "name": "Updated Name",
 "status": "inactive"
}
```

## Get User

GET /users/{user_id}

Example Response

``` json
{
 "user_id": "U1001",
 "name": "Test User",
 "status": "active"
}
```

------------------------------------------------------------------------

# IoT Data Model

Each IoT record contains:

``` json
{
 "user_id": "U1001",
 "metric_1": 34.5,
 "metric_2": 78,
 "metric_3": 1,
 "timestamp": 1769535468
}
```

------------------------------------------------------------------------

# IoT Data Ingestion

## REST API Ingestion

POST /iot/data

Example Request

``` json
{
 "user_id": "U1001",
 "metric_1": 45.2,
 "metric_2": 88,
 "metric_3": 0,
 "timestamp": 1710000100
}
```

### Validation Rules

  Field       Rule
  ----------- ------------------------------
  metric_1    value must be between 0--100
  metric_2    value must be between 0--200
  timestamp   cannot be in the future
  user        must exist and be active

Invalid data must return proper error messages.

------------------------------------------------------------------------

# WebSocket Data Ingestion

Endpoint

WS /ws/ingest

Authentication example

ws://localhost:8000/ws/ingest?token=JWT_TOKEN

Incoming message

``` json
{
 "user_id": "U1001",
 "metric_1": 45.2,
 "metric_2": 88,
 "metric_3": 0,
 "timestamp": 1710000100
}
```

Processing:

-   Validate IoT data
-   Store data in MongoDB
-   Broadcast to subscribers

------------------------------------------------------------------------

# Fetch IoT Data

## Latest Data

GET /users/{user_id}/iot/latest

Example response

``` json
{
 "metric_1": 45.2,
 "metric_2": 88,
 "metric_3": 0,
 "timestamp": 1710000100
}
```

## Historical Data

GET /users/{user_id}/iot/history?limit=50

Example response

``` json
[
 {
  "metric_1": 45.2,
  "metric_2": 88,
  "metric_3": 0,
  "timestamp": 1710000100
 }
]
```

------------------------------------------------------------------------

# WebSocket Subscription

Endpoint

WS /ws/subscribe?user_id=U1001

Behavior

-   Client subscribes to a user's IoT stream
-   When new data arrives the server pushes real-time updates

Example message

``` json
{
 "event": "NEW_DATA",
 "data": {
  "metric_1": 45.2,
  "metric_2": 88,
  "metric_3": 0,
  "timestamp": 1710000100
 }
}
```

------------------------------------------------------------------------

# WebSocket Authentication

Requirements

-   JWT must be validated during connection
-   Unauthorized connections must be rejected
-   Token expiry should disconnect clients

------------------------------------------------------------------------

# Database Design

## Users Collection

Example

``` json
{
 "_id": "U1001",
 "name": "Test User",
 "status": "active"
}
```

## IoT Data Collection

Example

``` json
{
 "user_id": "U1001",
 "metric_1": 45.2,
 "metric_2": 88,
 "metric_3": 0,
 "timestamp": 1710000100
}
```

Indexes

-   user_id
-   timestamp

------------------------------------------------------------------------

# Setup Instructions

## Clone Repository

git clone https://github.com/your-repo/iot-streaming-service.git

cd iot-streaming-service

## Create Virtual Environment

python -m venv venv

source venv/bin/activate

## Install Dependencies

pip install -r requirements.txt

## Run Server

uvicorn app.main:app --reload

Swagger documentation

http://localhost:8000/docs

------------------------------------------------------------------------

# Docker (Optional)

## Using Docker Compose

Start all services:

```bash
docker-compose up -d
```

This will start:
- MongoDB on port 27017
- FastAPI on port 8000

## Manual Docker

Build image

    docker build -t iot-service .

Run container

    docker run -p 8000:8000 iot-service

------------------------------------------------------------------------

# Testing

Run unit tests

pytest

------------------------------------------------------------------------

# Design Decisions

### FastAPI

Chosen because it provides:

-   Async support
-   High performance
-   Automatic OpenAPI documentation

### MongoDB

Selected due to:

-   Flexible schema
-   Suitable for time-series IoT data
-   Horizontal scalability

### WebSockets

Used to provide:

-   Real-time data streaming
-   Low latency communication

### JWT Authentication

Ensures:

-   Secure APIs
-   Stateless authentication

------------------------------------------------------------------------

# Future Improvements

-   Redis Pub/Sub for scalable WebSocket broadcasting
-   Kafka integration for streaming pipelines
-   Rate limiting for APIs
-   IoT analytics and aggregation
-   Monitoring using Prometheus and Grafana
