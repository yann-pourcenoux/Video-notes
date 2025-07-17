"""Service for interacting with the Ollama API."""

import ollama


def get_available_models() -> list[str]:
    """Fetch the list of available models from the Ollama API.

    Returns:
        A list of model names available locally.
    """
    try:
        response = ollama.Client().list()
        models = response.models
        return [model.model for model in models]
    except Exception:
        return []
