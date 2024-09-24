import websocket
import json
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

# WebSocket URL
ws_url = "wss://s-usc1a-nss-2031.firebaseio.com/.ws?v=5&ls=w0OvG95EuDEzMbmlgZNGMxBoirEFAG2g&ns=firepad"

# Updated Request body
request_body = {
    "t": "d",
    "d": {
        "r": 18,
        "a": "q",
        "b": {
            "p": "/demo/sukrit/history",
            "q": {
                "sp": None,
                "sn": "A0"
            },
            "t": 1,
            "h": ""
        }
    }
}

def is_url(string):
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # IPv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # IPv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(url_pattern, string) is not None

def extract_strings(data, min_words=3):
    extracted_strings = []
    if isinstance(data, dict):
        for value in data.values():
            extracted_strings.extend(extract_strings(value, min_words))
    elif isinstance(data, list):
        for item in data:
            extracted_strings.extend(extract_strings(item, min_words))
    elif isinstance(data, str):
        if is_url(data) or len(data.split()) >= min_words:
            extracted_strings.append(data.strip())
    return extracted_strings

def on_message(ws, message):
    # Check for empty message
    if not message.strip():
        logging.warning("Received an empty message")
        return

    # Log the raw message for debugging
    logging.info("Raw message received: %s", message)
    
    try:
        data = json.loads(message)
        logging.debug("Parsed JSON data: %s", data)
        strings = extract_strings(data)
        logging.info("Extracted strings: %s", strings)
        for s in strings:
            print(s)
    except json.JSONDecodeError as e:
        logging.error("Failed to decode JSON: %s. Raw message: %s", e, message)
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)


def on_error(ws, error):
    logging.error("Error: %s", error)

def on_close(ws):
    logging.info("Connection closed")

def on_open(ws):
    logging.info("Connection opened, sending request...")
    ws.send(json.dumps(request_body))

# Create a WebSocket application
ws = websocket.WebSocketApp(ws_url,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

# Start the WebSocket
ws.run_forever()
