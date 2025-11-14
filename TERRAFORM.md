# Terraform Infrastructure Documentation

## Overview

This Terraform configuration deploys the Basic Movie Recommender application as a Google Cloud Run service. Cloud Run is a fully managed serverless platform that automatically scales your containerized applications.

## Implementation Details

### Configuration Variables

The infrastructure uses the following configurable variables:

**GCP Configuration:**
- `credentials_file`: Path to GCP service account credentials JSON file (default: `credentials-gcp.json`)
- `project_id`: GCP project ID (default: `isn2025-2`)
- `region`: GCP region for deployment (default: `southamerica-east1`)

**Service Configuration:**
- `service_name`: Name of the Cloud Run service (default: `basic-movie-recommender`)
- `image`: Container image URI from Google Artifact Registry
- `port`: Container port (default: `8080`)
- `min_instances`: Minimum number of instances (default: `0` - scales to zero)
- `max_instances`: Maximum number of instances (default: `3`)
- `allow_unauthenticated`: Enable public access (default: `true`)

**Application Secrets (Required):**
- `omdbapi_uri`: OMDb API endpoint URI
- `omdbapi_key`: OMDb API key
- `mongodb_uri`: MongoDB connection string

### Resources Created

1. **Cloud Run Service** (`google_cloud_run_v2_service`)
   - Deploys the containerized application
   - Configures environment variables for API credentials
   - Sets up auto-scaling (0-3 instances)
   - Allows all ingress traffic
   - Disables deletion protection for easier management

2. **IAM Binding** (`google_cloud_run_v2_service_iam_member`)
   - Conditionally grants public access (`allUsers`) when `allow_unauthenticated` is `true`
   - Uses the `roles/run.invoker` role

### Outputs

- `service_name`: The deployed service name
- `service_uri`: The public URL of the deployed service

## Prerequisites

1. **GCP Account & Project**
   - A GCP project with billing enabled
   - Cloud Run API enabled
   - Artifact Registry API enabled (for container images)

2. **Service Account Credentials**
   - A service account with the following roles:
     - `roles/run.admin` (to create/update Cloud Run services)
     - `roles/iam.serviceAccountUser` (to manage IAM bindings)
   - Download the credentials JSON file

3. **Terraform Installation**
   ```bash
   # macOS
   brew install terraform
   
   # Linux
   wget https://releases.hashicorp.com/terraform/1.x.x/terraform_1.x.x_linux_amd64.zip
   unzip terraform_1.x.x_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

4. **Container Image**
   - The Docker image must already exist in Google Artifact Registry
   - Image URI format: `REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE_NAME`

## Usage

### Initial Setup

1. **Place your GCP credentials file** in the project root:
   ```bash
   cp /path/to/your/service-account-key.json credentials-gcp.json
   ```

2. **Initialize Terraform:**
   ```bash
   terraform init
   ```
   This downloads the Google Cloud provider plugin.

### Deployment

**Option 1: Using terraform.tfvars file (Recommended)**

Create a `terraform.tfvars` file:
```hcl
project_id = "your-project-id"
region = "southamerica-east1"
service_name = "basic-movie-recommender"
image = "southamerica-east1-docker.pkg.dev/your-project/repo/image-name"
omdbapi_uri = "https://www.omdbapi.com/"
omdbapi_key = "your-omdb-api-key"
mongodb_uri = "mongodb+srv://user:pass@cluster.mongodb.net/dbname"
```

Then deploy:
```bash
terraform plan    # Review changes
terraform apply   # Apply changes
```

**Option 2: Using command-line variables**

```bash
terraform apply \
  -var="omdbapi_uri=https://www.omdbapi.com/" \
  -var="omdbapi_key=your-key" \
  -var="mongodb_uri=mongodb+srv://..."
```

**Option 3: Using environment variables**

Set variables with `TF_VAR_` prefix:
```bash
export TF_VAR_omdbapi_uri="https://www.omdbapi.com/"
export TF_VAR_omdbapi_key="your-key"
export TF_VAR_mongodb_uri="mongodb+srv://..."
terraform apply
```

### Viewing Outputs

After deployment, view the service URL:
```bash
terraform output service_uri
```

### Updating the Service

To update configuration or redeploy:
```bash
terraform plan    # Review changes
terraform apply   # Apply updates
```

### Destroying Infrastructure

To remove all resources:
```bash
terraform destroy
```

**Note:** This will delete the Cloud Run service. Make sure you have backups if needed.

## Customization Examples

### Change Scaling Configuration

Edit `main.tf` or override variables:
```bash
terraform apply -var="min_instances=1" -var="max_instances=10"
```

### Disable Public Access

```bash
terraform apply -var="allow_unauthenticated=false"
```

### Use Different Region

```bash
terraform apply -var="region=us-central1"
```

## Troubleshooting

### Authentication Errors
- Verify `credentials-gcp.json` exists and is valid
- Ensure service account has required permissions

### Image Not Found
- Verify the image exists in Artifact Registry
- Check image URI format matches your registry

### Permission Denied
- Ensure Cloud Run API is enabled: `gcloud services enable run.googleapis.com`
- Verify service account has `roles/run.admin` role

### Variable Not Set
- Required variables (`omdbapi_uri`, `omdbapi_key`, `mongodb_uri`) must be provided
- Use `terraform.tfvars` or command-line flags

## Security Considerations

1. **Credentials File**: Never commit `credentials-gcp.json` to version control
2. **Secrets**: Consider using Google Secret Manager for sensitive values instead of plain variables
3. **Public Access**: Set `allow_unauthenticated=false` if you need authenticated access only
4. **IAM**: Review IAM bindings regularly to follow principle of least privilege

## Additional Resources

- [Terraform Google Provider Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Terraform Cloud Run Resources](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service)

