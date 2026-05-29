import os
import sys
from datetime import datetime
from typing import Optional
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
from Profile.models.user_profile import ProfileFact
from Profile.memory.profile_manager import ProfileManager
from Profile.profile_extractor import extract_profile_with_ai
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


# Persistent memory stores
event_manager = EventManager()
profile_manager = ProfileManager()


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


def query_memory_with_prompt(client: genai.Client, user_query: str) -> str:
    """RAG-style query: Retrieves behavioral analytics and recent memories, injects them into a Gemini prompt, and returns a natural coaching answer."""
    # 1. Retrieve raw data and computed behavioral analytics
    events = event_manager.get_events("default_user")
    analytics = event_manager.get_behavioral_analytics("default_user", days=30)
    profile_summary = profile_manager.get_profile_summary("default_user")
    profile_facts = profile_manager.get_facts("default_user")
    
    # 2. Format memory context
    memory_context = "=== USER STORED MEMORIES & ANALYTICS ===\n"
    memory_context += analytics.get("summary_markdown", "") + "\n\n"
    memory_context += profile_summary.get("summary_markdown", "") + "\n"
    
    if not events and not profile_facts:
        memory_context += "(No specific events or profile facts stored yet. Tell me some first!)\n"
    
    if events:
        memory_context += "\n--- Recent Detailed Events Log (Past 5 logs) ---\n"
        recent_events = events[-5:]
        for i, ev in enumerate(recent_events, 1):
            details = []
            if ev.study_hours: details.append(f"Studied: {ev.study_hours} hrs")
            if ev.mood: details.append(f"Mood: {ev.mood}")
            if ev.bible_read is not None: details.append(f"Read Bible: {ev.bible_read}")
            if ev.prayer_done is not None: details.append(f"Prayed: {ev.prayer_done}")
            
            duration = ev.calculate_sleep_duration()
            if duration:
                details.append(f"Sleep: {ev.sleep_time} to {ev.wake_time} ({duration} hrs)")
            else:
                if ev.sleep_time: details.append(f"Slept: {ev.sleep_time}")
                if ev.wake_time: details.append(f"Woke up: {ev.wake_time}")
                
            if ev.notes: details.append(f"Notes: {ev.notes}")
            if ev.tags: details.append(f"Tags: {ev.tags}")
            
            ts_str = ev.timestamp.strftime('%Y-%m-%d %H:%M') if hasattr(ev.timestamp, 'strftime') else str(ev.timestamp)
            memory_context += f"Event #{i} [{ev.event_type}] ({ts_str}): {', '.join(details)}\n"
            
    if profile_facts:
        memory_context += "\n--- Recent Profile Facts (full list) ---\n"
        for i, prof in enumerate(profile_facts, 1):
            memory_context += (
                f"Fact #{i} [{prof.topic}/{prof.trait_type}]: {prof.statement}\n"
            )
            
    # 3. Formulate LLM prompt
    system_prompt = f"""You are a helpful Personal AI Life Assistant & Behavior Coach. Below is the structured memory context and calculated behavioral analytics of the user. 
Answer the user's question accurately using ONLY this context. When asked about habits, sleep patterns, mood trends, or spiritual consistency, leverage the statistics in the Behavioral Insights block to provide premium, personalized coaching, patterns, and advice.

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
                    notes=extracted.notes,
                    raw_message=user_input,
                    metadata=extracted.json() if hasattr(extracted, 'json') else str(extracted)
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
                db_fact = ProfileFact.from_extraction(
                    user_id="default_user",
                    extracted=extracted,
                    raw_message=user_input,
                )
                profile_manager.add_fact(db_fact)
                
                if HAS_RICH:
                    table = Table(title="[bold green]✓ Profile Fact Saved to Memory[/bold green]", show_header=True)
                    table.add_column("Field", style="cyan")
                    table.add_column("Extracted Value", style="magenta")
                    table.add_row("topic", extracted.topic)
                    table.add_row("trait_type", extracted.trait_type)
                    table.add_row("statement", extracted.statement)
                    if extracted.polarity:
                        table.add_row("polarity", extracted.polarity)
                    table.add_row("confidence", str(extracted.confidence))
                    console.print(table)
                else:
                    print(f"✓ Profile fact saved: {db_fact.model_dump(exclude_none=True)}")

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
