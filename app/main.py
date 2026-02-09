from fastapi import FastAPI
from app.api.v1.route_appointment import router as route_appointment
from app.api.v1.route_availability import router as route_availability
from app.api.v1.route_user import router as route_user
from app.api.v1.route_auth import router as route_auth
from app.api.v1.route_provider_service import router as route_provider_service
from app.api.v1.route_service import router as route_service

app = FastAPI(
    title="Appointment Booking System",
    description="this is a course management with minimal usage of authentication and post managing",
    contact={"name": "Kamran Rezaei"},
    )



@app.get("/")
async def health_check():
    return {"message": "Appointment Booking System API is running 🚀"}

app.include_router(route_auth)
app.include_router(route_user)
app.include_router(route_service)
app.include_router(route_provider_service)
app.include_router(route_availability)
app.include_router(route_appointment)