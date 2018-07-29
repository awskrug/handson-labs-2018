import json

try:
    from util.event_parser import EVENT_PARSER
except Exception:
    from .util.event_parser import EVENT_PARSER


def get_body(event):
    return json.loads(event['body'])


def handler(raw_event, context):
    print(raw_event)
    for event in raw_event['Records']:
        event = EVENT_PARSER(get_body(event))
        if event.sns:
            print(event)

    return 'hellow'
