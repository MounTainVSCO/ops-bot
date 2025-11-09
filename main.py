import os
import sys
from dotenv import load_dotenv
from bots.role.feedback_bot import FeedbackBot

def main():
    """Main entry point for the feedback bot."""
    # Load .env.local if it exists (for local development)
    # In GitHub Actions, environment variables are set directly
    load_dotenv(".env.local", override=False)
    
    try:
        # Get environment variables - support both naming conventions
        notion_db = os.getenv("NOTION_FEEDBACK_DB") or os.getenv("NOTION_DATABASE_ID")
        slack_webhook = os.getenv("SLACK_FEEDBACK_WEBHOOK") or os.getenv("SLACK_WEBHOOK_URL") or os.getenv("SLACK_WEBHOOK")
        
        # Check for introduction mode
        # Can be triggered via environment variable or command line argument
        mode = os.getenv("BOT_MODE", "").lower()
        if len(sys.argv) > 1:
            # Join all arguments in case user passes a phrase like "introduce yourself to the people"
            mode = " ".join(sys.argv[1:]).lower()
        
        print(f"🔍 Debug: Mode detected = '{mode}'", file=sys.stderr)
        print(f"🔍 Debug: BOT_MODE env = '{os.getenv('BOT_MODE', '')}'", file=sys.stderr)
        print(f"🔍 Debug: Command line args = {sys.argv[1:]}", file=sys.stderr)
        
        bot = FeedbackBot(
            notion_db=notion_db,
            slack_webhook=slack_webhook,
            bot_name="Feedback"
        )
        
        # Check if user wants introduction (handles various phrases)
        intro_keywords = ["introduce", "intro", "introduce yourself"]
        if any(keyword in mode for keyword in intro_keywords):
            print("✅ Running in introduction mode", file=sys.stderr)
            bot.introduce()
        else:
            print("✅ Running in normal feedback mode", file=sys.stderr)
            bot.run()
            print("✅ Feedback bot completed successfully")
            
    except ValueError as e:
        print(f"❌ Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running feedback bot: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
