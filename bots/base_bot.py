import os
import requests
import sys
from typing import Optional, List, Dict, Any


class NotionSlackBot:
    def __init__(self, notion_db: Optional[str], slack_webhook: Optional[str], bot_name: str):
        """Initialize the Notion-Slack bot with validation."""
        self.notion_db = notion_db or os.getenv("NOTION_DATABASE_ID")
        self.slack_webhook = slack_webhook or os.getenv("SLACK_WEBHOOK_URL")
        self.bot_name = bot_name
        self.notion_token = os.getenv("NOTION_TOKEN")
        
        # Validate required environment variables
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN environment variable is required")
        if not self.notion_db:
            raise ValueError("NOTION_DATABASE_ID or notion_db parameter is required")
        if not self.slack_webhook:
            raise ValueError("SLACK_WEBHOOK_URL or slack_webhook parameter is required")
        
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def get_items(self) -> List[Dict[str, Any]]:
        """Query Notion database and return ALL items (handles pagination)."""
        try:
            url = f"https://api.notion.com/v1/databases/{self.notion_db}/query"
            all_items = []
            has_more = True
            start_cursor = None
            
            while has_more:
                payload = {}
                if start_cursor:
                    payload["start_cursor"] = start_cursor
                
                res = requests.post(url, headers=self.headers, json=payload)
                res.raise_for_status()
                data = res.json()
                
                items = data.get("results", [])
                all_items.extend(items)
                
                has_more = data.get("has_more", False)
                if has_more:
                    start_cursor = data.get("next_cursor")
            
            return all_items
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching from Notion: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}", file=sys.stderr)
            raise

    def send_slack(self, text: str, blocks: Optional[List[Dict[str, Any]]] = None) -> None:
        """Send a message to Slack via webhook. Handles long messages by splitting."""
        # Slack has a limit of ~4000 characters per message
        MAX_MESSAGE_LENGTH = 3500  # Leave some buffer
        
        try:
            if len(text) <= MAX_MESSAGE_LENGTH:
                # Message is short enough, send as-is
                payload = {"text": text}
                if blocks:
                    payload["blocks"] = blocks
                res = requests.post(self.slack_webhook, json=payload)
                res.raise_for_status()
            else:
                # Split message into chunks
                chunks = []
                current_chunk = ""
                lines = text.split("\n")
                
                for line in lines:
                    if len(current_chunk) + len(line) + 1 > MAX_MESSAGE_LENGTH:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = line + "\n"
                    else:
                        current_chunk += line + "\n"
                
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Send each chunk
                for i, chunk in enumerate(chunks, 1):
                    chunk_text = f"*Part {i}/{len(chunks)}*\n{chunk}"
                    payload = {"text": chunk_text}
                    res = requests.post(self.slack_webhook, json=payload)
                    res.raise_for_status()
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending to Slack: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}", file=sys.stderr)
            raise

    def introduce(self) -> None:
        """Send an introduction message to Slack."""
        intro_message = f"""👋 *Hello! I'm the {self.bot_name} Bot!*

*What I do:*
• I monitor your Notion database for feedback items
• I automatically sync feedback from Notion to Slack
• I help keep your team informed about user feedback and sentiment

*My capabilities:*
• 📊 Fetch all feedback items from your Notion database
• 🧠 Track sentiment analysis
• 📝 Summarize feedback for quick review
• ⚡ Run automatically on schedule or on-demand

*How to use me:*
• I run automatically every day at 9 AM UTC
• You can also trigger me manually via GitHub Actions
• Just say "introduce yourself" to see this message again!

*Current configuration:*
• Monitoring Notion database: `{self.notion_db[:20]}...` (ID hidden for security)
• Bot name: {self.bot_name}

Let me know if you need anything! 🚀"""
        self.send_slack(intro_message)
        print(f"✅ Introduction sent to Slack")

    def run(self):
        """Default behavior, can be overridden."""
        items = self.get_items()
        for item in items:
            try:
                title_prop = item.get("properties", {}).get("Name", {}).get("title", [])
                title = title_prop[0].get("plain_text", "Untitled") if title_prop else "Untitled"
                self.send_slack(f"💬 Feedback item: {title}")
            except Exception as e:
                print(f"⚠️ Error processing item: {e}", file=sys.stderr)
                continue
