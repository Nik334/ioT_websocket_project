from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.auth.dependencies import get_current_user
from app.database import get_database
from app.models.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def get_users(
    limit: int = Query(default=100, ge=1, le=1000),
    _current_user: dict = Depends(get_current_user),
):
    db = get_database()
    cursor = db.users.find().limit(limit)
    docs = await cursor.to_list(length=limit)
    return [
        UserResponse(user_id=doc["_id"], name=doc["name"], status=doc["status"])
        for doc in docs
    ]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, _current_user: dict = Depends(get_current_user)
):
    db = get_database()
    existing = await db.users.find_one({"_id": user.user_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {user.user_id} already exists",
        )
    doc = {"_id": user.user_id, "name": user.name, "status": user.status}
    await db.users.insert_one(doc)
    return UserResponse(user_id=user.user_id, name=user.name, status=user.status)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, _current_user: dict = Depends(get_current_user)):
    db = get_database()
    doc = await db.users.find_one({"_id": user_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return UserResponse(user_id=doc["_id"], name=doc["name"], status=doc["status"])


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user: UserUpdate,
    _current_user: dict = Depends(get_current_user),
):
    db = get_database()
    existing = await db.users.find_one({"_id": user_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    update_data = {k: v for k, v in user.model_dump().items() if v is not None}
    if update_data:
        await db.users.update_one({"_id": user_id}, {"$set": update_data})
    updated = await db.users.find_one({"_id": user_id})
    return UserResponse(
        user_id=updated["_id"], name=updated["name"], status=updated["status"]
    )
