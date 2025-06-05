import os
import sys
import pytest
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def get_required_env_var(name: str) -> str:
    """Get required environment variable or exit if not set."""
    value = os.getenv(name)
    if value is None:
        print(f"Error: Required environment variable '{name}' is not set")
        sys.exit(1)
    return value

# MongoDB connection settings from environment variables
MONGO_URI = get_required_env_var('MONGO_URI')
MONGO_TEST_DB = get_required_env_var('MONGO_TEST_DB')
MONGO_TEST_COLLECTION = get_required_env_var('MONGO_TEST_COLLECTION')

@pytest.fixture(scope='module')
def mongo_client():
    """Create a MongoDB client connection."""
    client = MongoClient(MONGO_URI)
    yield client
    # Cleanup after tests
    client.drop_database(MONGO_TEST_DB)
    client.close()

@pytest.fixture(scope='function')
def test_collection(mongo_client):
    """Get test collection and clean it before each test."""
    collection = mongo_client[MONGO_TEST_DB][MONGO_TEST_COLLECTION]
    collection.delete_many({})  # Clean collection before each test
    return collection

def test_mongodb_connection(mongo_client):
    """Test that we can connect to MongoDB."""
    # This will raise an exception if connection fails
    mongo_client.server_info()
    assert mongo_client is not None

def test_write_and_read_post(test_collection):
    """Test writing a post to MongoDB and reading it back."""
    # Test data
    test_post = {
        'title': 'Test Post',
        'content': 'This is a test post content',
        'author': 'Test Author',
        'created_at': datetime.utcnow(),
        'tags': ['test', 'integration']
    }
    
    # Insert the test post
    result = test_collection.insert_one(test_post)
    assert result.inserted_id is not None
    
    # Read the post back
    retrieved_post = test_collection.find_one({'_id': result.inserted_id})
    assert retrieved_post is not None
    assert retrieved_post['title'] == test_post['title']
    assert retrieved_post['content'] == test_post['content']
    assert retrieved_post['author'] == test_post['author']
    assert retrieved_post['tags'] == test_post['tags']

def test_find_multiple_posts(test_collection):
    """Test writing multiple posts and finding them."""
    # Insert multiple test posts
    test_posts = [
        {
            'title': f'Test Post {i}',
            'content': f'Content for test post {i}',
            'author': 'Test Author',
            'created_at': datetime.utcnow(),
            'tags': ['test', f'tag{i}']
        }
        for i in range(3)
    ]
    
    result = test_collection.insert_many(test_posts)
    assert len(result.inserted_ids) == 3
    
    # Find all posts
    all_posts = list(test_collection.find())
    assert len(all_posts) == 3
    
    # Find posts by author
    author_posts = list(test_collection.find({'author': 'Test Author'}))
    assert len(author_posts) == 3
    
    # Find posts by tag
    tagged_posts = list(test_collection.find({'tags': 'test'}))
    assert len(tagged_posts) == 3 