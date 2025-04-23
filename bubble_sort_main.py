import os
import sys
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import openai
import asyncio
from rich.console import Console
from rich.panel import Panel

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

console = Console(force_terminal=True)

# Load environment variables and setup OpenAI
load_dotenv()

# Add error handling for OpenAI initialization
try:
    genai.configure(api_key='samplekey')  # Replace with your actual API key
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    console.print(f"[red]Failed to initialize Gemini: {e}[/red]")
    raise

async def generate_with_timeout(prompt, timeout=10):
    """Generate content with a timeout"""
    try:
        loop = asyncio.get_running_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a sorting algorithm visualization agent."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
            ),
            timeout=timeout
        )
        if not response:
            raise ValueError("No response generated")
        
        # Extract the text from OpenAI response
        text = response.choices[0].message.content
        cleaned_text = text.encode('ascii', 'ignore').decode('ascii')
        
        class CleanedResponse:
            def __init__(self, text):
                self.text = text
        return CleanedResponse(cleaned_text)
            
    except asyncio.TimeoutError:
        console.print("[red]Request timed out[/red]")
        return None
    except Exception as e:
        console.print(f"[red]Error in generate_with_timeout: {str(e)}[/red]")
        return None

async def get_llm_response(prompt):
    """Get response from LLM with timeout"""
    try:
        response = await generate_with_timeout(prompt)
        if response and hasattr(response, 'text'):
            return response.text.strip()
        return None
    except Exception as e:
        console.print(f"[red]Error in get_llm_response: {str(e)}[/red]")
        return None

async def main():
    try:
        console.print(Panel("Bubble Sort Visualizer", border_style="cyan"))

        server_params = StdioServerParameters(
            command="python",
            args=["bubble_sort_tools.py"]
        )

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    try:
                        await session.initialize()

                        system_prompt = """You are a sorting algorithm visualization agent that implements bubble sort step by step.
You have access to these tools:
- show_reasoning(steps: list) - Show your step-by-step reasoning process
- compare_elements(a: int, b: int) - Compare two elements and determine if they need to be swapped
- perform_swap(array: list, i: int, j: int) - Swap elements at positions i and j in the array
- verify_sorted(array: list) - Verify if the array is sorted

First show your reasoning, then perform comparisons and swaps step by step.

Respond with EXACTLY ONE line in one of these formats:
1. FUNCTION_CALL: function_name|param1|param2|...
2. FINAL_ANSWER: [sorted_array]

Example:
User: Sort [5, 2, 8, 1, 9]
Assistant: FUNCTION_CALL: show_reasoning|["1. Start with first pass through the array", "2. Compare adjacent elements", "3. Swap if left > right", "4. Continue until array is sorted"]
User: Next step?
Assistant: FUNCTION_CALL: compare_elements|5|2
User: Should swap: true
Assistant: FUNCTION_CALL: perform_swap|[5, 2, 8, 1, 9]|0|1
User: Array after swap: [2, 5, 8, 1, 9]
Assistant: FUNCTION_CALL: verify_sorted|[1, 2, 5, 8, 9]
User: Array is sorted
Assistant: FINAL_ANSWER: [1, 2, 5, 8, 9]"""

                        # Initial array to sort
                        array = [64, 34, 25, 12, 22, 11, 90]
                        console.print(Panel(f"Array to sort: {array}", border_style="cyan"))

                        prompt = f"{system_prompt}\n\nSort this array using bubble sort: {array}"
                        current_array = array.copy()

                        while True:
                            try:
                                response = await generate_with_timeout(prompt)
                                if not response or not response.text:
                                    console.print("[red]No response received from model[/red]")
                                    break

                                result = response.text.strip()
                                console.print(f"\n[yellow]Assistant:[/yellow] {result}")

                                if result.startswith("FUNCTION_CALL:"):
                                    try:
                                        _, function_info = result.split(":", 1)
                                        parts = [p.strip() for p in function_info.split("|")]
                                        func_name = parts[0]
                                        
                                        if func_name == "show_reasoning":
                                            try:
                                                steps_str = parts[1].strip('[]')
                                                steps = [step.strip().strip('"\'') for step in steps_str.split(',')]
                                                await session.call_tool("show_reasoning", arguments={"steps": steps})
                                                prompt += f"\nUser: Next step?"
                                            except Exception as e:
                                                console.print(f"[red]Error processing reasoning steps: {str(e)}[/red]")
                                            
                                        elif func_name == "compare_elements":
                                            try:
                                                a, b = map(int, parts[1:3])
                                                result = await session.call_tool("compare_elements", arguments={
                                                    "a": a,
                                                    "b": b
                                                })
                                                prompt += f"\nUser: Should swap: {result.content[0].text}"
                                            except Exception as e:
                                                console.print(f"[red]Error in compare section: {str(e)}[/red]")
                                                break
                                            
                                        elif func_name == "perform_swap":
                                            try:
                                                array_str, i, j = parts[1:]
                                                current_array = eval(array_str)
                                                result = await session.call_tool("perform_swap", arguments={
                                                    "array": current_array,
                                                    "i": int(i),
                                                    "j": int(j)
                                                })
                                                current_array = eval(result.content[0].text)
                                                prompt += f"\nUser: Array after swap: {current_array}"
                                            except Exception as e:
                                                console.print(f"[red]Error in swap section: {str(e)}[/red]")
                                                break
                                            
                                        elif func_name == "verify_sorted":
                                            try:
                                                array_str = parts[1]
                                                current_array = eval(array_str)
                                                result = await session.call_tool("verify_sorted", arguments={
                                                    "array": current_array
                                                })
                                                prompt += f"\nUser: Array is {'sorted' if result.content[0].text == 'True' else 'not sorted'}"
                                            except Exception as e:
                                                console.print(f"[red]Error in verify section: {str(e)}[/red]")
                                                break
                                            
                                    except Exception as e:
                                        console.print(f"[red]Error processing function call: {str(e)}[/red]")
                                        break

                                elif result.startswith("FINAL_ANSWER:"):
                                    try:
                                        final_array = eval(result.split("[")[1].split("]")[0])
                                        await session.call_tool("verify_sorted", arguments={
                                            "array": final_array
                                        })
                                    except Exception as e:
                                        console.print(f"[red]Error processing final answer: {str(e)}[/red]")
                                    break
                                
                                prompt += f"\nAssistant: {result}"

                            except Exception as e:
                                console.print(f"[red]Error in main loop: {str(e)}[/red]")
                                break

                    except Exception as e:
                        console.print(f"[red]Error in session: {str(e)}[/red]")

        except Exception as e:
            console.print(f"[red]Error in stdio_client: {str(e)}[/red]")

        console.print("\n[green]Sorting completed![/green]")

    except Exception as e:
        console.print(f"[red]Main error: {str(e)}[/red]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[yellow]Program terminated by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")