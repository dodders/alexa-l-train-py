#!/usr/bin/env python3
import os
import json
from myaws import handler

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

if __name__ == '__main__':
    print('Starting Lambda handler test...')
    print('=' * 60)

    try:
        # Call the Lambda handler
        context = MockContext()
        response = handler(mock_event, context)

        print('\n✓ Lambda handler executed successfully!')
        print('=' * 60)
        print('\nResponse:')
        print(json.dumps(response, indent=2))

        # Extract and display the speech output
        if 'response' in response:
            if 'outputSpeech' in response['response']:
                speech = response['response']['outputSpeech'].get('text',
                         response['response']['outputSpeech'].get('ssml', 'No speech found'))
                print('\n' + '=' * 60)
                print('Speech Output:')
                print('=' * 60)
                print(speech)
                print('=' * 60)

    except Exception as e:
        print(f'\n✗ Error testing Lambda handler:')
        print(f'  {type(e).__name__}: {str(e)}')
        import traceback
        traceback.print_exc()
