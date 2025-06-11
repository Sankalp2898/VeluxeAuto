import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import motor.motor_asyncio
import uuid
from contextlib import asynccontextmanager

# MongoDB client setup
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'veluxe_db')]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Veluxe backend...")
    yield
    # Shutdown
    print("Shutting down Veluxe backend...")

app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Car(BaseModel):
    id: str = None
    user_id: str
    brand: str
    model: str
    year: int
    mileage: int
    last_service_date: str
    vin: str
    color: str
    
class CarHealth(BaseModel):
    car_id: str
    oil_status: int  # 0-100
    brake_status: int  # 0-100
    battery_status: int  # 0-100
    tire_status: int  # 0-100
    last_updated: str
    ai_predictions: dict = {}

class ServiceBooking(BaseModel):
    id: str = None
    user_id: str
    car_id: str
    service_type: str
    pickup_type: str  # "white-glove" or "in-garage"
    appointment_date: str
    appointment_time: str
    status: str = "scheduled"
    special_instructions: str = ""

class User(BaseModel):
    id: str = None
    name: str
    email: str
    phone: str
    membership_tier: str = "Basic"  # Basic, Premium, Veluxe Elite
    created_at: str

class Event(BaseModel):
    id: str = None
    title: str
    description: str
    event_type: str  # "track-day", "meetup", "exclusive"
    date: str
    location: str
    max_attendees: int
    current_attendees: int = 0
    brands_filter: List[str] = []

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "veluxe-backend"}

@app.post("/api/users")
async def create_user(user: User):
    user.id = str(uuid.uuid4())
    user.created_at = datetime.now().isoformat()
    
    result = await db.users.insert_one(user.dict())
    if result.inserted_id:
        return {"success": True, "user_id": user.id}
    raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if user:
        user.pop('_id', None)
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/cars")
async def add_car(car: Car):
    car.id = str(uuid.uuid4())
    
    result = await db.cars.insert_one(car.dict())
    if result.inserted_id:
        # Initialize car health data
        health = CarHealth(
            car_id=car.id,
            oil_status=85,
            brake_status=92,
            battery_status=88,
            tire_status=76,
            last_updated=datetime.now().isoformat(),
            ai_predictions={
                "oil_change_due": "2024-08-15",
                "brake_inspection": "2024-09-01",
                "tire_rotation": "2024-07-20",
                "battery_check": "2024-12-01"
            }
        )
        await db.car_health.insert_one(health.dict())
        
        return {"success": True, "car_id": car.id}
    raise HTTPException(status_code=500, detail="Failed to add car")

@app.get("/api/cars/user/{user_id}")
async def get_user_cars(user_id: str):
    cars = []
    async for car in db.cars.find({"user_id": user_id}):
        car.pop('_id', None)
        cars.append(car)
    return cars

@app.get("/api/car-health/{car_id}")
async def get_car_health(car_id: str):
    health = await db.car_health.find_one({"car_id": car_id})
    if health:
        health.pop('_id', None)
        return health
    raise HTTPException(status_code=404, detail="Car health data not found")

@app.post("/api/bookings")
async def create_booking(booking: ServiceBooking):
    booking.id = str(uuid.uuid4())
    
    result = await db.bookings.insert_one(booking.dict())
    if result.inserted_id:
        return {"success": True, "booking_id": booking.id}
    raise HTTPException(status_code=500, detail="Failed to create booking")

@app.get("/api/bookings/user/{user_id}")
async def get_user_bookings(user_id: str):
    bookings = []
    async for booking in db.bookings.find({"user_id": user_id}):
        booking.pop('_id', None)
        bookings.append(booking)
    return bookings

@app.get("/api/events")
async def get_events():
    events = []
    async for event in db.events.find():
        event.pop('_id', None)
        events.append(event)
    return events

@app.post("/api/events/{event_id}/rsvp")
async def rsvp_event(event_id: str, user_id: str):
    # Check if already RSVP'd
    existing = await db.event_rsvps.find_one({"event_id": event_id, "user_id": user_id})
    if existing:
        return {"success": True, "message": "Already RSVP'd"}
    
    # Add RSVP
    rsvp = {
        "id": str(uuid.uuid4()),
        "event_id": event_id,
        "user_id": user_id,
        "created_at": datetime.now().isoformat()
    }
    
    result = await db.event_rsvps.insert_one(rsvp)
    if result.inserted_id:
        # Update event attendee count
        await db.events.update_one(
            {"id": event_id},
            {"$inc": {"current_attendees": 1}}
        )
        return {"success": True}
    
    raise HTTPException(status_code=500, detail="Failed to RSVP")

@app.post("/api/ai-predictions/{car_id}")
async def get_ai_predictions(car_id: str):
    # Placeholder for AI predictions - will be replaced with OpenAI integration
    predictions = {
        "overall_health": "Good",
        "next_service": "Oil change recommended in 2 weeks",
        "alerts": [
            "Tire pressure check recommended",
            "Brake fluid level is optimal"
        ],
        "maintenance_score": 87
    }
    
    # Update car health with AI predictions
    await db.car_health.update_one(
        {"car_id": car_id},
        {"$set": {
            "ai_predictions": predictions,
            "last_updated": datetime.now().isoformat()
        }}
    )
    
    return predictions

# Initialize sample data
@app.get("/api/debug/init-events")
async def init_sample_events():
    """Debug endpoint to initialize sample events"""
    # Create sample events
    sample_events = [
        {
            "id": str(uuid.uuid4()),
            "title": "Porsche Track Day",
            "description": "Exclusive track day at Laguna Seca for Porsche owners",
            "event_type": "track-day",
            "date": "2024-07-25",
            "location": "Laguna Seca Raceway, CA",
            "max_attendees": 50,
            "current_attendees": 23,
            "brands_filter": ["Porsche"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "BMW & Mercedes Meetup",
            "description": "Luxury German auto meetup in Beverly Hills",
            "event_type": "meetup",
            "date": "2024-08-10",
            "location": "Beverly Hills Hotel, CA",
            "max_attendees": 75,
            "current_attendees": 45,
            "brands_filter": ["BMW", "Mercedes"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Tesla Owners Exclusive",
            "description": "Private charging station unveiling and test drives",
            "event_type": "exclusive",
            "date": "2024-08-20",
            "location": "Tesla Fremont Factory, CA",
            "max_attendees": 30,
            "current_attendees": 18,
            "brands_filter": ["Tesla"]
        }
    ]
    
    # Insert events
    inserted_count = 0
    for event in sample_events:
        existing = await db.events.find_one({"title": event["title"]})
        if not existing:
            await db.events.insert_one(event)
            inserted_count += 1
    
    return {"success": True, "message": f"Initialized {inserted_count} sample events"}

@app.on_event("startup")
async def startup_event():
    # Create sample events
    sample_events = [
        {
            "id": str(uuid.uuid4()),
            "title": "Porsche Track Day",
            "description": "Exclusive track day at Laguna Seca for Porsche owners",
            "event_type": "track-day",
            "date": "2024-07-25",
            "location": "Laguna Seca Raceway, CA",
            "max_attendees": 50,
            "current_attendees": 23,
            "brands_filter": ["Porsche"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "BMW & Mercedes Meetup",
            "description": "Luxury German auto meetup in Beverly Hills",
            "event_type": "meetup",
            "date": "2024-08-10",
            "location": "Beverly Hills Hotel, CA",
            "max_attendees": 75,
            "current_attendees": 45,
            "brands_filter": ["BMW", "Mercedes"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Tesla Owners Exclusive",
            "description": "Private charging station unveiling and test drives",
            "event_type": "exclusive",
            "date": "2024-08-20",
            "location": "Tesla Fremont Factory, CA",
            "max_attendees": 30,
            "current_attendees": 18,
            "brands_filter": ["Tesla"]
        }
    ]
    
    # Insert events if they don't exist
    for event in sample_events:
        existing = await db.events.find_one({"title": event["title"]})
        if not existing:
            await db.events.insert_one(event)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)