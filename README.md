# alexa-l-train-py

An Alexa skill that provides real-time L train arrival times using the MTA GTFS-realtime API. Currently configured for Bedford Ave station.

## Overview

This AWS Lambda application integrates with Amazon Alexa to provide voice-activated subway arrival information. Users can ask Alexa for L train times and receive real-time data directly from the MTA.

## Architecture

- **Runtime**: Python 3.7 (local) / Python 3.6 (AWS Lambda)
- **Cloud Platform**: AWS Lambda
- **Voice Platform**: Amazon Alexa Skills Kit
- **Data Source**: MTA GTFS-realtime API
- **Deployment**: Serverless Framework
- **Dependencies**: ask-sdk, gtfs-realtime-bindings

## Prerequisites

Before deploying this application, ensure you have:

1. **Node.js and npm** (for Serverless Framework)
   ```bash
   node --version  # Should be v14 or higher
   npm --version
   ```

2. **Serverless Framework**
   ```bash
   npm install -g serverless
   ```

3. **Python 3.7+ and Pipenv**
   ```bash
   python3 --version
   pip install pipenv
   ```

4. **AWS CLI configured with credentials**
   ```bash
   aws configure --profile serverless
   ```
   You'll need:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region: `us-east-1`

5. **Alexa Developer Account**
   - Sign up at: https://developer.amazon.com/alexa

**Note**: As of 2024, the MTA API no longer requires authentication or API keys! The API is free and open to use without registration.

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <your-repo-url>
cd alexa-l-train-py
pipenv install
```

### 2. Create Production Environment File

Create a `.env` file in the project root for your configuration:

```bash
# Create .env from template
cp .env.example .env
```

Edit `.env` and add your Alexa Skill ID:

```bash
# MTA API Configuration
# NOTE: As of 2024, MTA APIs no longer require authentication!
# The API is free and open to use without registration.

# MTA API Endpoint URL (default is L train)
MTAURL=https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l

# Alexa Skill ID (you'll get this after creating the skill)
ALEXA_SKILL_ID=amzn1.ask.skill.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Important**:
- Never commit `.env` to version control (it's in `.gitignore`)
- Keep your Alexa Skill ID secure
- The MTA API endpoint can be customized to query different train lines (see Customization section)

### 3. Create Alexa Skill

1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Click "Create Skill"
3. Configure your skill:
   - **Skill name**: "L Train Times" (or your preferred name)
   - **Default language**: English (US)
   - **Choose a model**: Custom
   - **Choose a method to host**: Provision your own
4. Click "Create skill"
5. Copy the **Skill ID** from the top of the page (format: `amzn1.ask.skill.xxxxx`)
6. Add this Skill ID to your `.env` file as `ALEXA_SKILL_ID`

### 4. Configure Alexa Skill Interaction Model

In the Alexa Developer Console:

1. Go to the **Build** tab
2. In the left sidebar, click **Invocation**
   - Set invocation name: "l train" or "l train times"
3. Under **Intents**, ensure you have:
   - `AMAZON.CancelIntent`
   - `AMAZON.StopIntent`
   - `AMAZON.HelpIntent` (optional)
4. Click **Save Model** and **Build Model**

### 5. Deploy to AWS

Before deploying, make sure your Alexa Skill ID is set:

```bash
# Source your environment file
source .env

# Or export the Alexa Skill ID directly
export ALEXA_SKILL_ID=amzn1.ask.skill.xxxxx
```

Deploy the application:

```bash
# Make the deployment script executable (if not already)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The deployment script will:
- Check prerequisites
- Validate Alexa Skill ID (MTA API key no longer required!)
- Install dependencies
- Package the Lambda function
- Deploy to AWS
- Display the Lambda ARN

### 6. Link Lambda to Alexa Skill

After deployment completes, you'll see output like:

```
endpoints:
  alexaLTrain: arn:aws:lambda:us-east-1:123456789:function:alexa-l-train-py-dev-alexaLTrain
```

Copy the Lambda ARN and configure your Alexa Skill:

1. Go back to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Open your skill
3. Go to the **Build** tab, then click **Endpoint** in the left sidebar
4. Select "AWS Lambda ARN"
5. Paste your Lambda ARN in the "Default Region" field
6. Click **Save Endpoints**

### 7. Test Your Skill

#### Test in Alexa Developer Console:

1. Go to the **Test** tab
2. Enable testing: "Development" mode
3. Type or say: "open l train"
4. You should receive train arrival times

#### Test on Your Alexa Device:

If your Alexa device is linked to the same Amazon account:

```
"Alexa, open l train"
```

## Deployment Commands

### Deploy
```bash
./deploy.sh
```

### View Function Info
```bash
sls info
# or
serverless info
```

### View Logs
```bash
sls logs -f alexaLTrain --tail
# or
serverless logs -f alexaLTrain --tail
```

### Update After Code Changes
```bash
./deploy.sh  # Redeploy with new code
```

### Remove Deployment
```bash
sls remove
# or
serverless remove
```

## Project Structure

```
alexa-l-train-py/
├── myaws.py              # Lambda handler and Alexa request handlers
├── mta.py                # MTA API integration
├── serverless.yml        # Serverless Framework configuration
├── deploy.sh             # Deployment automation script
├── package.sh            # Manual packaging script
├── Pipfile               # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your production environment (not in git)
└── README.md             # This file
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MTAURL` | No | `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l` | MTA API endpoint URL for L train (no auth required!) |
| `ALEXA_SKILL_ID` | Yes | - | Your Alexa Skill ID from developer console |

## Troubleshooting

### Deployment fails with "credentials not found"
```bash
# Configure AWS credentials
aws configure --profile serverless
```

### Lambda returns "Internal Server Error"
```bash
# Check CloudWatch logs
sls logs -f alexaLTrain --tail
```

### Alexa skill can't connect to Lambda
- Verify the Lambda ARN is correctly configured in Alexa Developer Console
- Check that the ALEXA_SKILL_ID in your .env matches your skill
- Ensure Lambda is deployed in us-east-1 region

### "No trains found" or empty response
- Check MTA API status: https://api.mta.info/
- Test MTA API directly: `./run.sh` (no API key needed!)
- Ensure you're using the correct API endpoint with URL encoding: `nyct%2Fgtfs-l`
- Verify the train line is currently running (check MTA service status)

## Local Development and Testing

### Test MTA API Connection
```bash
# No API key needed! Just run the test script
./run.sh

# Or test with curl
curl "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l" | head -c 100
```

### Run in Virtual Environment
```bash
pipenv shell
python3 mta.py
```

### Manual Testing Lambda Handler
```bash
pipenv shell
python3 test_lambda.py
```

## Customization

### Change Station
Edit `mta.py` line 16 to change the target station:
```python
stop_id = "L08N"  # Bedford Ave (Northbound)
# Find station codes: https://atisdata.s3.amazonaws.com/Station/Stations.csv
```

### Support Multiple Stations
Modify the skill to accept station names as intent slots and update the Lambda handler to use dynamic station IDs.

### Change Train Line
Update `MTAURL` environment variable to point to different feed endpoints (note the URL encoding `%2F`):
- `nyct%2Fgtfs-123456` = 1, 2, 3, 4, 5, 6 trains
- `nyct%2Fgtfs-l` = L train
- `nyct%2Fgtfs-nqrw` = N, Q, R, W trains
- `nyct%2Fgtfs-ace` = A, C, E trains
- `nyct%2Fgtfs-bdfm` = B, D, F, M trains
- `nyct%2Fgtfs-g` = G train
- `nyct%2Fgtfs-jz` = J, Z trains
- `nyct%2Fgtfs-7` = 7 train
- `nyct%2Fgtfs-si` = Staten Island Railway

Example: `export MTAURL=https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace`

## API References

- [MTA Developer Resources](https://api.mta.info/) - Official MTA API documentation
- [MTA GTFS-realtime Feed Documentation](https://api.mta.info/#/landing) - Current API documentation (no registration required!)
- [Alexa Skills Kit SDK](https://github.com/alexa/alexa-skills-kit-sdk-for-python)
- [Serverless Framework](https://www.serverless.com/framework/docs/)
- [GTFS-realtime Reference](https://developers.google.com/transit/gtfs-realtime/)

## Security Notes

- Never commit `.env` file to version control
- Keep your Alexa Skill ID secure
- Use AWS IAM roles with minimal required permissions
- Consider using AWS Secrets Manager for production credentials
- **Good news**: No MTA API key management needed - the API is open access!

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
