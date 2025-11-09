import sys
from bots.base_bot import NotionSlackBot


class FeedbackBot(NotionSlackBot):
    def run(self):
        """Custom feedback bot logic - shows all feedback items in one message."""
        try:
            items = self.get_items()
            if not items:
                self.send_slack("ℹ️ No feedback items found in Notion database.")
                print(f"ℹ️ No items found in Notion database", file=sys.stderr)
                return
            
            # Build formatted message with all items
            message_parts = [f"📊 *All Feedback Items ({len(items)} total)*\n"]
            
            for idx, item in enumerate(items, 1):
                try:
                    # Safely extract title
                    title_prop = item.get("properties", {}).get("Name", {}).get("title", [])
                    title = title_prop[0].get("plain_text", "Untitled") if title_prop else "Untitled"
                    
                    # Safely extract sentiment
                    sentiment_prop = item.get("properties", {}).get("Sentiment", {}).get("select")
                    sentiment = sentiment_prop.get("name", "Unknown") if sentiment_prop else "Unknown"
                    
                    # Safely extract summary
                    summary_prop = item.get("properties", {}).get("Summary", {}).get("rich_text", [])
                    summary_text = summary_prop[0].get("plain_text", "No summary") if summary_prop else "No summary"
                    
                    # Format each item
                    item_text = f"\n*{idx}. {title}*\n"
                    item_text += f"   🧠 Sentiment: {sentiment}\n"
                    item_text += f"   📝 Summary: {summary_text[:200]}{'...' if len(summary_text) > 200 else ''}"
                    
                    message_parts.append(item_text)
                except Exception as e:
                    print(f"⚠️ Error processing feedback item {idx}: {e}", file=sys.stderr)
                    message_parts.append(f"\n*{idx}. [Error processing item]*")
                    continue
            
            # Send all items in one message
            full_message = "\n".join(message_parts)
            self.send_slack(full_message)
            print(f"✅ Sent {len(items)} feedback items to Slack")
            
        except Exception as e:
            print(f"❌ Error in feedback bot run: {e}", file=sys.stderr)
            self.send_slack(f"❌ Error fetching feedback: {str(e)}")
            raise
