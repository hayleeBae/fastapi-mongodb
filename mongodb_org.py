from fastapi import Query
from pymongo import MongoClient
from datetime import *
from bson import ObjectId

host = "localhost"
port = "27017"
client = MongoClient('mongodb+srv://baeeura94:healthcube@cluster0.avvlpgb.mongodb.net/')



def insert_item_many(data, db_name = None, collection_name = None):
    db = client[db_name]
    collection = db[collection_name]

    # response_queue가 비어있는 경우 처리
    if not data:
        return None
    # 여기서 response_queue를 딕셔너리 형태로 감싸서 처리
    try:
        # 여기서 response_queue를 딕셔너리 형태로 감싸서 처리
        documents = [
            {"timestamp": datetime.now(), "Response queue": [{"role": item["role"], "content": item["content"]} for item in data]}
        ]
        result = collection.insert_many(documents)
        inserted_ids = result.inserted_ids
        return inserted_ids
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")
        return None


def fetch_conversation_from_db(conversation_id):
    client = MongoClient('mongodb+srv://baeeura94:healthcube@cluster0.avvlpgb.mongodb.net/')
    db = client["HealthCube"]
    collection = db["user_chat_logs"]

    # Convert the string representation of ObjectId back to ObjectId
    conversation_id = ObjectId(conversation_id)

    # Fetch the conversation based on the specified "_id"
    conversation_document = collection.find_one({"_id": conversation_id})

    # Log the conversation document for debugging
    print(f"Conversation document: {conversation_document}")

    if conversation_document:
        # Extract the conversation content from the document
        conversation = conversation_document.get("Response queue")

        # Log the conversation content for debugging
        print(f"Conversation content: {conversation}")

        return conversation
    else:
        print(f"Conversation not found for ID: {conversation_id}")
        return None