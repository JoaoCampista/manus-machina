# Manus Machina v5.0

**Enterprise-Grade Multi-Agent Orchestration Framework - Complete Edition**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 O Framework COMPLETO

Manus Machina v5.0 é o **framework definitivo** para sistemas multi-agente, integrando TODAS as funcionalidades em uma arquitetura coesa e production-ready.

### ✨ Funcionalidades Completas

#### 🔵 Session & State Management
- ✅ Session lifecycle completo
- ✅ State com 4 escopos (session/user/app/temp)
- ✅ Artifacts (30+ tipos)
- ✅ Domain Events (20+ tipos)

#### 🟢 LLM Universal
- ✅ LiteLLM (100+ providers)
- ✅ OpenAI, Anthropic, Google, Cohere, Meta, Mistral
- ✅ Unified interface
- ✅ Fallback automático

#### 🟣 Database & Persistence
- ✅ SQLAlchemy + Alembic migrations
- ✅ PostgreSQL, MySQL, SQLite
- ✅ Optimized indexes
- ✅ Automatic schema management

#### 🔴 Evaluation & Quality
- ✅ LLM-as-Judge
- ✅ Tool trajectory matching
- ✅ Response similarity (ROUGE)
- ✅ Hallucination detection
- ✅ Safety scoring

#### 🟡 Memory & RAG
- ✅ Vector stores (FAISS, Pinecone, Weaviate, ChromaDB, Qdrant)
- ✅ Semantic search
- ✅ Long-term memory
- ✅ Context management

#### 🟠 Governance & Safety
- ✅ Safety filters (hate, violence, sexual, dangerous)
- ✅ Content moderation
- ✅ Rate limiting
- ✅ Cost tracking
- ✅ Budget alerts

#### 🔵 Resilience Patterns
- ✅ Circuit Breaker (CLOSED/OPEN/HALF_OPEN)
- ✅ Retry with 4 jitter types
- ✅ Saga pattern
- ✅ Timeout management

#### 🟢 Guardrails
- ✅ Input guards (prompt injection, PII)
- ✅ Output guards (toxicity, factuality, format)
- ✅ Action guards (domain allowlist)
- ✅ Guardrail engine

#### 🟣 Orchestration
- ✅ Workflow engine (graph-based)
- ✅ Conditional edges
- ✅ Saga orchestration
- ✅ Sequential/Parallel execution

#### 🔴 Communication
- ✅ Communication bus
- ✅ A2A protocol
- ✅ MCP support
- ✅ Multi-protocol (gRPC, AMQP, Kafka)

#### 🟡 Observability
- ✅ Structured logging (structlog)
- ✅ Distributed tracing (OpenTelemetry)
- ✅ Metrics (Prometheus)
- ✅ Complete audit trail

---

## 🚀 Quick Start

### Installation

```bash
pip install -e ".[all]"
```

### Basic Example

```python
import asyncio
from manus_machina import (
    InMemorySessionService,
    LiteLLMClient,
    LLMMessage,
    SimpleAgent,
    SimpleAgentConfig
)

async def main():
    # Create session
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        user_id="user123",
        app_name="demo"
    )
    
    # Create LLM client
    llm = LiteLLMClient(
        model="gemini/gemini-2.0-flash-exp",
        api_key="your_key"
    )
    
    # Create agent
    agent = SimpleAgent(
        config=SimpleAgentConfig(
            name="assistant",
            role="AI Assistant",
            goal="Help users",
            llm_client=llm
        )
    )
    
    # Execute task
    result = await agent.execute(
        task="Explain quantum computing",
        session=session
    )
    
    print(result)

asyncio.run(main())
```

---

## 📦 Architecture

```
┌──────────────────────────────────────────────────┐
│              Application Layer                    │
│         (Custom Agent Applications)               │
├──────────────────────────────────────────────────┤
│         Evaluation & Governance Layer             │
│  Evaluator │ Safety │ Rate Limiter │ Cost Track  │
├──────────────────────────────────────────────────┤
│            Orchestration Layer                    │
│     Workflow Engine    │    Saga Manager          │
├──────────────────────────────────────────────────┤
│              Agent Core Layer                     │
│  Session │ State │ Agents │ Tasks │ Crews         │
│  Resilience │ Guardrails │ Communication          │
│  Memory │ LLM Router │ Artifacts                  │
├──────────────────────────────────────────────────┤
│           Infrastructure Layer                    │
│  Database │ Vector Stores │ Observability         │
└──────────────────────────────────────────────────┘
```

---

## 📚 Complete Feature Matrix

| Category | Features | Status |
|----------|----------|--------|
| **Session** | Lifecycle, Metadata, Tags | ✅ |
| **State** | 4 scopes, Templating | ✅ |
| **Artifacts** | 30+ types, Versioning | ✅ |
| **Events** | 20+ types, Audit trail | ✅ |
| **LLM** | 100+ providers via LiteLLM | ✅ |
| **Database** | PostgreSQL, MySQL, SQLite | ✅ |
| **Migrations** | Alembic automatic | ✅ |
| **Evaluation** | LLM-as-Judge, Metrics | ✅ |
| **Memory** | 5+ vector stores | ✅ |
| **Governance** | Safety, Rate, Cost | ✅ |
| **Resilience** | Circuit Breaker, Retry, Saga | ✅ |
| **Guardrails** | Input/Output/Action guards | ✅ |
| **Orchestration** | Workflow, Conditional | ✅ |
| **Communication** | A2A, MCP, Multi-protocol | ✅ |
| **Observability** | Logs, Traces, Metrics | ✅ |

---

## 🎯 Why Manus Machina v5.0?

### vs Google ADK
- ✅ **100+ LLM providers** (vs Google-focused)
- ✅ **Cloud-agnostic** (vs Google Cloud)
- ✅ **Automatic migrations** (vs manual)
- ✅ **Complete evaluation** (vs basic)

### vs CrewAI
- ✅ **Session management**
- ✅ **State with 4 scopes**
- ✅ **Database layer**
- ✅ **Evaluation framework**
- ✅ **Resilience patterns**

### vs LangGraph
- ✅ **Session & state**
- ✅ **Evaluation**
- ✅ **Governance**
- ✅ **Circuit breaker**
- ✅ **Universal LLM support**

### vs AutoGen
- ✅ **Artifacts**
- ✅ **State templating**
- ✅ **Domain events**
- ✅ **Database persistence**
- ✅ **Comprehensive observability**

---

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Quick Start](docs/quickstart.md)
- [Core Concepts](docs/concepts.md)
- [API Reference](docs/api.md)
- [Examples](examples/)

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

MIT License - see [LICENSE](LICENSE).

---

## 🌟 Acknowledgments

Inspired by: Google ADK, LangChain, CrewAI, LiteLLM, Microsoft Azure, Anthropic

---

**Built with ❤️ by João Campista**
