# EAG-SESSION6
Bubble Sort Agentic AI

# Cognitive Bubble Sort Implementation

A cognitive architecture-based implementation of the Bubble Sort algorithm that combines user preferences, perception, memory, decision-making, and action layers to provide an interactive and personalized sorting experience.

## 🧠 Architecture Overview

This implementation follows a cognitive architecture with five main components:

### 1. Agent (`bubble_sort_agent.py`)
The main orchestrator that:
- Collects user preferences and input array
- Coordinates between cognitive layers
- Manages the sorting workflow
- Provides personalized visualization based on user preferences

Key features:
- User preference collection (name, visualization style, speed, color scheme, etc.)
- Adaptive output based on user preferences
- Progress tracking and visualization
- Error handling and session management

### 2. Perception (`bubble_sort_perception.py`)
Analyzes and understands the current state of sorting:

```python
class PerceptionResult:
    user_input: str        # Raw input
    intent: str           # Purpose of the operation
    current_array: List[int]  # Current state of array
    next_action: str      # Suggested next action
    is_sorted: bool       # Whether array is sorted
```

### 3. Memory (`bubble_sort_memory.py`)
Maintains the history and state of sorting operations:

```python
class MemoryItem:
    text: str            # Description of the memory
    type: Literal        # Type of operation
    array_state: List[int]  # Array state at this point
    timestamp: str       # When this happened
    tool_name: str       # Tool used
    tags: List[str]      # Memory tags
    session_id: str      # Session identifier
```

### 4. Decision Making (`bubble_sort_decision.py`)
Determines the next sorting action based on:
- Current array state
- Previous actions
- Available tools
- Sorting progress

### 5. Action (`bubble_sort_action.py`)
Executes sorting operations:

```python
class ToolCallResult:
    tool_name: str       # Tool being used
    arguments: Dict      # Tool parameters
    result: Union[str, list, dict]  # Operation result
    raw_response: Any    # Raw tool response
```

## 🔄 Workflow Example

Here's how a typical sorting session works:

1. **Initial Setup**:
```bash
🔄 Starting bubble sort for array: [64, 34, 25, 12, 22, 11, 90]

👋 Hello!
╭────────────────────────────────────────╮
│ Welcome to the Cognitive Bubble Sort Agent! │
╰────────────────────────────────────────╯
```

2. **User Preference Collection**:
```bash
What's your name? John
How would you like to visualize the sorting process? (detailed/simple/minimal) detailed
How fast should the sorting visualization be? (fast/medium/slow) medium
Which color scheme do you prefer? (colorful/monochrome/pastel) colorful
How detailed should the explanations be? (basic/intermediate/advanced) intermediate
What aspect of bubble sort interests you most? (algorithm steps/performance analysis/visualization/all) algorithm steps
```

3. **Sorting Process**:
```bash
[08:15:30] [loop] Step 1 started
[08:15:30] [perception] Intent: bubble_sort, Array state: [64, 34, 25, 12, 22, 11, 90]
[08:15:31] [memory] Retrieved 0 relevant memories
[08:15:31] [plan] Plan generated: FUNCTION_CALL: compare_elements|a=64|b=34
[08:15:31] [tool] compare_elements returned: true

[08:15:32] [loop] Step 2 started
[08:15:32] [perception] Intent: bubble_sort, Array state: [34, 64, 25, 12, 22, 11, 90]
...
```

4. **Final Result**:
```bash
✨ Sorting complete for John!
FINAL_ANSWER: [11, 12, 22, 25, 34, 64, 90]
```

## 🛠 Setup and Usage

1. Install required packages:
```bash
pip install openai python-dotenv rich faiss-cpu pydantic
```

2. Set up your OpenAI API key in the relevant files:
- `bubble_sort_perception.py`
- `bubble_sort_decision.py`

3. Run the sorting agent:
```bash
python bubble_sort_agent.py
```

## 🎨 Customization Options

The agent supports various user preferences:

1. **Visualization Modes**:
- `detailed`: Shows all steps and operations
- `simple`: Shows basic progress
- `minimal`: Shows only essential information

2. **Speed Settings**:
- `fast`: No delays between operations
- `medium`: 0.5s delay between steps
- `slow`: 1s delay between steps

3. **Color Schemes**:
- `colorful`: Full color output
- `monochrome`: Black and white
- `pastel`: Soft color palette

4. **Explanation Levels**:
- `basic`: Simple explanations
- `intermediate`: Detailed steps
- `advanced`: In-depth analysis

## 🔍 Technical Details

- Uses OpenAI's GPT-3.5-turbo for perception and decision-making
- Implements FAISS for efficient memory retrieval
- Follows MCP (Model-Control-Process) architecture
- Provides real-time visualization using Rich library
- Supports asynchronous operations with asyncio

## ⚠️ Error Handling

The implementation includes comprehensive error handling:
- Input validation
- API call error management
- Tool execution error handling
- State consistency checks
