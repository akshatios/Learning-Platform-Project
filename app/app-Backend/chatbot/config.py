import os
from typing import Dict, Any
from pydantic import BaseSettings

class ChatbotConfig(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 1000
    
    # Vector Store Configuration
    VECTOR_STORE_TYPE: str = "faiss"  # faiss, pinecone, chroma
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    VECTOR_DIMENSION: int = 1536
    
    # Memory Configuration
    MEMORY_WINDOW_SIZE: int = 10
    MAX_CONVERSATION_LENGTH: int = 50
    
    # Response Configuration
    MAX_RESPONSE_LENGTH: int = 500
    RESPONSE_TIMEOUT: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 20
    RATE_LIMIT_PER_HOUR: int = 100
    
    # Analytics Configuration
    ENABLE_ANALYTICS: bool = True
    ANALYTICS_RETENTION_DAYS: int = 90
    
    # Feedback Configuration
    ENABLE_FEEDBACK: bool = True
    MIN_FEEDBACK_RATING: int = 1
    MAX_FEEDBACK_RATING: int = 5
    
    # Cache Configuration
    ENABLE_CACHE: bool = True
    CACHE_TTL_SECONDS: int = 3600
    
    # Security Configuration
    ENABLE_CONTENT_FILTER: bool = True
    MAX_MESSAGE_LENGTH: int = 1000
    
    class Config:
        env_file = ".env"

# Global configuration instance
chatbot_config = ChatbotConfig()

# Intent classification mappings
INTENT_MAPPINGS = {
    "course_inquiry": [
        "course", "class", "lesson", "tutorial", "learn", "study",
        "programming", "python", "java", "javascript", "web development"
    ],
    "enrollment_help": [
        "enroll", "register", "signup", "payment", "buy", "purchase",
        "price", "cost", "fee", "subscription"
    ],
    "technical_support": [
        "error", "bug", "problem", "issue", "not working", "broken",
        "help", "support", "troubleshoot"
    ],
    "learning_path": [
        "career", "path", "roadmap", "guidance", "recommend", "suggest",
        "beginner", "advanced", "next step"
    ],
    "progress_tracking": [
        "progress", "certificate", "completion", "grade", "score",
        "achievement", "badge"
    ]
}

# Response templates for different intents
RESPONSE_TEMPLATES = {
    "greeting": [
        "Hello! I'm your learning assistant. How can I help you today?",
        "Hi there! I'm here to help with your learning journey. What would you like to know?",
        "Welcome! I can help you with courses, enrollment, and learning guidance. What's on your mind?"
    ],
    "course_not_found": [
        "I couldn't find specific courses matching your query. Let me show you some popular options:",
        "No exact matches found, but here are some related courses you might be interested in:",
        "I don't see that specific course, but I can recommend similar alternatives:"
    ],
    "enrollment_success": [
        "Great choice! Here's how to enroll in this course:",
        "Perfect! Let me guide you through the enrollment process:",
        "Excellent selection! Here's what you need to do next:"
    ],
    "technical_issue": [
        "I understand you're experiencing a technical issue. Let me help you resolve it:",
        "Technical problems can be frustrating. Here's how we can fix this:",
        "Let's troubleshoot this issue step by step:"
    ]
}

# Course categories and their descriptions
COURSE_CATEGORIES = {
    "programming": {
        "name": "Programming & Development",
        "description": "Learn coding languages and software development",
        "popular_courses": ["Python", "JavaScript", "Java", "C++"]
    },
    "data_science": {
        "name": "Data Science & AI",
        "description": "Master data analysis, machine learning, and AI",
        "popular_courses": ["Machine Learning", "Data Analysis", "Deep Learning"]
    },
    "web_development": {
        "name": "Web Development",
        "description": "Build modern websites and web applications",
        "popular_courses": ["React", "Node.js", "HTML/CSS", "Full Stack"]
    },
    "mobile_development": {
        "name": "Mobile Development",
        "description": "Create mobile apps for iOS and Android",
        "popular_courses": ["React Native", "Flutter", "iOS Development"]
    },
    "cloud_computing": {
        "name": "Cloud Computing",
        "description": "Learn cloud platforms and DevOps practices",
        "popular_courses": ["AWS", "Azure", "Docker", "Kubernetes"]
    },
    "cybersecurity": {
        "name": "Cybersecurity",
        "description": "Protect systems and data from cyber threats",
        "popular_courses": ["Ethical Hacking", "Network Security", "CISSP"]
    }
}

# Skill level mappings
SKILL_LEVELS = {
    "beginner": {
        "description": "New to the subject, no prior experience",
        "recommended_duration": "2-4 months",
        "prerequisites": "None"
    },
    "intermediate": {
        "description": "Some experience, familiar with basics",
        "recommended_duration": "1-3 months",
        "prerequisites": "Basic knowledge required"
    },
    "advanced": {
        "description": "Experienced, looking to master advanced concepts",
        "recommended_duration": "1-2 months",
        "prerequisites": "Strong foundation required"
    }
}