"""
YouthMind AI - Mental Health Support Chatbot
An AI-powered chatbot to support youth mental wellbeing through empathetic conversations,
mood tracking, and resource recommendations.

Created for YUVAi Global Youth Challenge 2025
Theme: Empowering people and communities
"""

from flask import Flask, render_template, request, jsonify, session
import json
import random
from datetime import datetime
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load mental health resources and responses
class MentalHealthBot:
    def __init__(self):
        self.mood_history = []
        self.conversation_context = []

        # Mental health keywords and responses
        self.keywords = {
            'anxious': ['anxiety', 'worried', 'nervous', 'stressed', 'panic'],
            'sad': ['sad', 'depressed', 'down', 'unhappy', 'lonely', 'hopeless'],
            'angry': ['angry', 'mad', 'frustrated', 'annoyed', 'irritated'],
            'happy': ['happy', 'good', 'great', 'excited', 'wonderful', 'awesome'],
            'tired': ['tired', 'exhausted', 'sleepy', 'fatigue', 'drained'],
            'confused': ['confused', 'lost', 'uncertain', 'unclear', 'stuck']
        }

        self.responses = {
            'anxious': [
                "I hear that you're feeling anxious. That's completely valid. Would you like to try a quick breathing exercise? Breathe in for 4 counts, hold for 4, and breathe out for 4.",
                "Anxiety can be overwhelming. Remember, it's okay to take things one step at a time. What's one small thing you can do right now to feel a bit calmer?",
                "Thank you for sharing. Anxiety is your mind trying to protect you, but sometimes it goes into overdrive. Let's ground ourselves - can you name 5 things you can see right now?"
            ],
            'sad': [
                "I'm sorry you're feeling down. Your feelings are valid, and it's brave of you to share them. Would you like to talk about what's on your mind?",
                "Sadness is a natural emotion, though it can feel heavy. Remember, it's temporary. What's one small thing that usually brings you comfort?",
                "Thank you for trusting me with this. Sometimes, just acknowledging our feelings can help. Would you like some suggestions for gentle activities that might help?"
            ],
            'angry': [
                "It sounds like you're feeling frustrated. That's understandable. Would it help to talk about what's triggering this feeling?",
                "Anger is a valid emotion. Sometimes it's telling us that something isn't right. Let's try to understand it together. What's at the root of this feeling?",
                "I hear your frustration. It takes courage to recognize and name our emotions. Would a quick physical activity like stretching or a brief walk help release some of that tension?"
            ],
            'happy': [
                "That's wonderful to hear! I'm so glad you're feeling good. What's bringing you joy today?",
                "It's great that you're in a positive space! These moments are precious. Would you like to note down what's working well for you?",
                "Your positive energy is amazing! Celebrating good moments is important for mental health. Keep nurturing what makes you feel this way!"
            ],
            'tired': [
                "Feeling exhausted can be really challenging. Are you getting enough rest? Sometimes our bodies need more recovery time than we think.",
                "Fatigue can be physical or emotional. Let's think about self-care - when was the last time you did something just for you?",
                "Being tired is your body's way of asking for attention. Can you take a short break today to recharge, even if just for 10 minutes?"
            ],
            'confused': [
                "Feeling uncertain is completely normal, especially during challenging times. Would it help to break down what's confusing you?",
                "Confusion often means we're processing a lot. Let's try to untangle this together. What's the main thing that feels unclear?",
                "It's okay not to have all the answers right now. Sometimes we need to sit with uncertainty. What's one small step you could take toward clarity?"
            ],
            'default': [
                "Thank you for sharing with me. I'm here to listen and support you. How are you feeling right now?",
                "I appreciate you opening up. Everyone's mental health journey is unique. What would be most helpful for you today?",
                "Your wellbeing matters. Would you like to talk about what's on your mind, or would you prefer some coping strategies?"
            ]
        }

        self.coping_strategies = {
            'breathing': "Try the 4-7-8 breathing technique: Breathe in for 4 seconds, hold for 7 seconds, breathe out for 8 seconds. Repeat 4 times.",
            'grounding': "Use the 5-4-3-2-1 technique: Name 5 things you see, 4 things you can touch, 3 things you hear, 2 things you smell, 1 thing you taste.",
            'journaling': "Try writing down your thoughts without judgment. Sometimes putting feelings on paper helps process them.",
            'movement': "Physical activity releases endorphins. Even a 5-minute walk or some stretching can help shift your mood.",
            'social': "Connecting with someone you trust can help. Consider reaching out to a friend, family member, or counselor.",
            'mindfulness': "Try a 5-minute mindfulness exercise: Focus on your breath and notice your thoughts without judging them."
        }

        self.emergency_resources = {
            'crisis': "If you're in immediate danger or having thoughts of self-harm, please reach out for help immediately.",
            'hotlines': {
                'International': 'https://www.opencounseling.com/suicide-hotlines',
                'India': 'AASRA: 91-22-27546669',
                'US': '988 Suicide & Crisis Lifeline',
                'UK': '116 123 (Samaritans)'
            }
        }

    def detect_mood(self, message):
        """Detect mood from user message"""
        message_lower = message.lower()

        # Check for crisis keywords
        crisis_keywords = ['suicide', 'kill myself', 'end my life', 'self-harm', 'hurt myself']
        if any(keyword in message_lower for keyword in crisis_keywords):
            return 'crisis'

        # Detect primary mood
        for mood, keywords in self.keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return mood

        return 'default'

    def get_response(self, message, mood_rating=None):
        """Generate appropriate response based on message and context"""
        mood = self.detect_mood(message)

        # Handle crisis situation
        if mood == 'crisis':
            return {
                'response': "I'm really concerned about what you've shared. Your life matters, and there are people who want to help. Please reach out to a crisis helpline immediately. Would you like me to provide you with emergency contact information?",
                'mood': 'crisis',
                'resources': self.emergency_resources,
                'urgent': True
            }

        # Normal conversation
        if mood in self.responses:
            response_text = random.choice(self.responses[mood])
        else:
            response_text = random.choice(self.responses['default'])

        # Add coping strategy suggestion occasionally
        suggest_coping = random.random() < 0.3
        coping_suggestion = None

        if suggest_coping and mood in ['anxious', 'sad', 'angry', 'tired']:
            strategy = random.choice(list(self.coping_strategies.keys()))
            coping_suggestion = {
                'title': strategy.capitalize(),
                'description': self.coping_strategies[strategy]
            }

        return {
            'response': response_text,
            'mood': mood,
            'coping_strategy': coping_suggestion,
            'urgent': False
        }

# Initialize bot
bot = MentalHealthBot()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        mood_rating = data.get('mood_rating', None)

        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Get bot response
        bot_response = bot.get_response(message, mood_rating)

        # Store mood if rating provided
        if mood_rating:
            if 'mood_history' not in session:
                session['mood_history'] = []
            session['mood_history'].append({
                'rating': mood_rating,
                'timestamp': datetime.now().isoformat()
            })
            session.modified = True

        return jsonify(bot_response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mood-history')
def mood_history():
    """Get mood tracking history"""
    history = session.get('mood_history', [])
    return jsonify(history)

@app.route('/resources')
def resources():
    """Get mental health resources"""
    resources = {
        'hotlines': bot.emergency_resources['hotlines'],
        'coping_strategies': bot.coping_strategies,
        'articles': [
            {
                'title': 'Understanding Anxiety',
                'url': 'https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response'
            },
            {
                'title': 'Teen Mental Health',
                'url': 'https://www.nimh.nih.gov/health/topics/child-and-adolescent-mental-health'
            }
        ]
    }
    return jsonify(resources)

@app.route('/clear-session')
def clear_session():
    """Clear session data"""
    session.clear()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
