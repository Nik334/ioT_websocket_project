from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.database import connect_to_mongo, close_mongo_connection
from app.routers.users import router as users_router
from app.routers.iot import router as iot_router
from app.websockets.ingest import router as ws_ingest_router
from app.websockets.subscribe import router as ws_subscribe_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="IoT Data Ingestion & Streaming Service",
    description="A scalable backend for managing users, ingesting IoT data, and streaming real-time updates",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(iot_router)
app.include_router(ws_ingest_router)
app.include_router(ws_subscribe_router)


@app.get("/")
async def root():
    return {"message": "IoT Data Ingestion & Streaming Service", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}