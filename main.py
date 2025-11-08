import os
from bots.feedback_bot import FeedbackBot

def main():
    bot = FeedbackBot(
        notion_db=os.getenv("NOTION_FEEDBACK_DB"),
        slack_webhook=os.getenv("SLACK_FEEDBACK_WEBHOOK"),
        bot_name="Feedback"
    )
    bot.run()

if __name__ == "__main__":
    main()
