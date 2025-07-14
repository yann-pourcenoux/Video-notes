#!/usr/bin/env python3
"""Command-line interface for Video Notes."""

import click
import ollama
from ollama import ChatResponse, chat

from video_notes.models import ProcessingConfig
from video_notes.services import process_video


@click.group()
def cli() -> None:
    """Video Notes: Download and summarize YouTube video transcripts using AI."""
    pass


@cli.command()
@click.argument("youtube_url")
@click.option(
    "--model",
    "-m",
    default="gemma3:12b",
    type=str,
    help="Model to use for summarization (Ollama model name, defaults to gemma3:12b)",
)
@click.option(
    "--output-folder",
    "-o",
    default=".",
    type=str,
    help="Directory where output files should be saved (defaults to current directory)",
)
@click.option(
    "--save-transcript",
    is_flag=True,
    default=False,
    help="Save the transcript file in addition to the summary (defaults to False)",
)
def process(youtube_url: str, model: str, output_folder: str, save_transcript: bool) -> None:
    """Download transcript and generate summary in one command.

    youtube_url (str): The YouTube video URL to process.
    model (str): The Ollama model to use for summarization.
    output_folder (str): Directory where output files should be saved.
    save_transcript (bool): Whether to save the transcript file.
    """
    config = ProcessingConfig(
        youtube_url=youtube_url,
        model=model,
        output_folder=output_folder,
        save_transcript=save_transcript,
    )

    click.echo(f"🎯 URL: {youtube_url}")
    click.echo("🤖 AI Provider: ollama")
    click.echo(f"🧠 Model: {model}")
    click.echo("🌡️ Temperature: 0.0 (fixed)")
    click.echo(f"📁 Output folder: {output_folder}")
    click.echo(f"📄 Save transcript: {'Yes' if save_transcript else 'No'}")

    result = process_video(config)

    if not result.success:
        raise click.ClickException(result.error_message or "Failed to process transcript")

    click.echo("🎉 Processing complete!")
    click.echo(f"📄 Summary written to: {result.summary_file}")
    if save_transcript and result.transcript_file:
        click.echo(f"📝 Transcript written to: {result.transcript_file}")


def _is_ollama_available(model: str = "gemma3:12b") -> bool:
    """Check if Ollama service is available.

    Args:
        model: Model to test with.

    Returns:
        bool: True if Ollama is running and accessible.
    """
    try:
        # Try a simple chat to check if Ollama is running
        test_response: ChatResponse = chat(
            model=model,
            messages=[{"role": "user", "content": "test"}],
            options={"temperature": 0.0},
        )
        return test_response.message is not None
    except Exception:
        return False


@cli.command()
def info() -> None:
    """Show information about available Ollama models."""
    click.echo("📋 Video Notes - Ollama Information\n")

    # First check if Ollama service is running
    try:
        client = ollama.Client()
        models_response = client.list()
        available_models = [model["model"] for model in models_response.models]
    except Exception:
        click.echo("❌ Ollama service is not running!")
        click.echo("\n💡 To get started, follow the installation guide in the README")
        return

    click.echo("🤖 Ollama Service:")
    click.echo("   ✅ Ollama (Local)")

    if not available_models:
        click.echo("   ⚠️  No models installed")
        click.echo("\n💡 Download a model to get started:")
        click.echo("   • For quick testing: ollama pull gemma3:4b")
        click.echo("   • For better quality: ollama pull gemma3:12b")
        click.echo("   • For best quality: ollama pull gemma3:27b")
        return

    # Test with the first available model
    test_model = available_models[0]
    default_model = "gemma3:12b"

    # Check if default model is available, otherwise use first available
    working_model = default_model if default_model in available_models else test_model

    if _is_ollama_available(working_model):
        click.echo(f"   ✅ Tested with model: {working_model}")
    else:
        click.echo(f"   ⚠️  Model {working_model} may have issues")

    # Show available models
    models_to_show = available_models[:5]
    click.echo(f"   Default model: {default_model}")
    click.echo(f"   Available models: {', '.join(models_to_show)}")
    if len(available_models) > 5:
        click.echo(f"   ... and {len(available_models) - 5} more")

    click.echo("\n💡 Usage examples:")
    click.echo("   video-notes process <url>")
    click.echo(f"   video-notes process <url> --model {available_models[0]}")
    click.echo("   video-notes process <url> --output-folder ./summaries")
    click.echo("   video-notes process <url> --save-transcript")
    click.echo("   video-notes process <url> -m gemma3:4b -o ~/Documents --save-transcript")


if __name__ == "__main__":
    cli()
