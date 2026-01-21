class ChatbotWidget {
    constructor() {
        this.isOpen = false;
        this.apiUrl = 'http://127.0.0.1:8001/api/v1/chatbot';
        this.sessionId = this.generateSessionId();
        this.isTyping = false;
        this.messageQueue = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadChatHistory();
        this.initializeQuickActions();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    bindEvents() {
        const toggle = document.getElementById('chatbot-toggle');
        const close = document.getElementById('chatbot-close');
        const send = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');
        const clearBtn = document.getElementById('chatbot-clear');

        toggle.addEventListener('click', () => this.toggleChat());
        close.addEventListener('click', () => this.closeChat());
        send.addEventListener('click', () => this.sendMessage());
        clearBtn?.addEventListener('click', () => this.clearChat());
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        input.addEventListener('input', () => this.autoResizeInput(input));
    }

    initializeQuickActions() {
        const quickActions = [
            { text: "Show available courses", action: "courses" },
            { text: "How to enroll?", action: "enrollment" },
            { text: "Learning paths", action: "paths" },
            { text: "Technical support", action: "support" }
        ];

        const container = document.getElementById('quick-actions');
        if (container) {
            quickActions.forEach(action => {
                const btn = document.createElement('button');
                btn.className = 'quick-action-btn';
                btn.textContent = action.text;
                btn.onclick = () => this.handleQuickAction(action.action);
                container.appendChild(btn);
            });
        }
    }

    handleQuickAction(action) {
        const messages = {
            courses: "What courses are available?",
            enrollment: "How do I enroll in a course?",
            paths: "Can you suggest a learning path for me?",
            support: "I need technical support"
        };

        const message = messages[action];
        if (message) {
            document.getElementById('chatbot-input').value = message;
            this.sendMessage();
        }
    }

    autoResizeInput(input) {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    }

    toggleChat() {
        const container = document.getElementById('chatbot-container');
        
        if (this.isOpen) {
            this.closeChat();
        } else {
            container.classList.remove('hidden');
            this.isOpen = true;
            this.focusInput();
        }
    }

    closeChat() {
        const container = document.getElementById('chatbot-container');
        container.classList.add('hidden');
        this.isOpen = false;
    }

    focusInput() {
        setTimeout(() => {
            document.getElementById('chatbot-input').focus();
        }, 300);
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message || this.isTyping) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        input.value = '';
        input.style.height = 'auto';

        // Show typing indicator
        this.showTypingIndicator();
        this.isTyping = true;

        try {
            const response = await this.callChatbotAPI(message);
            this.hideTypingIndicator();
            this.addMessage(response.response, 'bot', {
                intent: response.intent,
                sources: response.sources,
                timestamp: response.timestamp
            });
            
            // Show feedback buttons for bot messages
            this.addFeedbackButtons(response.timestamp);
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot', { error: true });
            console.error('Chatbot API error:', error);
        } finally {
            this.isTyping = false;
        }
    }

    async callChatbotAPI(message) {
        const token = localStorage.getItem('authToken');
        const userContext = this.getUserContext();
        
        const response = await fetch(`${this.apiUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : ''
            },
            body: JSON.stringify({
                message: message,
                user_context: userContext,
                session_id: this.sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    getUserContext() {
        // Get user context from localStorage or current page
        return {
            enrolled_courses: JSON.parse(localStorage.getItem('enrolledCourses') || '[]'),
            user_level: localStorage.getItem('userLevel') || 'beginner',
            interests: JSON.parse(localStorage.getItem('userInterests') || '[]'),
            current_page: window.location.pathname
        };
    }

    addMessage(content, type, metadata = {}) {
        const messagesContainer = document.getElementById('chatbot-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        messageDiv.dataset.timestamp = metadata.timestamp || Date.now();
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (type === 'bot' && metadata.sources && metadata.sources.length > 0) {
            contentDiv.innerHTML = `
                <div class="message-text">${content}</div>
                <div class="message-sources">
                    <small>Sources: ${metadata.sources.map(s => s.title).join(', ')}</small>
                </div>
            `;
        } else {
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(contentDiv);
        
        // Add intent badge for bot messages
        if (type === 'bot' && metadata.intent) {
            const intentBadge = document.createElement('span');
            intentBadge.className = 'intent-badge';
            intentBadge.textContent = metadata.intent.replace('_', ' ');
            messageDiv.appendChild(intentBadge);
        }
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        this.saveChatHistory();
    }

    addFeedbackButtons(messageId) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const lastMessage = messagesContainer.lastElementChild;
        
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'feedback-buttons';
        feedbackDiv.innerHTML = `
            <button class="feedback-btn thumbs-up" onclick="chatbot.submitFeedback('${messageId}', 5)">
                <i class="fas fa-thumbs-up"></i>
            </button>
            <button class="feedback-btn thumbs-down" onclick="chatbot.submitFeedback('${messageId}', 1)">
                <i class="fas fa-thumbs-down"></i>
            </button>
        `;
        
        lastMessage.appendChild(feedbackDiv);
    }

    async submitFeedback(messageId, rating) {
        try {
            const token = localStorage.getItem('authToken');
            
            await fetch(`${this.apiUrl}/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : ''
                },
                body: JSON.stringify({
                    message_id: messageId,
                    rating: rating
                })
            });
            
            // Visual feedback
            const feedbackBtns = document.querySelectorAll(`[onclick*="${messageId}"]`);
            feedbackBtns.forEach(btn => {
                btn.style.opacity = '0.5';
                btn.disabled = true;
            });
            
        } catch (error) {
            console.error('Error submitting feedback:', error);
        }
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages');
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message';
        typingDiv.id = 'typing-indicator';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'typing-indicator';
        typingContent.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        typingDiv.appendChild(typingContent);
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async clearChat() {
        try {
            const token = localStorage.getItem('authToken');
            
            await fetch(`${this.apiUrl}/clear-memory`, {
                method: 'POST',
                headers: {
                    'Authorization': token ? `Bearer ${token}` : ''
                }
            });
            
            this.clearChatHistory();
            
        } catch (error) {
            console.error('Error clearing chat:', error);
        }
    }

    saveChatHistory() {
        const messages = document.getElementById('chatbot-messages').innerHTML;
        localStorage.setItem(`chatHistory_${this.sessionId}`, messages);
    }

    loadChatHistory() {
        const savedHistory = localStorage.getItem(`chatHistory_${this.sessionId}`);
        if (savedHistory) {
            document.getElementById('chatbot-messages').innerHTML = savedHistory;
        } else {
            this.showWelcomeMessage();
        }
    }

    showWelcomeMessage() {
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.innerHTML = `
            <div class="message bot-message">
                <div class="message-content">
                    <div class="welcome-message">
                        <h4>👋 Hi! I'm your Learning Assistant</h4>
                        <p>I can help you with:</p>
                        <ul>
                            <li>🎓 Course recommendations</li>
                            <li>📝 Enrollment guidance</li>
                            <li>🛤️ Learning paths</li>
                            <li>🔧 Technical support</li>
                        </ul>
                        <p>What would you like to know?</p>
                    </div>
                </div>
            </div>
        `;
    }

    clearChatHistory() {
        localStorage.removeItem(`chatHistory_${this.sessionId}`);
        this.showWelcomeMessage();
    }
}

// Initialize chatbot when DOM is loaded
let chatbot;
document.addEventListener('DOMContentLoaded', () => {
    chatbot = new ChatbotWidget();
});