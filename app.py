#! usr/bin/env python3

"""
[Script holds data for request/response into proper channels.]
"""

import os
import datetime
import logging
import requests

from slack_sdk import WebClient
from flask import Flask, request, Response, json, jsonify
from slackeventsapi import SlackEventAdapter
from collections import OrderedDict, deque
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# init's flask app
app = Flask('__name__')

# This pulls our signing secret so we can handle events.
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

# Oauth Token, signing secret was exported to venv workspace
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# api_call is another way we can call end points on the slack api.
BOT_ID = client.api_call("auth.test")['user_id']

# queue
break_queue = deque(maxlen=3)

# Slash command for accessing break view
@app.route('/slack/break', methods=["GET", "POST"])
def break_bot():
    """[Slash command for break punch]"""

    # break payload
    blocks = json.loads("""
	[
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Select your status below:",
				"emoji": true
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "actions",
			"elements": [
                {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Break",
						"emoji": true
					},
					"value": "break_15",
					"style": "primary"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Lunch",
						"emoji": true
					},
					"value": "lunch_break",
					"url": "https://login.microsoftonline.com/common/oauth2/authorize?response_type=id_token&client_id=5e3ce6c0-2b1f-4285-8d4b-75ee78787346&redirect_uri=https%3A%2F%2Fteams.microsoft.com%2Fgo&state=b5fbec62-e8fb-4c7b-9bba-38819548e949&&client-request-id=ccef4b15-7e19-47d0-aa2c-1cb30187c14a&x-client-SKU=Js&x-client-Ver=1.0.9&nonce=2ace73c2-e3cf-43ee-82c6-d3ed58c364bc&domain_hint=z",
					"style": "primary"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "In a meeting",
						"emoji": true
					},
					"value": "meeting_break",
					"style": "primary"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Back from break",
						"emoji": true
					},
					"value": "user_back",
					"action_id": "actionId-4",
					"style": "danger"
				}
			]
		},
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Don't forget to type /break and select back from break once you've returned!",
				"emoji": true
			}
		}
    ]""")

    # response variable
    response = {
        "blocks": blocks,
    }

    return json.jsonify(response), 200


# interactive endpoint
@app.route('/slack/actions', methods=['GET', 'POST'])
def message_actions():
    '''[parses actions from payload]'''

    # json payload
    form_json = json.loads(request.form['payload'])

    # break option
    selection = form_json['actions'][0]['value']

    # user_name
    user_name = form_json['user']['name']
    print(user_name.capitalize())

    # timestamp for executing break command - messing with datetime
    timestamp = json.loads(form_json['container']['message_ts'])

    if timestamp:
        x = datetime.datetime.now()
        emp_break = x.strftime('%m-%d-%Y %I:%M%p')
        print(emp_break)
    
    # selection menu
    while break_queue.maxlen > len(break_queue):
        if selection == "break_15" and user_name not in break_queue:
            break_queue.insert(0, user_name)
            message_text = "taking a quick break"
        elif selection == "lunch_break" and user_name not in break_queue:
            break_queue.insert(0, user_name)
            message_text = "going to lunch"
        elif selection == "meeting_break" and user_name not in break_queue:
            break_queue.insert(0, user_name)
            message_text = "in a meeting"
        break
    else:
        message_text = "queue is full"
        
    if selection == "user_back" and user_name in break_queue:
        break_queue.remove(user_name)
        message_text = "is back"

    print('Current in queue:', break_queue)

    client.chat_postMessage(
        channel=form_json['channel']['id'],
        text=f'{user_name}, {message_text}'
    )

    requests.post(form_json['response_url'])

    return ''

# The endpoint for help slash command
@app.route('/slack/help', methods=["POST"])
def slash_help():
    '''[A function help command message]'''

    # parse json
    data = request.form
    channel_id = data.get('channel_id')
    user_id = data.get('user_id')

    # compose response message
    response = client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text="BreakBot Helper",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Hi there 👋 I see you need help with Trackstat",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*:one: Use the `/break` command*. \n• Type `/break` to select the type of break you are taking. Try it out by using the `/break` command in this channel."
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*:two: Type of Breaks to Select:*\n• Taking a break :brb: \n\n• Lunch :shallow_pan_of_food:\n\n• In a Meeting :virtual-meeting:"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*:three: Returning From Break:* \n• Do not forget to use `/break` and select *back from break* once you've returned from your break :back:"
                }
            }
        ]
    )

    return ''

# The endpoint for queue slash command
@app.route('/slack/queue', methods=["POST"])
def usersInQueue():
    '''[A function for break queue]'''
    
    # parse json
    data = request.form
    channel_id = data.get('channel_id')

    if len(break_queue) == 0:
        usersQueue = "No one on break"
    elif len(break_queue) >= 3:
        usersQueue = "Queue is full, 3 people on break, please wait until someone returns"
    else:
        queued = list(break_queue)
        usersQueue = ", ".join(queued)

    # compose response message
    return f'*Current Break Queue:* _{usersQueue}_'


if __name__ == "__main__":
    app.run()
