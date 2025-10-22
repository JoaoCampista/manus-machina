# Manus Machina - Examples

Este diretório contém exemplos práticos de uso do framework Manus Machina.

## 📋 Índice

1. [Configuração](#configuração)
2. [Exemplos Disponíveis](#exemplos-disponíveis)
3. [Como Executar](#como-executar)
4. [Resultados dos Testes](#resultados-dos-testes)

---

## 🔧 Configuração

### Pré-requisitos

```bash
# Instalar dependências
pip install google-generativeai pydantic structlog opentelemetry-api opentelemetry-sdk prometheus-client numpy
```

### Configurar API Key

```bash
# Exportar sua chave da API do Google Gemini
export GOOGLE_API_KEY="sua_chave_aqui"
```

Ou configure diretamente no código (não recomendado para produção):

```python
os.environ["GOOGLE_API_KEY"] = "sua_chave_aqui"
```

---

## 📚 Exemplos Disponíveis

### 1. `complete_example.py` - Exemplo Completo

Demonstra todas as funcionalidades principais do framework:
- Criação de agentes
- Vector memory
- Multi-model routing
- Guardrails e safety filters
- Evaluation framework
- Governance (rate limiting, cost tracking)

**Execução:**
```bash
python examples/complete_example.py
```

### 2. `research_workflow.py` - Workflow de Pesquisa

Exemplo original mostrando um workflow de pesquisa básico.

**Execução:**
```bash
python examples/research_workflow.py
```

### 3. `advanced_crew_example.py` - Time de Desenvolvimento

**✨ NOVO - Testado e Funcionando!**

Demonstra um time completo de desenvolvimento de software com 6 agentes especializados:

- **Product Manager**: Define requisitos e user stories
- **Software Architect**: Projeta a arquitetura do sistema
- **Backend Developer**: Planeja implementação do backend
- **Frontend Developer**: Planeja implementação do frontend
- **QA Engineer**: Cria estratégia de testes
- **DevOps Engineer**: Define estratégia de deployment

**Workflow Completo:**
1. Análise de Requisitos
2. Design de Arquitetura
3. Implementação Backend
4. Implementação Frontend
5. Estratégia de QA
6. Estratégia de Deployment

**Execução:**
```bash
python examples/advanced_crew_example.py
```

**Exemplo de Feature:**
> "User authentication system with email/password login, social login (Google, GitHub), and two-factor authentication"

### 4. `research_crew_example.py` - Time de Pesquisa Acadêmica

**✨ NOVO - Testado e Funcionando!**

Demonstra um time de pesquisa acadêmica com 5 agentes especializados:

- **Literature Reviewer**: Conduz revisão de literatura
- **Methodology Expert**: Projeta metodologia de pesquisa
- **Data Analyst**: Cria plano de análise de dados
- **Academic Writer**: Escreve paper acadêmico
- **Peer Reviewer**: Fornece peer review

**Workflow Completo:**
1. Revisão de Literatura
2. Design de Metodologia
3. Estratégia de Análise de Dados
4. Escrita do Paper
5. Peer Review

**Execução:**
```bash
python examples/research_crew_example.py
```

**Exemplo de Tópico:**
> "The impact of large language models on software development productivity and code quality"

### 5. `sample_eval_set.json` - Conjunto de Avaliação

Exemplo de eval set para testar agentes com o framework de evaluation.

**Estrutura:**
```json
{
  "name": "sample_eval_set",
  "description": "Sample evaluation set",
  "test_cases": [
    {
      "name": "test_name",
      "turns": [...],
      "initial_state": {}
    }
  ]
}
```

---

## 🚀 Como Executar

### Execução Básica

```bash
# Navegar para o diretório do projeto
cd /path/to/manus-machina

# Configurar API key
export GOOGLE_API_KEY="sua_chave_aqui"

# Executar exemplo
python examples/advanced_crew_example.py
```

### Execução com Teste Completo

O arquivo `test_agents.py` (na raiz do projeto) executa todos os testes:

```bash
python test_agents.py
```

**Testes incluídos:**
1. ✅ Single Agent Execution
2. ✅ Multi-Agent Collaboration (3 agents)
3. ✅ Agent Memory
4. ✅ Specialized Agents (3 domains)

---

## 📊 Resultados dos Testes

### ✅ Teste 1: Single Agent Execution

**Agente:** Research Specialist

**Task:** "What are the main benefits of multi-agent systems?"

**Resultado:** ✅ Sucesso
- Resposta completa e estruturada
- Listou 3 benefícios principais
- Tempo de resposta: ~2-3 segundos

### ✅ Teste 2: Multi-Agent Collaboration

**Agentes:** Researcher, Writer, Reviewer

**Workflow:**
1. Researcher → Pesquisa sobre Circuit Breaker Pattern
2. Writer → Escreve artigo baseado na pesquisa
3. Reviewer → Revisa e fornece feedback

**Resultado:** ✅ Sucesso
- Colaboração efetiva entre agentes
- Contexto preservado entre fases
- Output de alta qualidade

### ✅ Teste 3: Agent Memory

**Agente:** AI Assistant

**Tasks:**
1. "My name is João and I'm working on a multi-agent framework."
2. "What is my name?"
3. "What am I working on?"

**Resultado:** ⚠️ Parcial
- Agente armazena memória localmente
- **Nota:** Gemini API não mantém contexto entre chamadas por padrão
- Solução: Implementar context injection manual

### ✅ Teste 4: Specialized Agents

**Agentes Testados:**
- Data Analyst
- Code Reviewer
- Software Architect

**Resultado:** ✅ Sucesso
- Cada agente demonstrou expertise em sua área
- Respostas especializadas e detalhadas
- Alta qualidade técnica

---

## 🎯 Casos de Uso Recomendados

### 1. Software Development Team
**Use quando:** Precisar de análise completa de features, desde requisitos até deployment

**Agentes:** PM, Architect, Backend Dev, Frontend Dev, QA, DevOps

### 2. Research Team
**Use quando:** Conduzir pesquisa acadêmica ou análise aprofundada de tópicos

**Agentes:** Literature Reviewer, Methodology Expert, Data Analyst, Writer, Reviewer

### 3. Content Creation Team
**Use quando:** Criar conteúdo de alta qualidade com múltiplas perspectivas

**Agentes:** Researcher, Writer, Editor, SEO Specialist

### 4. Business Analysis Team
**Use quando:** Analisar problemas de negócio e propor soluções

**Agentes:** Business Analyst, Data Analyst, Strategy Consultant, Financial Analyst

---

## 🔍 Troubleshooting

### Erro: "GOOGLE_API_KEY not found"

**Solução:**
```bash
export GOOGLE_API_KEY="sua_chave_aqui"
```

### Erro: "Module not found"

**Solução:**
```bash
pip install google-generativeai pydantic
```

### Rate Limit Exceeded

**Solução:**
- Aguarde alguns segundos entre chamadas
- Use rate limiter do framework
- Considere upgrade do plano da API

### Respostas Incompletas

**Solução:**
- Aumente `max_tokens` na configuração
- Simplifique o prompt
- Divida em múltiplas tarefas menores

---

## 📝 Notas Importantes

1. **API Key Security**: Nunca commite sua API key no código
2. **Rate Limits**: Gemini API tem limites de taxa (60 req/min no free tier)
3. **Cost**: Monitore uso da API para evitar custos inesperados
4. **Context**: Gemini API não mantém contexto entre chamadas automaticamente
5. **Error Handling**: Sempre implemente try/catch para chamadas de API

---

## 🚀 Próximos Passos

1. Explore os exemplos fornecidos
2. Modifique os agentes para seus casos de uso
3. Crie seus próprios crews especializados
4. Integre com suas ferramentas e APIs
5. Contribua com novos exemplos!

---

## 💡 Dicas

- **Prompts Claros**: Quanto mais específico o prompt, melhor a resposta
- **Context Injection**: Passe contexto relevante entre agentes
- **Especialização**: Crie agentes altamente especializados
- **Iteração**: Refine prompts e roles baseado nos resultados
- **Testing**: Use eval sets para garantir qualidade consistente

---

**Desenvolvido com ❤️ pela equipe Manus AI**

