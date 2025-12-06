# Stock Slackbot Scaffold

A simple Slackbot application written with FastAPI and Python Async

## What this scaffold does

This repository provides a minimal Slack bot backend:

- Exposes `POST /slack/events` to receive Slack Events API callbacks
- Verifies Slack signatures (using `SLACK_SIGNING_SECRET`)
- Handles basic `message` events and reactions via a small `handlers.py` module
- Is structured so you can add your own routes, commands, and background logic

It does **not** include any business logic – it's meant as a clean starting point.

# Pre-requisites

- Configure a [Slack application](https://docs.slack.dev/tools/bolt-python/building-an-app) in your workspace. Include the following permissions and event subscriptions:
    - Actions: `chat:write`
    - Information: `channels:history`, `reactions:read`
    - Events: `message.channels`, `reaction_added`
- Setup a free [Ngrok account](https://ngrok.com/pricing) to expose the bot to the world.

# Runtime Environment Configuration

This scaffold uses a single environment variable, `RUNTIME_ENVIRONMENT_TYPE`, to determine how the bot loads secrets and what safety rules apply.
This ensures a clean separation between local development and deployable environments.

| Value            | Description                               | Allowed Secret Source        |
|------------------|-------------------------------------------|-------------------------------|
| development      | Local development on a laptop             | `.env` file                   |
| non-production   | Staging, preview, sandbox environments    | Environment variables only    |
| production       | Production deployments                    | Environment variables only    |

## 🚀 Running the Slack Bot

### 🧪 Local Development

- Clone this repository
- Create a new virtualenv `python -m ~/path/to/stock-slackbot-scafofld`
- Activate virtualenv `source bin ~/path/to/stock-slackbot-scafofld/bin/activate`
- Install pre-requisites `pip install -r requirements.txt`
- For local testing, create a .env file (`touch .env`) in the root directory and populate the following fields:
    - SLACK_BOT_TOKEN
    - SLACK_SIGNING_SECRET
    - SLACK_CLIENT_ID
    - SLACK_CLIENT_SECRET
    - SLACK_BOT_USER_ID

- Expose it to the world
`ngrok http --url=noticeably-nearby-dory.ngrok-free.app 8000`

- Start the bot
`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## From a container

> **Reminder**: Start ngrok (see above)

- Docker run
```
docker run -e SLACK_BOT_TOKEN=your-slack-bot-token \
  -e SLACK_SIGNING_SECRET=your-signing-secret \
  -e SLACK_CLIENT_ID=your-client-id \
  -e SLACK_CLIENT_SECRET=your-client-secret \
  -p 8000:8000 \
  talaniz/stock-slackbot-scaffold:latest
  ```