import os
import json
from slack_bolt import App
from dotenv import load_dotenv
from fastapi import FastAPI

from broker import cloudamqp
from chatgpt_helper import chagptify_text

# Load environment variables from .env file
load_dotenv()

# Initializes your app with your bot token
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

fastapi_app = FastAPI()


def post_response_to_slack(slack_message, slack_channel, thread_ts):
    message = f"\n {slack_message} \n"
    
    app.client.chat_postMessage(
        channel=slack_channel,
        text=message,
        thread_ts=thread_ts
    )


def callback(ch, method, properties, body):
    """ 
    The logic for sending messages to Open API and posting the 
    response to Slack
    """
    body = json.loads(body.decode('utf-8'))
    chatgpt_prompt = body.get("prompt")
    slack_channel = body.get("channel")
    thread_ts = body.get("thread_ts")
    
    # Generate ChatGPT response to user prompt
    chatgpt_response = chagptify_text(message=chatgpt_prompt)

    # Send code recommendation to Slack
    post_response_to_slack(
        slack_message=chatgpt_response, 
        slack_channel=slack_channel,
        thread_ts=thread_ts
    )


def main():
    cloudamqp.consume_message(callback=callback)
    

# Run the app with a FastAPI server
@fastapi_app.on_event("startup")
def startup_event():
    """ Code to run during startup """
    main()


@fastapi_app.on_event("shutdown")
def shutdown_event():
    """ Code to run during shutdown """
    pass