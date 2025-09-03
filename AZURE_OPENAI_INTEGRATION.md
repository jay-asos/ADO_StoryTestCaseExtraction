# Azure OpenAI Service Integration Guide

This document explains how to configure and use Azure OpenAI Service alongside the existing OpenAI integration.

## Overview

The system now supports both OpenAI and Azure OpenAI Service with automatic provider switching. You can easily switch between providers using configuration settings while maintaining full compatibility.

## Configuration

### 1. Environment Variables

Add these settings to your `.env` file:

```bash
# AI Service Configuration
AI_SERVICE_PROVIDER=AZURE_OPENAI  # Options: OPENAI, AZURE_OPENAI

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo  # Your deployment name
AZURE_OPENAI_MODEL=gpt-35-turbo  # Model name in Azure OpenAI

# OpenAI Configuration (kept for compatibility)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

### 2. Azure OpenAI Setup Requirements

Before configuring, ensure you have:

1. **Azure OpenAI Service Resource**: Create an Azure OpenAI resource in the Azure portal
2. **Model Deployment**: Deploy a model (e.g., GPT-3.5-turbo or GPT-4) in your Azure OpenAI resource
3. **API Key**: Get the API key from your Azure OpenAI resource
4. **Endpoint URL**: Note your resource endpoint URL

### 3. Configuration Steps

1. **Get Azure OpenAI Details**:
   - Go to Azure Portal → Your OpenAI Resource
   - Copy the endpoint URL (e.g., `https://your-resource.openai.azure.com/`)
   - Copy one of the API keys
   - Note your deployment name (the name you gave when deploying the model)

2. **Update .env File**:
   ```bash
   # Switch to Azure OpenAI
   AI_SERVICE_PROVIDER=AZURE_OPENAI
   
   # Add your Azure OpenAI settings
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-actual-api-key
   AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
   ```

3. **Test Configuration**:
   ```bash
   python3 test_ai_client.py
   ```

## Dashboard Configuration

The web dashboard now includes Azure OpenAI configuration options:

1. **Access Configuration**: Click the "Configuration" button in the dashboard
2. **Select AI Provider**: Choose between "OpenAI" and "Azure OpenAI Service"
3. **Configure Settings**: Enter your Azure OpenAI settings when Azure OpenAI is selected
4. **Save & Test**: Use the connection test to verify your configuration

## Benefits of Azure OpenAI Service

### Advantages:
- **Enterprise Security**: Data stays within your Azure tenant
- **Compliance**: Better compliance with corporate data policies
- **Private Networking**: VNet integration and private endpoints
- **Regional Control**: Deploy in specific Azure regions
- **Cost Management**: Enterprise pricing and billing integration
- **SLA Guarantees**: Enterprise-grade service level agreements

### Use Cases:
- Corporate environments with strict data governance
- Applications requiring regional data residency
- Integration with existing Azure infrastructure
- Enhanced security and compliance requirements

## Code Changes Made

### 1. AI Client Factory (`src/ai_client.py`)
- Unified interface for both OpenAI and Azure OpenAI
- Automatic provider switching based on configuration
- Built-in retry logic with exponential backoff
- Proper error handling and logging

### 2. Configuration Management (`config/settings.py`)
- Added Azure OpenAI configuration variables
- Enhanced validation for both AI services
- Backward compatibility with existing OpenAI settings

### 3. Component Updates
All AI-powered components now use the unified client:
- **Story Extractor** (`src/story_extractor.py`)
- **Enhanced Story Creator** (`src/enhanced_story_creator.py`)  
- **Test Case Extractor** (`src/test_case_extractor.py`)

### 4. Dashboard Integration (`templates/dashboard.html`)
- Azure OpenAI configuration UI
- Provider selection radio buttons
- Conditional settings display
- Connection testing for both providers

## Migration Path

### Immediate Use (Current State):
- System defaults to OpenAI (existing behavior)
- All existing functionality preserved
- No changes required to continue using OpenAI

### Switching to Azure OpenAI:
1. Set up Azure OpenAI resource and deployment
2. Update `.env` file with Azure OpenAI settings
3. Change `AI_SERVICE_PROVIDER=AZURE_OPENAI`
4. Test with `python3 test_ai_client.py`
5. Verify story extraction functionality

### Hybrid Approach:
- Keep both configurations in `.env`
- Switch between providers by changing `AI_SERVICE_PROVIDER`
- Test different models and pricing options

## Troubleshooting

### Common Issues:

1. **Authentication Errors**:
   - Verify API key is correct
   - Check endpoint URL format
   - Ensure deployment exists

2. **Model Not Found**:
   - Verify deployment name matches exactly
   - Check model is deployed and available
   - Confirm API version compatibility

3. **Network Issues**:
   - Check firewall/proxy settings
   - Verify Azure OpenAI resource is accessible
   - Test endpoint connectivity

### Testing Commands:
```bash
# Test current configuration
python3 test_ai_client.py

# Test story extraction (requires valid Epic ID)
python3 -c "from src.story_extractor import StoryExtractor; print('Story extractor ready')"

# Verify settings
python3 -c "from config.settings import Settings; print(f'AI Provider: {Settings.AI_SERVICE_PROVIDER}')"
```

## API Compatibility

Both providers use the same interface:
```python
from src.ai_client import get_ai_client

# Get client (automatically selects provider)
client = get_ai_client()

# Use unified interface
response = client.chat_completion(messages, temperature=0.7)
```

This ensures seamless switching between providers without code changes in the consuming components.

## Next Steps

1. **Test Current Implementation**: Run `python3 test_ai_client.py` to verify OpenAI works
2. **Set Up Azure OpenAI**: Create Azure OpenAI resource when ready
3. **Configure & Switch**: Update `.env` and test Azure OpenAI
4. **Monitor Performance**: Compare response times and costs
5. **Choose Provider**: Select the best option for your use case

The system is now ready to support both AI providers with easy switching and full feature compatibility.
