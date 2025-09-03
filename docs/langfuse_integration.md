# LangFuse Integration Guide

Agent Zero now includes comprehensive LangFuse integration for complete observability and tracing of all agent operations.

## Overview

LangFuse is an open-source LLM engineering platform that provides:
- 📊 **Comprehensive Tracing** - Track every conversation, tool call, and LLM interaction
- 🔍 **Detailed Analytics** - Understand performance, costs, and usage patterns
- 🐛 **Debugging Support** - Trace through complex agent workflows step by step
- 📈 **Performance Monitoring** - Monitor response times, token usage, and success rates

## What Gets Traced

The integration captures **everything** that happens in Agent Zero:

### 🤖 Agent Operations
- Complete agent monologues and conversations
- Message loop iterations and decision making
- Agent context switches and subordinate calls
- Intervention handling and user interactions

### 🛠 Tool Executions
- All tool calls with full input arguments
- Tool execution results and outputs
- Success/failure status and error handling
- Tool performance and execution time

### 🧠 LLM Interactions
- Chat model calls (GPT-4, Claude, etc.)
- Utility model calls for summarization
- Browser model interactions
- Token usage and response metrics

### 💾 Memory Operations
- Memory save and recall operations
- Knowledge base queries and imports
- Memory consolidation processes
- Vector database interactions

### 📚 History Management
- Message history compression
- Topic summarization
- Bulk operations and cleanup

## Quick Setup

### 1. Install LangFuse
```bash
pip install langfuse>=2.0.0
# Or if using the provided requirements.txt:
pip install -r requirements.txt
```

### 2. Get LangFuse Credentials
- Sign up at [https://cloud.langfuse.com](https://cloud.langfuse.com)
- Or deploy your own instance
- Get your Public Key and Secret Key from the project settings

### 3. Configure Environment Variables
```bash
# Required
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key-here

# Optional (with defaults)
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true
LANGFUSE_DEBUG=false
LANGFUSE_SAMPLE_RATE=1.0
```

### 4. Run Agent Zero
That's it! All your agent interactions will now be automatically traced to LangFuse.

## Configuration Options

### Basic Configuration
```bash
# Enable/disable tracing entirely
LANGFUSE_ENABLED=true

# Debug mode (shows detailed LangFuse logs)
LANGFUSE_DEBUG=false

# Sample rate (0.0 = no tracing, 1.0 = trace everything)
LANGFUSE_SAMPLE_RATE=1.0
```

### Granular Tracing Controls
```bash
# Control what gets traced (all default to true)
LANGFUSE_TRACE_USER_MESSAGES=true
LANGFUSE_TRACE_AGENT_RESPONSES=true
LANGFUSE_TRACE_TOOL_CALLS=true
LANGFUSE_TRACE_LLM_CALLS=true
LANGFUSE_TRACE_MEMORY_OPERATIONS=true
LANGFUSE_TRACE_HISTORY_OPERATIONS=true
```

### Custom Host (Self-Hosted)
```bash
# For self-hosted LangFuse instances
LANGFUSE_HOST=https://your-langfuse-instance.com
```

## Understanding Your Traces

### Trace Structure
Each agent conversation creates a **Trace** with the following hierarchy:

```
🔍 Trace: "Agent A0 Monologue"
├── 🤖 Observation: "Message Loop - Iteration 0"
│   ├── 🧠 Observation: "LLM Call: openai/gpt-4"
│   └── 🛠 Observation: "Tool: code_execution"
├── 🤖 Observation: "Message Loop - Iteration 1"
│   ├── 🧠 Observation: "LLM Call: openai/gpt-4"
│   └── 🛠 Observation: "Tool: response"
└── 💾 Observation: "Memory: save_memory"
```

### Key Metadata
Each trace includes rich metadata:
- **Agent Information**: Agent number, name, model configurations
- **Context**: Session ID, conversation context, user interactions
- **Performance**: Token usage, response times, success rates
- **Content**: Sanitized inputs/outputs, tool arguments, results

### Sessions and Users
- **Session ID**: Maps to Agent Zero context ID for conversation grouping
- **User ID**: Also maps to context ID for user activity tracking
- **Tags**: Automatic tagging by agent number, operation type, success status

## Viewing Your Data

### LangFuse Dashboard
1. Visit your LangFuse instance (cloud.langfuse.com or your host)
2. Navigate to your project
3. View traces, sessions, and analytics

### Key Views
- **Traces**: See individual conversations and their complete flow
- **Sessions**: Group multiple interactions by user/context
- **Models**: Analyze LLM usage, costs, and performance
- **Scores**: Add custom scoring and evaluation metrics

## Advanced Usage

### Programmatic Access
```python
from python.helpers.langfuse_tracer import get_tracer, configure_tracing

# Get the global tracer
tracer = get_tracer()

# Check if tracing is enabled
if tracer.is_enabled():
    print("LangFuse tracing is active!")

# Configure tracing at runtime
configure_tracing(
    enabled=True,
    sample_rate=0.5,  # Only trace 50% of operations
    trace_tool_calls=False  # Disable tool call tracing
)
```

### Manual Tracing
```python
from python.helpers.langfuse_tracer import trace_user_message

# Manually trace a user message
trace_user_message(
    message="Hello, how can you help me?",
    attachments=["file1.txt"],
    context_id="user_123"
)
```

### Custom Decorators
The integration provides decorators for custom tracing:
```python
from python.helpers.langfuse_tracer import trace_tool_execution

@trace_tool_execution("my_custom_tool")
async def my_tool_execute(self, **kwargs):
    # Your tool implementation
    return Response("Tool completed", False)
```

## Performance Impact

The LangFuse integration is designed to be lightweight:
- **Minimal Overhead**: Asynchronous tracing with background processing
- **Automatic Batching**: Traces are batched and sent efficiently
- **Error Isolation**: Tracing errors never break agent functionality
- **Smart Sampling**: Configurable sampling rates for production use

## Troubleshooting

### Common Issues

**1. Traces Not Appearing**
```bash
# Check your credentials
echo $LANGFUSE_PUBLIC_KEY
echo $LANGFUSE_SECRET_KEY

# Enable debug mode
export LANGFUSE_DEBUG=true
```

**2. Connection Issues**
```bash
# Check host configuration
echo $LANGFUSE_HOST

# Test connectivity
curl -I https://cloud.langfuse.com
```

**3. Partial Tracing**
```bash
# Check if tracing is enabled
echo $LANGFUSE_ENABLED

# Check sample rate
echo $LANGFUSE_SAMPLE_RATE
```

### Debug Mode
Enable detailed logging:
```bash
export LANGFUSE_DEBUG=true
```

This will show:
- Connection status
- Trace creation and updates
- API call details
- Error messages

### Manual Flush
Force sending pending traces:
```python
from python.helpers.langfuse_tracer import flush_traces
flush_traces()
```

## Security and Privacy

### Data Handling
- **Automatic Truncation**: Large content is automatically truncated for tracing
- **No Sensitive Data**: Credentials and secrets are not logged
- **Configurable Sampling**: Reduce data volume with sampling rates
- **Local Processing**: Data is processed locally before sending

### Content Filtering
The integration automatically:
- Truncates long text content (configurable limits)
- Excludes sensitive argument names (passwords, keys, tokens)
- Sanitizes file paths and system information
- Compresses large JSON structures

### Self-Hosted Option
For maximum privacy, deploy your own LangFuse instance:
```bash
# Example Docker deployment
docker run -d \
  --name langfuse \
  -p 3000:3000 \
  -e DATABASE_URL=postgresql://... \
  langfuse/langfuse:latest
```

## Examples and Use Cases

### Development and Debugging
- **Trace Complex Workflows**: Follow multi-agent conversations step by step
- **Debug Tool Failures**: See exactly what inputs caused tool errors
- **Optimize LLM Usage**: Identify expensive or slow model calls
- **Monitor Memory Usage**: Track how agents use their memory systems

### Production Monitoring
- **Performance Analytics**: Monitor response times and success rates
- **Cost Tracking**: Track token usage and LLM costs across agents
- **Error Detection**: Get alerts when agents fail or behave unexpectedly
- **Usage Patterns**: Understand how users interact with your agents

### Research and Analysis
- **Conversation Analysis**: Study how agents solve different types of problems
- **Model Comparison**: A/B test different models and configurations
- **User Behavior**: Analyze how different users interact with agents
- **Feature Impact**: Measure the impact of new agent capabilities

## Integration Architecture

### Extension System
The LangFuse integration uses Agent Zero's extension system:
- `_20_langfuse_init.py` - Initialize tracing for new agents
- `_10_langfuse_trace.py` - Start traces for monologues
- `_20_langfuse_llm_trace.py` - Trace LLM calls
- `_30_langfuse_response_trace.py` - Trace agent responses
- `_10_langfuse_trace_complete.py` - Complete traces

### Tool Integration
All tools automatically get tracing through the base `Tool` class:
- Input argument capture
- Execution timing
- Output and error handling
- Metadata enrichment

### Memory Integration
Memory operations are traced through decorators:
- `@trace_memory_operation` - General memory operations
- `@trace_memory_consolidation` - Memory cleanup processes
- `@trace_knowledge_import` - Bulk knowledge imports

## Next Steps

1. **Set up LangFuse** following the Quick Setup guide
2. **Run some conversations** with your agents to generate traces
3. **Explore the dashboard** to understand your agent behavior
4. **Configure sampling and filtering** for production use
5. **Set up alerts and monitoring** for key metrics

For more advanced features and API usage, see the [LangFuse Documentation](https://langfuse.com/docs).

---

**Need Help?**
- 📖 [LangFuse Documentation](https://langfuse.com/docs)
- 💬 [LangFuse Discord](https://discord.gg/7NXusRtqYU)  
- 🐛 [Report Issues](https://github.com/langfuse/langfuse/issues)
- 📧 [Agent Zero Issues](https://github.com/frdel/agent-zero/issues)