from bubble_sort_perception import PerceptionResult
from bubble_sort_memory import MemoryItem
from typing import List, Optional
import openai
import datetime

def generate_plan(
    perception: PerceptionResult,
    memory_items: List[MemoryItem],
    tool_descriptions: str
) -> str:
    """Generates next sorting action based on current state and history"""
    
    # Initialize OpenAI
    openai.api_key = "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"  # Replace with your API key
    
    memory_text = "\n".join(
        f"- Array: {m.array_state}, Action: {m.type}" 
        for m in memory_items[-3:]  # Last 3 memories
    )

    prompt = f"""
You are a bubble sort algorithm executor. Based on the current state:

Current Array: {perception.current_array}
Last Actions:
{memory_text}

Available Tools:
{tool_descriptions}

Determine the next step in bubble sort algorithm:
1. If array needs sorting:
   - Compare adjacent elements
   - Swap if needed
2. If no more swaps needed:
   - Verify if array is sorted
3. If verified sorted:
   - Return final answer

Respond with EXACTLY ONE of:
1. FUNCTION_CALL: compare_elements|a=X|b=Y
2. FUNCTION_CALL: perform_swap|array=[...]|i=X|j=Y
3. FUNCTION_CALL: verify_sorted|array=[...]
4. FINAL_ANSWER: [sorted_array]
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a bubble sort algorithm executor."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Decision error: {e}")
        return "FINAL_ANSWER: [error]"

timestamp: str = datetime.datetime.now().isoformat()