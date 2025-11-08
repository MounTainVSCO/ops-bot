from bots.base_bot import NotionSlackBot

class FeedbackBot(NotionSlackBot):
    def run(self):
        """Custom feedback bot logic."""
        items = self.get_items()
        for item in items:
            title = item["properties"]["Name"]["title"][0]["plain_text"]
            sentiment = item["properties"].get("Sentiment", {}).get("select", {}).get("name", "Unknown")
            summary = item["properties"].get("Summary", {}).get("rich_text", [])
            summary_text = summary[0]["plain_text"] if summary else "No summary"
            msg = f"💭 *New Feedback:* {title}\n🧠 Sentiment: {sentiment}\n📝 {summary_text}"
            self.send_slack(msg)
