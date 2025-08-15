#!/usr/bin/env python3
"""
GitHub Setup Script for Windows ChatGPT MCP Tool

This script helps set up the GitHub repository for the Windows ChatGPT MCP tool.
It provides instructions and automated steps for GitHub deployment.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip(), True
    except subprocess.CalledProcessError as e:
        return e.stderr.strip(), False

def check_git_status():
    """Check if git is initialized and configured."""
    print("🔍 Checking Git status...")
    
    # Check if git is initialized
    output, success = run_command("git status")
    if not success:
        print("❌ Git repository not initialized")
        return False
    
    print("✅ Git repository is initialized")
    
    # Check git configuration
    name_output, name_success = run_command("git config user.name")
    email_output, email_success = run_command("git config user.email")
    
    if name_success and email_success:
        print(f"✅ Git configured with user: {name_output} <{email_output}>")
    else:
        print("⚠️  Git user configuration incomplete")
    
    return True

def check_remote_repository():
    """Check if remote repository is configured."""
    print("\n🔍 Checking remote repository...")
    
    output, success = run_command("git remote -v")
    if success and "origin" in output:
        print("✅ Remote repository configured:")
        print(output)
        return True
    else:
        print("❌ No remote repository configured")
        return False

def display_github_setup_instructions():
    """Display instructions for GitHub setup."""
    print("\n" + "="*60)
    print("📋 GITHUB SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n1. 🌐 Create GitHub Repository:")
    print("   - Go to https://github.com/kyungsuk-kim")
    print("   - Click 'New repository'")
    print("   - Repository name: windows-chatgpt-mcp")
    print("   - Description: Windows ChatGPT MCP tool for Claude integration")
    print("   - Make it public")
    print("   - Don't initialize with README (we already have files)")
    print("   - Click 'Create repository'")
    
    print("\n2. 🔐 Set up Authentication:")
    print("   Option A - Personal Access Token (Recommended):")
    print("   - Go to GitHub Settings > Developer settings > Personal access tokens")
    print("   - Generate new token (classic)")
    print("   - Select scopes: repo, workflow")
    print("   - Copy the token")
    print("   - Use token as password when pushing")
    print()
    print("   Option B - SSH Key:")
    print("   - Generate SSH key: ssh-keygen -t ed25519 -C 'your-email@example.com'")
    print("   - Add to GitHub: Settings > SSH and GPG keys")
    print("   - Change remote URL: git remote set-url origin git@github.com:kyungsuk-kim/windows-chatgpt-mcp.git")
    
    print("\n3. 📤 Push to GitHub:")
    print("   - Run: git push -u origin main")
    print("   - Enter your GitHub username and token/password when prompted")
    
    print("\n4. ✅ Verify Deployment:")
    print("   - Visit: https://github.com/kyungsuk-kim/windows-chatgpt-mcp")
    print("   - Check that all files are uploaded correctly")
    print("   - Verify README.md displays properly")

def main():
    """Main function to run GitHub setup checks and instructions."""
    print("🚀 Windows ChatGPT MCP - GitHub Setup")
    print("="*50)
    
    # Change to project directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    print(f"📁 Working directory: {project_dir}")
    
    # Check git status
    git_ok = check_git_status()
    
    # Check remote repository
    remote_ok = check_remote_repository()
    
    # Display setup instructions
    display_github_setup_instructions()
    
    print("\n" + "="*60)
    print("📝 CURRENT STATUS:")
    print("="*60)
    print(f"Git initialized: {'✅' if git_ok else '❌'}")
    print(f"Remote configured: {'✅' if remote_ok else '❌'}")
    print(f"Ready to push: {'✅' if git_ok and remote_ok else '❌'}")
    
    if git_ok and remote_ok:
        print("\n🎉 Repository is ready for GitHub deployment!")
        print("💡 Run 'git push -u origin main' to deploy to GitHub")
    else:
        print("\n⚠️  Please complete the setup steps above before pushing to GitHub")
    
    print("\n📚 Additional Resources:")
    print("- GitHub Docs: https://docs.github.com/en/get-started")
    print("- Git Tutorial: https://git-scm.com/docs/gittutorial")

if __name__ == "__main__":
    main()