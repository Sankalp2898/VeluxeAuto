#!/usr/bin/env python3
import requests
import json
import time
import random
from datetime import datetime, timedelta
import os
import sys

# Get the backend URL from the frontend .env file
def get_backend_url():
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    return None

BACKEND_URL = get_backend_url()
if not BACKEND_URL:
    print("Error: Could not find REACT_APP_BACKEND_URL in frontend/.env")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Test data for luxury cars
CAR_BRANDS = ["Mercedes", "Porsche", "Tesla", "BMW"]
CAR_MODELS = {
    "Mercedes": ["S-Class", "E-Class", "GLE", "AMG GT"],
    "Porsche": ["911", "Taycan", "Cayenne", "Panamera"],
    "Tesla": ["Model S", "Model 3", "Model X", "Model Y"],
    "BMW": ["7 Series", "5 Series", "X5", "i8"]
}
CAR_COLORS = ["Black", "White", "Silver", "Midnight Blue", "British Racing Green", "Burgundy"]

# Helper function to generate a random VIN
def generate_vin():
    chars = "0123456789ABCDEFGHJKLMNPRSTUVWXYZ"
    vin = "".join(random.choice(chars) for _ in range(17))
    return vin

# Helper function to format test results
def format_result(test_name, success, response=None, error=None):
    result = {
        "test": test_name,
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if response:
        if hasattr(response, 'json'):
            try:
                result["response"] = response.json()
            except:
                result["response"] = response.text
        else:
            result["response"] = response
            
    if error:
        result["error"] = str(error)
        
    return result

# Helper function to print test results
def print_result(result):
    status = "✅ PASSED" if result["success"] else "❌ FAILED"
    print(f"{status} - {result['test']}")
    
    if not result["success"] and "error" in result:
        print(f"  Error: {result['error']}")
    
    if "response" in result:
        if isinstance(result["response"], dict) or isinstance(result["response"], list):
            print(f"  Response: {json.dumps(result['response'], indent=2)}")
        else:
            print(f"  Response: {result['response']}")
    
    print()

# Test functions
def test_health_check():
    try:
        response = requests.get(f"{API_URL}/health")
        success = response.status_code == 200 and response.json().get("status") == "healthy"
        return format_result("Health Check", success, response)
    except Exception as e:
        return format_result("Health Check", False, error=str(e))

def test_create_user():
    try:
        user_data = {
            "name": "Alexander Hamilton",
            "email": "alex.hamilton@veluxe.com",
            "phone": "+1-555-123-4567",
            "membership_tier": random.choice(["Basic", "Premium", "Veluxe Elite"]),
            "created_at": datetime.now().isoformat()
        }
        
        response = requests.post(f"{API_URL}/users", json=user_data)
        success = response.status_code == 200 and "user_id" in response.json()
        result = format_result("Create User", success, response)
        
        if success:
            result["user_id"] = response.json()["user_id"]
            
        return result
    except Exception as e:
        return format_result("Create User", False, error=str(e))

def test_get_user(user_id):
    try:
        response = requests.get(f"{API_URL}/users/{user_id}")
        success = response.status_code == 200 and response.json().get("id") == user_id
        return format_result(f"Get User (ID: {user_id})", success, response)
    except Exception as e:
        return format_result(f"Get User (ID: {user_id})", False, error=str(e))

def test_add_car(user_id):
    try:
        brand = random.choice(CAR_BRANDS)
        model = random.choice(CAR_MODELS[brand])
        
        car_data = {
            "user_id": user_id,
            "brand": brand,
            "model": model,
            "year": random.randint(2018, 2024),
            "mileage": random.randint(1000, 50000),
            "last_service_date": (datetime.now() - timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d"),
            "vin": generate_vin(),
            "color": random.choice(CAR_COLORS)
        }
        
        response = requests.post(f"{API_URL}/cars", json=car_data)
        success = response.status_code == 200 and "car_id" in response.json()
        result = format_result("Add Car", success, response)
        
        if success:
            result["car_id"] = response.json()["car_id"]
            result["car_data"] = car_data
            
        return result
    except Exception as e:
        return format_result("Add Car", False, error=str(e))

def test_get_user_cars(user_id):
    try:
        response = requests.get(f"{API_URL}/cars/user/{user_id}")
        success = response.status_code == 200 and isinstance(response.json(), list)
        return format_result(f"Get User Cars (User ID: {user_id})", success, response)
    except Exception as e:
        return format_result(f"Get User Cars (User ID: {user_id})", False, error=str(e))

def test_get_car_health(car_id):
    try:
        response = requests.get(f"{API_URL}/car-health/{car_id}")
        success = response.status_code == 200 and response.json().get("car_id") == car_id
        return format_result(f"Get Car Health (Car ID: {car_id})", success, response)
    except Exception as e:
        return format_result(f"Get Car Health (Car ID: {car_id})", False, error=str(e))

def test_get_ai_predictions(car_id):
    try:
        response = requests.post(f"{API_URL}/ai-predictions/{car_id}")
        success = response.status_code == 200 and "overall_health" in response.json()
        return format_result(f"Get AI Predictions (Car ID: {car_id})", success, response)
    except Exception as e:
        return format_result(f"Get AI Predictions (Car ID: {car_id})", False, error=str(e))

def test_create_booking(user_id, car_id):
    try:
        # Generate a date 1-14 days in the future
        future_date = datetime.now() + timedelta(days=random.randint(1, 14))
        appointment_date = future_date.strftime("%Y-%m-%d")
        
        # Generate a time between 9 AM and 5 PM
        hour = random.randint(9, 17)
        minute = random.choice([0, 15, 30, 45])
        appointment_time = f"{hour:02d}:{minute:02d}"
        
        booking_data = {
            "user_id": user_id,
            "car_id": car_id,
            "service_type": random.choice(["Oil Change", "Brake Service", "Tire Rotation", "Full Inspection", "Battery Replacement"]),
            "pickup_type": random.choice(["white-glove", "in-garage"]),
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "special_instructions": "Please handle with extra care. Call before arrival."
        }
        
        response = requests.post(f"{API_URL}/bookings", json=booking_data)
        success = response.status_code == 200 and "booking_id" in response.json()
        result = format_result("Create Booking", success, response)
        
        if success:
            result["booking_id"] = response.json()["booking_id"]
            
        return result
    except Exception as e:
        return format_result("Create Booking", False, error=str(e))

def test_get_user_bookings(user_id):
    try:
        response = requests.get(f"{API_URL}/bookings/user/{user_id}")
        success = response.status_code == 200 and isinstance(response.json(), list)
        return format_result(f"Get User Bookings (User ID: {user_id})", success, response)
    except Exception as e:
        return format_result(f"Get User Bookings (User ID: {user_id})", False, error=str(e))

def test_get_events():
    try:
        response = requests.get(f"{API_URL}/events")
        success = response.status_code == 200 and isinstance(response.json(), list) and len(response.json()) > 0
        result = format_result("Get Events", success, response)
        
        if success and len(response.json()) > 0:
            result["event_id"] = response.json()[0]["id"]
            
        return result
    except Exception as e:
        return format_result("Get Events", False, error=str(e))

def test_rsvp_event(event_id, user_id):
    try:
        # Add user_id as a query parameter
        response = requests.post(f"{API_URL}/events/{event_id}/rsvp?user_id={user_id}")
        success = response.status_code == 200 and response.json().get("success") == True
        return format_result(f"RSVP to Event (Event ID: {event_id})", success, response)
    except Exception as e:
        return format_result(f"RSVP to Event (Event ID: {event_id})", False, error=str(e))

def run_all_tests():
    print("\n🔍 VELUXE BACKEND API TESTING 🔍\n")
    print(f"Testing against API URL: {API_URL}\n")
    
    results = []
    
    # Test health check
    health_result = test_health_check()
    results.append(health_result)
    print_result(health_result)
    
    if not health_result["success"]:
        print("❌ Health check failed. Aborting remaining tests.")
        return results
    
    # Test user creation and retrieval
    user_result = test_create_user()
    results.append(user_result)
    print_result(user_result)
    
    if not user_result["success"] or "user_id" not in user_result:
        print("❌ User creation failed. Aborting remaining tests.")
        return results
    
    user_id = user_result["user_id"]
    
    get_user_result = test_get_user(user_id)
    results.append(get_user_result)
    print_result(get_user_result)
    
    # Test car addition and retrieval
    car_result = test_add_car(user_id)
    results.append(car_result)
    print_result(car_result)
    
    if not car_result["success"] or "car_id" not in car_result:
        print("❌ Car addition failed. Aborting car-related tests.")
    else:
        car_id = car_result["car_id"]
        
        get_cars_result = test_get_user_cars(user_id)
        results.append(get_cars_result)
        print_result(get_cars_result)
        
        # Test car health and AI predictions
        car_health_result = test_get_car_health(car_id)
        results.append(car_health_result)
        print_result(car_health_result)
        
        ai_predictions_result = test_get_ai_predictions(car_id)
        results.append(ai_predictions_result)
        print_result(ai_predictions_result)
        
        # Test booking creation and retrieval
        booking_result = test_create_booking(user_id, car_id)
        results.append(booking_result)
        print_result(booking_result)
        
        get_bookings_result = test_get_user_bookings(user_id)
        results.append(get_bookings_result)
        print_result(get_bookings_result)
    
    # Test events and RSVP
    events_result = test_get_events()
    results.append(events_result)
    print_result(events_result)
    
    if not events_result["success"] or "event_id" not in events_result:
        print("❌ Events retrieval failed. Skipping RSVP test.")
    else:
        event_id = events_result["event_id"]
        
        rsvp_result = test_rsvp_event(event_id, user_id)
        results.append(rsvp_result)
        print_result(rsvp_result)
    
    # Print summary
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    
    print("\n📊 TEST SUMMARY 📊")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests / total_tests) * 100:.2f}%")
    
    if passed_tests == total_tests:
        print("\n✅ ALL TESTS PASSED! The Veluxe backend API is working correctly.")
    else:
        print("\n❌ SOME TESTS FAILED. Please check the detailed results above.")
    
    return results

if __name__ == "__main__":
    run_all_tests()