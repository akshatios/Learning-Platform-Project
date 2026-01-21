from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from typing import Dict, List

class ChatbotPrompts:
    
    # System prompt for learning platform assistant
    SYSTEM_PROMPT = """You are an intelligent learning platform assistant for a comprehensive online education platform. Your role is to help students, teachers, and administrators with:

1. Course Information & Recommendations
2. Learning Path Guidance
3. Technical Support
4. Platform Navigation
5. Enrollment & Payment Queries
6. Progress Tracking

PERSONALITY TRAITS:
- Friendly, professional, and encouraging
- Patient with beginners
- Knowledgeable about education and technology
- Proactive in offering relevant suggestions

RESPONSE GUIDELINES:
- Keep responses concise but informative
- Use bullet points for multiple items
- Always provide actionable next steps
- Ask clarifying questions when needed
- Suggest relevant courses when appropriate

AVAILABLE COURSE CATEGORIES:
- Programming (Python, Java, JavaScript, etc.)
- Data Science & AI
- Web Development
- Mobile Development
- Cloud Computing
- Cybersecurity
- Digital Marketing
- Design & UI/UX

PLATFORM FEATURES:
- Course enrollment and payment
- Progress tracking and certificates
- Interactive assignments and quizzes
- Live sessions and recorded lectures
- Community forums and peer interaction
- Career guidance and job placement support"""

    # Course recommendation prompt
    COURSE_RECOMMENDATION_PROMPT = PromptTemplate(
        input_variables=["user_query", "user_level", "available_courses", "user_interests"],
        template="""
        Based on the user's query and profile, recommend the most suitable courses:
        
        User Query: {user_query}
        User Level: {user_level}
        User Interests: {user_interests}
        
        Available Courses:
        {available_courses}
        
        Provide 3 specific course recommendations with:
        1. Course name and brief description
        2. Why it matches their needs
        3. Expected learning outcomes
        4. Difficulty level and duration
        
        Format as a friendly, encouraging response.
        """
    )

    # Technical support prompt
    TECHNICAL_SUPPORT_PROMPT = PromptTemplate(
        input_variables=["issue_description", "user_role", "platform_section"],
        template="""
        Help resolve this technical issue:
        
        Issue: {issue_description}
        User Role: {user_role}
        Platform Section: {platform_section}
        
        Provide:
        1. Step-by-step troubleshooting
        2. Common causes and solutions
        3. When to contact support
        4. Prevention tips
        
        Be clear and non-technical in explanations.
        """
    )

    # Learning path guidance prompt
    LEARNING_PATH_PROMPT = PromptTemplate(
        input_variables=["career_goal", "current_skills", "time_commitment", "available_courses"],
        template="""
        Create a personalized learning path:
        
        Career Goal: {career_goal}
        Current Skills: {current_skills}
        Time Commitment: {time_commitment}
        
        Available Courses:
        {available_courses}
        
        Suggest:
        1. Sequential course order
        2. Estimated timeline
        3. Key milestones
        4. Skill progression
        5. Portfolio projects
        
        Make it motivating and achievable.
        """
    )

    # Enrollment assistance prompt
    ENROLLMENT_PROMPT = PromptTemplate(
        input_variables=["course_name", "user_query", "pricing_info", "enrollment_status"],
        template="""
        Assist with course enrollment:
        
        Course: {course_name}
        Query: {user_query}
        Pricing: {pricing_info}
        Status: {enrollment_status}
        
        Provide information about:
        1. Enrollment process
        2. Payment options
        3. Course access details
        4. Refund policy
        5. Next steps
        
        Be helpful and address any concerns.
        """
    )

    @staticmethod
    def get_chat_prompt_template():
        """Returns the main chat prompt template"""
        system_message = SystemMessagePromptTemplate.from_template(ChatbotPrompts.SYSTEM_PROMPT)
        human_message = HumanMessagePromptTemplate.from_template(
            """
            Context Information:
            {context}
            
            User Query: {user_input}
            
            Please provide a helpful response based on the context and your knowledge of the learning platform.
            """
        )
        
        return ChatPromptTemplate.from_messages([system_message, human_message])

    @staticmethod
    def get_intent_classification_prompt():
        """Classifies user intent for better response routing"""
        return PromptTemplate(
            input_variables=["user_input"],
            template="""
            Classify the user's intent from the following message:
            "{user_input}"
            
            Possible intents:
            1. course_inquiry - asking about specific courses
            2. enrollment_help - need help with enrollment/payment
            3. technical_support - platform issues or bugs
            4. learning_path - career guidance and course recommendations
            5. progress_tracking - questions about progress, certificates
            6. general_info - basic platform information
            7. other - doesn't fit above categories
            
            Respond with only the intent category.
            """
        )