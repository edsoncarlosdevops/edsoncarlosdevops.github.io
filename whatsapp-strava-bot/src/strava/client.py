import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from stravalib.client import Client


class StravaClient:
    """Client for interacting with Strava API"""

    def __init__(self):
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.verify_token = os.getenv('STRAVA_VERIFY_TOKEN')

        if not all([self.client_id, self.client_secret]):
            raise ValueError("Strava credentials not found in environment variables")

    def get_authorization_url(self, redirect_uri: str = 'http://localhost:8000/strava/callback') -> str:
        """Generate authorization URL for OAuth"""
        client = Client()
        url = client.authorization_url(
            client_id=self.client_id,
            redirect_uri=redirect_uri,
            scope=['activity:read_all', 'profile:read_all']
        )
        return url

    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        client = Client()
        token_response = client.exchange_code_for_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            code=code
        )
        return token_response

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh an expired access token"""
        client = Client()
        token_response = client.refresh_access_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=refresh_token
        )
        return token_response

    def get_activity(self, activity_id: int, access_token: str) -> Optional[Dict]:
        """Get detailed activity information"""
        client = Client(access_token=access_token)
        try:
            activity = client.get_activity(activity_id)
            return {
                'id': activity.id,
                'name': activity.name,
                'distance': float(activity.distance) / 1000,  # Convert to km
                'moving_time': activity.moving_time.total_seconds() if activity.moving_time else 0,
                'elapsed_time': activity.elapsed_time.total_seconds() if activity.elapsed_time else 0,
                'type': activity.type,
                'start_date': activity.start_date,
                'athlete_id': activity.athlete.id
            }
        except Exception as e:
            print(f"Error getting activity {activity_id}: {e}")
            return None

    def get_athlete(self, access_token: str) -> Optional[Dict]:
        """Get athlete information"""
        client = Client(access_token=access_token)
        try:
            athlete = client.get_athlete()
            return {
                'id': athlete.id,
                'firstname': athlete.firstname,
                'lastname': athlete.lastname,
                'username': athlete.username
            }
        except Exception as e:
            print(f"Error getting athlete info: {e}")
            return None

    def get_athlete_activities(self, access_token: str, after: datetime = None,
                              before: datetime = None, limit: int = 30) -> List[Dict]:
        """Get athlete activities"""
        client = Client(access_token=access_token)
        try:
            activities = client.get_activities(after=after, before=before, limit=limit)
            result = []
            for activity in activities:
                if activity.type == 'Run':  # Only running activities
                    result.append({
                        'id': activity.id,
                        'name': activity.name,
                        'distance': float(activity.distance) / 1000,  # Convert to km
                        'moving_time': activity.moving_time.total_seconds() if activity.moving_time else 0,
                        'elapsed_time': activity.elapsed_time.total_seconds() if activity.elapsed_time else 0,
                        'type': activity.type,
                        'start_date': activity.start_date
                    })
            return result
        except Exception as e:
            print(f"Error getting activities: {e}")
            return []

    def subscribe_to_webhook(self, callback_url: str) -> Optional[int]:
        """Subscribe to Strava webhook events"""
        url = "https://www.strava.com/api/v3/push_subscriptions"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'callback_url': callback_url,
            'verify_token': self.verify_token
        }

        try:
            response = requests.post(url, data=data)
            if response.status_code == 201:
                subscription_id = response.json().get('id')
                print(f"Successfully subscribed to webhook. Subscription ID: {subscription_id}")
                return subscription_id
            else:
                print(f"Failed to subscribe to webhook: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error subscribing to webhook: {e}")
            return None

    def get_subscriptions(self) -> List[Dict]:
        """Get current webhook subscriptions"""
        url = "https://www.strava.com/api/v3/push_subscriptions"
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get subscriptions: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error getting subscriptions: {e}")
            return []

    def delete_subscription(self, subscription_id: int) -> bool:
        """Delete a webhook subscription"""
        url = f"https://www.strava.com/api/v3/push_subscriptions/{subscription_id}"
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        try:
            response = requests.delete(url, params=params)
            return response.status_code == 204
        except Exception as e:
            print(f"Error deleting subscription: {e}")
            return False
