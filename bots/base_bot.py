import os
import requests

class NotionSlackBot:
    def __init__(self, notion_db, slack_webhook, bot_name):
        self.notion_db = notion_db
        self.slack_webhook = slack_webhook
        self.bot_name = bot_name
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def get_items(self):
        url = f"https://api.notion.com/v1/databases/{self.notion_db}/query"
        res = requests.post(url, headers=self.headers)
        res.raise_for_status()
        return res.json().get("results", [])

    def send_slack(self, text):
        payload = {"text": text}
        res = requests.post(self.slack_webhook, json=payload)
        res.raise_for_status()

    def run(self):
        """Default behavior, can be overridden."""
        for item in self.get_items():
            title = item["properties"]["Name"]["title"][0]["plain_text"]
            self.send_slack(f"💬 Feedback item: {title}")
