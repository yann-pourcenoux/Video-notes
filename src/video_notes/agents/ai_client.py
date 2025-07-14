"""AI client for agent text generation using Ollama."""

import click
from ollama import ChatResponse, chat


def generate_with_messages(messages: list[dict[str, str]], model: str = "gemma3:12b") -> str | None:
    """Generate text using Ollama chat API with messages.

    This is the primary function used by agents for AI text generation.

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys.
        model: Ollama model name to use.

    Returns:
        Generated text or None if failed.
    """
    try:
        response: ChatResponse = chat(
            model=model,
            messages=messages,
            options={
                "temperature": 0,
            },
        )

        # Access the message content from the response
        if response.message and response.message.content:
            return str(response.message.content).strip()
        return None

    except Exception as e:
        click.echo(f"❌ Error calling Ollama: {e}", err=True)
        return None
