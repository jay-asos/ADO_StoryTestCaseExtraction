#!/bin/bash

# STAX (Story & Test Automation eXtractor) - Docker Container Startup Script

set -e

echo "[DOCKER-STARTUP] Starting STAX (Story & Test Automation eXtractor) application..."

# Create necessary directories
mkdir -p logs snapshots

# Set proper permissions
chmod 755 logs snapshots

# Check if monitor configuration exists, create default if not
if [ ! -f "monitor_config.json" ]; then
    echo "[DOCKER-STARTUP] Creating default monitor configuration..."
    cat > monitor_config.json << EOF
{
    "poll_interval_seconds": 300,
    "auto_sync": true,
    "auto_extract_new_epics": true,
    "log_level": "INFO",
    "max_concurrent_syncs": 3,
    "retry_attempts": 3,
    "retry_delay_seconds": 60
}
EOF
fi

# Validate critical environment variables
if [ -z "$PLATFORM_TYPE" ]; then
    echo "[DOCKER-STARTUP] WARNING: PLATFORM_TYPE not set, defaulting to ADO"
    export PLATFORM_TYPE="ADO"
fi

if [ "$PLATFORM_TYPE" = "ADO" ]; then
    if [ -z "$ADO_ORGANIZATION" ] || [ -z "$ADO_PROJECT" ] || [ -z "$ADO_PAT" ]; then
        echo "[DOCKER-STARTUP] ERROR: ADO configuration incomplete. Required: ADO_ORGANIZATION, ADO_PROJECT, ADO_PAT"
        exit 1
    fi
    echo "[DOCKER-STARTUP] ADO configuration validated"
elif [ "$PLATFORM_TYPE" = "JIRA" ]; then
    if [ -z "$JIRA_BASE_URL" ] || [ -z "$JIRA_USERNAME" ] || [ -z "$JIRA_TOKEN" ]; then
        echo "[DOCKER-STARTUP] ERROR: JIRA configuration incomplete. Required: JIRA_BASE_URL, JIRA_USERNAME, JIRA_TOKEN"
        exit 1
    fi
    echo "[DOCKER-STARTUP] JIRA configuration validated"
fi

# Validate AI service configuration
if [ "$AI_SERVICE_PROVIDER" = "OPENAI" ]; then
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "[DOCKER-STARTUP] ERROR: OpenAI configuration incomplete. Required: OPENAI_API_KEY"
        exit 1
    fi
    echo "[DOCKER-STARTUP] OpenAI configuration validated"
elif [ "$AI_SERVICE_PROVIDER" = "AZURE_OPENAI" ]; then
    if [ -z "$AZURE_OPENAI_ENDPOINT" ] || [ -z "$AZURE_OPENAI_API_KEY" ] || [ -z "$AZURE_OPENAI_DEPLOYMENT_NAME" ]; then
        echo "[DOCKER-STARTUP] ERROR: Azure OpenAI configuration incomplete. Required: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME"
        exit 1
    fi
    echo "[DOCKER-STARTUP] Azure OpenAI configuration validated"
else
    echo "[DOCKER-STARTUP] ERROR: AI_SERVICE_PROVIDER must be either 'OPENAI' or 'AZURE_OPENAI'"
    exit 1
fi

echo "[DOCKER-STARTUP] Configuration validation complete"
echo "[DOCKER-STARTUP] Starting Monitor API on port 5001..."

# Start the application
exec python -m src.monitor_api
