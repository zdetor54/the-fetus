# Security Configuration

## Sensitive Files Setup

This project uses template files for sensitive configuration. To set up your environment:

1. **Environment Variables**: 
   - Copy `keys.env.template` to `keys.env`
   - Fill in your actual API keys and secrets
   - `keys.env` is ignored by Git and will not be committed

2. **Azure Deployment Configuration**:
   - Copy `deployment.json.template` to `deployment.json`
   - Fill in your actual Azure credentials
   - `deployment.json` is ignored by Git and will not be committed

⚠️ **NEVER commit actual API keys, passwords, or secrets to Git!**

These files are listed in `.gitignore` to prevent accidental commits.
