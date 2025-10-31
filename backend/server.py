from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ------------------------------
# App Key (CODE CONSTANT as requested)
# Manually change this value to update the app key.
# Default per requirement: "123456"
APP_KEY = "123456"

# "Special function" activation logic: active only when APP_KEY == "123456"
# If you change APP_KEY manually below, this flag will reflect automatically on restart.
SPECIAL_FUNCTION_ACTIVE = APP_KEY == "123456"

# ------------------------------
# MongoDB connection (unchanged)
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class KeyPayload(BaseModel):
    key: str


# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)

    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()

    _ = await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)

    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])

    return status_checks


# ------------------------------
# Key and Special Function Endpoints
# NOTE: We do NOT expose the key value itself. Only validation and special status.

@api_router.post("/key/validate")
async def validate_key(payload: KeyPayload):
    try:
        is_valid = payload.key == APP_KEY
        return {"valid": is_valid}
    except Exception as e:
        logging.exception("Key validation error")
        raise HTTPException(status_code=500, detail="Internal error during key validation")


@api_router.get("/special")
async def special_status():
    # The special function is considered active when APP_KEY == "123456"
    # Update rule: change APP_KEY constant to adjust behavior
    message = (
        "Special function ACTIVE (APP_KEY is '123456')."
        if SPECIAL_FUNCTION_ACTIVE
        else "Special function INACTIVE (APP_KEY is not '123456')."
    )
    return {"active": SPECIAL_FUNCTION_ACTIVE, "message": message}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
