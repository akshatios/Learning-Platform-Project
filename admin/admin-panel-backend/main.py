from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import connect_to_mongo, close_mongo_connection
from core.routes import api_router
from middleware.auth_middleware import AuthMiddleware
from middleware.allowed_hosts import AllowedHostsMiddleware

app = FastAPI(title="Learning Platform Admin Panel", version="1.0.0")

# Middleware
app.add_middleware(AllowedHostsMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Learning Platform Admin Panel API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)