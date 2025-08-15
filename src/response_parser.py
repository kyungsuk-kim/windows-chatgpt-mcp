"""
Response Parser - Parse and format ChatGPT responses

This module provides functionality to parse, clean, and format ChatGPT responses
for use with the MCP protocol. It handles different response types including
text, code, and error responses.
"""

import re
import html
import logging
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Union

from .exceptions import ValidationError, ParsingError


class ResponseType(Enum):
    """Enumeration of different response types."""
    TEXT = "text"
    CODE = "code"
    ERROR = "error"
    MIXED = "mixed"


@dataclass
class ChatGPTResponse:
    """Data model for parsed ChatGPT responses."""
    content: str
    response_type: ResponseType
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResponseParser:
    """
    Parser for ChatGPT responses with cleaning and formatting capabilities.
    
    This class handles parsing raw ChatGPT responses, cleaning the content,
    detecting response types, and formatting for MCP protocol consumption.
    """
    
    def __init__(self):
        """Initialize the ResponseParser."""
        self.logger = logging.getLogger(__name__)
        
        # Regex patterns for content detection
        self.code_block_pattern = re.compile(r'```(\w+)?\s*\n(.*?)\n\s*```', re.DOTALL)
        self.inline_code_pattern = re.compile(r'`([^`]+)`')
        self.error_keywords = [
            "sorry", "can't", "cannot", "unable", "error", "apologize",
            "don't understand", "not sure", "unclear", "policy", "restriction"
        ]
        
        # HTML tags to preserve (safe tags)
        self.safe_html_tags = ['code', 'pre', 'em', 'strong', 'b', 'i']
        
    def parse_response(self, raw_response: Union[Dict[str, Any], str]) -> ChatGPTResponse:
        """
        Parse a raw ChatGPT response into a structured format.
        
        Args:
            raw_response: Raw response data from ChatGPT
            
        Returns:
            ChatGPTResponse: Parsed and structured response
            
        Raises:
            ValidationError: If the input is invalid
            ParsingError: If parsing fails
        """
        if raw_response is None:
            raise ValidationError("Response cannot be None", field="raw_response", value=None)
        
        # Handle string input
        if isinstance(raw_response, str):
            if not raw_response.strip():
                raise ValidationError("Response content cannot be empty", field="content", value=raw_response)
            
            return ChatGPTResponse(
                content=self.clean_text(raw_response),
                response_type=self.detect_response_type(raw_response),
                timestamp=datetime.now().isoformat()
            )
        
        # Handle dictionary input
        if not isinstance(raw_response, dict):
            raise ValidationError("Response must be a string or dictionary", field="raw_response", value=type(raw_response))
        
        content = raw_response.get("content", "")
        if not content or not content.strip():
            raise ValidationError("Response content cannot be empty", field="content", value=content)
        
        # Clean and sanitize content
        cleaned_content = self.clean_text(content)
        sanitized_content = self.sanitize_content(cleaned_content)
        
        # Determine response type
        response_type_str = raw_response.get("type", "")
        if response_type_str:
            try:
                response_type = ResponseType(response_type_str)
                # If type is provided but not recognized, detect from content
            except ValueError:
                response_type = self.detect_response_type(sanitized_content)
        else:
            response_type = self.detect_response_type(sanitized_content)
        
        # Extract metadata
        metadata = {}
        for key, value in raw_response.items():
            if key not in ["content", "type", "timestamp"]:
                metadata[key] = value
        
        return ChatGPTResponse(
            content=sanitized_content,
            response_type=response_type,
            timestamp=raw_response.get("timestamp"),
            metadata=metadata
        )
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and control characters.
        
        Args:
            text: Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove control characters except newlines and tabs
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Max 2 consecutive newlines
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Multiple spaces/tabs to single space
        
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def sanitize_content(self, content: str) -> str:
        """
        Sanitize content for security by removing potentially harmful elements.
        
        Args:
            content: Content to sanitize
            
        Returns:
            str: Sanitized content
        """
        if not content:
            return ""
        
        # For code content, we want to preserve formatting and special characters
        # Only remove truly dangerous patterns without HTML escaping everything
        sanitized = content
        
        # Remove potentially harmful patterns
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def detect_response_type(self, content: str) -> ResponseType:
        """
        Automatically detect the response type based on content.
        
        Args:
            content: Response content to analyze
            
        Returns:
            ResponseType: Detected response type
        """
        if not content:
            return ResponseType.TEXT
        
        content_lower = content.lower()
        
        # Check for code blocks
        if self.code_block_pattern.search(content) or self.inline_code_pattern.search(content):
            return ResponseType.CODE
        
        # Check for error indicators
        if any(keyword in content_lower for keyword in self.error_keywords):
            return ResponseType.ERROR
        
        # Default to text
        return ResponseType.TEXT
    
    def extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from response content.
        
        Args:
            content: Content to extract code blocks from
            
        Returns:
            List[Dict[str, str]]: List of code blocks with language and code
        """
        code_blocks = []
        
        for match in self.code_block_pattern.finditer(content):
            language = match.group(1) or "text"
            code = match.group(2).strip()
            
            code_blocks.append({
                "language": language,
                "code": code
            })
        
        return code_blocks
    
    def format_for_mcp(self, response: ChatGPTResponse) -> Dict[str, Any]:
        """
        Format a ChatGPTResponse for MCP protocol consumption.
        
        Args:
            response: Parsed ChatGPT response
            
        Returns:
            Dict[str, Any]: MCP-formatted response
        """
        formatted = {
            "type": response.response_type.value,
            "content": response.content
        }
        
        # Add timestamp if available
        if response.timestamp:
            formatted["timestamp"] = response.timestamp
        
        # Add metadata
        formatted.update(response.metadata)
        
        # Add response-type specific fields
        if response.response_type == ResponseType.CODE:
            code_blocks = self.extract_code_blocks(response.content)
            if code_blocks:
                formatted["language"] = code_blocks[0]["language"]
                formatted["code_blocks"] = code_blocks
        
        return formatted
    
    def parse_streaming_response(self, chunks: List[Dict[str, Any]]) -> ChatGPTResponse:
        """
        Parse a streaming response from multiple chunks.
        
        Args:
            chunks: List of response chunks
            
        Returns:
            ChatGPTResponse: Combined response from all chunks
            
        Raises:
            ValidationError: If chunks are invalid
        """
        if not chunks:
            raise ValidationError("Chunks list cannot be empty", field="chunks", value=chunks)
        
        # Combine content from all chunks
        combined_content = ""
        response_type = ResponseType.TEXT
        timestamp = None
        metadata = {"chunks": len(chunks)}
        
        for i, chunk in enumerate(chunks):
            if "content" not in chunk:
                raise ValidationError(f"Chunk {i} missing content", field="content", value=chunk)
            
            combined_content += chunk["content"]
            
            # Use timestamp from first chunk
            if timestamp is None and "timestamp" in chunk:
                timestamp = chunk["timestamp"]
            
            # Collect metadata from chunks
            for key, value in chunk.items():
                if key not in ["content", "type", "timestamp", "chunk_id", "final"]:
                    metadata[key] = value
        
        # Clean and detect type for combined content
        cleaned_content = self.clean_text(combined_content)
        response_type = self.detect_response_type(cleaned_content)
        
        return ChatGPTResponse(
            content=cleaned_content,
            response_type=response_type,
            timestamp=timestamp,
            metadata=metadata
        )