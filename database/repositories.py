from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from models.post import Post
from utils.config import get_config

config = get_config()

# MongoDB setup
mongo_client = MongoClient(config.MONGO_URI)
mongo_db = mongo_client[config.MONGO_DB]

def get_mongo():
    return mongo_db

class PostRepository:
    def __init__(self):
        self.db = get_mongo()
        self.collection = self.db.posts

    def create_post(self, post: Post) -> Post:
        post_dict = post.dict(by_alias=True)
        post_dict["created_at"] = datetime.utcnow()
        post_dict["updated_at"] = datetime.utcnow()
        result = self.collection.insert_one(post_dict)
        post_dict["_id"] = result.inserted_id
        return Post(**post_dict)

    def get_post(self, post_id: str) -> Optional[Post]:
        post = self.collection.find_one({"_id": ObjectId(post_id)})
        if post:
            return Post(**post)
        return None

    def get_posts(self, skip: int = 0, limit: int = None) -> List[Post]:
        if limit is None:
            limit = config.POSTS_PER_PAGE
        posts = self.collection.find().skip(skip).limit(limit)
        return [Post(**post) for post in posts]

    def get_user_posts(self, user_id: int, skip: int = 0, limit: int = None) -> List[Post]:
        if limit is None:
            limit = config.POSTS_PER_PAGE
        posts = self.collection.find({"author_id": user_id}).skip(skip).limit(limit)
        return [Post(**post) for post in posts]

    def update_post(self, post_id: str, post: Post) -> Optional[Post]:
        post_dict = post.dict(by_alias=True)
        post_dict["updated_at"] = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": post_dict}
        )
        if result.modified_count:
            return self.get_post(post_id)
        return None

    def delete_post(self, post_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(post_id)})
        return result.deleted_count > 0 