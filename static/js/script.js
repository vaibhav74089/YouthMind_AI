// YouthMind AI - Client-side JavaScript

class ChatApp {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.emergencyBanner = document.getElementById('emergency-banner');
        this.moodFeedback = document.getElementById('mood-feedback');
        this.currentMood = null;

        this.init();
    }

    init() {
        // Event listeners
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Mood selector
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectMood(e.target));
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });

        // Set initial timestamp
        this.updateTimestamp();
    }

    selectMood(btn) {
        // Remove previous selection
        document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));

        // Add selection
        btn.classList.add('selected');
        this.currentMood = btn.getAttribute('data-mood');

        // Show feedback
        const moodLabels = {
            '1': 'I hear you. It's okay to not be okay. 💙',
            '2': 'Thank you for sharing. Let's work through this together.',
            '3': 'That's perfectly fine. Every day is different.',
            '4': 'Great to hear! Keep up the positive energy! ✨',
            '5': 'Wonderful! What's making you feel so good? 🌟'
        };

        this.moodFeedback.textContent = moodLabels[this.currentMood];
        this.moodFeedback.style.animation = 'fadeIn 0.3s ease-out';
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();

        if (!message) return;

        // Disable input while processing
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;

        // Add user message to chat
        this.addMessage(message, 'user');

        // Clear input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    mood_rating: this.currentMood
                })
            });

            const data = await response.json();

            // Remove typing indicator
            this.removeTypingIndicator();

            // Handle crisis situation
            if (data.urgent) {
                this.showEmergencyBanner();
            }

            // Add bot response
            this.addMessage(data.response, 'bot', data.coping_strategy);

        } catch (error) {
            console.error('Error:', error);
            this.removeTypingIndicator();
            this.addMessage('I'm sorry, I'm having trouble connecting right now. Please try again in a moment.', 'bot');
        }

        // Re-enable input
        this.messageInput.disabled = false;
        this.sendBtn.disabled = false;
        this.messageInput.focus();
    }

    addMessage(text, type, copingStrategy = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Split text into paragraphs
        const paragraphs = text.split('\n').filter(p => p.trim());
        paragraphs.forEach(para => {
            const p = document.createElement('p');
            p.textContent = para;
            contentDiv.appendChild(p);
        });

        // Add coping strategy if provided
        if (copingStrategy) {
            const strategyDiv = document.createElement('div');
            strategyDiv.className = 'coping-strategy';
            strategyDiv.innerHTML = `
                <h4>💡 ${copingStrategy.title}</h4>
                <p>${copingStrategy.description}</p>
            `;
            contentDiv.appendChild(strategyDiv);
        }

        messageDiv.appendChild(contentDiv);

        // Add timestamp
        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = this.getTimestamp();
        messageDiv.appendChild(timestamp);

        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message bot-message typing-indicator';
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        this.chatContainer.appendChild(indicator);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    showEmergencyBanner() {
        this.emergencyBanner.classList.remove('hidden');
        this.scrollToBottom();
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    getTimestamp() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    updateTimestamp() {
        const timestamps = document.querySelectorAll('.timestamp');
        timestamps.forEach(ts => {
            if (!ts.textContent) {
                ts.textContent = this.getTimestamp();
            }
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

// Service Worker for offline support (optional enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/sw.js');
    });
}