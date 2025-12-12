# Alexa L Train Times - Project Overview

## Purpose
This is a Python AWS Lambda application that implements an Alexa skill to retrieve real-time L train arrival times from the MTA (Metropolitan Transportation Authority) using the MTA's GTFS-realtime API.

## Architecture

### High-Level Flow
1. User invokes Alexa skill with voice command
2. Alexa sends LaunchRequest to AWS Lambda function
3. Lambda function queries MTA GTFS-realtime API
4. Lambda parses protobuf data to extract train arrival times
5. Lambda returns formatted response to Alexa
6. Alexa speaks the train times to the user

### Technology Stack
- **Runtime**: Python 3.12 (Pipenv and Lambda)
- **Cloud Platform**: AWS Lambda
- **Voice Platform**: Amazon Alexa Skills Kit
- **Data Source**: MTA GTFS-realtime API
- **Deployment**: Serverless Framework
- **Dependencies**:
  - `ask-sdk`: Amazon Alexa Skills Kit SDK for Python
  - `gtfs-realtime-bindings`: Google Transit GTFS-realtime protocol buffers
  - `urllib3`: 2.6.2+ (transitive dependency, security-patched version)

## Project Structure

### Core Files

#### `mta.py`
The MTA data fetching module that handles all interactions with the MTA API.

**Key Functions**:
- `get_stop_times()`: Fetches real-time train data from MTA GTFS-realtime API
  - Reads environment variable: `MTAURL` (default: L train endpoint with URL encoding)
  - **No authentication required** - MTA APIs are open access as of 2024
  - Targets Bedford Ave station (stop ID: `L08N`)
  - Parses protobuf feed to extract arrival times
  - Returns up to 5 upcoming train arrival times as datetime objects
  - Location: Lines 11-38

- `get_next_trains()`: Converts stop times to minutes from now
  - Calls `get_stop_times()` to fetch arrival times
  - Calculates time gaps in minutes from current time
  - Returns list of integers representing minutes until arrival
  - Location: Lines 41-48

**Important Notes**:
- Currently hardcoded to Bedford Ave station (`L08N`)
- Uses new MTA API endpoint: `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l`
- Can be run standalone with `python3 mta.py`
- **Updated 2024**: No API key required - MTA APIs are now open access!
- **URL Encoding**: Uses `%2F` for forward slash in URL path

#### `myaws.py`
The AWS Lambda handler and Alexa skill request processor.

**Request Handlers**:

1. **`LaunchRequestHandler`** (Lines 36-54)
   - Primary handler for Alexa skill invocation
   - Calls `get_stop_times()` from mta.py
   - Converts train times to natural language using `getwords()`
   - Returns Alexa response with speech and card

2. **`CancelAndStopIntentHandler`** (Lines 58-67)
   - Handles AMAZON.CancelIntent and AMAZON.StopIntent
   - Returns "Goodbye!" and ends session

3. **`SessionEndedRequestHandler`** (Lines 71-77)
   - Handles session cleanup (currently no cleanup needed)

4. **`AllExceptionHandler`** (Lines 81-92)
   - Catch-all exception handler
   - Logs exceptions to CloudWatch
   - Returns user-friendly error message

**Helper Functions**:
- `getwords(traintimes)`: Converts array of train times (in minutes) to natural language speech text (Lines 21-31)
  - Handles empty results, single train, and multiple trains
  - Note: Contains potential bugs in list indexing logic

**Lambda Handler Creation**:
- Uses `SkillBuilder` from ask-sdk-core
- Registers all request handlers and exception handler
- Exports `handler` function as Lambda entry point (Line 102)

#### `test_lambda.py`
Basic test file that imports and initializes the myaws module.

#### `serverless.yml`
Serverless Framework configuration for AWS deployment.

**Configuration**:
- Service name: `alexa-l-train-py`
- Provider: AWS
- Runtime: Python 3.12
- Region: us-east-1
- Profile: serverless
- Function: `alexaLTrain` with handler `myaws.handler`

### Build and Deployment Files

#### `Pipfile` / `Pipfile.lock`
Python dependency management using Pipenv.

**Dependencies**:
- `gtfs-realtime-bindings`: For parsing MTA GTFS-realtime protobuf data
- `ask-sdk`: Amazon Alexa Skills Kit SDK

**Python Version**: 3.12

#### `package.sh`
Shell script to package Lambda function with dependencies.

**Process**:
1. Copies all site-packages from virtual environment
2. Copies Python source files (excluding test files)
3. Creates `lambda-package.zip` for deployment
4. Cleans up temporary files

**Note**: References specific virtualenv path: `~/.local/share/virtualenvs/alexa-l-train-py-2ECeZEfi/`

#### `run.sh`
Local development script to test MTA data fetching.

**Environment Variables**:
- `MTAURL`: https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l

**Note**: No API key required! The MTA API is now open access as of 2024. Simply run the script to test.

## Environment Variables

The application requires these environment variables in the Lambda function:
- `MTAURL`: MTA API endpoint URL (default: `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l`)
  - **No API key required** - The MTA API is open access!

## Data Flow

### MTA API Integration
1. Application makes direct HTTPS GET request to `{MTAURL}` (no authentication headers required)
2. Connects to MTA GTFS-realtime endpoint at api-endpoint.mta.info
3. Receives protobuf-encoded FeedMessage
4. Parses feed to extract trip updates
5. Filters for specific stop ID (Bedford Ave: L08N)
6. Extracts arrival timestamps from matching stop_time_updates
7. Converts timestamps to datetime objects

### Alexa Response Format
- **Card Title**: "L Train Times"
- **Speech Output**: Natural language description of train times
  - Example: "The next L trains leave in 3, 5, 8, 12, and 15 minutes."
- **Session**: Kept open after initial response

## Known Issues and Technical Debt

1. **`getwords()` function** (myaws.py:21-31):
   - Contains potential list indexing bugs
   - Line 24: `len(traintimes == 1)` should likely be `len(traintimes) == 1`
   - Line 28: `range(0, len(traintimes - 2))` should likely be `range(0, len(traintimes) - 2)`
   - Line 30: String formatting issue with tuple instead of format

2. **Hardcoded Station**:
   - Bedford Ave station (L08N) is hardcoded in mta.py:16
   - No ability to query different stations without code changes

3. **API Migration Complete**:
   - ✅ Code has been updated to use new MTA API endpoint (api-endpoint.mta.info)
   - ✅ Old datamine.mta.info references removed
   - ✅ **No API key required** - MTA APIs are now open access (as of 2024)
   - ✅ URL encoding properly implemented (`nyct%2Fgtfs-l`)

5. **Error Handling**:
   - Limited error handling for API failures or network issues
   - No retry logic for MTA API calls

## Development and Deployment

### Local Development
```bash
# Install dependencies
pipenv install

# Run locally (tests MTA data fetching)
./run.sh
```

### Packaging for Lambda
```bash
# Create deployment package
./package.sh
```

### Deployment
Uses Serverless Framework for deployment to AWS:
```bash
serverless deploy
```

### Testing the Lambda
The Lambda can be tested locally by running `test_lambda.py`, which imports the handler.

## Alexa Skill Configuration

The Alexa skill should be configured to:
- Trigger this Lambda function on LaunchRequest
- Support standard intents: AMAZON.CancelIntent, AMAZON.StopIntent
- Region: us-east-1 (where Lambda is deployed)

## Future Enhancement Opportunities

1. Allow users to specify different L train stations via Alexa intent slots
2. Support multiple subway lines (not just L train)
3. Add direction filtering (northbound vs southbound)
4. Implement caching to reduce API calls
5. Add more robust error handling and retry logic
6. Fix bugs in `getwords()` function
7. Move API credentials to AWS Secrets Manager or environment variables
8. Add comprehensive unit tests
9. Implement CI/CD pipeline for automated deployment
10. Add logging and monitoring with CloudWatch metrics

## API References

- **MTA Developer Portal**: https://api.mta.info/ (Documentation - no registration required!)
- **MTA GTFS-realtime API Endpoint**: https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l
- **GTFS-realtime Reference**: https://developers.google.com/transit/gtfs-realtime/
- **Alexa Skills Kit SDK for Python**: https://github.com/alexa/alexa-skills-kit-sdk-for-python
- **Serverless Framework**: https://www.serverless.com/framework/docs/

**API History**:
- **Pre-May 2020**: datamine.mta.info with query parameter authentication
- **May 2020-2024**: api-endpoint.mta.info with header-based authentication (x-api-key)
- **2024+**: api-endpoint.mta.info with no authentication required (open access)

## Important Context for AI Assistants

When working with this codebase:
1. The application is production-ready but has known bugs in the text formatting logic
2. **API Status (2024)**: The MTA API is now **open access** - no authentication required!
   - The old datamine.mta.info endpoint was shut down in May 2020
   - Current endpoint: `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l`
   - No API key registration or management needed
   - URL encoding is important: use `%2F` instead of `/` in the path
3. The MTA API uses protobuf format (GTFS-realtime), requiring specific parsing
4. Alexa skills have specific request/response formats that must be followed
5. The Lambda function must be fast to avoid Alexa timeout
6. Environment variables must be set in AWS Lambda configuration for production use
7. **Python Version**: The codebase now uses Python 3.12 for both local development and Lambda runtime
8. **Security**: urllib3 has been upgraded to 2.6.2+ to address CVE-2025-50181, CVE-2025-66471, and other vulnerabilities
9. **Deployment is now simpler** - only Alexa Skill ID is required, no MTA API key needed
