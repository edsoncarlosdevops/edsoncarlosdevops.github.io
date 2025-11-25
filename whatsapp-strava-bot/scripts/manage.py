#!/usr/bin/env python3
"""
Management script for Strava WhatsApp Bot
Useful commands for administration
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.database.models import DatabaseManager
from src.strava.client import StravaClient

load_dotenv()


def list_athletes():
    """List all registered athletes"""
    db = DatabaseManager()
    session = db.get_session()

    try:
        from src.database.models import Athlete
        athletes = session.query(Athlete).all()

        if not athletes:
            print("No athletes registered yet.")
            return

        print(f"\n{'ID':<10} {'Strava ID':<12} {'Name':<30} {'Phone':<20}")
        print("-" * 72)

        for athlete in athletes:
            phone = athlete.phone_number or 'N/A'
            print(f"{athlete.id:<10} {athlete.strava_id:<12} {athlete.name:<30} {phone:<20}")

        print(f"\nTotal: {len(athletes)} athlete(s)")
    finally:
        session.close()


def list_activities(limit=10):
    """List recent activities"""
    db = DatabaseManager()
    session = db.get_session()

    try:
        from src.database.models import Activity
        activities = session.query(Activity).order_by(
            Activity.start_date.desc()
        ).limit(limit).all()

        if not activities:
            print("No activities found.")
            return

        print(f"\n{'ID':<8} {'Athlete':<25} {'Distance':<12} {'Date':<20} {'Notified'}")
        print("-" * 90)

        for activity in activities:
            notified = "✅" if activity.notified else "❌"
            date_str = activity.start_date.strftime("%Y-%m-%d %H:%M")
            print(f"{activity.id:<8} {activity.athlete_name:<25} {activity.distance:<12.2f} {date_str:<20} {notified}")

        print(f"\nShowing {len(activities)} most recent activities")
    finally:
        session.close()


def get_webhook_info():
    """Get current webhook subscriptions"""
    client = StravaClient()
    subscriptions = client.get_subscriptions()

    if not subscriptions:
        print("No webhook subscriptions found.")
        print("\nTo create a subscription, run:")
        print("  curl -X POST http://localhost:8000/strava/webhook/subscribe")
        return

    print(f"\nActive webhook subscriptions:")
    print("-" * 60)

    for sub in subscriptions:
        print(f"ID: {sub['id']}")
        print(f"Callback URL: {sub['callback_url']}")
        print(f"Created: {sub.get('created_at', 'N/A')}")
        print("-" * 60)


def delete_webhook(subscription_id):
    """Delete a webhook subscription"""
    client = StravaClient()

    if client.delete_subscription(int(subscription_id)):
        print(f"✅ Subscription {subscription_id} deleted successfully")
    else:
        print(f"❌ Failed to delete subscription {subscription_id}")


def show_stats():
    """Show general statistics"""
    db = DatabaseManager()
    session = db.get_session()

    try:
        from src.database.models import Athlete, Activity
        from sqlalchemy import func

        total_athletes = session.query(func.count(Athlete.id)).scalar()
        total_activities = session.query(func.count(Activity.id)).scalar()
        total_distance = session.query(func.sum(Activity.distance)).scalar() or 0

        print("\n📊 Statistics")
        print("-" * 40)
        print(f"Total athletes: {total_athletes}")
        print(f"Total activities: {total_activities}")
        print(f"Total distance: {total_distance:.2f} km")

        if total_activities > 0:
            avg_distance = total_distance / total_activities
            print(f"Average distance per run: {avg_distance:.2f} km")

    finally:
        session.close()


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/manage.py <command>")
        print("\nAvailable commands:")
        print("  list-athletes              - List all registered athletes")
        print("  list-activities [limit]    - List recent activities (default: 10)")
        print("  webhook-info               - Show webhook subscriptions")
        print("  webhook-delete <id>        - Delete a webhook subscription")
        print("  stats                      - Show general statistics")
        return 1

    command = sys.argv[1]

    if command == "list-athletes":
        list_athletes()
    elif command == "list-activities":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_activities(limit)
    elif command == "webhook-info":
        get_webhook_info()
    elif command == "webhook-delete":
        if len(sys.argv) < 3:
            print("Error: subscription ID required")
            return 1
        delete_webhook(sys.argv[2])
    elif command == "stats":
        show_stats()
    else:
        print(f"Unknown command: {command}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
