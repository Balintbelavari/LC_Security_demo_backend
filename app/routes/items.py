from fastapi import APIRouter, HTTPException
from app.database import items_collection
from app.models import Item
from bson import ObjectId

router = APIRouter()

@router.get("/items")
async def get_items():
    items = await items_collection.find().to_list(100)
    return [{"id": str(item["_id"]), **item} for item in items]

@router.post("/items")
async def create_item(item: Item):
    new_item = await items_collection.insert_one(item.dict())
    return {"id": str(new_item.inserted_id)}

@router.get("/items/{item_id}")
async def get_item(item_id: str):
    item = await items_collection.find_one({"_id": ObjectId(item_id)})
    if item:
        return {"id": str(item["_id"]), **item}
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await items_collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 1:
        return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")
