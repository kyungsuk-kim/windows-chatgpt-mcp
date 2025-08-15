#!/usr/bin/env python3
"""
HTML Documentation Deployment Script
Helps deploy the enhanced HTML installation documentation to GitHub.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    """Main deployment function."""
    print("🚀 HTML Documentation Deployment Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("docs/installation.html").exists():
        print("❌ Error: installation.html not found in docs/ directory")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check git status
    print("📋 Checking git status...")
    status = run_command("git status --porcelain")
    
    if status:
        print("📝 Found uncommitted changes:")
        print(status)
        
        # Check if installation.html is staged
        staged_files = run_command("git diff --cached --name-only")
        if "docs/installation.html" not in (staged_files or ""):
            print("📁 Adding installation.html to staging...")
            run_command("git add docs/installation.html")
        
        # Commit if needed
        print("💾 Committing changes...")
        commit_message = "Update HTML installation documentation"
        run_command(f'git commit -m "{commit_message}"')
    
    # Check remote
    print("🌐 Checking remote repository...")
    remote = run_command("git remote -v")
    if "github.com/kyungsuk-kim/windows-chatgpt-mcp" in (remote or ""):
        print("✅ Correct remote repository detected")
    else:
        print("⚠️  Warning: Remote repository may not be correct")
        print(f"Current remote: {remote}")
    
    # Show current branch
    branch = run_command("git branch --show-current")
    print(f"📍 Current branch: {branch}")
    
    # Instructions for manual push
    print("\n🔄 Next Steps:")
    print("1. Review the changes with: git log --oneline -5")
    print("2. Push to GitHub with: git push origin main")
    print("3. Visit your GitHub repository to see the updated documentation")
    print("4. The HTML documentation will be available at:")
    print("   https://github.com/kyungsuk-kim/windows-chatgpt-mcp/blob/main/docs/installation.html")
    
    # Show file info
    html_file = Path("docs/installation.html")
    if html_file.exists():
        size = html_file.stat().st_size
        print(f"\n📄 Documentation file info:")
        print(f"   File: {html_file}")
        print(f"   Size: {size:,} bytes")
        print(f"   Last modified: {html_file.stat().st_mtime}")
    
    print("\n✅ Deployment preparation complete!")
    print("The enhanced HTML documentation includes:")
    print("  • Comprehensive installation guide")
    print("  • Interactive features (progress bar, copy buttons)")
    print("  • Responsive design for mobile devices")
    print("  • Advanced configuration options")
    print("  • Detailed troubleshooting section")
    print("  • Distribution and deployment guide")

if __name__ == "__main__":
    main()