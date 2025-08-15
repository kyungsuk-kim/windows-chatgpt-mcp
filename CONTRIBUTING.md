# Contributing to Windows ChatGPT MCP Tool

Thank you for your interest in contributing to the Windows ChatGPT MCP Tool! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow:

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors
- Report any unacceptable behavior to the project maintainers

## Getting Started

### Prerequisites

- Windows 11 (or Windows 10 1903+)
- Python 3.8 or higher
- Git for version control
- ChatGPT desktop application for testing
- Claude Desktop or VS Code with Claude CLI for integration testing

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/windows-chatgpt-mcp.git
   cd windows-chatgpt-mcp
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e .[dev]
```

### 3. Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

### 4. Verify Setup

```bash
# Run tests
python -m pytest

# Run linting
flake8 src tests
black --check src tests

# Test MCP server
python -m src.mcp_server --test
```

## Contributing Process

### 1. Choose an Issue

- Look for issues labeled `good first issue` for beginners
- Check existing issues before creating new ones
- Comment on issues you'd like to work on

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 3. Make Changes

- Follow the coding standards below
- Write tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 4. Test Your Changes

```bash
# Run full test suite
python run_tests.py

# Run specific tests
python -m pytest tests/test_your_module.py

# Test integration
python examples/automation_scripts/test_integration.py
```

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use Black for code formatting
- Use type hints for all functions
- Maximum line length: 88 characters

### Code Organization

```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import pyautogui
from mcp import Server

# Local imports
from .config import Config
from .exceptions import WindowsAutomationError
```

### Naming Conventions

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Documentation

- Use docstrings for all public functions and classes
- Follow Google docstring format
- Include type information and examples

```python
def send_message(self, message: str, timeout: int = 30) -> Dict[str, Any]:
    """Send a message to ChatGPT and return the response.
    
    Args:
        message: The message to send to ChatGPT
        timeout: Maximum time to wait for response in seconds
        
    Returns:
        Dictionary containing response data and metadata
        
    Raises:
        WindowsAutomationError: If ChatGPT window cannot be found
        TimeoutError: If response takes longer than timeout
        
    Example:
        >>> response = handler.send_message("Hello, ChatGPT!")
        >>> print(response['content'])
    """
```

## Testing Guidelines

### Test Structure

```
tests/
├── test_mcp_server.py          # MCP server tests
├── test_windows_automation.py  # Automation tests
├── test_config.py              # Configuration tests
├── test_integration.py         # End-to-end tests
└── fixtures/                   # Test data and mocks
```

### Writing Tests

- Use pytest framework
- Mock external dependencies (Windows APIs, ChatGPT app)
- Test both success and failure scenarios
- Include integration tests for critical paths

```python
import pytest
from unittest.mock import Mock, patch
from src.windows_automation import WindowsAutomationHandler

class TestWindowsAutomationHandler:
    @pytest.fixture
    def handler(self):
        return WindowsAutomationHandler()
    
    @patch('src.windows_automation.pyautogui')
    def test_send_message_success(self, mock_pyautogui, handler):
        # Test implementation
        pass
    
    def test_send_message_invalid_input(self, handler):
        with pytest.raises(ValueError):
            handler.send_message("")
```

### Test Coverage

- Aim for >90% code coverage
- Focus on critical functionality
- Include edge cases and error conditions

## Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings and inline comments
2. **User Documentation**: README, setup guides, usage examples
3. **API Documentation**: Technical reference for developers
4. **Troubleshooting**: Common issues and solutions

### Documentation Standards

- Write clear, concise explanations
- Include practical examples
- Keep documentation up-to-date with code changes
- Use consistent formatting and style

### Building Documentation

```bash
# Generate API documentation
python -m pydoc -w src

# Validate markdown
markdownlint docs/*.md
```

## Submitting Changes

### Pull Request Process

1. **Update Documentation**: Ensure all documentation is current
2. **Add Tests**: Include tests for new functionality
3. **Run Full Test Suite**: Verify all tests pass
4. **Update Changelog**: Add entry to CHANGELOG.md
5. **Create Pull Request**: Use the PR template

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Review Process

- All PRs require at least one review
- Address reviewer feedback promptly
- Maintain a respectful, collaborative tone
- Be open to suggestions and improvements

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist

1. Update version numbers in:
   - `setup.py`
   - `src/__version__.py`
   - `CHANGELOG.md`

2. Run full test suite
3. Build and test packages
4. Create release notes
5. Tag release in Git
6. Publish packages

## Getting Help

### Resources

- **Documentation**: Check the `docs/` directory
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Ask for feedback on draft PRs

### Communication

- Be specific about problems and questions
- Include relevant code snippets and error messages
- Provide system information (Windows version, Python version)
- Be patient and respectful

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- README.md contributors section
- GitHub contributors page

Thank you for contributing to the Windows ChatGPT MCP Tool! Your efforts help make this tool better for everyone.