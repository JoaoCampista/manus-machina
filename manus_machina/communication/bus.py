"""Communication bus for agent-to-agent communication."""

from typing import Any, Dict, List, Optional, Callable, Awaitable
from pydantic import BaseModel, Field
from enum import Enum
import asyncio


class MessageProtocol(str, Enum):
    """Supported communication protocols."""
    A2A = "a2a"  # Agent-to-Agent
    MCP = "mcp"  # Model Context Protocol
    GRPC = "grpc"
    AMQP = "amqp"  # RabbitMQ
    KAFKA = "kafka"


class Message(BaseModel):
    """A message in the communication bus."""
    
    sender: str = Field(..., description="Sender agent name")
    recipient: str = Field(..., description="Recipient agent name")
    content: Dict[str, Any] = Field(..., description="Message content")
    protocol: MessageProtocol = Field(default=MessageProtocol.A2A)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CommunicationBus:
    """
    Central communication bus for agent-to-agent communication.
    
    Supports multiple protocols and routing strategies.
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Message], Awaitable[None]]]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
    
    def subscribe(
        self,
        agent_name: str,
        handler: Callable[[Message], Awaitable[None]]
    ) -> None:
        """
        Subscribe an agent to receive messages.
        
        Args:
            agent_name: Agent name
            handler: Message handler function
        """
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(handler)
    
    async def send(
        self,
        sender: str,
        recipient: str,
        message: Dict[str, Any],
        protocol: MessageProtocol = MessageProtocol.A2A
    ) -> None:
        """
        Send a message to another agent.
        
        Args:
            sender: Sender agent name
            recipient: Recipient agent name
            message: Message content
            protocol: Communication protocol
        """
        msg = Message(
            sender=sender,
            recipient=recipient,
            content=message,
            protocol=protocol
        )
        
        await self.message_queue.put(msg)
    
    async def broadcast(
        self,
        sender: str,
        message: Dict[str, Any],
        protocol: MessageProtocol = MessageProtocol.A2A
    ) -> None:
        """
        Broadcast a message to all subscribed agents.
        
        Args:
            sender: Sender agent name
            message: Message content
            protocol: Communication protocol
        """
        for recipient in self.subscribers.keys():
            if recipient != sender:
                await self.send(sender, recipient, message, protocol)
    
    async def start(self) -> None:
        """Start the communication bus."""
        self._running = True
        asyncio.create_task(self._process_messages())
    
    async def stop(self) -> None:
        """Stop the communication bus."""
        self._running = False
    
    async def _process_messages(self) -> None:
        """Process messages from the queue."""
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                # Deliver to subscribers
                handlers = self.subscribers.get(message.recipient, [])
                for handler in handlers:
                    await handler(message)
                
            except asyncio.TimeoutError:
                continue
    
    def __repr__(self) -> str:
        return f"CommunicationBus(subscribers={len(self.subscribers)})"

