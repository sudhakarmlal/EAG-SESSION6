from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import openai
import re
import ast

load_dotenv()

class PerceptionResult(BaseModel):
    user_input: str
    intent: Optional[str]
    current_array: List[int]
    next_action: Optional[str] = None
    is_sorted: bool = False

def extract_perception(user_input: str) -> PerceptionResult:
    """Extracts sorting state and next action from user input"""
    
    # Initialize OpenAI
    openai.api_key = "your-api-key-here"  # Replace with your API key
    
    prompt = f"""
Analyze this bubble sort step input and extract:
1. The current array state
2. What needs to be done next
3. Whether the array appears to be sorted

Input: {user_input}

Return as a Python dictionary with:
- current_array: list of integers
- next_action: string (compare/swap/verify)
- is_sorted: boolean
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sorting algorithm analyzer."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content
        parsed = ast.literal_eval(result)
        
        return PerceptionResult(
            user_input=user_input,
            intent="bubble_sort",
            current_array=parsed["current_array"],
            next_action=parsed["next_action"],
            is_sorted=parsed["is_sorted"]
        )

    except Exception as e:
        # Default perception if analysis fails
        array_match = re.findall(r'\[[\d\s,]+\]', user_input)
        current_array = ast.literal_eval(array_match[0]) if array_match else []
        
        return PerceptionResult(
            user_input=user_input,
            intent="bubble_sort",
            current_array=current_array,
            next_action="compare",
            is_sorted=False
        )