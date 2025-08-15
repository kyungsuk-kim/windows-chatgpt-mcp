# GitHub Deployment Guide

This document provides step-by-step instructions for deploying the Windows ChatGPT MCP tool to GitHub.

## Repository Information

- **Repository URL**: https://github.com/kyungsuk-kim/windows-chatgpt-mcp
- **Owner**: kyungsuk-kim
- **Repository Name**: windows-chatgpt-mcp

## Deployment Status

✅ Git repository initialized  
✅ Project files added to git  
✅ Initial commit created  
✅ Remote repository configured  
✅ Branch renamed to 'main'  
⏳ **Pending**: Push to GitHub (requires authentication)

## Prerequisites

Before pushing to GitHub, ensure you have:

1. **GitHub Account**: Access to the kyungsuk-kim GitHub account
2. **Repository Created**: The repository `windows-chatgpt-mcp` must exist on GitHub
3. **Authentication**: Either Personal Access Token or SSH key configured

## Step-by-Step Deployment

### 1. Create GitHub Repository

1. Go to https://github.com/kyungsuk-kim
2. Click "New repository" or go to https://github.com/new
3. Fill in repository details:
   - **Repository name**: `windows-chatgpt-mcp`
   - **Description**: `Windows ChatGPT MCP tool for Claude integration`
   - **Visibility**: Public (recommended for open source)
   - **Initialize**: Do NOT check "Add a README file" (we already have one)
4. Click "Create repository"

### 2. Set Up Authentication

#### Option A: Personal Access Token (Recommended)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Set expiration and select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
4. Click "Generate token"
5. **Important**: Copy the token immediately (you won't see it again)

#### Option B: SSH Key

1. Generate SSH key:
   ```cmd
   ssh-keygen -t ed25519 -C "your-email@example.com"
   ```
2. Add to SSH agent:
   ```cmd
   ssh-add ~/.ssh/id_ed25519
   ```
3. Copy public key:
   ```cmd
   type ~/.ssh/id_ed25519.pub
   ```
4. Add to GitHub: Settings → SSH and GPG keys → New SSH key
5. Update remote URL:
   ```cmd
   git remote set-url origin git@github.com:kyungsuk-kim/windows-chatgpt-mcp.git
   ```

### 3. Push to GitHub

1. **Navigate to project directory**:
   ```cmd
   cd windows-chatgpt-mcp
   ```

2. **Verify git status**:
   ```cmd
   git status
   git log --oneline
   ```

3. **Push to GitHub**:
   ```cmd
   git push -u origin main
   ```

4. **Enter credentials when prompted**:
   - Username: `kyungsuk-kim`
   - Password: Your Personal Access Token (if using HTTPS)

### 4. Verify Deployment

1. Visit https://github.com/kyungsuk-kim/windows-chatgpt-mcp
2. Verify all files are present:
   - ✅ README.md displays correctly
   - ✅ Source code in `src/` directory
   - ✅ Documentation in `docs/` directory
   - ✅ Tests in `tests/` directory
   - ✅ Configuration files (setup.py, requirements.txt, etc.)

## Troubleshooting

### Authentication Issues

**Error**: `Permission denied` or `403 Forbidden`
- **Solution**: Check your Personal Access Token or SSH key
- **Verify**: Token has correct scopes (`repo`, `workflow`)
- **Try**: Regenerate token if it's expired

**Error**: `Repository not found`
- **Solution**: Ensure the repository exists on GitHub
- **Check**: Repository name matches exactly: `windows-chatgpt-mcp`
- **Verify**: You have access to the kyungsuk-kim account

### Git Issues

**Error**: `fatal: not a git repository`
- **Solution**: Run `git init` in the project directory
- **Then**: Re-run the deployment steps

**Error**: `nothing to commit`
- **Solution**: Run `git add .` to stage all files
- **Then**: Run `git commit -m "Initial commit"`

## Post-Deployment Tasks

After successful deployment:

1. **Create Release**:
   - Go to repository → Releases → Create a new release
   - Tag version: `v1.0.0`
   - Release title: `Windows ChatGPT MCP Tool v1.0.0`
   - Add release notes from CHANGELOG.md

2. **Set Up GitHub Actions** (Optional):
   - Add CI/CD workflows for automated testing
   - Set up automated releases

3. **Update Documentation**:
   - Ensure all links point to the correct repository
   - Update installation instructions with correct URLs

4. **Configure Repository Settings**:
   - Add topics/tags for discoverability
   - Set up branch protection rules
   - Configure issue templates

## Automated Setup Script

For convenience, you can use the automated setup script:

```cmd
python scripts/github_setup.py
```

This script will:
- Check git configuration
- Verify remote repository setup
- Display detailed setup instructions
- Provide status information

## Support

If you encounter issues during deployment:

1. Check the troubleshooting section above
2. Review GitHub's documentation: https://docs.github.com/en/get-started
3. Consult Git documentation: https://git-scm.com/docs

## Security Notes

- Never commit sensitive information (API keys, passwords)
- Use `.gitignore` to exclude sensitive files
- Regularly rotate Personal Access Tokens
- Use SSH keys for enhanced security

---

**Last Updated**: $(date)  
**Repository**: https://github.com/kyungsuk-kim/windows-chatgpt-mcp