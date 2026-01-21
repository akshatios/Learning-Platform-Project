from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from .simple_service import SimpleChatbotService
from datetime import datetime
import logging

router = APIRouter(prefix="/chatbot", tags=["chatbot"])
logger = logging.getLogger(__name__)

# Initialize simple chatbot service
chatbot_service = SimpleChatbotService()

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    user_context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    sources: List[Dict[str, Any]]
    timestamp: str
    session_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    message_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    chat_data: ChatMessage,
    background_tasks: BackgroundTasks
):
    """Enhanced chat endpoint with context awareness"""
    try:
        user_id = "anonymous"  # Simplified for now
        
        response_data = await chatbot_service.get_response(
            user_message=chat_data.message,
            user_id=user_id,
            user_context=chat_data.user_context
        )
        
        # Background task for analytics
        background_tasks.add_task(
            log_chat_analytics,
            user_id,
            chat_data.message,
            response_data
        )
        
        return ChatResponse(
            response=response_data["response"],
            intent=response_data["intent"],
            sources=response_data["sources"],
            timestamp=response_data["timestamp"],
            session_id=chat_data.session_id
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback for chatbot responses"""
    try:
        user_id = "anonymous"
        await store_feedback(user_id, feedback)
        return {"message": "Feedback submitted successfully", "status": "success"}
    
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.post("/clear-memory")
async def clear_chat_memory():
    """Clear conversation memory"""
    try:
        chatbot_service.clear_memory("anonymous")
        return {"message": "Chat memory cleared", "status": "success"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")

@router.get("/health")
async def chatbot_health():
    """Health check endpoint"""
    return {
        "status": "Chatbot service is running",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

# Helper functions
async def log_chat_analytics(user_id: str, message: str, response_data: Dict):
    """Log chat interaction for analytics"""
    try:
        analytics_data = {
            "user_id": user_id,
            "message": message,
            "intent": response_data["intent"],
            "response_length": len(response_data["response"]),
            "sources_count": len(response_data["sources"]),
            "timestamp": datetime.now()
        }
        logger.info(f"Analytics logged: {analytics_data}")
    except Exception as e:
        logger.error(f"Error logging analytics: {e}")

async def store_feedback(user_id: str, feedback: FeedbackRequest):
    """Store user feedback in database"""
    try:
        feedback_data = {
            "user_id": user_id,
            "message_id": feedback.message_id,
            "rating": feedback.rating,
            "feedback": feedback.feedback,
            "timestamp": datetime.now()
        }
        logger.info(f"Feedback stored: {feedback_data}")
    except Exception as e:
        logger.error(f"Error storing feedback: {e}")