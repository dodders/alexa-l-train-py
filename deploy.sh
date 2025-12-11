#!/usr/bin/env bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "  Alexa L Train - Deployment Script"
echo "========================================="
echo ""

# Check for required tools
echo "Checking prerequisites..."

if ! command -v pipenv &> /dev/null; then
    echo -e "${RED}Error: pipenv is not installed${NC}"
    echo "Install with: pip install pipenv"
    exit 1
fi

if ! command -v serverless &> /dev/null && ! command -v sls &> /dev/null; then
    echo -e "${RED}Error: serverless framework is not installed${NC}"
    echo "Install with: npm install -g serverless"
    exit 1
fi

if ! command -v zip &> /dev/null; then
    echo -e "${RED}Error: zip is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All required tools found${NC}"
echo ""

# Check for required environment variables
echo "Checking environment variables..."

# Note: MTAKEY no longer required as of 2024 - MTA APIs are now open access
echo -e "${GREEN}✓ MTA API key not required (APIs are now open access)${NC}"

if [ -z "$ALEXA_SKILL_ID" ]; then
    echo -e "${YELLOW}Warning: ALEXA_SKILL_ID environment variable is not set${NC}"
    echo "Set it with: export ALEXA_SKILL_ID=amzn1.ask.skill.xxxxx"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✓ Environment variables checked${NC}"
echo ""

# Install dependencies
echo "Installing dependencies..."
pipenv install

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Package Lambda function
echo "Packaging Lambda function..."

# Clean up old package
if [ -f "lambda-package.zip" ]; then
    echo "Removing old lambda-package.zip..."
    rm lambda-package.zip
fi

if [ -d "target" ]; then
    echo "Removing old target directory..."
    rm -rf target
fi

# Get the site-packages path from pipenv
SITE_PACKAGES=$(pipenv --venv)/lib/python*/site-packages

# Create target directory and copy dependencies
echo "Copying dependencies from virtual environment..."
mkdir -p target
cp -r $SITE_PACKAGES/* target/

# Remove unnecessary files to reduce package size
echo "Cleaning up unnecessary files..."
find target -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find target -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find target -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find target -type f -name "*.pyc" -delete 2>/dev/null || true

# Copy Python source files (excluding test files)
echo "Copying application code..."
for file in *.py; do
    if [[ ! $file =~ ^test_ ]]; then
        cp "$file" target/
    fi
done

# Create zip package
echo "Creating deployment package..."
cd target/
zip -r -q ../lambda-package.zip .
cd ..

# Clean up target directory
rm -rf target

PACKAGE_SIZE=$(du -h lambda-package.zip | cut -f1)
echo -e "${GREEN}✓ Lambda package created: lambda-package.zip ($PACKAGE_SIZE)${NC}"
echo ""

# Deploy using serverless
echo "Deploying to AWS..."
echo ""

if command -v sls &> /dev/null; then
    SLS_CMD="sls"
else
    SLS_CMD="serverless"
fi

$SLS_CMD deploy

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Deployment failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Deployment completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "To view function info:"
echo "  $SLS_CMD info"
echo ""
echo "To view logs:"
echo "  $SLS_CMD logs -f alexaLTrain --tail"
echo ""
echo "To remove deployment:"
echo "  $SLS_CMD remove"
echo ""
