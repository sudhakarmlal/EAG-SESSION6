from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import math
import re

console = Console()
mcp = FastMCP("BubbleSortVisualizer")

@mcp.tool()
def show_reasoning(steps: list) -> TextContent:
    """Show the step-by-step reasoning process for bubble sort"""
    console.print("[blue]FUNCTION CALL:[/blue] show_reasoning()")
    for i, step in enumerate(steps, 1):
        console.print(Panel(
            f"{step}",
            title=f"Step {i}",
            border_style="cyan"
        ))
    return TextContent(
        type="text",
        text="Reasoning shown"
    )

@mcp.tool()
def compare_elements(a: int, b: int) -> TextContent:
    """Compare two elements and determine if they need to be swapped"""
    console.print("[blue]FUNCTION CALL:[/blue] compare_elements()")
    console.print(f"[blue]Comparing:[/blue] {a} and {b}")
    
    should_swap = a > b
    console.print(f"[{'red' if should_swap else 'green'}]Result: {a} {'>' if should_swap else '<='} {b}[/{'red' if should_swap else 'green'}]")
    
    return TextContent(
        type="text",
        text=str(should_swap)
    )

@mcp.tool()
def perform_swap(array: list, i: int, j: int) -> TextContent:
    """Swap elements at positions i and j in the array"""
    console.print("[blue]FUNCTION CALL:[/blue] perform_swap()")
    try:
        # Create a visual representation of the swap
        before = array.copy()
        array[i], array[j] = array[j], array[i]
        
        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("State", style="cyan")
        table.add_column("Array", style="yellow")
        table.add_column("Swapped Elements", style="red")
        
        table.add_row(
            "Before",
            str(before),
            f"{before[i]} ↔ {before[j]}"
        )
        table.add_row(
            "After",
            str(array),
            f"Positions {i} and {j}"
        )
        
        console.print(table)
        
        return TextContent(
            type="text",
            text=str(array)
        )
    except Exception as e:
        console.print(f"[red]Error during swap: {str(e)}[/red]")
        return TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )

@mcp.tool()
def verify_sorted(array: list) -> TextContent:
    """Verify if the array is sorted in ascending order"""
    console.print("[blue]FUNCTION CALL:[/blue] verify_sorted()")
    
    is_sorted = all(array[i] <= array[i+1] for i in range(len(array)-1))
    
    if is_sorted:
        console.print(Panel(
            f"[green]✓ Array is correctly sorted: {array}[/green]",
            title="Verification Result",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[red]✗ Array is not sorted: {array}[/red]",
            title="Verification Result",
            border_style="red"
        ))
    
    return TextContent(
        type="text",
        text=str(is_sorted)
    )

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio")
