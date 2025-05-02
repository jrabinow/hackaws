

import os
import sys
import traceback

import click
from dotenv import load_dotenv

from duck.chat_handler import ChatHandler


load_dotenv()


def main():
    """Main entry point for the application."""
    try:

        # Create a chat handler
        chat_handler = ChatHandler()

        # Always use chat interface
        click.echo("Debug Agent - Chat Interface")
        click.echo("Type 'help' for assistance or 'exit' to quit.")
        click.echo("---")

        # Start interactive chat session
        run_chat_interface(chat_handler)

    except Exception as e:
        traceback_str = traceback.format_exc()
        click.echo(f"Traceback:\n{traceback_str}", err=True)
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


def run_chat_interface(chat_handler):
    """Run the interactive chat interface."""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.styles import Style

    # Create a prompt session with history
    session = PromptSession(history=InMemoryHistory())

    # Define prompt style
    style = Style.from_dict({
        'prompt': '#00aa00 bold',
    })

    while True:
        try:
            # Get user input with styled prompt
            user_input = session.prompt("You > ", style=style)

            # Check for exit command
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                click.echo("Ending session. Goodbye!")
                break

            # Process the query
            response = chat_handler.process_query(user_input)

            # Display the response
            click.echo(f"\nAgent > {response}\n")

        except KeyboardInterrupt:
            # Handle Ctrl+C
            click.echo("\nEnding session. Goodbye!")
            break
        except Exception as e:
            click.echo(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
