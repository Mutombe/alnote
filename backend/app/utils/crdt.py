import uuid
import json
from collections import defaultdict
from typing import Dict, List, Tuple

class VectorClock:
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.clock = defaultdict(int)
        self.clock[device_id] = 0

    def increment(self):
        self.clock[self.device_id] += 1
        return self.clock.copy()

    def merge(self, other):
        for k, v in other.items():
            if k not in self.clock or v > self.clock[k]:
                self.clock[k] = v

class CRDTEngine:
    def __init__(self, note_id: str):
        self.note_id = note_id
        self.data = {}
        self.tombstones = set()
        self.version_vector = defaultdict(int)

    def apply_operation(self, op: dict, device_id: str) -> dict:
        """Apply CRDT operation and return new state"""
        op_type = op['type']
        op_id = op['id']
        vector = op['vector']
        
        # Merge version vectors
        for k, v in vector.items():
            if k not in self.version_vector or v > self.version_vector[k]:
                self.version_vector[k] = v
                
        # Check if operation is obsolete
        if op_id in self.tombstones:
            return self.get_state()
            
        if op_type == "insert":
            # Conflict resolution: last write wins
            if op_id not in self.data or op['vector'][device_id] > self.data[op_id]['vector'].get(device_id, -1):
                self.data[op_id] = {
                    'type': 'text',
                    'content': op['content'],
                    'position': op['position'],
                    'vector': op['vector']
                }
        elif op_type == "delete":
            if op_id in self.data:
                del self.data[op_id]
                self.tombstones.add(op_id)
                
        return self.get_state()
    
    def get_state(self) -> dict:
        """Get current document state"""
        # Sort by position and convert to content
        sorted_ops = sorted(
            [op for op in self.data.values()], 
            key=lambda x: x['position']
        )
        
        content = "".join([op['content'] for op in sorted_ops])
        return {
            "content": content,
            "version_vector": dict(self.version_vector)
        }
    
    def generate_operation(self, op_type: str, content: str, position: int, device_id: str) -> dict:
        """Generate a new CRDT operation"""
        op_id = str(uuid.uuid4())
        new_vector = self.version_vector.copy()
        new_vector[device_id] += 1
        
        return {
            "id": op_id,
            "type": op_type,
            "content": content,
            "position": position,
            "vector": new_vector,
            "device_id": device_id,
            "note_id": self.note_id
        }