import asyncio
import time
import os
import datetime
from bubble_sort_perception import extract_perception
from bubble_sort_memory import MemoryManager, MemoryItem
from bubble_sort_decision import generate_plan
from bubble_sort_action import execute_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def log(stage: str, msg: str):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")

def get_user_preferences():
    """Gather user preferences before starting the sorting process"""
    console.print(Panel.fit("Welcome to the Cognitive Bubble Sort Agent!", 
                          title="👋 Hello!", 
                          border_style="cyan"))
    
    preferences = {}
    
    # Get user name
    preferences['name'] = Prompt.ask("\n[cyan]What's your name?[/cyan]")
    
    # Get visualization preference
    preferences['visualization'] = Prompt.ask(
        "\n[cyan]How would you like to visualize the sorting process?[/cyan]",
        choices=["detailed", "simple", "minimal"],
        default="detailed"
    )
    
    # Get speed preference
    preferences['speed'] = Prompt.ask(
        "\n[cyan]How fast should the sorting visualization be?[/cyan]",
        choices=["fast", "medium", "slow"],
        default="medium"
    )
    
    # Get color scheme preference
    preferences['color_scheme'] = Prompt.ask(
        "\n[cyan]Which color scheme do you prefer?[/cyan]",
        choices=["colorful", "monochrome", "pastel"],
        default="colorful"
    )
    
    # Get explanation detail level
    preferences['explanation_level'] = Prompt.ask(
        "\n[cyan]How detailed should the explanations be?[/cyan]",
        choices=["basic", "intermediate", "advanced"],
        default="intermediate"
    )
    
    # Get learning focus
    preferences['learning_focus'] = Prompt.ask(
        "\n[cyan]What aspect of bubble sort interests you most?[/cyan]",
        choices=["algorithm steps", "performance analysis", "visualization", "all"],
        default="all"
    )

    console.print("\n[green]Thank you for sharing your preferences![/green]")
    console.print(Panel(
        "\n".join([f"[cyan]{k}:[/cyan] {v}" for k, v in preferences.items()]),
        title="Your Preferences",
        border_style="green"
    ))
    
    return input("\nPress Enter to start the sorting process..."), preferences

max_steps = 10  # Increased for bubble sort as it might need more steps

async def main(array_to_sort: list, user_preferences: dict):
    try:
        console.print(Panel(
            f"Starting Bubble Sort for {user_preferences['name']}'s array",
            border_style="cyan"
        ))
        
        server_params = StdioServerParameters(
            command="python",
            args=["bubble_sort_tools.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                console.print("[green]Session initialized[/green]")

                tools = await session.list_tools()
                tool_descriptions = "\n".join(
                    f"- {tool.name}: {getattr(tool, 'description', 'No description')}" 
                    for tool in tools.tools
                )

                log("agent", f"{len(tools.tools)} tools loaded")

                memory = MemoryManager()
                session_id = f"session-{int(time.time())}"
                initial_input = f"Sort this array using bubble sort: {array_to_sort}"
                current_input = initial_input
                step = 0

                # Store user preferences in memory
                memory.add(MemoryItem(
                    text=f"User preferences: {user_preferences}",
                    type="general",
                    array_state=array_to_sort,
                    tool_name="preferences",
                    user_query="initial_preferences",
                    tags=["preferences"],
                    session_id=session_id
                ))

                while step < max_steps:
                    # Adjust output based on user preferences
                    if user_preferences['visualization'] == 'minimal':
                        log("loop", f"Step {step + 1}")
                    else:
                        log("loop", f"Step {step + 1} started")

                    # Perception with user context
                    perception = extract_perception(current_input)
                    if user_preferences['visualization'] != 'minimal':
                        log("perception", f"Intent: {perception.intent}, Array state: {perception.current_array}")

                    # Memory with context
                    retrieved = memory.retrieve(query=current_input, top_k=3, session_filter=session_id)
                    if user_preferences['visualization'] == 'detailed':
                        log("memory", f"Retrieved {len(retrieved)} relevant memories")

                    # Decision
                    plan = generate_plan(perception, retrieved, tool_descriptions)
                    if user_preferences['visualization'] != 'minimal':
                        log("plan", f"Plan generated: {plan}")

                    if plan.startswith("FINAL_ANSWER:"):
                        console.print(Panel(
                            f"✨ Sorting complete for {user_preferences['name']}!\n{plan}",
                            border_style="green"
                        ))
                        break

                    # Action with user preferences
                    try:
                        result = await execute_tool(session, tools.tools, plan)
                        
                        # Adjust output based on visualization preference
                        if user_preferences['visualization'] == 'detailed':
                            log("tool", f"{result.tool_name} returned: {result.result}")
                        elif user_preferences['visualization'] == 'simple':
                            log("tool", f"Step completed: {result.tool_name}")

                        # Extract array state from result if possible
                        try:
                            array_state = eval(result.result) if isinstance(result.result, str) and result.result.startswith('[') else None
                        except:
                            array_state = None

                        # Store in memory
                        memory.add(MemoryItem(
                            text=f"Tool call: {result.tool_name} with {result.arguments}, got: {result.result}",
                            type="tool_output",
                            array_state=array_state,
                            tool_name=result.tool_name,
                            user_query=current_input,
                            tags=[result.tool_name],
                            session_id=session_id
                        ))

                        # Add delay based on speed preference
                        if user_preferences['speed'] == 'slow':
                            await asyncio.sleep(1)
                        elif user_preferences['speed'] == 'medium':
                            await asyncio.sleep(0.5)

                        current_input = f"Previous array state: {perception.current_array}\nTool output: {result.result}\nContinue sorting."

                    except Exception as e:
                        log("error", f"Tool execution failed: {e}")
                        break

                    step += 1

    except Exception as e:
        console.print(f"[red]Agent Error: {str(e)}[/red]")

    log("agent", f"Bubble Sort completed for {user_preferences['name']}.")

if __name__ == "__main__":
    # Get initial array from user
    console.print("\n[cyan]Please enter the numbers to sort (space-separated):[/cyan]")
    console.print("[cyan]Example: 64 34 25 12 22 11 90[/cyan]")
    
    while True:
        try:
            user_input = input("Numbers: ")
            array = [int(x) for x in user_input.split()]
            if len(array) < 2:
                console.print("[red]Please enter at least 2 numbers[/red]")
                continue
            break
        except ValueError:
            console.print("[red]Please enter valid numbers separated by spaces[/red]")
    
    # Get user preferences
    _, preferences = get_user_preferences()
    
    # Start the sorting process
    console.print(f"\n🔄 Starting bubble sort for array: {array}")
    asyncio.run(main(array, preferences))