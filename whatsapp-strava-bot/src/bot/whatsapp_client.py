import requests
import os
from typing import Optional


class WhatsAppClient:
    """Client to communicate with WhatsApp bot API"""

    def __init__(self, api_url: str = None):
        self.api_url = api_url or "http://localhost:3000"
        self.group_id = os.getenv('WHATSAPP_GROUP_ID')

    def send_message(self, message: str, group_id: str = None) -> bool:
        """
        Send a message to WhatsApp group

        Args:
            message: Message to send
            group_id: Optional group ID (uses default if not provided)

        Returns:
            True if successful, False otherwise
        """
        target_group = group_id or self.group_id

        if not target_group:
            print("❌ No WhatsApp group ID configured")
            return False

        try:
            response = requests.post(
                f"{self.api_url}/send-message",
                json={
                    'message': message,
                    'groupId': target_group
                },
                timeout=10
            )

            if response.status_code == 200:
                print("✅ Message sent successfully")
                return True
            else:
                print(f"❌ Failed to send message: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False

    def is_ready(self) -> bool:
        """Check if WhatsApp bot is ready"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'ready'
        except Exception as e:
            print(f"❌ Error checking WhatsApp bot status: {e}")

        return False

    def get_groups(self) -> list:
        """Get list of available WhatsApp groups"""
        try:
            response = requests.get(f"{self.api_url}/groups", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('groups', [])
        except Exception as e:
            print(f"❌ Error getting groups: {e}")

        return []
