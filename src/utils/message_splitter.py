"""
Message splitting utilities for Discord's 2000 character limit.
Intelligently splits messages while preserving formatting.
"""

import re
from typing import List


def split_message(
    content: str,
    max_length: int = 2000,
    preserve_code_blocks: bool = True,
    preserve_sentences: bool = True,
) -> List[str]:
    """
    Split a message into chunks that fit Discord's character limit.
    
    Args:
        content: The message content to split
        max_length: Maximum length per chunk (default: 2000)
        preserve_code_blocks: Try to keep code blocks intact
        preserve_sentences: Try to split on sentence boundaries
    
    Returns:
        List of message chunks
    """
    if len(content) <= max_length:
        return [content]
    
    chunks: List[str] = []
    
    # Handle code blocks specially
    if preserve_code_blocks and "```" in content:
        chunks = _split_with_code_blocks(content, max_length)
    else:
        chunks = _split_simple(content, max_length, preserve_sentences)
    
    return chunks


def _split_with_code_blocks(content: str, max_length: int) -> List[str]:
    """Split content while preserving code blocks."""
    chunks: List[str] = []
    current_chunk = ""
    
    # Split by code blocks
    parts = re.split(r"(```[\s\S]*?```)", content)
    
    for part in parts:
        # Check if this is a code block
        is_code_block = part.startswith("```") and part.endswith("```")
        
        if is_code_block:
            # If code block is too large, we have to split it
            if len(part) > max_length:
                # Try to split by lines within the code block
                lines = part.split("\n")
                code_lang = lines[0] if lines else "```"
                
                temp_chunk = code_lang + "\n"
                for line in lines[1:-1]:  # Skip first (```) and last (```)
                    if len(temp_chunk) + len(line) + 5 > max_length:  # +5 for \n```
                        temp_chunk += "```"
                        chunks.append(temp_chunk)
                        temp_chunk = code_lang + "\n"
                    temp_chunk += line + "\n"
                
                temp_chunk += "```"
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                chunks.append(temp_chunk)
            else:
                # Code block fits, try to add to current chunk
                if len(current_chunk) + len(part) > max_length:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = part
                else:
                    current_chunk += part
        else:
            # Regular text
            if len(current_chunk) + len(part) > max_length:
                # Need to split
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # Split the text part
                text_chunks = _split_simple(part, max_length, preserve_sentences=True)
                chunks.extend(text_chunks[:-1])
                current_chunk = text_chunks[-1] if text_chunks else ""
            else:
                current_chunk += part
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def _split_simple(content: str, max_length: int, preserve_sentences: bool) -> List[str]:
    """Simple text splitting with optional sentence preservation."""
    chunks: List[str] = []
    current_chunk = ""
    
    if preserve_sentences:
        # Split by sentences
        sentences = re.split(r"([.!?]+\s+)", content)
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + punctuation
            
            if len(current_chunk) + len(full_sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If single sentence is too long, split by words
                if len(full_sentence) > max_length:
                    word_chunks = _split_by_words(full_sentence, max_length)
                    chunks.extend(word_chunks[:-1])
                    current_chunk = word_chunks[-1] if word_chunks else ""
                else:
                    current_chunk = full_sentence
            else:
                current_chunk += full_sentence
    else:
        # Split by words
        chunks = _split_by_words(content, max_length)
        return chunks
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def _split_by_words(content: str, max_length: int) -> List[str]:
    """Split content by words."""
    chunks: List[str] = []
    current_chunk = ""
    
    words = content.split()
    
    for word in words:
        if len(current_chunk) + len(word) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # If single word is too long, split it
            if len(word) > max_length:
                for i in range(0, len(word), max_length):
                    chunks.append(word[i:i + max_length])
                current_chunk = ""
            else:
                current_chunk = word
        else:
            current_chunk += (" " if current_chunk else "") + word
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def estimate_chunks(content: str, max_length: int = 2000) -> int:
    """
    Estimate the number of chunks a message will be split into.
    
    Args:
        content: The message content
        max_length: Maximum length per chunk
    
    Returns:
        Estimated number of chunks
    """
    if len(content) <= max_length:
        return 1
    
    # Simple estimation
    return (len(content) + max_length - 1) // max_length
