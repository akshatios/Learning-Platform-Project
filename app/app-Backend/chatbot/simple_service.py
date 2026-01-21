from fastapi import HTTPException
from typing import Dict, Any, Optional
import json
import os
import logging
from datetime import datetime
from core.database import get_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleChatbotService:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
    async def get_response(self, user_message: str, user_id: str = None, user_context: Dict = None) -> Dict[str, Any]:
        """Generate response using Gemini API"""
        try:
            # Get course context
            course_context = await self._get_course_context(user_message)
            
            # Classify intent
            intent = self._classify_intent(user_message)
            
            # Generate response
            if self.gemini_api_key:
                response_text = self._call_gemini_api(user_message, course_context, intent)
            else:
                response_text = self._get_fallback_response(user_message, intent, course_context)
            
            return {
                "response": response_text,
                "intent": intent,
                "sources": course_context[:3],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I'm experiencing technical difficulties. Please try again or contact support.",
                "intent": "error",
                "sources": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_course_context(self, query: str) -> list:
        """Get relevant courses from database"""
        try:
            db = get_database()
            courses_collection = db.courses
            
            # Get all courses first
            all_courses = await courses_collection.find().to_list(length=10)
            logger.info(f"Found {len(all_courses)} total courses")
            
            # Simple keyword search
            keywords = query.lower().split()
            search_terms = [keyword for keyword in keywords if len(keyword) > 2]
            logger.info(f"All search terms: {search_terms}")
            
            if search_terms:
                # Filter out generic terms
                filtered_terms = [term for term in search_terms if term not in ['course', 'courses', 'class', 'tutorial', 'want', 'buy', 'purchase', 'about', 'the', 'how', 'but']]
                logger.info(f"Filtered search terms: {filtered_terms}")
                
                if filtered_terms:
                    # Search for specific terms only
                    courses = []
                    for term in filtered_terms:
                        logger.info(f"Searching for term: {term}")
                        # Try exact match first
                        exact_matches = await courses_collection.find({"title": {"$regex": f"^{term}$", "$options": "i"}}).to_list(length=5)
                        logger.info(f"Exact matches for '{term}': {len(exact_matches)}")
                        courses.extend(exact_matches)
                        
                        # If no exact matches, try partial matches
                        if not exact_matches:
                            partial_matches = await courses_collection.find({
                                "$or": [
                                    {"title": {"$regex": term, "$options": "i"}},
                                    {"description": {"$regex": term, "$options": "i"}}
                                ]
                            }).to_list(length=3)
                            logger.info(f"Partial matches for '{term}': {len(partial_matches)}")
                            courses.extend(partial_matches)
                    
                    # Remove duplicates
                    seen = set()
                    unique_courses = []
                    for course in courses:
                        course_id = str(course.get('_id'))
                        if course_id not in seen:
                            seen.add(course_id)
                            unique_courses.append(course)
                    
                    courses = unique_courses[:5]
                    logger.info(f"Found {len(courses)} matching courses after filtering")
                else:
                    # No specific terms, check if asking for all courses
                    if any(word in query.lower() for word in ['available', 'all', 'show', 'list']):
                        courses = all_courses[:5]
                        logger.info(f"Showing all available courses: {len(courses)}")
                    else:
                        courses = []
            else:
                courses = all_courses[:5]
            
            result = [{"title": course.get("title", ""), "description": course.get("description", ""), "price": course.get("price", 0)} for course in courses]
            logger.info(f"Returning courses: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting course context: {e}")
            return []
    
    def _classify_intent(self, message: str) -> str:
        """Simple intent classification"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["course", "learn", "study", "tutorial"]):
            return "course_inquiry"
        elif any(word in message_lower for word in ["enroll", "buy", "purchase", "payment", "price"]):
            return "enrollment_help"
        elif any(word in message_lower for word in ["error", "problem", "issue", "help", "support"]):
            return "technical_support"
        elif any(word in message_lower for word in ["path", "career", "roadmap", "recommend"]):
            return "learning_path"
        else:
            return "general_info"
    
    def _call_gemini_api(self, message: str, course_context: list, intent: str) -> str:
        """Call Gemini API using REST API"""
        try:
            import requests
            
            api_key = self.gemini_api_key
            if not api_key:
                return self._get_fallback_response(message, intent, course_context)
            
            # Build context
            context_text = ""
            if course_context:
                context_text = f"IMPORTANT: Our platform currently has exactly {len(course_context)} courses available:\n"
                for course in course_context[:5]:
                    context_text += f"- {course['title']}: {course['description']} (${course['price']})\n"
                context_text += "\nPlease use ONLY this information about available courses. Do not make up numbers or mention courses not listed above.\n"
            
            # Create prompt
            system_prompt = self._get_system_prompt(intent)
            full_prompt = f"{system_prompt}\n\nIMPORTANT: Only use the course information provided in the context. Do not invent or assume additional courses exist.\n\nUser Query: {message}\n\nContext: {context_text}\n\nPlease provide a helpful but CONCISE response (maximum 3-4 sentences) using ONLY the context provided:"
            
            # Call Gemini REST API
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    return text.strip()
            
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return self._get_fallback_response(message, intent, course_context)
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._get_fallback_response(message, intent, course_context)
    
    def _get_system_prompt(self, intent: str) -> str:
        """Get system prompt based on intent"""
        prompts = {
            "course_inquiry": "You are a helpful learning platform assistant. Help users find and understand courses. Be friendly, informative and CONCISE.",
            "enrollment_help": "You are a learning platform assistant helping with enrollment and payments. Provide clear, SHORT guidance on how to enroll.",
            "technical_support": "You are a technical support assistant. Help users resolve platform issues with BRIEF step-by-step instructions.",
            "learning_path": "You are a career guidance assistant. Help users plan their learning journey with SHORT, focused recommendations.",
            "general_info": "You are a friendly learning platform assistant. Answer questions about the platform and courses helpfully but BRIEFLY."
        }
        return prompts.get(intent, prompts["general_info"])
    
    def _get_fallback_response(self, message: str, intent: str, course_context: list) -> str:
        """Generate fallback response without API"""
        
        if intent == "course_inquiry":
            if course_context:
                response = "Here are some courses that might interest you:\n\n"
                for course in course_context[:3]:
                    response += f"📚 **{course['title']}**\n{course['description']}\nPrice: ${course['price']}\n\n"
                response += "Would you like to know more about any of these courses?"
                return response
            else:
                if any(word in message.lower() for word in ['available', 'all', 'show', 'list']):
                    return "Let me show you all available courses. Please wait while I fetch them for you!"
                return "I'd be happy to help you find courses! Could you tell me what subject you're interested in learning?"
        
        elif intent == "enrollment_help":
            return """To enroll in a course:
            
1. 📋 Browse available courses
2. 💳 Click 'Buy Now' on your chosen course  
3. 🔐 Complete payment securely
4. 🎓 Start learning immediately!

Need help with a specific course? Let me know which one!"""
        
        elif intent == "technical_support":
            return """I'm here to help with technical issues! 

Common solutions:
• 🔄 Try refreshing the page
• 🧹 Clear your browser cache
• 🌐 Check your internet connection
• 📱 Try a different browser

Still having trouble? Please describe the specific issue you're experiencing."""
        
        elif intent == "learning_path":
            return """I can help you plan your learning journey! 🎯

Popular learning paths:
• **Web Development**: HTML/CSS → JavaScript → React/Node.js
• **Data Science**: Python → Statistics → Machine Learning
• **Mobile Development**: Java/Kotlin → Android or Swift → iOS

What's your career goal? I'll suggest the best path for you!"""
        
        else:
            return """Hi! I'm your learning assistant 👋

I can help you with:
• 📚 Finding courses
• 💳 Enrollment guidance  
• 🛠️ Technical support
• 🎯 Learning path recommendations

What would you like to know?"""
    
    def clear_memory(self, user_id: str = None):
        """Clear conversation memory (placeholder)"""
        logger.info(f"Memory cleared for user: {user_id}")
    
    def refresh_knowledge_base(self):
        """Refresh knowledge base (placeholder)"""
        logger.info("Knowledge base refresh requested")
    
    def get_conversation_history(self, user_id: str) -> list:
        """Get conversation history (placeholder)"""
        return []