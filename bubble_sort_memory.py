from typing import List, Optional, Literal
from pydantic import BaseModel
from datetime import datetime
import numpy as np
import faiss

class SortingStep(BaseModel):
    array_state: List[int]
    action_taken: str
    result: str
    timestamp: str = datetime.now().isoformat()

class MemoryItem(BaseModel):
    text: str
    type: Literal["comparison", "swap", "verification", "general", "tool_output"] = "general"
    array_state: Optional[List[int]] = None
    timestamp: str = datetime.now().isoformat()
    tool_name: Optional[str] = None
    user_query: Optional[str] = None
    tags: List[str] = []
    session_id: Optional[str] = None

class MemoryManager:
    def __init__(self):
        self.steps: List[SortingStep] = []
        self.index = None
        self.data: List[MemoryItem] = []
        self.embeddings: List[np.ndarray] = []

    def add_step(self, array_state: List[int], action: str, result: str):
        step = SortingStep(
            array_state=array_state,
            action_taken=action,
            result=result
        )
        self.steps.append(step)

    def add(self, item: MemoryItem):
        self.data.append(item)
        if item.array_state:
            # Convert array state to embedding (simplified version)
            emb = np.array(item.array_state, dtype=np.float32)
            self.embeddings.append(emb)

            if self.index is None:
                self.index = faiss.IndexFlatL2(len(emb))
            self.index.add(np.stack([emb]))

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        type_filter: Optional[str] = None,
        tag_filter: Optional[List[str]] = None,
        session_filter: Optional[str] = None
    ) -> List[MemoryItem]:
        if not self.data:
            return []
            
        # Simple retrieval based on recency
        filtered = self.data
        if type_filter:
            filtered = [item for item in filtered if item.type == type_filter]
        if session_filter:
            filtered = [item for item in filtered if item.session_id == session_filter]
            
        return filtered[-top_k:]

    def get_sorting_history(self) -> List[SortingStep]:
        return self.steps