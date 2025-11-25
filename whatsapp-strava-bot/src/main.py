#!/usr/bin/env python3
"""
Main entry point for the Strava WhatsApp Bot
Starts both the WhatsApp bot (Node.js) and the webhook server (Python)
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def start_whatsapp_bot():
    """Start the WhatsApp bot (Node.js)"""
    print("🚀 Starting WhatsApp bot...")
    return subprocess.Popen(
        ['node', 'src/whatsapp/bot.js'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )


def start_webhook_server():
    """Start the webhook server (Python FastAPI)"""
    print("🚀 Starting webhook server...")
    port = int(os.getenv('WEBHOOK_PORT', 8000))

    return subprocess.Popen(
        ['uvicorn', 'src.bot.webhook_server:app', '--host', '0.0.0.0', '--port', str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )


def main():
    """Main function to start all services"""
    print("=" * 60)
    print("🏃‍♂️ Strava WhatsApp Bot")
    print("=" * 60)

    # Check environment variables
    required_vars = ['STRAVA_CLIENT_ID', 'STRAVA_CLIENT_SECRET', 'STRAVA_VERIFY_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return 1

    processes = []

    try:
        # Start WhatsApp bot
        whatsapp_process = start_whatsapp_bot()
        processes.append(('WhatsApp Bot', whatsapp_process))
        time.sleep(3)  # Give it time to start

        # Start webhook server
        webhook_process = start_webhook_server()
        processes.append(('Webhook Server', webhook_process))

        print("\n✅ All services started successfully!")
        print("\n📋 Next steps:")
        print("1. Scan the QR code with WhatsApp")
        print("2. Set the WHATSAPP_GROUP_ID in .env file")
        print("3. Register athletes by visiting: http://localhost:8000/strava/auth")
        print("4. Subscribe to Strava webhooks (see documentation)")
        print("\nPress Ctrl+C to stop all services\n")

        # Monitor processes
        while True:
            for name, process in processes:
                output = process.stdout.readline()
                if output:
                    print(f"[{name}] {output.strip()}")

                # Check if process died
                if process.poll() is not None:
                    print(f"❌ {name} stopped unexpectedly")
                    return 1

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping all services...")

    finally:
        for name, process in processes:
            print(f"Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

        print("✅ All services stopped")

    return 0


if __name__ == "__main__":
    sys.exit(main())
