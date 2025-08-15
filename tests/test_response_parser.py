"""
Unit tests for Response Parser functionality.

Tests response parsing, cleaning, and formatting logic for ChatGPT responses.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from src.response_parser import ResponseParser, ChatGPTResponse, ResponseType
from src.exceptions import ValidationError, ParsingError


class TestChatGPTResponse:
    """Test the ChatGPTResponse data model."""
    
    def test_chatgpt_response_creation(self):
        """Test creating a ChatGPTResponse instance."""
        response = ChatGPTResponse(
            content="Hello, how can I help you?",
            response_type=ResponseType.TEXT,
            timestamp="2024-01-01T12:00:00Z",
            metadata={"tokens": 100}
        )
        
        assert response.content == "Hello, how can I help you?"
        assert response.response_type == ResponseType.TEXT
        assert response.timestamp == "2024-01-01T12:00:00Z"
        assert response.metadata == {"tokens": 100}
    
    def test_chatgpt_response_optional_fields(self):
        """Test creating a ChatGPTResponse with optional fields."""
        response = ChatGPTResponse(
            content="Test response",
            response_type=ResponseType.TEXT
        )
        
        assert response.content == "Test response"
        assert response.response_type == ResponseType.TEXT
        assert response.timestamp is None
        assert response.metadata == {}


class TestResponseParser:
    """Test the ResponseParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create a ResponseParser instance."""
        return ResponseParser()
    
    def test_parser_initialization(self, parser):
        """Test ResponseParser initialization."""
        assert parser is not None
        assert hasattr(parser, 'parse_response')
        assert hasattr(parser, 'clean_text')
        assert hasattr(parser, 'format_for_mcp')
    
    def test_clean_text_basic(self, parser):
        """Test basic text cleaning functionality."""
        # Test removing extra whitespace
        dirty_text = "  Hello   world  \n\n  "
        clean_text = parser.clean_text(dirty_text)
        assert clean_text == "Hello world"
        
        # Test removing special characters
        dirty_text = "Hello\x00world\x01test"
        clean_text = parser.clean_text(dirty_text)
        assert clean_text == "Helloworldtest"
    
    def test_clean_text_empty_input(self, parser):
        """Test cleaning empty or whitespace-only text."""
        assert parser.clean_text("") == ""
        assert parser.clean_text("   ") == ""
        assert parser.clean_text("\n\n\t\t") == ""
    
    def test_clean_text_unicode_handling(self, parser):
        """Test handling of unicode characters."""
        unicode_text = "Hello 🌍 world! 你好"
        clean_text = parser.clean_text(unicode_text)
        assert "🌍" in clean_text
        assert "你好" in clean_text
    
    def test_parse_response_text_content(self, parser):
        """Test parsing text response content."""
        raw_response = {
            "content": "This is a test response from ChatGPT.",
            "type": "text",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        parsed = parser.parse_response(raw_response)
        
        assert isinstance(parsed, ChatGPTResponse)
        assert parsed.content == "This is a test response from ChatGPT."
        assert parsed.response_type == ResponseType.TEXT
        assert parsed.timestamp == "2024-01-01T12:00:00Z"
    
    def test_parse_response_code_content(self, parser):
        """Test parsing code response content."""
        raw_response = {
            "content": "```python\nprint('Hello, world!')\n```",
            "type": "code",
            "language": "python"
        }
        
        parsed = parser.parse_response(raw_response)
        
        assert parsed.response_type == ResponseType.CODE
        assert "print('Hello, world!')" in parsed.content
        assert parsed.metadata.get("language") == "python"
    
    def test_parse_response_error_content(self, parser):
        """Test parsing error response content."""
        raw_response = {
            "content": "I'm sorry, I encountered an error processing your request.",
            "type": "error",
            "error_code": "PROCESSING_ERROR"
        }
        
        parsed = parser.parse_response(raw_response)
        
        assert parsed.response_type == ResponseType.ERROR
        assert "error processing" in parsed.content.lower()
        assert parsed.metadata.get("error_code") == "PROCESSING_ERROR"
    
    def test_parse_response_invalid_input(self, parser):
        """Test parsing with invalid input."""
        # Test None input
        with pytest.raises(ValidationError):
            parser.parse_response(None)
        
        # Test missing content
        with pytest.raises(ValidationError):
            parser.parse_response({"type": "text"})
        
        # Test empty content
        with pytest.raises(ValidationError):
            parser.parse_response({"content": "", "type": "text"})
    
    def test_parse_response_unknown_type(self, parser):
        """Test parsing with unknown response type."""
        raw_response = {
            "content": "Test content",
            "type": "unknown_type"
        }
        
        # Should default to TEXT type
        parsed = parser.parse_response(raw_response)
        assert parsed.response_type == ResponseType.TEXT
    
    def test_format_for_mcp_text_response(self, parser):
        """Test formatting text response for MCP."""
        response = ChatGPTResponse(
            content="Hello, this is a test response.",
            response_type=ResponseType.TEXT
        )
        
        formatted = parser.format_for_mcp(response)
        
        assert isinstance(formatted, dict)
        assert formatted["type"] == "text"
        assert formatted["content"] == "Hello, this is a test response."
    
    def test_format_for_mcp_code_response(self, parser):
        """Test formatting code response for MCP."""
        response = ChatGPTResponse(
            content="print('Hello, world!')",
            response_type=ResponseType.CODE,
            metadata={"language": "python"}
        )
        
        formatted = parser.format_for_mcp(response)
        
        assert formatted["type"] == "code"
        assert formatted["language"] == "python"
        assert "print('Hello, world!')" in formatted["content"]
    
    def test_format_for_mcp_error_response(self, parser):
        """Test formatting error response for MCP."""
        response = ChatGPTResponse(
            content="An error occurred",
            response_type=ResponseType.ERROR,
            metadata={"error_code": "TEST_ERROR"}
        )
        
        formatted = parser.format_for_mcp(response)
        
        assert formatted["type"] == "error"
        assert formatted["error_code"] == "TEST_ERROR"
        assert formatted["content"] == "An error occurred"
    
    def test_format_for_mcp_with_metadata(self, parser):
        """Test formatting response with metadata for MCP."""
        response = ChatGPTResponse(
            content="Test content",
            response_type=ResponseType.TEXT,
            timestamp="2024-01-01T12:00:00Z",
            metadata={"tokens": 50, "model": "gpt-4"}
        )
        
        formatted = parser.format_for_mcp(response)
        
        assert formatted["timestamp"] == "2024-01-01T12:00:00Z"
        assert formatted["tokens"] == 50
        assert formatted["model"] == "gpt-4"
    
    def test_extract_code_blocks(self, parser):
        """Test extracting code blocks from response content."""
        content_with_code = """
        Here's a Python example:
        
        ```python
        def hello():
            print("Hello, world!")
        ```
        
        And here's some JavaScript:
        
        ```javascript
        console.log("Hello, world!");
        ```
        """
        
        code_blocks = parser.extract_code_blocks(content_with_code)
        
        assert len(code_blocks) == 2
        assert code_blocks[0]["language"] == "python"
        assert "def hello():" in code_blocks[0]["code"]
        assert code_blocks[1]["language"] == "javascript"
        assert "console.log" in code_blocks[1]["code"]
    
    def test_extract_code_blocks_no_code(self, parser):
        """Test extracting code blocks when none exist."""
        content_without_code = "This is just plain text with no code blocks."
        
        code_blocks = parser.extract_code_blocks(content_without_code)
        
        assert len(code_blocks) == 0
    
    def test_detect_response_type(self, parser):
        """Test automatic response type detection."""
        # Test code detection
        code_content = "```python\nprint('hello')\n```"
        assert parser.detect_response_type(code_content) == ResponseType.CODE
        
        # Test error detection
        error_content = "I'm sorry, I can't help with that request."
        assert parser.detect_response_type(error_content) == ResponseType.ERROR
        
        # Test normal text
        text_content = "Here's some helpful information about your question."
        assert parser.detect_response_type(text_content) == ResponseType.TEXT
    
    def test_sanitize_content(self, parser):
        """Test content sanitization for security."""
        # Test removing potentially harmful content
        harmful_content = "<script>alert('xss')</script>Hello world"
        sanitized = parser.sanitize_content(harmful_content)
        assert "<script>" not in sanitized
        assert "Hello world" in sanitized
        
        # Test preserving safe HTML-like content
        safe_content = "Use <code>print()</code> to output text"
        sanitized = parser.sanitize_content(safe_content)
        assert "<code>" in sanitized  # Should preserve safe tags
    
    def test_parse_streaming_response(self, parser):
        """Test parsing streaming response chunks."""
        chunks = [
            {"content": "Hello", "type": "text", "chunk_id": 1},
            {"content": " world", "type": "text", "chunk_id": 2},
            {"content": "!", "type": "text", "chunk_id": 3, "final": True}
        ]
        
        complete_response = parser.parse_streaming_response(chunks)
        
        assert complete_response.content == "Hello world!"
        assert complete_response.response_type == ResponseType.TEXT
        assert complete_response.metadata.get("chunks") == 3
    
    def test_parse_streaming_response_invalid(self, parser):
        """Test parsing invalid streaming response."""
        # Test empty chunks
        with pytest.raises(ValidationError):
            parser.parse_streaming_response([])
        
        # Test chunks without content
        invalid_chunks = [{"type": "text", "chunk_id": 1}]
        with pytest.raises(ValidationError):
            parser.parse_streaming_response(invalid_chunks)


class TestResponseParserIntegration:
    """Integration tests for ResponseParser with different response formats."""
    
    @pytest.fixture
    def parser(self):
        """Create a ResponseParser instance."""
        return ResponseParser()
    
    def test_full_parsing_workflow(self, parser):
        """Test complete parsing workflow from raw to MCP format."""
        raw_response = {
            "content": "  Here's a Python function:\n\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n```\n\nThis function takes a name and returns a greeting.  ",
            "type": "mixed",
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {"model": "gpt-4", "tokens": 45}
        }
        
        # Parse the response
        parsed = parser.parse_response(raw_response)
        
        # Verify parsing
        assert parsed.response_type == ResponseType.MIXED  # Should preserve mixed type
        assert "def greet(name):" in parsed.content
        assert parsed.timestamp == "2024-01-01T12:00:00Z"
        
        # Format for MCP
        formatted = parser.format_for_mcp(parsed)
        
        # Verify formatting
        assert formatted["type"] == "mixed"
        assert formatted["timestamp"] == "2024-01-01T12:00:00Z"
        assert formatted["metadata"]["model"] == "gpt-4"
        assert formatted["metadata"]["tokens"] == 45
    
    def test_error_response_workflow(self, parser):
        """Test parsing and formatting error responses."""
        raw_error = {
            "content": "I apologize, but I cannot process that request due to content policy restrictions.",
            "type": "error",
            "error_code": "CONTENT_POLICY_VIOLATION",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        parsed = parser.parse_response(raw_error)
        formatted = parser.format_for_mcp(parsed)
        
        assert parsed.response_type == ResponseType.ERROR
        assert formatted["type"] == "error"
        assert formatted["error_code"] == "CONTENT_POLICY_VIOLATION"
        assert "content policy" in formatted["content"].lower()
    
    def test_complex_mixed_content(self, parser):
        """Test parsing complex mixed content responses."""
        complex_content = """
        I'll help you with that Python problem. Here are a few approaches:
        
        **Approach 1: Using a loop**
        ```python
        def sum_numbers(numbers):
            total = 0
            for num in numbers:
                total += num
            return total
        ```
        
        **Approach 2: Using built-in sum()**
        ```python
        def sum_numbers(numbers):
            return sum(numbers)
        ```
        
        Both approaches will work, but the second one is more Pythonic.
        """
        
        raw_response = {
            "content": complex_content,
            "type": "educational",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        parsed = parser.parse_response(raw_response)
        formatted = parser.format_for_mcp(parsed)
        
        # Should detect as code due to multiple code blocks
        assert parsed.response_type == ResponseType.CODE
        assert "def sum_numbers" in parsed.content
        assert "Pythonic" in parsed.content
        
        # Should extract code blocks
        code_blocks = parser.extract_code_blocks(parsed.content)
        assert len(code_blocks) == 2
        assert all(block["language"] == "python" for block in code_blocks)


if __name__ == "__main__":
    pytest.main([__file__])