# MongoDB interaction code will go here

from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["click2earn"]
users = db["users"]

def get_user(user_id):
    user = users.find_one({"user_id": user_id})
    if not user:
        users.insert_one({
            "user_id": user_id,
            "wallet": 0.0,
            "ref_by": None,
            "clicks": {},
            "referrals": [],
            "joined_on": None
        })
        user = users.find_one({"user_id": user_id})
    return user

def update_wallet(user_id, amount):
    users.update_one({"user_id": user_id}, {"$inc": {"wallet": amount}})
