from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import get_current_user
from app.database import get_database
from app.models.iot_data import IoTDataCreate, IoTDataResponse, IoTDataBrief
from app.services.websocket_manager import websocket_manager

router = APIRouter(tags=["IoT Data"])


@router.post("/data", response_model=IoTDataResponse, status_code=status.HTTP_201_CREATED)
async def ingest_iot_data(
    data: IoTDataCreate, _current_user: dict = Depends(get_current_user)
):
    db = get_database()
    user = await db.users.find_one({"_id": data.user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {data.user_id} not found",
        )
    if user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {data.user_id} is not active",
        )
    doc = {
        "user_id": data.user_id,
        "metric_1": data.metric_1,
        "metric_2": data.metric_2,
        "metric_3": data.metric_3,
        "timestamp": data.timestamp,
    }
    broadcast_doc = doc.copy()
    await db.iot_data.insert_one(doc)
    await websocket_manager.broadcast(data.user_id, broadcast_doc)
    return IoTDataResponse(**doc)


@router.get("/users/{user_id}/iot/latest", response_model=IoTDataBrief)
async def get_latest_iot_data(
    user_id: str, _current_user: dict = Depends(get_current_user)
):
    db = get_database()
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    doc = await db.iot_data.find_one(
        {"user_id": user_id}, sort=[("timestamp", -1)]
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No IoT data found for user {user_id}",
        )
    return IoTDataBrief(
        metric_1=doc["metric_1"],
        metric_2=doc["metric_2"],
        metric_3=doc["metric_3"],
        timestamp=doc["timestamp"],
    )


@router.get("/users/{user_id}/iot/history", response_model=list[IoTDataBrief])
async def get_iot_history(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=1000),
    _current_user: dict = Depends(get_current_user),
):
    db = get_database()
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    cursor = db.iot_data.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [
        IoTDataBrief(
            metric_1=doc["metric_1"],
            metric_2=doc["metric_2"],
            metric_3=doc["metric_3"],
            timestamp=doc["timestamp"],
        )
        for doc in docs
    ]