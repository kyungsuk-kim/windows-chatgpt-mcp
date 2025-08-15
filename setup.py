#!/usr/bin/env python3
"""
Setup script for Windows ChatGPT MCP Tool
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Windows ChatGPT MCP Tool - Enables Claude to interact with ChatGPT on Windows 11"

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name="windows-chatgpt-mcp",
    version="1.0.0",
    description="MCP tool for Windows 11 that enables Claude to interact with ChatGPT desktop application",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Windows ChatGPT MCP Tool Developer",
    author_email="developer@example.com",
    url="https://github.com/example/windows-chatgpt-mcp",
    project_urls={
        "Bug Reports": "https://github.com/example/windows-chatgpt-mcp/issues",
        "Source": "https://github.com/example/windows-chatgpt-mcp",
        "Documentation": "https://github.com/example/windows-chatgpt-mcp#readme",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=3.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: System Shells",
        "Topic :: Utilities",
        "Environment :: Win32 (MS Windows)",
    ],
    keywords="mcp claude chatgpt windows automation gui desktop",
    entry_points={
        "console_scripts": [
            "windows-chatgpt-mcp=windows_chatgpt_mcp.mcp_server:main",
            "chatgpt-mcp-verify=windows_chatgpt_mcp.verify:main",
        ],
    },
    include_package_data=True,
    package_data={
        "windows_chatgpt_mcp": [
            "config/*.json",
            "examples/*.json",
        ],
    },
    zip_safe=False,
    platforms=["win32", "win_amd64"],
)