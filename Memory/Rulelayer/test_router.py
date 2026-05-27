import os
import sys
from dotenv import load_dotenv

# Ensure the project root is in the python path so imports work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()

from Memory.Rulelayer.rulelayer import Rulelayer
from Memory.Rulelayer.airouter import AIRouter
from Memory.Rulelayer.hybridrouter import HybridRouter
from google import genai

# Setup console styling
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def print_header(title):
    if HAS_RICH:
        console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]"))
    else:
        print("\n" + "=" * 60)
        print(f" {title.upper()} ")
        print("=" * 60)


def run_tests():
    # 1. Initialize API Client
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDrNgEGwWUUv5NoONCols-gCV2_x2i27hM")
    
    print_header("Initializing Hybrid Memory Router System")
    
    if api_key == "AIzaSyDrNgEGwWUUv5NoONCols-gCV2_x2i27hM":
        if HAS_RICH:
            console.print("[yellow][!] Warning: Using project fallback Gemini API Key.[/yellow]")
        else:
            print("Warning: Using project fallback Gemini API Key.")
    else:
        if HAS_RICH:
            console.print("[green][OK] Loaded custom GEMINI_API_KEY from environment.[/green]")
        else:
            print("Loaded custom GEMINI_API_KEY from environment.")

    # 2. Instantiate Routers
    client = genai.Client(api_key=api_key)
    
    rule_layer = Rulelayer()
    ai_router = AIRouter(client=client, model="gemini-2.5-flash")
    hybrid_router = HybridRouter(rule_layer=rule_layer, ai_router=ai_router)

    # 3. Define Test Suite
    test_cases = [
        # Explicit/Exact matching rules (Rule Layer)
        {
            "message": "Today I studied chemistry and learned about atomic bonds.",
            "expected_source": "rule",
            "expected_type": "event",
            "description": "Rule Layer: Explicit event match ('today i', 'i studied')"
        },
        {
            "message": "I prefer to wake up at 5:00 AM every single day.",
            "expected_source": "rule",
            "expected_type": "profile",
            "description": "Rule Layer: Explicit profile match ('i prefer')"
        },
        {
            "message": "haha nice that was a cool explanation!",
            "expected_source": "rule",
            "expected_type": "ignore",
            "description": "Rule Layer: Explicit ignore match ('haha', 'nice', 'cool')"
        },
        # Semantic, non-exact matching rules (AI Router Fallback)
        {
            "message": "I spent four long hours hitting the textbooks for my calculus final exam.",
            "expected_source": "ai",
            "expected_type": "event",
            "description": "AI Fallback: Semantic event match (no exact rule)"
        },
        {
            "message": "I struggle immensely with public speaking and get anxious easily.",
            "expected_source": "ai",
            "expected_type": "profile",
            "description": "AI Fallback: Semantic profile match (no exact rule)"
        },
        {
            "message": "Could you explain the difference between a database and a vector index?",
            "expected_source": "ai",
            "expected_type": "chat",
            "description": "AI Fallback: Generic chat conversation"
        },
        {
            "message": "OK",
            "expected_source": "rule",
            "expected_type": "ignore",
            "description": "Rule Layer: Case-insensitive ignore match ('ok')"
        }
    ]

    # 4. Run Tests & Collect Results
    results = []
    
    for case in test_cases:
        msg = case["message"]
        desc = case["description"]
        
        if HAS_RICH:
            console.print(f"\n[bold magenta]Testing Case:[/bold magenta] {desc}")
            console.print(f"[dim]Input Message:[/dim] \"{msg}\"")
        else:
            print(f"\nTesting Case: {desc}")
            print(f"Input Message: \"{msg}\"")
            
        # Run classification
        res = hybrid_router.classify(msg)
        results.append((case, res))
        
        if HAS_RICH:
            console.print(f"-> [bold green]Result:[/bold green] type=[bold]{res['type']}[/bold], source=[bold cyan]{res['source']}[/bold cyan], confidence={res['confidence']:.2f}")
            console.print(f"-> [dim]Reasoning:[/dim] {res['reason']}")
        else:
            print(f"-> Result: type={res['type']}, source={res['source']}, confidence={res['confidence']:.2f}")
            print(f"-> Reasoning: {res['reason']}")

    # 5. Print Summary Table
    print_header("Test Performance Summary Table")
    
    if HAS_RICH:
        table = Table(title="Memory Router Test Results", show_header=True, header_style="bold magenta")
        table.add_column("Message Context", style="dim", width=30)
        table.add_column("Expected (Type/Source)", justify="center")
        table.add_column("Actual (Type/Source)", justify="center")
        table.add_column("Confidence", justify="right")
        table.add_column("Outcome", justify="center")
        
        for case, res in results:
            expected = f"{case['expected_type']} ({case['expected_source']})"
            actual = f"{res['type']} ({res['source']})"
            
            # Check success
            success = (case['expected_type'] == res['type']) and (case['expected_source'] == res['source'])
            outcome = "[bold green]PASS[/bold green]" if success else "[bold red]FAIL[/bold red]"
            
            table.add_row(
                case['message'][:28] + "..." if len(case['message']) > 30 else case['message'],
                expected,
                actual,
                f"{res['confidence']:.2f}",
                outcome
            )
        console.print(table)
    else:
        print("\n" + "-" * 75)
        print(f"{'Message':<30} | {'Expected':<15} | {'Actual':<15} | {'Outcome'}")
        print("-" * 75)
        for case, res in results:
            expected = f"{case['expected_type']}({case['expected_source']})"
            actual = f"{res['type']}({res['source']})"
            success = (case['expected_type'] == res['type']) and (case['expected_source'] == res['source'])
            outcome = "PASS" if success else "FAIL"
            msg_trunc = case['message'][:27] + "..." if len(case['message']) > 30 else case['message']
            print(f"{msg_trunc:<30} | {expected:<15} | {actual:<15} | {outcome}")
        print("-" * 75)


if __name__ == "__main__":
    run_tests()
