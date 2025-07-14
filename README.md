# Video Notes

A modular Python package for downloading and summarizing YouTube video transcripts using AI agents and local LLM models via Ollama.

## Installation

```bash
# Clone and install with uv
git clone https://github.com/yourusername/video-notes.git
cd video-notes
uv sync
```

## Pre-commit Hooks Setup

To ensure code quality and consistency, install the pre-commit hooks:

```bash
# Install pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# Run hooks manually (optional)
uv run pre-commit run --all-files
```

The pre-commit hooks will automatically handle:

- Code formatting with Ruff
- Linting and quality checks
- Type checking with MyPy
- Security scanning
- Documentation validation

## CLI Usage

### Prerequisites

**Install Ollama:**

Follow the installation guide at [Ollama's official GitHub repository](https://github.com/ollama/ollama).

```bash
# After installing Ollama, pull the model
ollama pull gemma3:12b
```

### Commands

**Check available models:**

```bash
uv run video-notes info
```

**Process video (download + summarize):**

```bash
uv run video-notes process "https://www.youtube.com/watch?v=5sLYAQS9sWQ"
```

**Common options:**

```bash
# Use specific model
uv run video-notes process "URL" --model "llama3:8b"

# Verbose output
uv run video-notes process "URL" --verbose

# Custom output files
uv run video-notes process "URL" --transcript-file my_transcript.txt --summary-file my_summary.md
```

For detailed help on any command:

```bash
uv run video-notes --help
uv run video-notes COMMAND --help
```

## Architecture

Video Notes uses a modular agent-based architecture with specialized agents for different tasks:

- **Chunk Sizing Agent**: Analyzes text and determines optimal chunking strategy
- **Theme Routing Agent**: Detects content themes and determines focus areas
- **Chunk Summarizer Agent**: Summarizes individual text chunks with contextual awareness
- **Chunk Combiner Agent**: Combines multiple chunk summaries into cohesive content
- **Filename Generator Agent**: Creates meaningful, sanitized filenames based on content
- **Final Markdown Agent**: Generates well-formatted markdown with metadata and structure

This modular approach ensures scalable, maintainable, and testable code with clear separation of concerns.

## License

MIT License - see [LICENSE](LICENSE) file for details.
