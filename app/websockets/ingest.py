from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.params import Query

from app.auth.jwt_handler import verify_token
from app.database import get_database
from app.models.iot_data import IoTDataCreate
from app.services.websocket_manager import websocket_manager

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/ingest")
async def websocket_ingest(
    websocket: WebSocket,
    token: str = Query(...)
):
    payload = verify_token(token)
    if payload is None:
        await websocket.close(code=4001)
        return
    
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            import json
            try:
                data_dict = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                continue
            
            try:
                iot_data = IoTDataCreate(**data_dict)
            except Exception as e:
                await websocket.send_text(json.dumps({"error": str(e)}))
                continue
            
            db = get_database()
            user = await db.users.find_one({"_id": iot_data.user_id})
            if not user:
                await websocket.send_text(json.dumps({"error": f"User {iot_data.user_id} not found"}))
                continue
            if user.get("status") != "active":
                await websocket.send_text(json.dumps({"error": f"User {iot_data.user_id} is not active"}))
                continue
            
            doc = {
                "user_id": iot_data.user_id,
                "metric_1": iot_data.metric_1,
                "metric_2": iot_data.metric_2,
                "metric_3": iot_data.metric_3,
                "timestamp": iot_data.timestamp,
            }
            await db.iot_data.insert_one(doc)
            await websocket_manager.broadcast(iot_data.user_id, doc)
            await websocket.send_text(json.dumps({"status": "stored", "data": doc}))
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


@router.websocket("/ws/subscribe")
async def websocket_subscribe(
    websocket: WebSocket,
    user_id: str = Query(...)
):
    await websocket_manager.connect(websocket)
    await websocket_manager.subscribe(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.unsubscribe(websocket, user_id)
        websocket_manager.disconnect(websocket)