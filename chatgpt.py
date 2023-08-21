import json
import uuid
import requests


def get_response(prompt, conversation_id=None, parent_message_id=None):
    url = "http://127.0.0.1:8008/api/conversation/talk"

    message_id = str(uuid.uuid4())

    if parent_message_id is None:
        parent_message_id = str(uuid.uuid4())

    json_data = {
        "prompt": prompt,
        "model": "gpt-3",
        "message_id": message_id,
        "parent_message_id": parent_message_id,
        "conversation_id": conversation_id,
        "stream": False
    }

    response = requests.post(url, json=json_data).content.decode()
    json_response = json.loads(response)

    return json_response
