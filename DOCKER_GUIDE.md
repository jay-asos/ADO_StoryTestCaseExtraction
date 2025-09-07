# Docker Containerization Guide

This project has been fully containerized and can be deployed using Docker and Docker Compose.

## 🐳 Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose v2.0+

### 1. Development Deployment

```bash
# Clone the repository
git clone https://github.com/papai0709/ADO_StoryTestCaseExtraction.git
cd ADO_StoryTestCaseExtraction

# Copy environment template
cp .env.docker .env

# Edit .env with your configuration
nano .env

# Build and run
docker-compose up --build
```

Access the application at `http://localhost:5001`

### 2. Production Deployment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up --build -d

# Or with nginx reverse proxy
docker-compose -f docker-compose.prod.yml --profile production up --build -d
```

Access the application at `http://localhost:80`

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PLATFORM_TYPE` | Yes | `ADO` | Platform type: `ADO` or `JIRA` |
| `ADO_ORGANIZATION` | Yes* | - | Azure DevOps organization name |
| `ADO_PROJECT` | Yes* | - | Azure DevOps project name |
| `ADO_PAT` | Yes* | - | Azure DevOps Personal Access Token |
| `JIRA_BASE_URL` | Yes** | - | JIRA instance URL |
| `JIRA_USERNAME` | Yes** | - | JIRA username/email |
| `JIRA_TOKEN` | Yes** | - | JIRA API token |
| `JIRA_PROJECT_KEY` | Yes** | - | JIRA project key |
| `AI_SERVICE_PROVIDER` | Yes | `OPENAI` | AI provider: `OPENAI` or `AZURE_OPENAI` |
| `OPENAI_API_KEY` | Yes*** | - | OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Yes**** | - | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Yes**** | - | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Yes**** | - | Azure OpenAI deployment name |

\* Required when `PLATFORM_TYPE=ADO`  
\** Required when `PLATFORM_TYPE=JIRA`  
\*** Required when `AI_SERVICE_PROVIDER=OPENAI`  
\**** Required when `AI_SERVICE_PROVIDER=AZURE_OPENAI`

### Configuration Files

The container expects these configuration files to be mounted or created:

- `monitor_config.json` - Monitor settings (auto-created if missing)
- `monitor_state.json` - Runtime state (auto-created)
- `enhanced_monitor_state.json` - Enhanced state (auto-created)

## 📁 Volume Mounts

### Development
```yaml
volumes:
  - ./logs:/app/logs              # Log files
  - ./snapshots:/app/snapshots    # Epic snapshots
  - ./monitor_config.json:/app/monitor_config.json  # Monitor config
```

### Production
```yaml
volumes:
  - app_logs:/app/logs           # Persistent log storage
  - app_snapshots:/app/snapshots # Persistent snapshot storage
  - app_config:/app/config       # Configuration storage
```

## 🚀 Deployment Options

### Option 1: Development with Docker Compose
```bash
docker-compose up --build
```

### Option 2: Production with Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### Option 3: Standalone Docker Container
```bash
# Build image
docker build -t ado-story-extractor .

# Run container
docker run -d \
  --name ado-story-extractor \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/snapshots:/app/snapshots \
  ado-story-extractor
```

### Option 4: Cloud Deployment

#### Azure Container Instances
```bash
# Create resource group
az group create --name ado-story-extractor --location eastus

# Deploy container
az container create \
  --resource-group ado-story-extractor \
  --name ado-story-extractor \
  --image your-registry/ado-story-extractor:latest \
  --dns-name-label ado-story-extractor \
  --ports 5001 \
  --environment-variables \
    PLATFORM_TYPE=ADO \
    ADO_ORGANIZATION=your-org \
    ADO_PROJECT=your-project \
    AI_SERVICE_PROVIDER=OPENAI \
  --secure-environment-variables \
    ADO_PAT=your-pat \
    OPENAI_API_KEY=your-key
```

#### AWS ECS/Fargate
```json
{
  "family": "ado-story-extractor",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "ado-story-extractor",
      "image": "your-registry/ado-story-extractor:latest",
      "portMappings": [
        {
          "containerPort": 5001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "PLATFORM_TYPE", "value": "ADO"},
        {"name": "AI_SERVICE_PROVIDER", "value": "OPENAI"}
      ],
      "secrets": [
        {"name": "ADO_PAT", "valueFrom": "arn:aws:secretsmanager:region:account:secret:ado-pat"},
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"}
      ]
    }
  ]
}
```

## 🔒 Security Best Practices

### 1. Use Secrets Management
- Store sensitive credentials in Docker secrets or cloud secret managers
- Never commit `.env` files with real credentials

### 2. Non-Root User
- Container runs as non-root user `app` for security
- Application files owned by `app:app`

### 3. Resource Limits
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### 4. Health Checks
- Built-in health check endpoint: `/api/health`
- Container health monitoring included

## 🛠️ Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs ado-story-extractor

# Common issues:
# 1. Missing required environment variables
# 2. Invalid credentials
# 3. Port conflicts
```

### Configuration Issues
```bash
# Validate environment variables
docker exec ado-story-extractor env | grep -E "(ADO|JIRA|OPENAI)"

# Check configuration files
docker exec ado-story-extractor ls -la *.json
```

### Performance Issues
```bash
# Monitor resource usage
docker stats ado-story-extractor

# Scale in production
docker-compose -f docker-compose.prod.yml up --scale ado-story-extractor=3
```

## 🔄 Updates and Maintenance

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up --build -d
```

### Backup Data
```bash
# Backup volumes
docker run --rm -v ado_logs:/data -v $(pwd):/backup alpine tar czf /backup/logs-backup.tar.gz -C /data .
```

### Log Management
```bash
# View logs
docker-compose logs -f ado-story-extractor

# Rotate logs
docker-compose exec ado-story-extractor find /app/logs -name "*.log" -mtime +7 -delete
```

## 📊 Monitoring and Observability

### Health Monitoring
- Health check endpoint: `http://localhost:5001/api/health`
- Container health status in Docker/Kubernetes
- Application metrics via dashboard

### Log Management
- Logs persisted in volumes
- Structured logging for better parsing
- Log rotation and cleanup

### Metrics Collection
- Application performance metrics
- Resource usage monitoring
- Integration with monitoring systems (Prometheus, etc.)

## 🌐 Production Considerations

1. **Load Balancing**: Use nginx or cloud load balancers
2. **SSL/TLS**: Configure HTTPS for production
3. **Monitoring**: Integrate with monitoring solutions
4. **Backup**: Regular backup of volumes and configuration
5. **Updates**: Implement CI/CD for automated deployments
6. **Scaling**: Consider horizontal scaling for high loads

This containerized setup provides a robust, scalable, and secure deployment option for the ADO Story Test Case Extraction application.
