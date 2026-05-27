import os
import sys
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Ensure root directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()

from Memory.Rulelayer.rulelayer import Rulelayer
from Memory.Rulelayer.airouter import AIRouter
from Memory.Rulelayer.hybridrouter import HybridRouter
from Event.event import Event
from Event.event_manager import EventManager
from google import genai

# Setup rich styling if available
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


# Pydantic schemas for AI Extraction
class ExtractedEventData(BaseModel):
    event_type: str = Field(description="Generic category of the event, e.g. study, sleep, work, health, spirituality")
    study_hours: Optional[float] = Field(None, description="Number of hours spent studying, if mentioned")
    mood: Optional[str] = Field(None, description="User mood or physical feeling, if mentioned")
    bible_read: Optional[bool] = Field(None, description="Whether the user read the bible, if mentioned")
    prayer_done: Optional[bool] = Field(None, description="Whether the user prayed, if mentioned")
    sleep_time: Optional[str] = Field(None, description="Time user went to bed (e.g. '11:00 PM'), if mentioned")
    wake_time: Optional[str] = Field(None, description="Time user woke up (e.g. '6:30 AM'), if mentioned")
    notes: Optional[str] = Field(None, description="Any extra context or descriptive summary of the event")


class ExtractedProfileData(BaseModel):
    preference_or_habit: str = Field(description="The habit, standard, preference, or struggle stated by the user (e.g. 'Prefers working late', 'Struggles to focus in noisy rooms')")
    topic: Literal["lifestyle", "productivity", "diet", "spirituality", "general"] = Field(description="The main topic category")


# In-memory database stores
event_manager = EventManager()
profile_store = []  # List of dicts representing user profile facts


def get_client():
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDrNgEGwWUUv5NoONCols-gCV2_x2i27hM")
    return genai.Client(api_key=api_key)


def extract_event_with_ai(client: genai.Client, message: str) -> ExtractedEventData:
    """Uses Gemini to extract structured event variables from the raw prompt."""
    prompt = f"Analyze this user event message and extract all mentioned variables: \"{message}\""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ExtractedEventData,
        }
    )
    import json
    return ExtractedEventData(**json.loads(response.text))


def extract_profile_with_ai(client: genai.Client, message: str) -> ExtractedProfileData:
    """Uses Gemini to extract structural habits or preferences from the raw prompt."""
    prompt = f"Extract the specific personal preference, habit, or struggle from this statement: \"{message}\""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ExtractedProfileData,
        }
    )
    import json
    return ExtractedProfileData(**json.loads(response.text))


def query_memory_with_prompt(client: genai.Client, user_query: str) -> str:
    """RAG-style query: Retrieves all stored memories, injects them into a Gemini prompt, and returns a natural answer."""
    # 1. Retrieve raw data
    events = event_manager.get_events("default_user")
    
    # 2. Format memory context
    memory_context = "=== USER STORED MEMORIES ===\n"
    if not events and not profile_store:
        memory_context += "(No memories stored yet. Tell me some events or habits first!)\n"
    
    if events:
        memory_context += "\n--- Events Log ---\n"
        for i, ev in enumerate(events, 1):
            details = []
            if ev.study_hours: details.append(f"Studied: {ev.study_hours} hrs")
            if ev.mood: details.append(f"Mood: {ev.mood}")
            if ev.bible_read is not None: details.append(f"Read Bible: {ev.bible_read}")
            if ev.prayer_done is not None: details.append(f"Prayed: {ev.prayer_done}")
            if ev.sleep_time: details.append(f"Slept: {ev.sleep_time}")
            if ev.wake_time: details.append(f"Woke up: {ev.wake_time}")
            if ev.notes: details.append(f"Notes: {ev.notes}")
            
            memory_context += f"Event #{i} [{ev.event_type}] ({ev.timestamp.strftime('%Y-%m-%d %H:%M')}): {', '.join(details)}\n"
            
    if profile_store:
        memory_context += "\n--- Profile Habits & Characteristics ---\n"
        for i, prof in enumerate(profile_store, 1):
            memory_context += f"Fact #{i} [{prof['topic']}]: {prof['preference_or_habit']}\n"
            
    # 3. Formulate LLM prompt
    system_prompt = f"""You are a helpful Personal AI Life Assistant. Below is the structured memory context of the user. 
Answer the user's question accurately using ONLY this context. If the answer is not in the context, be honest and say so.

{memory_context}

User Question: "{user_query}"
Assistant response:"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=system_prompt
    )
    return response.text


def main():
    if HAS_RICH:
        console.print(Panel("[bold green]🧠 Welcome to the Interactive Memory Console! 🧠[/bold green]\n\n"
                            "Here, you can test how prompts classify, extract, and query your assistant's memory layer.\n"
                            "• [bold cyan]Type any prompt[/bold cyan] to see the Hybrid Router class and AI data extraction.\n"
                            "• [bold yellow]Type '/query <your question>'[/bold yellow] to query stored memories with AI.\n"
                            "• [bold red]Type 'exit'[/bold red] to quit."))
    else:
        print("="*60)
        print("🧠 Welcome to the Interactive Memory Console! 🧠")
        print("• Type any prompt to see Hybrid Router classification and AI extraction.")
        print("• Type '/query <your question>' to query stored memories with natural prompts.")
        print("• Type 'exit' to quit.")
        print("="*60)

    try:
        client = get_client()
        rule_layer = Rulelayer()
        ai_router = AIRouter(client=client, model="gemini-2.5-flash")
        hybrid_router = HybridRouter(rule_layer=rule_layer, ai_router=ai_router)
    except Exception as e:
        if HAS_RICH:
            console.print(f"[bold red]Initialization Error:[/bold red] {e}")
        else:
            print(f"Initialization Error: {e}")
        return

    while True:
        try:
            if HAS_RICH:
                user_input = console.input("\n[bold green]Prompt[/bold green] ➔ ").strip()
            else:
                user_input = input("\nPrompt > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        # Check for Memory Query Prompt
        if user_input.startswith('/query '):
            query = user_input[7:].strip()
            if HAS_RICH:
                console.print(f"\n[bold yellow]🔍 Querying stored memories for:[/bold yellow] \"{query}\"")
            else:
                print(f"\n🔍 Querying stored memories for: \"{query}\"")
                
            try:
                answer = query_memory_with_prompt(client, query)
                if HAS_RICH:
                    console.print(Panel(answer, title="[bold green]AI Assistant Memory Response[/bold green]", border_style="green"))
                else:
                    print("-" * 60)
                    print(answer)
                    print("-" * 60)
            except Exception as e:
                print(f"Error querying memory: {e}")
            continue

        # Otherwise, process the prompt through classification + extraction
        if HAS_RICH:
            console.print(f"\n[bold cyan]1. Routing Prompt...[/bold cyan]")
        else:
            print("\n1. Routing Prompt...")
            
        try:
            route = hybrid_router.classify(user_input)
            category = route["type"]
            source = route["source"]
            reason = route["reason"]
            
            if HAS_RICH:
                console.print(f"➔ [bold]Category:[/bold] [bold yellow]{category}[/bold yellow] (via [cyan]{source}[/cyan])")
                console.print(f"➔ [dim]Reason:[/dim] {reason}")
            else:
                print(f"➔ Category: {category} (via {source})")
                print(f"➔ Reason: {reason}")

            # AI Structured Memory Extraction & DB Save
            if category == "event":
                if HAS_RICH:
                    console.print(f"\n[bold cyan]2. Extracting Event details with AI...[/bold cyan]")
                else:
                    print("\n2. Extracting Event details with AI...")
                
                extracted = extract_event_with_ai(client, user_input)
                
                # Convert to Event schema and save in EventManager
                db_event = Event(
                    user_id="default_user",
                    event_type=extracted.event_type,
                    timestamp=datetime.utcnow(),
                    study_hours=extracted.study_hours,
                    mood=extracted.mood,
                    bible_read=extracted.bible_read,
                    prayer_done=extracted.prayer_done,
                    sleep_time=extracted.sleep_time,
                    wake_time=extracted.wake_time,
                    notes=extracted.notes
                )
                event_manager.add_event(db_event)
                
                if HAS_RICH:
                    # Show extracted variables as table
                    table = Table(title="[bold green]✓ Event Logged to Memory[/bold green]", show_header=True)
                    table.add_column("Field", style="cyan")
                    table.add_column("Extracted Value", style="magenta")
                    table.add_row("event_type", db_event.event_type)
                    if db_event.study_hours: table.add_row("study_hours", f"{db_event.study_hours} hrs")
                    if db_event.mood: table.add_row("mood", db_event.mood)
                    if db_event.bible_read is not None: table.add_row("bible_read", str(db_event.bible_read))
                    if db_event.prayer_done is not None: table.add_row("prayer_done", str(db_event.prayer_done))
                    if db_event.sleep_time: table.add_row("sleep_time", db_event.sleep_time)
                    if db_event.wake_time: table.add_row("wake_time", db_event.wake_time)
                    if db_event.notes: table.add_row("notes", db_event.notes)
                    console.print(table)
                else:
                    print(f"✓ Event logged: {db_event.dict(exclude_none=True)}")

            elif category == "profile":
                if HAS_RICH:
                    console.print(f"\n[bold cyan]2. Extracting Profile preference/habit with AI...[/bold cyan]")
                else:
                    print("\n2. Extracting Profile preference/habit with AI...")
                
                extracted = extract_profile_with_ai(client, user_input)
                profile_store.append(extracted.dict())
                
                if HAS_RICH:
                    table = Table(title="[bold green]✓ Preference Saved to User Profile[/bold green]", show_header=True)
                    table.add_column("Field", style="cyan")
                    table.add_column("Extracted Value", style="magenta")
                    table.add_row("topic", extracted.topic)
                    table.add_row("preference_or_habit", extracted.preference_or_habit)
                    console.print(table)
                else:
                    print(f"✓ Profile fact saved: {extracted.dict()}")

            elif category == "ignore":
                if HAS_RICH:
                    console.print("[dim]⚡ Low-value message ignored. Not saved to memory database.[/dim]")
                else:
                    print("⚡ Low-value message ignored. Not saved to memory database.")

            elif category == "chat":
                if HAS_RICH:
                    console.print("[yellow]💬 Chat conversation message. Sent to standard chatbot responder.[/yellow]")
                else:
                    print("💬 Chat conversation message. Sent to standard chatbot responder.")

        except Exception as e:
            if HAS_RICH:
                console.print(f"[bold red]Error processing prompt:[/bold red] {e}")
            else:
                print(f"Error processing prompt: {e}")


if __name__ == "__main__":
    main()
