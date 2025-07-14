# Video Notes Services - Ollama Documentation

This directory contains the core AI services for video transcript processing and summarization using Ollama.

## Overview

The Video Notes application uses Ollama for local AI-powered text generation with a modern agent-based architecture:

- **AIService**: Direct Ollama integration for text generation using modern chat API
- **PromptBuilder**: Utility for building structured prompts for agents
- **TranscriptProcessor**: Orchestrates the agent-based workflow

## Modern Agent-Based Architecture

The `AIService` class provides a clean interface to Ollama models using the modern `chat` API with messages format, designed specifically to support the agent-based architecture.

### Key Features

- Modern Ollama chat API integration with messages format
- Flexible text generation for specialized agents
- Model management and availability checking
- Clean error handling and recovery
- Minimal, focused interface

## Modern Chat API Integration

### Core Method: `generate_with_messages`

All agents use the primary generation method:

```python
from video_notes.services.ai_service import AIService

ai_service = AIService(model='gemma3:12b')

# Agents use this method for all AI generation
messages = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': 'Summarize this text...'},
]
response = ai_service.generate_with_messages(messages, temperature=0.0)
```

### Agent Integration

Agents build their own prompts and use AIService for execution:

```python
# Theme Routing Agent
messages = PromptBuilder.build_theme_analysis_messages(text, video_metadata)
theme_response = ai_service.generate_with_messages(messages, temperature=0.1)

# Chunk Summarizer Agent
messages = PromptBuilder.build_summary_messages(chunk, focus_areas)
summary_response = ai_service.generate_with_messages(messages, temperature=0.0)

# Chunk Combiner Agent
messages = PromptBuilder.build_combination_messages(summaries, theme)
combined_response = ai_service.generate_with_messages(messages, temperature=0.0)
```

## AIService API Reference

### Core Methods

| Method | Purpose | Parameters |
|--------|---------|------------|
| `generate_with_messages(messages, temperature)` | Primary AI generation | messages list, temperature |
| `generate(prompt, temperature)` | Simple prompt generation | prompt string, temperature |

### Utility Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `is_available()` | Check Ollama status | bool |
| `list_models()` | Get available models | list[str] |
| `get_default_model()` | Get current model | str |
| `get_active_provider()` | Get provider name | str |

## Configuration

Initialize with your preferred model:

```python
# Use default model
ai_service = AIService()

# Use specific model
ai_service = AIService(model="llama3:8b")

# With timeout
ai_service = AIService(model="gemma3:12b", timeout=600)
```

## Error Handling

The AIService handles errors gracefully:

```python
response = ai_service.generate_with_messages(messages)
if response is None:
    # Handle generation failure
    print("AI generation failed")
else:
    # Process successful response
    print(f"Generated: {response}")
```

## Integration with PromptBuilder

The `PromptBuilder` utility creates structured messages for the AIService:

```python
from video_notes.services.prompt_builder import PromptBuilder

# Build messages for different agent types
summary_messages = PromptBuilder.build_summary_messages(text, focus_areas)
theme_messages = PromptBuilder.build_theme_analysis_messages(text, metadata)
combination_messages = PromptBuilder.build_combination_messages(summaries, theme)

# Use with AIService
response = ai_service.generate_with_messages(summary_messages)
```

This clean separation allows agents to focus on their specific logic while AIService handles the LLM communication layer.
