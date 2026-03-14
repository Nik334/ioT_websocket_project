# IoT Data Ingestion & Streaming Service --- Development Plan

This document describes the complete implementation plan for building a
**Generic IoT Data Ingestion & Real-Time Streaming Service** using
**FastAPI, MongoDB, WebSockets, and JWT authentication**.

The goal is to design a scalable backend capable of:

-   Managing users
-   Ingesting IoT data
-   Fetching latest and historical IoT data
-   Streaming real-time updates via WebSockets
-   Securing APIs with JWT authentication

------------------------------------------------------------------------

# Tech Stack

  Technology         Purpose
  ------------------ --------------------------
  Python 3.10+       Backend language
  FastAPI            Async REST API framework
  MongoDB            NoSQL database
  Motor              Async MongoDB driver
  WebSockets         Real-time data streaming
  JWT (PyJWT)        Authentication
  Passlib            Password hashing
  Pytest             Testing framework
  HTTPX              Async API testing
  Docker             Containerization
  Redis (Optional)   Pub/Sub scaling

------------------------------------------------------------------------

# Phase 1: Project Setup

## 1. Initialize Project Structure

Create base project layout.

    app/
    tests/
    Dockerfile
    docker-compose.yml
    requirements.txt
    README.md
    plan.md

Create internal folders:

    app/
    ├── routers/
    ├── services/
    ├── models/
    ├── auth/
    ├── websockets/

------------------------------------------------------------------------

## 2. Setup Virtual Environment

Create environment and install dependencies.

``` bash
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn motor pyjwt passlib pytest httpx websockets
```

Create `requirements.txt`.

------------------------------------------------------------------------

## 3. Docker Setup (Optional)

Create:

-   Dockerfile
-   docker-compose.yml

docker-compose should include:

-   FastAPI container
-   MongoDB container

------------------------------------------------------------------------

# Phase 2: Database & Configuration

## 4. MongoDB Connection

Use **Motor (async MongoDB driver)**.

File:

    app/database.py

Responsibilities:

-   Create MongoDB client
-   Initialize database connection
-   Provide collections to services

------------------------------------------------------------------------

## 5. Collections & Indexes

### Users Collection

    users

Indexes:

-   user_id

### IoT Data Collection

    iot_data

Indexes:

-   user_id
-   timestamp

Recommended composite index:

    (user_id, timestamp)

------------------------------------------------------------------------

# Phase 3: Authentication

## 6. JWT Utility Module

File:

    app/auth/jwt_handler.py

Functions:

-   create_access_token()
-   verify_token()

Use **PyJWT**.

------------------------------------------------------------------------

## 7. Login Endpoint

Endpoint:

    POST /auth/login

Request:

``` json
{
 "username": "admin",
 "password": "password"
}
```

Response:

``` json
{
 "access_token": "JWT_TOKEN"
}
```

------------------------------------------------------------------------

## 8. Authentication Dependency

Create FastAPI dependency that:

-   Extracts JWT from headers
-   Verifies token
-   Protects routes

Header format:

    Authorization: Bearer <token>

------------------------------------------------------------------------

# Phase 4: User Management APIs

## 9. User Models

File:

    app/models/user.py

Fields:

-   user_id
-   name
-   status

------------------------------------------------------------------------

## 10. Create User

Endpoint:

    POST /users

Insert user into MongoDB.

------------------------------------------------------------------------

## 11. Update User

Endpoint:

    PUT /users/{user_id}

Update user fields.

------------------------------------------------------------------------

## 12. Get User

Endpoint:

    GET /users/{user_id}

Return user details.

------------------------------------------------------------------------

# Phase 5: IoT Data Ingestion (REST)

## 13. IoT Data Model

File:

    app/models/iot_data.py

Schema:

``` json
{
 "user_id": "U1001",
 "metric_1": 34.5,
 "metric_2": 78,
 "metric_3": 1,
 "timestamp": 1769535468
}
```

Validation Rules:

-   metric_1 → 0--100
-   metric_2 → 0--200
-   timestamp → cannot be in the future

------------------------------------------------------------------------

## 14. Ingest IoT Data

Endpoint:

    POST /iot/data

Steps:

1.  Validate payload
2.  Verify user exists
3.  Verify user is active
4.  Store data in MongoDB
5.  Broadcast update to WebSocket subscribers

------------------------------------------------------------------------

# Phase 6: Fetch IoT Data

## 15. Latest IoT Data

Endpoint:

    GET /users/{user_id}/iot/latest

Return most recent record.

------------------------------------------------------------------------

## 16. Historical IoT Data

Endpoint:

    GET /users/{user_id}/iot/history?limit=50

Return last N records sorted by timestamp.

------------------------------------------------------------------------

# Phase 7: WebSocket Real-Time Streaming

## 17. WebSocket Manager

File:

    app/services/websocket_manager.py

Responsibilities:

-   Track active connections
-   Manage subscriptions per user_id
-   Broadcast messages

------------------------------------------------------------------------

## 18. WebSocket Ingest

Endpoint:

    WS /ws/ingest?token=JWT_TOKEN

Steps:

1.  Authenticate client
2.  Receive IoT data
3.  Validate payload
4.  Store in MongoDB
5.  Broadcast to subscribers

------------------------------------------------------------------------

## 19. WebSocket Subscribe

Endpoint:

    WS /ws/subscribe?user_id=U1001

Behavior:

-   Client subscribes to a user data stream
-   Whenever new data arrives the client receives real-time updates

Example message:

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

# Phase 8: Testing

Testing tools:

-   pytest
-   httpx.AsyncClient

Test coverage:

### Auth Tests

-   login success
-   invalid credentials

### User Tests

-   create user
-   update user
-   get user

### IoT Tests

-   valid ingestion
-   invalid metrics
-   future timestamp validation

### Data Fetch Tests

-   latest record
-   historical records

### WebSocket Tests

-   websocket ingestion
-   websocket subscription

------------------------------------------------------------------------

# Phase 9: Documentation

## Swagger / OpenAPI

Automatically available via FastAPI.

Access:

    /docs

------------------------------------------------------------------------

## README

README must include:

-   setup instructions
-   authentication flow
-   API examples
-   WebSocket examples
-   design decisions

------------------------------------------------------------------------

# Suggested Directory Structure

    app/
    ├── main.py
    ├── config.py
    ├── database.py

    ├── auth/
    │   ├── jwt_handler.py
    │   └── routes.py

    ├── models/
    │   ├── user.py
    │   └── iot_data.py

    ├── routers/
    │   ├── users.py
    │   └── iot.py

    ├── services/
    │   └── websocket_manager.py

    ├── websockets/
    │   ├── ingest.py
    │   └── subscribe.py

    tests/
    ├── test_auth.py
    ├── test_users.py
    ├── test_iot.py
    └── test_websockets.py

    Dockerfile
    docker-compose.yml
    requirements.txt
    README.md
    plan.md
