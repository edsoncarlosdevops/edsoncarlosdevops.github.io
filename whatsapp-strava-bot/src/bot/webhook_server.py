from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
import os
from datetime import datetime
from typing import Optional

from src.database.models import DatabaseManager
from src.strava.client import StravaClient
from src.rankings.calculator import RankingCalculator
from src.bot.whatsapp_client import WhatsAppClient


app = FastAPI(title="Strava WhatsApp Bot")

# Initialize components
db_manager = DatabaseManager()
strava_client = StravaClient()
ranking_calc = RankingCalculator()
whatsapp_client = WhatsAppClient()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "running", "service": "Strava WhatsApp Bot"}


@app.get("/webhook")
async def verify_webhook(
    request: Request,
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """
    Verify Strava webhook subscription
    This endpoint is called by Strava to verify the webhook
    """
    print(f"🔍 Webhook verification request received")
    print(f"Mode: {hub_mode}, Token: {hub_verify_token}")

    verify_token = os.getenv('STRAVA_VERIFY_TOKEN')

    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        print("✅ Webhook verified successfully")
        return JSONResponse(content={"hub.challenge": hub_challenge})
    else:
        print("❌ Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle Strava webhook events
    Called when an athlete creates a new activity
    """
    try:
        data = await request.json()
        print(f"📥 Webhook event received: {data}")

        # Check if it's a new activity
        if data.get('object_type') != 'activity':
            return {"status": "ignored", "reason": "not an activity"}

        if data.get('aspect_type') != 'create':
            return {"status": "ignored", "reason": "not a creation event"}

        # Get activity details
        activity_id = data.get('object_id')
        owner_id = data.get('owner_id')

        print(f"🏃 New activity detected: ID={activity_id}, Athlete={owner_id}")

        # Get athlete from database to get access token
        athlete = db_manager.get_athlete_by_strava_id(owner_id)

        if not athlete:
            print(f"⚠️ Athlete {owner_id} not found in database")
            return {"status": "ignored", "reason": "athlete not registered"}

        if not athlete.access_token:
            print(f"⚠️ Athlete {owner_id} has no access token")
            return {"status": "ignored", "reason": "no access token"}

        # Get activity details from Strava
        activity_data = strava_client.get_activity(activity_id, athlete.access_token)

        if not activity_data:
            print(f"❌ Failed to get activity details for {activity_id}")
            return {"status": "error", "reason": "failed to get activity"}

        # Only process running activities
        if activity_data['type'] != 'Run':
            print(f"⚠️ Activity {activity_id} is not a run, ignoring")
            return {"status": "ignored", "reason": "not a run"}

        # Save activity to database
        activity = db_manager.add_activity(
            strava_activity_id=activity_data['id'],
            athlete_strava_id=owner_id,
            athlete_name=f"{athlete.name}",
            name=activity_data['name'],
            distance=activity_data['distance'],
            moving_time=int(activity_data['moving_time']),
            elapsed_time=int(activity_data['elapsed_time']),
            activity_type=activity_data['type'],
            start_date=activity_data['start_date']
        )

        # Send WhatsApp notification
        message = ranking_calc.get_activity_notification(
            athlete_name=athlete.name,
            distance=activity_data['distance'],
            moving_time=int(activity_data['moving_time']),
            activity_name=activity_data['name']
        )

        success = whatsapp_client.send_message(message)

        if success:
            db_manager.mark_activity_notified(activity_id)
            print(f"✅ Notification sent for activity {activity_id}")
        else:
            print(f"⚠️ Failed to send notification for activity {activity_id}")

        return {"status": "processed", "activity_id": activity_id}

    except Exception as e:
        print(f"❌ Error handling webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/ranking/weekly")
async def get_weekly_ranking():
    """Get weekly ranking"""
    try:
        start_date, end_date = ranking_calc.get_week_range()
        activities = db_manager.get_activities_by_period(start_date, end_date)
        ranking = ranking_calc.calculate_ranking(activities)
        message = ranking_calc.format_ranking_message(ranking, "semanal")

        return {"message": message, "ranking": ranking}
    except Exception as e:
        print(f"❌ Error getting weekly ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ranking/monthly")
async def get_monthly_ranking():
    """Get monthly ranking"""
    try:
        start_date, end_date = ranking_calc.get_month_range()
        activities = db_manager.get_activities_by_period(start_date, end_date)
        ranking = ranking_calc.calculate_ranking(activities)
        message = ranking_calc.format_ranking_message(ranking, "mensal")

        return {"message": message, "ranking": ranking}
    except Exception as e:
        print(f"❌ Error getting monthly ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/strava/auth")
async def strava_auth():
    """Get Strava authorization URL"""
    webhook_url = os.getenv('WEBHOOK_URL', 'http://localhost:8000')
    redirect_uri = f"{webhook_url}/strava/callback"
    auth_url = strava_client.get_authorization_url(redirect_uri)
    return {"auth_url": auth_url}


@app.get("/strava/callback")
async def strava_callback(code: str, scope: str):
    """Handle Strava OAuth callback"""
    try:
        # Exchange code for token
        token_response = strava_client.exchange_code_for_token(code)

        # Get athlete info
        access_token = token_response['access_token']
        athlete_data = strava_client.get_athlete(access_token)

        if not athlete_data:
            raise HTTPException(status_code=400, detail="Failed to get athlete info")

        # Save to database
        athlete = db_manager.add_athlete(
            strava_id=athlete_data['id'],
            name=f"{athlete_data['firstname']} {athlete_data['lastname']}",
            access_token=token_response['access_token'],
            refresh_token=token_response['refresh_token'],
            token_expires_at=datetime.fromtimestamp(token_response['expires_at'])
        )

        return {
            "status": "success",
            "message": f"Athlete {athlete_data['firstname']} {athlete_data['lastname']} registered successfully!"
        }

    except Exception as e:
        print(f"❌ Error in callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/strava/webhook/subscribe")
async def subscribe_webhook():
    """Subscribe to Strava webhooks"""
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        raise HTTPException(status_code=400, detail="WEBHOOK_URL not configured")

    callback_url = f"{webhook_url}/webhook"
    subscription_id = strava_client.subscribe_to_webhook(callback_url)

    if subscription_id:
        return {"status": "success", "subscription_id": subscription_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to subscribe to webhook")


@app.get("/strava/webhook/subscriptions")
async def get_subscriptions():
    """Get current webhook subscriptions"""
    subscriptions = strava_client.get_subscriptions()
    return {"subscriptions": subscriptions}


@app.get("/athletes")
async def list_athletes():
    """List all registered athletes"""
    session = db_manager.get_session()
    try:
        from src.database.models import Athlete
        athletes = session.query(Athlete).all()
        result = [{
            'id': a.id,
            'strava_id': a.strava_id,
            'name': a.name,
            'phone_number': a.phone_number
        } for a in athletes]
        return {"athletes": result}
    finally:
        session.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('WEBHOOK_PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
