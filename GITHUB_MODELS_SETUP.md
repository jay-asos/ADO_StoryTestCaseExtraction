# GitHub Models Configuration Guide

## 🚀 Free Unlimited Testing with GitHub Models!

GitHub Models provides **free, unlimited access** to various AI models including GPT-4 variants using your GitHub Personal Access Token (PAT).

## Getting Started

### Step 1: Get Your GitHub Personal Access Token (PAT) with Correct Permissions

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `AI Models Access`
4. **CRITICAL**: Select the **`models` scope** ✅
   - Scroll down in the permissions list
   - Find and check **`models`** (this is required for accessing GitHub Models)
   - You may also need `repo` or `read:user` depending on your use case
5. Set expiration (recommend: 90 days or No expiration for testing)
6. Click **"Generate token"**
7. **Copy the token immediately** (you won't see it again!)

**Important**: Your token MUST have the `models` permission, or you'll get an "unauthorized" error.

### Step 2: Configure Your .env File

Update your `.env` file:

```bash
# AI Service Provider - Set to 'GITHUB' to use GitHub Models
AI_SERVICE_PROVIDER=GITHUB

# GitHub Personal Access Token
GITHUB_TOKEN=ghp_your_token_here

# GitHub Model Selection (all are FREE!)
# Recommended models:
#   - gpt-4.1-mini (fast, capable, recommended)
#   - gpt-4.1 (more powerful)
#   - gpt-4o (multimodal)
#   - phi-4 (Microsoft's efficient model)
#   - meta/llama-3.3-70b-instruct (Meta's latest)
GITHUB_MODEL=gpt-4.1-mini
```

### Step 3: Run Your Application

```bash
python main.py
```

## Available Models (All FREE!)

### OpenAI Models
- `gpt-4.1` - Most capable GPT-4 variant
- `gpt-4.1-mini` - Fast and efficient (recommended)
- `gpt-4.1-nano` - Ultra-fast
- `gpt-4o` - Multimodal (text + images)
- `gpt-4o-mini` - Affordable multimodal
- `o1` - Advanced reasoning
- `o1-mini` - Efficient reasoning

### Microsoft Models
- `phi-4` - Highly capable 14B model
- `phi-4-mini-instruct` - 3.8B efficient model
- `phi-4-reasoning` - State-of-the-art reasoning

### Meta Models
- `meta/llama-3.3-70b-instruct` - Enhanced reasoning
- `meta/meta-llama-3.1-405b-instruct` - Most powerful Llama
- `meta/meta-llama-3.1-8b-instruct` - Fast and efficient

### Others
- `deepseek/deepseek-r1` - Excellent reasoning
- `mistral-ai/mistral-large-2411` - Advanced capabilities
- Many more!

## Features

✅ **100% Free** - No costs, no rate limits!  
✅ **No Credit Card** - Just your GitHub account  
✅ **OpenAI Compatible** - Same API format  
✅ **Multiple Models** - Switch instantly  
✅ **Unlimited Requests** - Test as much as you want  

## Troubleshooting

### "Invalid Authentication"
- Check your GitHub token is correct
- Ensure token has read permissions
- Regenerate token if expired

### "Model Not Found"
- Check model name format (e.g., `gpt-4.1-mini` not `gpt-4.1mini`)
- Try a different model from the list above

### Need Help?
- GitHub Models Docs: https://docs.github.com/en/rest/models
- Model Catalog: https://github.com/marketplace/models

## Example Usage

Your existing code works exactly the same:

```python
from src.ai_client import AIClientFactory

# Automatically uses GitHub Models when AI_SERVICE_PROVIDER=GITHUB
client = AIClientFactory.create_client()

response = client.chat_completion([
    {"role": "user", "content": "Hello!"}
])
print(response)
```

That's it! Enjoy unlimited free AI testing! 🎉
