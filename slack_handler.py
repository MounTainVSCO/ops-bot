"""
Slack event handler for receiving commands from Slack.
This can be deployed as a serverless function or run as a service.
"""
import os
import json
import hmac
import hashlib
import time
import requests
from flask import Flask, request, jsonify
from bots.role.feedback_bot import FeedbackBot

app = Flask(__name__)

# Get Slack credentials
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

def verify_slack_request(request):
    """Verify that the request came from Slack."""
    if not SLACK_SIGNING_SECRET:
        return True  # Skip verification if secret not set (for development)
    
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False  # Request is older than 5 minutes
    
    sig_basestring = f"v0:{timestamp}:{request.get_data(as_text=True)}"
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    slack_signature = request.headers.get('X-Slack-Signature', '')
    return hmac.compare_digest(my_signature, slack_signature)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    """Handle Slack events."""
    if not verify_slack_request(request):
        return jsonify({'error': 'Invalid request'}), 403
    
    data = request.json
    
    # URL verification challenge
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})
    
    # Handle event callbacks
    if data.get('type') == 'event_callback':
        event = data.get('event', {})
        
        # Only process app_mentions (when bot is mentioned)
        if event.get('type') == 'app_mentions':
            text = event.get('text', '').lower()
            channel = event.get('channel')
            
            # Check for introduction command
            if 'introduce' in text or 'intro' in text:
                bot = FeedbackBot(
                    notion_db=os.getenv("NOTION_DATABASE_ID"),
                    slack_webhook=os.getenv("SLACK_WEBHOOK"),
                    bot_name="Feedback"
                )
                bot.introduce()
                return jsonify({'status': 'ok'})
            
            # Check for feedback command
            elif 'feedback' in text or 'show' in text or 'list' in text:
                bot = FeedbackBot(
                    notion_db=os.getenv("NOTION_DATABASE_ID"),
                    slack_webhook=os.getenv("SLACK_WEBHOOK"),
                    bot_name="Feedback"
                )
                bot.run()
                return jsonify({'status': 'ok'})
    
    return jsonify({'status': 'ok'})

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

