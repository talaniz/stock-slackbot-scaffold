"""Main module for Stock Slackbot Scaffold.

Environment Handling
--------------------
This application uses the RUNTIME_ENVIRONMENT_TYPE variable to determine how
secrets are loaded and which safety rules apply.

Valid values:
  - "development"
  - "non-production"
  - "production"

Behavior:
  • If RUNTIME_ENVIRONMENT_TYPE is not set, the app defaults to "development".
  • Any other unexpected value will cause the application to raise an exception.

Secret Loading Rules:
  • development:
        - A local .env file must exist.
        - Secrets are read from the .env file.
  • non-production / production:
        - .env files are disallowed and will trigger an exception.
        - Required Slack secrets must be provided as environment variables:
              SLACK_BOT_USER_ID
              SLACK_BOT_TOKEN
              SLACK_SIGNING_SECRET

These constraints ensure a safe local workflow and a secure, deployable
configuration for staging and production environments.

"""
import asyncio
import os

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request

from app.slack.router import handle_slack_event
from lib.logging_config import logger

VALID_ENVIRONMENTS = {"development", "production", "non-production"}

env = os.getenv("RUNTIME_ENVIRONMENT_TYPE")

if env is None:
    env = "development"
    os.environ["RUNTIME_ENVIRONMENT_TYPE"] = env
    logger.info("RUNTIME_ENVIRONMENT_TYPE not set. Defaulting to 'development'.")
else:
    env = env.lower().strip()
    if env not in VALID_ENVIRONMENTS:
        raise ValueError(
            f"Invalid RUNTIME_ENVIRONMENT_TYPE '{env}'. Must be one of "
            f"{', '.join(VALID_ENVIRONMENTS)}."
        )
    logger.info(f"RUNTIME_ENVIRONMENT_TYPE detected: '{env}'")

# Handle .env file usage rules

dotenv_path = Path(".env")
dotenv_exists = dotenv_path.exists()

if env == "development":
    if dotenv_exists:
        logger.info(".env file found. Loading environment variables for development.")
        load_dotenv()

        # Required values for all environments
        missing = []
        required_vars = [
            "SLACK_BOT_USER_ID",
            "SLACK_BOT_TOKEN",
            "SLACK_SIGNING_SECRET",
        ]

        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)

        if missing:
            raise EnvironmentError(
                f"Missing required environment variables in development: {', '.join(missing)}"
            )
    else:
        logger.info("No .env file present — relying only on system environment variables.")

else:
    # Non-development environments
    if dotenv_exists:
        raise EnvironmentError(
            f".env file cannot be used when RUNTIME_ENVIRONMENT_TYPE = '{env}'. "
            "Use real environment variables instead."
        )

    # Validate required system environment variables
    missing = []
    for var in ["SLACK_BOT_USER_ID", "SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET"]:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        raise EnvironmentError(
            f"Missing required environment variables for {env}: {', '.join(missing)}"
        )

    logger.info(f"All required environment variables present for '{env}'.")

app = FastAPI()

# Slack API Base URL
SLACK_API_URL = "https://slack.com/api/chat.postMessage"


@app.post("/slack/events")
async def slack_events(request: Request):
    """Handles incoming Slack messages and responds if bot is mentioned."""
    payload = await request.json()

    # Slack challenge verification (for initial setup)
    if "challenge" in payload:
        return {"challenge": payload["challenge"]}

    asyncio.create_task(handle_slack_event(payload))
    return {"status": "ok"}

