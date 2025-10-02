# Cloud Deployment Guide

## Overview

This guide covers deploying the CRC OCR Pipeline to cloud environments (AWS, Azure, GCP) for scalable, production-ready processing.

## Architecture Options

### Option 1: Serverless Processing (Recommended for Batch)

**AWS Stack**:
- S3: Input/output storage
- Lambda: Processing functions (15min limit)
- Step Functions: Orchestrate pipeline
- ECR: Container images
- CloudWatch: Logging and monitoring

**Azure Stack**:
- Blob Storage: Input/output storage
- Azure Functions: Processing (Premium plan for long runs)
- Logic Apps: Workflow orchestration
- Container Registry: Container images
- Application Insights: Monitoring

**GCP Stack**:
- Cloud Storage: Input/output storage
- Cloud Run: Processing containers
- Cloud Workflows: Orchestration
- Artifact Registry: Container images
- Cloud Logging: Monitoring

### Option 2: Container-Based (Recommended for API)

**AWS ECS/Fargate**:
```yaml
# docker-compose.yml
version: '3.8'
services:
  ocr-api:
    image: crc-ocr-pipeline:latest
    environment:
      - DPI=300
      - TEMPLATE_PATH=/templates
    volumes:
      - ./templates:/templates:ro
      - ./artifacts:/artifacts
    ports:
      - "8000:8000"
```

**Kubernetes Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ocr-pipeline
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ocr-pipeline
  template:
    metadata:
      labels:
        app: ocr-pipeline
    spec:
      containers:
      - name: ocr-processor
        image: crc-ocr-pipeline:v1.0.0
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: templates
          mountPath: /app/templates
          readOnly: true
      volumes:
      - name: templates
        configMap:
          name: ocr-templates
```

## Docker Configuration

### Dockerfile

```dockerfile
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ ./scripts/
COPY templates/ ./templates/
COPY configs/ ./configs/

# Create output directory
RUN mkdir -p /app/artifacts

# Set environment variables
ENV PYTHONPATH=/app
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Run as non-root user
RUN useradd -m -u 1000 ocruser && chown -R ocruser:ocruser /app
USER ocruser

ENTRYPOINT ["python"]
CMD ["scripts/api_server.py"]
```

### .dockerignore

```
# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/

# Data
artifacts/
data/

# Development
.git/
.github/
.vscode/
.idea/
*.md
!README.md

# Tests
tests/
.pytest_cache/
.coverage

# Documentation
docs/
*.log
```

## Environment Configuration

### Environment Variables

```bash
# .env.production
DPI=300
TEMPLATE_DIR=/app/templates
OUTPUT_DIR=/app/artifacts
MAX_PAGES=100
TIMEOUT_SECONDS=900

# AWS specific
AWS_REGION=us-east-1
S3_INPUT_BUCKET=crc-ocr-input
S3_OUTPUT_BUCKET=crc-ocr-output

# Monitoring
LOG_LEVEL=INFO
METRICS_ENABLED=true
SENTRY_DSN=https://...

# Security
API_KEY_REQUIRED=true
MAX_FILE_SIZE_MB=50
```

### Secrets Management

**AWS Secrets Manager**:
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
secrets = get_secret('ocr-pipeline/prod')
api_key = secrets['api_key']
```

**Azure Key Vault**:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://ocr-vault.vault.azure.net",
    credential=credential
)

api_key = client.get_secret("api-key").value
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy OCR Pipeline

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest ruff mypy black
      
      - name: Lint with ruff
        run: ruff check scripts/
      
      - name: Type check with mypy
        run: mypy scripts/
      
      - name: Run tests
        run: pytest tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - name: Deploy to staging
        run: |
          # Add your deployment commands here
          echo "Deploying to staging environment"

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Deploy to production
        run: |
          # Add your deployment commands here
          echo "Deploying to production environment"
```

## Monitoring and Logging

### CloudWatch/Application Insights Configuration

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured logging for cloud environments."""
    
    def __init__(self, service_name: str):
        self.logger = logging.getLogger(service_name)
        self.service_name = service_name
    
    def log(self, level: str, message: str, **kwargs):
        """Log with structured format."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_processing(self, run_id: str, step: str, status: str, metrics: dict):
        """Log processing step with metrics."""
        self.log(
            "INFO",
            f"Processing step {step}",
            run_id=run_id,
            step=step,
            status=status,
            metrics=metrics
        )

# Usage
logger = StructuredLogger("ocr-pipeline")
logger.log_processing(
    run_id="20251001_185300",
    step="step2_align_and_crop",
    status="success",
    metrics={
        "pages_processed": 26,
        "mean_error_px": 0.00,
        "processing_time_sec": 45.2
    }
)
```

### Metrics Collection

```python
from dataclasses import dataclass
from typing import Dict, Any
import time

@dataclass
class ProcessingMetrics:
    """Metrics for monitoring."""
    run_id: str
    step_name: str
    start_time: float
    end_time: float
    pages_processed: int
    pages_failed: int
    mean_quality: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "step_name": self.step_name,
            "duration_sec": self.end_time - self.start_time,
            "pages_processed": self.pages_processed,
            "pages_failed": self.pages_failed,
            "success_rate": self.pages_processed / (self.pages_processed + self.pages_failed),
            "mean_quality": self.mean_quality
        }

def send_metrics_to_cloudwatch(metrics: ProcessingMetrics):
    """Send metrics to CloudWatch."""
    import boto3
    cloudwatch = boto3.client('cloudwatch')
    
    cloudwatch.put_metric_data(
        Namespace='OCRPipeline',
        MetricData=[
            {
                'MetricName': 'PagesProcessed',
                'Value': metrics.pages_processed,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'Step', 'Value': metrics.step_name}
                ]
            },
            {
                'MetricName': 'ProcessingDuration',
                'Value': metrics.end_time - metrics.start_time,
                'Unit': 'Seconds',
                'Dimensions': [
                    {'Name': 'Step', 'Value': metrics.step_name}
                ]
            }
        ]
    )
```

## Scaling Configuration

### Auto-scaling Rules

**AWS ECS**:
```json
{
  "AutoScalingGroupName": "ocr-pipeline-asg",
  "PolicyName": "scale-on-queue-depth",
  "PolicyType": "TargetTrackingScaling",
  "TargetTrackingConfiguration": {
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "SQSQueueApproximateNumberOfMessagesVisible"
    },
    "TargetValue": 10.0
  }
}
```

**Kubernetes HPA**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ocr-pipeline-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ocr-pipeline
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Cost Optimization

### Best Practices

1. **Use Spot Instances**: For non-critical batch processing
2. **Implement Queue-based Processing**: Process during off-peak hours
3. **Optimize Container Size**: Remove unnecessary dependencies
4. **Use Reserved Capacity**: For predictable workloads
5. **Implement Lifecycle Policies**: Auto-delete old artifacts

### Cost Monitoring

```python
def estimate_processing_cost(pages: int, region: str = "us-east-1"):
    """Estimate processing cost."""
    # Example rates (update with current pricing)
    rates = {
        "lambda_per_gb_sec": 0.0000166667,
        "s3_storage_gb_month": 0.023,
        "cloudwatch_logs_gb": 0.50
    }
    
    # Estimate resources
    memory_gb = 2
    duration_sec = pages * 3  # 3 sec per page
    storage_gb = pages * 0.005  # 5MB per page
    
    cost = (
        memory_gb * duration_sec * rates["lambda_per_gb_sec"] +
        storage_gb * rates["s3_storage_gb_month"] +
        (pages * 0.001) * rates["cloudwatch_logs_gb"]  # 1MB logs per page
    )
    
    return round(cost, 4)
```

## Security Best Practices

### Network Security

1. **Use VPC**: Deploy in private subnets
2. **Security Groups**: Restrict inbound/outbound traffic
3. **API Gateway**: Add authentication layer
4. **WAF Rules**: Protect against common attacks

### Data Security

1. **Encryption at Rest**: Enable S3/Blob encryption
2. **Encryption in Transit**: Use TLS 1.2+
3. **Access Controls**: IAM roles with least privilege
4. **Audit Logging**: Enable CloudTrail/Activity Log

### Compliance

```python
# Example: PII detection and redaction
import re

def detect_pii(text: str) -> list[str]:
    """Detect potential PII in extracted text."""
    patterns = {
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "phone": r'\b\d{3}-\d{3}-\d{4}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    }
    
    findings = []
    for pii_type, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            findings.append(f"Found {pii_type}: {len(matches)} instances")
    
    return findings
```

## Disaster Recovery

### Backup Strategy

1. **Automated S3 Replication**: Cross-region for artifacts
2. **Config Versioning**: Store in version control
3. **Database Backups**: If using persistent storage
4. **Regular Testing**: Quarterly DR drills

### Recovery Procedures

```bash
# Restore from backup
aws s3 sync s3://ocr-backup/run_YYYYMMDD_HHMMSS/ ./recovery/

# Rebuild from archived scripts
cd recovery/scripts_archive
python step1_find_anchors.py --run-dir ../

# Verify restoration
python validate_run.py recovery/
```

## Support and Maintenance

### Health Checks

```python
from fastapi import FastAPI
from typing import Dict

app = FastAPI()

@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    # Check dependencies
    try:
        import cv2
        import pytesseract
        tesseract_version = pytesseract.get_tesseract_version()
        
        return {
            "status": "healthy",
            "tesseract_version": str(tesseract_version),
            "opencv_version": cv2.__version__
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/metrics")
def get_metrics():
    """Return processing metrics."""
    return {
        "runs_total": 1234,
        "runs_success": 1200,
        "runs_failed": 34,
        "avg_processing_time_sec": 45.2
    }
```

---

**Last Updated**: October 1, 2025
**Version**: 1.0.0
