import os
import sys

from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()

from Core.orchestrator import MemoryOrchestrator

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

DEFAULT_USER = "default_user"


def _print_route(result) -> None:
    if HAS_RICH:
        console.print(
            f"➔ [bold]Category:[/bold] [bold yellow]{result.route_type}[/bold yellow] "
            f"(via [cyan]{result.source}[/cyan])"
        )
        console.print(f"➔ [dim]Reason:[/dim] {result.reason}")
    else:
        print(f"➔ Category: {result.route_type} (via {result.source})")
        print(f"➔ Reason: {result.reason}")


def _print_result(result) -> None:
    if result.action == "event_saved":
        ev = result.data.get("event", {})
        if HAS_RICH:
            table = Table(title="[bold green]✓ Event Logged to Memory[/bold green]", show_header=True)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="magenta")
            for key in (
                "event_type",
                "study_hours",
                "mood",
                "bible_read",
                "prayer_done",
                "sleep_time",
                "wake_time",
                "notes",
            ):
                if ev.get(key) is not None:
                    table.add_row(key, str(ev[key]))
            console.print(table)
        else:
            print(f"✓ Event logged: {ev}")

    elif result.action == "profile_saved":
        prof = result.data.get("profile", {})
        if HAS_RICH:
            table = Table(title="[bold green]✓ Profile Fact Saved[/bold green]", show_header=True)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="magenta")
            for key in ("topic", "trait_type", "statement", "polarity", "confidence"):
                if prof.get(key) is not None:
                    table.add_row(key, str(prof[key]))
            console.print(table)
        else:
            print(f"✓ Profile saved: {prof}")

    elif result.action == "ignored":
        if HAS_RICH:
            console.print("[dim]⚡ Low-value message ignored.[/dim]")
        else:
            print("⚡ Message ignored.")

    elif result.action == "chat_reply":
        if HAS_RICH:
            console.print(
                Panel(
                    result.message,
                    title="[bold green]Assistant[/bold green]",
                    border_style="green",
                )
            )
        else:
            print(f"\nAssistant: {result.message}\n")


def main():
    if HAS_RICH:
        console.print(
            Panel(
                "[bold green]🧠 Interactive Memory Console[/bold green]\n\n"
                "• Type any message — routed to event / profile / chat / ignore\n"
                "• [bold yellow]/query <question>[/bold yellow] — memory-grounded coaching answer\n"
                "• [bold red]exit[/bold red] — quit",
            )
        )
    else:
        print("Interactive Memory Console — type messages, /query <q>, or exit")

    try:
        orchestrator = MemoryOrchestrator()
    except ValueError as e:
        msg = f"Initialization error: {e}\nSet GEMINI_API_KEY in .env (see .env.example)."
        if HAS_RICH:
            console.print(f"[bold red]{msg}[/bold red]")
        else:
            print(msg)
        return

    while True:
        try:
            if HAS_RICH:
                user_input = console.input("\n[bold green]Prompt[/bold green] ➔ ").strip()
            else:
                user_input = input("\nPrompt > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if user_input.startswith("/query "):
            question = user_input[7:].strip()
            if not question:
                continue
            try:
                if HAS_RICH:
                    console.print(f'\n[bold yellow]🔍 Query:[/bold yellow] "{question}"')
                answer = orchestrator.query_memory(DEFAULT_USER, question)
                if HAS_RICH:
                    console.print(
                        Panel(answer, title="[bold green]Memory Response[/bold green]", border_style="green")
                    )
                else:
                    print(answer)
            except Exception as e:
                print(f"Error: {e}")
            continue

        if HAS_RICH:
            console.print("\n[bold cyan]1. Routing...[/bold cyan]")
        else:
            print("\n1. Routing...")

        try:
            result = orchestrator.process_message(DEFAULT_USER, user_input)
            _print_route(result)
            if result.action != "chat_reply" and HAS_RICH:
                console.print(f"\n[bold cyan]2. Result[/bold cyan]")
            elif result.action != "chat_reply":
                print("2. Result")
            _print_result(result)
        except Exception as e:
            if HAS_RICH:
                console.print(f"[bold red]Error:[/bold red] {e}")
            else:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
