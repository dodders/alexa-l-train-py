#!/usr/bin/env python3
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Set up environment variables for MTA API
os.environ['MTAURL'] = 'http://datamine.mta.info/mta_esi.php?key='
os.environ['MTAKEY'] = '9a707b925e75f2830938dba89a0c62f2'
os.environ['MTAFEEDID'] = '2'

# Mock Alexa LaunchRequest event
mock_event = {
    "version": "1.0",
    "session": {
        "new": True,
        "sessionId": "amzn1.echo-api.session.test",
        "application": {
            "applicationId": "amzn1.ask.skill.test"
        },
        "user": {
            "userId": "amzn1.ask.account.test"
        }
    },
    "context": {
        "System": {
            "application": {
                "applicationId": "amzn1.ask.skill.test"
            },
            "user": {
                "userId": "amzn1.ask.account.test"
            },
            "device": {
                "deviceId": "amzn1.ask.device.test",
                "supportedInterfaces": {}
            }
        }
    },
    "request": {
        "type": "LaunchRequest",
        "requestId": "amzn1.echo-api.request.test",
        "timestamp": "2024-01-01T00:00:00Z",
        "locale": "en-US"
    }
}

# Mock context object (Lambda context)
class MockContext:
    def __init__(self):
        self.function_name = "alexa-l-train-test"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:alexa-l-train-test"
        self.aws_request_id = "test-request-id"

# Mock MTA data with realistic train times in minutes
def mock_get_next_trains():
    """Mock function that returns simulated train arrival times in minutes"""
    return [3, 7, 12, 18, 25]

if __name__ == '__main__':
    print('Starting Lambda handler test with MOCKED MTA data...')
    print('=' * 60)

    # Patch the get_next_trains function to use our mock
    with patch('mta.get_next_trains', side_effect=mock_get_next_trains):
        try:
            # Import handler after patching
            from myaws import handler

            # Call the Lambda handler
            context = MockContext()
            response = handler(mock_event, context)

            print('\n✓ Lambda handler executed successfully!')
            print('=' * 60)
            print('\nFull Response:')
            print(json.dumps(response, indent=2))

            # Extract and display the speech output
            if 'response' in response:
                if 'outputSpeech' in response['response']:
                    output_speech = response['response']['outputSpeech']
                    speech = output_speech.get('text', output_speech.get('ssml', 'No speech found'))

                    print('\n' + '=' * 60)
                    print('Speech Output (what Alexa will say):')
                    print('=' * 60)
                    print(speech)
                    print('=' * 60)

                    # Check if there's a card
                    if 'card' in response['response']:
                        card = response['response']['card']
                        print('\nCard Display:')
                        print('=' * 60)
                        print(f"Title: {card.get('title', 'N/A')}")
                        print(f"Content: {card.get('content', card.get('text', 'N/A'))}")
                        print('=' * 60)

        except Exception as e:
            print(f'\n✗ Error testing Lambda handler:')
            print(f'  {type(e).__name__}: {str(e)}')
            import traceback
            traceback.print_exc()
