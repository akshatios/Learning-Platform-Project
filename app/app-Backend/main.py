from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.database import connect_to_mongo, close_mongo_connection
from core.routes import api_router
from middleware.auth_middleware import AuthMiddleware
from chatbot.enhanced_routes import router as chatbot_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(title="Learning Platform App Backend", version="1.0.0", lifespan=lifespan)

# Middleware
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(chatbot_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Learning Platform App Backend API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)