"""Workflow orchestration similar to LangGraph."""

from typing import Any, Dict, List, Optional, Callable, Awaitable
from pydantic import BaseModel, Field
from enum import Enum


class NodeType(str, Enum):
    """Type of workflow node."""
    AGENT = "agent"
    FUNCTION = "function"
    CONDITION = "condition"


class WorkflowNode(BaseModel):
    """A node in the workflow graph."""
    
    name: str = Field(..., description="Node name")
    node_type: NodeType = Field(..., description="Node type")
    handler: Any = Field(..., description="Node handler (agent or function)")
    
    class Config:
        arbitrary_types_allowed = True


class Workflow:
    """
    Workflow orchestration using graph-based approach.
    
    Similar to LangGraph's StateGraph.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: Dict[str, List[str]] = {}
        self.conditional_edges: Dict[str, Callable] = {}
        self.entry_point: Optional[str] = None
    
    def add_node(
        self,
        name: str,
        handler: Any,
        node_type: NodeType = NodeType.FUNCTION
    ) -> "Workflow":
        """
        Add a node to the workflow.
        
        Args:
            name: Node name
            handler: Node handler (agent or function)
            node_type: Type of node
            
        Returns:
            Self for chaining
        """
        self.nodes[name] = WorkflowNode(
            name=name,
            node_type=node_type,
            handler=handler
        )
        return self
    
    def add_edge(self, from_node: str, to_node: str) -> "Workflow":
        """
        Add a directed edge between nodes.
        
        Args:
            from_node: Source node
            to_node: Target node
            
        Returns:
            Self for chaining
        """
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)
        return self
    
    def add_conditional_edge(
        self,
        from_node: str,
        condition: Callable[[Any], str],
        edge_mapping: Dict[str, str]
    ) -> "Workflow":
        """
        Add a conditional edge.
        
        Args:
            from_node: Source node
            condition: Function that returns edge key
            edge_mapping: Mapping from edge key to target node
            
        Returns:
            Self for chaining
        """
        def conditional_router(state: Any) -> str:
            edge_key = condition(state)
            return edge_mapping.get(edge_key, "__end__")
        
        self.conditional_edges[from_node] = conditional_router
        return self
    
    def set_entry_point(self, node_name: str) -> "Workflow":
        """Set the entry point of the workflow."""
        self.entry_point = node_name
        return self
    
    async def execute(self, initial_state: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute the workflow.
        
        Args:
            initial_state: Initial state
            
        Returns:
            Final state
        """
        if not self.entry_point:
            raise ValueError("Entry point not set")
        
        state = initial_state or {}
        current_node = self.entry_point
        
        while current_node != "__end__":
            # Execute current node
            node = self.nodes.get(current_node)
            if not node:
                raise ValueError(f"Node {current_node} not found")
            
            # Execute handler
            if node.node_type == NodeType.AGENT:
                result = await node.handler.execute(
                    task=state.get("task", ""),
                    context=state
                )
            else:
                result = await node.handler(state)
            
            # Update state
            state["last_result"] = result
            state[f"{current_node}_result"] = result
            
            # Determine next node
            if current_node in self.conditional_edges:
                current_node = self.conditional_edges[current_node](state)
            elif current_node in self.edges:
                next_nodes = self.edges[current_node]
                current_node = next_nodes[0] if next_nodes else "__end__"
            else:
                current_node = "__end__"
        
        return state
    
    def __repr__(self) -> str:
        return f"Workflow(name={self.name}, nodes={len(self.nodes)}, edges={len(self.edges)})"

