from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import jwt
import bcrypt
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Configuration
JWT_SECRET = "xspace_crypto_secret_key_2025"
JWT_ALGORITHM = "HS256"
security = HTTPBearer()

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    password_hash: str
    balance: float = 10000.0
    is_admin: bool = False
    is_bot: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_profit_loss: float = 0.0
    total_invested: float = 0.0

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Investment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    asset_type: str  # 'crypto' or 'tesla'
    asset_name: str  # 'BTC', 'ETH', 'TESLA'
    symbol: str
    amount: float
    purchase_price: float
    current_price: float
    quantity: float
    profit_loss: float
    multiplier: float = 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: str  # 'buy', 'sell'
    asset_name: str
    amount: float
    price: float
    quantity: float
    profit_loss: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AssetPrice(BaseModel):
    symbol: str
    name: str
    current_price: float
    price_change_24h: float
    price_change_percentage_24h: float
    asset_type: str

# Mock asset data
MOCK_ASSETS = {
    "BTC": {"name": "Bitcoin", "price": 45000, "change": 2.5, "type": "crypto"},
    "ETH": {"name": "Ethereum", "price": 3200, "change": -1.2, "type": "crypto"},
    "ADA": {"name": "Cardano", "price": 0.85, "change": 4.1, "type": "crypto"},
    "DOT": {"name": "Polkadot", "price": 12.5, "change": -0.8, "type": "crypto"},
    "TESLA": {"name": "Tesla Inc", "price": 950, "change": 1.8, "type": "stock"},
}

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, is_admin: bool = False) -> str:
    payload = {
        "user_id": user_id,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_jwt_token(token)
    user = await db.users.find_one({"id": payload["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Initialize bot users
async def create_bot_users():
    bot_count = await db.users.count_documents({"is_bot": True})
    if bot_count < 20:
        bot_names = [
            "CryptoKing2024", "TeslaBull", "BlockchainPro", "ElonFan", "BitcoinMaster",
            "EthereumGuru", "TradingBot", "DiamondHands", "CryptoWhale", "TeslaInvestor",
            "HODLer", "MoonLander", "TechTrader", "FutureInvestor", "DigitalGold",
            "ElectricCars", "SmartInvestor", "CryptoNinja", "StockMaster", "InvestmentPro"
        ]
        
        for i, name in enumerate(bot_names):
            existing = await db.users.find_one({"username": name})
            if not existing:
                initial_investment = random.uniform(5000, 50000)
                profit_loss = random.uniform(-2000, 15000)
                
                bot_user = User(
                    email=f"{name.lower()}@example.com",
                    username=name,
                    password_hash=hash_password("botpassword"),
                    balance=initial_investment + profit_loss,
                    is_bot=True,
                    total_invested=initial_investment,
                    total_profit_loss=profit_loss,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
                )
                await db.users.insert_one(bot_user.dict())
                
                # Create some investments for bots
                for asset_symbol in random.sample(list(MOCK_ASSETS.keys()), random.randint(2, 4)):
                    asset = MOCK_ASSETS[asset_symbol]
                    investment_amount = random.uniform(1000, 10000)
                    quantity = investment_amount / asset["price"]
                    current_value = quantity * asset["price"]
                    profit_loss = current_value - investment_amount
                    
                    investment = Investment(
                        user_id=bot_user.id,
                        asset_type=asset["type"],
                        asset_name=asset["name"],
                        symbol=asset_symbol,
                        amount=investment_amount,
                        purchase_price=asset["price"] * random.uniform(0.8, 1.2),
                        current_price=asset["price"],
                        quantity=quantity,
                        profit_loss=profit_loss,
                        multiplier=random.uniform(0.5, 3.0)
                    )
                    await db.investments.insert_one(investment.dict())

# API Routes
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password
    )
    
    await db.users.insert_one(user.dict())
    token = create_jwt_token(user.id)
    
    return {
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "balance": user.balance
        }
    }

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user["id"], user.get("is_admin", False))
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "balance": user["balance"],
            "is_admin": user.get("is_admin", False)
        }
    }

@api_router.get("/assets")
async def get_assets():
    assets = []
    for symbol, data in MOCK_ASSETS.items():
        # Add some random fluctuation to prices
        current_price = data["price"] * random.uniform(0.98, 1.02)
        change_24h = random.uniform(-5, 5)
        
        assets.append(AssetPrice(
            symbol=symbol,
            name=data["name"],
            current_price=current_price,
            price_change_24h=change_24h,
            price_change_percentage_24h=change_24h,
            asset_type=data["type"]
        ))
    
    return assets

@api_router.get("/portfolio")
async def get_portfolio(current_user: User = Depends(get_current_user)):
    investments = await db.investments.find({"user_id": current_user.id}).to_list(1000)
    return [Investment(**inv) for inv in investments]

@api_router.post("/invest")
async def create_investment(
    asset_symbol: str,
    amount: float,
    multiplier: float = 1.0,
    current_user: User = Depends(get_current_user)
):
    if asset_symbol not in MOCK_ASSETS:
        raise HTTPException(status_code=400, detail="Invalid asset")
    
    if amount > current_user.balance:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    asset = MOCK_ASSETS[asset_symbol]
    quantity = (amount * multiplier) / asset["price"]
    
    investment = Investment(
        user_id=current_user.id,
        asset_type=asset["type"],
        asset_name=asset["name"],
        symbol=asset_symbol,
        amount=amount,
        purchase_price=asset["price"],
        current_price=asset["price"],
        quantity=quantity,
        profit_loss=0.0,
        multiplier=multiplier
    )
    
    # Update user balance
    new_balance = current_user.balance - amount
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"balance": new_balance, "total_invested": current_user.total_invested + amount}}
    )
    
    await db.investments.insert_one(investment.dict())
    
    # Create transaction record
    transaction = Transaction(
        user_id=current_user.id,
        type="buy",
        asset_name=asset["name"],
        amount=amount,
        price=asset["price"],
        quantity=quantity
    )
    await db.transactions.insert_one(transaction.dict())
    
    return {"message": "Investment created successfully", "investment": investment}

@api_router.get("/leaderboard")
async def get_leaderboard():
    users = await db.users.find(
        {"is_bot": {"$in": [True, False]}},
        {"password_hash": 0}
    ).sort("total_profit_loss", -1).limit(20).to_list(20)
    
    return [
        {
            "username": user["username"],
            "total_profit_loss": user.get("total_profit_loss", 0),
            "total_invested": user.get("total_invested", 0),
            "is_bot": user.get("is_bot", False)
        }
        for user in users
    ]

@api_router.get("/admin/users")
async def get_all_users(current_user: User = Depends(get_admin_user)):
    users = await db.users.find({}, {"password_hash": 0, "_id": 0}).to_list(1000)
    return users

@api_router.get("/admin/stats")
async def get_admin_stats(current_user: User = Depends(get_admin_user)):
    total_users = await db.users.count_documents({"is_bot": False})
    total_bots = await db.users.count_documents({"is_bot": True})
    total_investments = await db.investments.count_documents({})
    
    # Calculate total platform value
    total_invested = await db.users.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$total_invested"}}}
    ]).to_list(1)
    
    total_platform_value = total_invested[0]["total"] if total_invested else 0
    
    return {
        "total_users": total_users,
        "total_bots": total_bots,
        "total_investments": total_investments,
        "total_platform_value": total_platform_value
    }

@api_router.post("/admin/create-admin")
async def create_admin():
    # Create admin user if doesn't exist
    admin_exists = await db.users.find_one({"email": "admin@xspace.com"})
    if not admin_exists:
        admin_user = User(
            email="admin@xspace.com",
            username="admin",
            password_hash=hash_password("admin123"),
            is_admin=True,
            balance=100000.0
        )
        await db.users.insert_one(admin_user.dict())
        return {"message": "Admin user created", "email": "admin@xspace.com", "password": "admin123"}
    return {"message": "Admin already exists"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await create_bot_users()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()