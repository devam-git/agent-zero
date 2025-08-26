# Hierarchical Agent Workflow Documentation

## Overview
This document explains how to create hierarchical agent workflows in Langflow where a manager agent orchestrates multiple sub-agents that function as specialized tools.

## Architecture Pattern

### Core Components
1. **Manager Agent** - Central coordinator that receives user requests and delegates tasks
2. **Sub-Agent 1** - Specialized agent configured as a tool (e.g., Research Specialist)
3. **Sub-Agent 2** - Another specialized agent configured as a tool (e.g., Content Creator)
4. **Input/Output Components** - User interface elements

### Connection Pattern
```
ChatInput → Manager Agent → ChatOutput
            ↑
    Sub-Agent 1 (as tool)
            ↑
    Sub-Agent 2 (as tool)
```

## Key Configuration Details

### Agent as Tool Setup
- Sub-agents must be connected using `component_as_tool` output
- Connection pattern: `sub_agent.connect("manager_agent", "component_as_tool", "tools")`
- Each sub-agent needs specific `system_prompt` defining its specialty

### Manager Agent Configuration
- Should have comprehensive `system_prompt` explaining available tools
- Must include instructions on when to use each sub-agent
- Can handle multiple tool connections simultaneously

## Implementation Example

### Basic Hierarchical Structure
```python
from builder import LangflowBuilder

def create_hierarchical_agent_workflow():
    builder = LangflowBuilder(
        name="Hierarchical Agent Workflow",
        description="Manager agent with research and content creation sub-agents"
    )
    
    # Sub-Agent 1: Research Specialist
    builder.add_component("research_agent", "Agent", {
        "system_prompt": """You are a Research Specialist agent. Your role is to:
        - Conduct thorough research on given topics
        - Find credible sources and data
        - Provide comprehensive research summaries
        - Focus on accuracy and factual information
        
        When called by the manager agent, provide detailed research findings.""",
        "agent_type": "openai-functions",
        "max_iterations": 5
    })
    
    # Sub-Agent 2: Content Creator
    builder.add_component("content_agent", "Agent", {
        "system_prompt": """You are a Content Creator agent. Your role is to:
        - Create engaging written content
        - Transform research into readable formats
        - Write articles, summaries, and reports
        - Focus on clarity and audience engagement
        
        When called by the manager agent, create polished content.""",
        "agent_type": "openai-functions", 
        "max_iterations": 5
    })
    
    # Manager Agent
    builder.add_component("manager_agent", "Agent", {
        "system_prompt": """You are a Manager Agent that coordinates research and content creation tasks.

Available Tools:
1. Research Specialist - Use for gathering information, finding sources, conducting research
2. Content Creator - Use for writing, editing, and creating polished content

Your process:
1. Analyze the user's request
2. Determine what information needs to be researched
3. Use the Research Specialist to gather relevant information
4. Use the Content Creator to transform research into final deliverable
5. Coordinate between agents as needed
6. Provide the final result to the user

Always explain your process and reasoning to the user.""",
        "agent_type": "openai-functions",
        "max_iterations": 10
    })
    
    # Input/Output Components
    builder.add_component("input", "ChatInput", {
        "input_value": "Research sustainable energy technologies and create a comprehensive article about the top 5 most promising solutions for 2024.",
        "sender": "User",
        "sender_name": "User"
    })
    
    builder.add_component("output", "ChatOutput", {
        "sender": "Machine", 
        "sender_name": "Manager Agent"
    })
    
    # Connect Sub-Agents as Tools to Manager
    builder.connect("research_agent", "manager_agent", "component_as_tool", "tools")
    builder.connect("content_agent", "manager_agent", "component_as_tool", "tools")
    
    # Connect Main Flow
    builder.connect("input", "manager_agent", "message", "input_value")
    builder.connect("manager_agent", "output", "response", "input_value")
    
    return builder.build()
```

## Advanced Patterns

### Adding External Tools to Sub-Agents
Sub-agents can also have their own tools:

```python
# Add web search to research agent
builder.add_component("web_search", "WebSearch")
builder.connect("web_search", "research_agent", "component_as_tool", "tools")

# Add calculator to research agent  
builder.add_component("calculator", "Calculator")
builder.connect("calculator", "research_agent", "component_as_tool", "tools")
```

### Multi-Level Hierarchy
Create deeper hierarchies by making agents that are both tools and managers:

```python
# Level 1: Top Manager
# Level 2: Department Managers (each with specialized sub-agents)
# Level 3: Specialist Agents
```

## Best Practices

### System Prompt Design
1. **Clear Role Definition** - Each agent should have a specific, well-defined purpose
2. **Tool Usage Instructions** - Manager agents need explicit instructions on when to use each tool
3. **Communication Protocols** - Define how agents should format their responses
4. **Error Handling** - Include fallback behaviors

### Agent Specialization
1. **Research Agents** - Information gathering, fact-checking, source validation
2. **Analysis Agents** - Data processing, pattern recognition, insights generation
3. **Creative Agents** - Content creation, writing, ideation
4. **Technical Agents** - Code generation, calculations, technical tasks

### Performance Optimization
1. **Iteration Limits** - Set appropriate `max_iterations` for each agent
2. **Temperature Settings** - Lower for research agents, higher for creative agents
3. **Tool Selection** - Only give agents the tools they actually need

## Common Use Cases

### Content Production Pipeline
- Research Agent → Analysis Agent → Writing Agent → Editor Agent

### Customer Service Hierarchy  
- Triage Agent → Specialist Agents (Billing, Technical, Sales)

### Data Processing Workflow
- Ingestion Agent → Processing Agent → Analysis Agent → Reporting Agent

### Development Team Simulation
- Project Manager Agent → Developer Agents → QA Agent → Documentation Agent

## Troubleshooting

### Common Issues
1. **Tool Connection Errors** - Ensure using `component_as_tool` output type
2. **Infinite Loops** - Set reasonable `max_iterations` limits
3. **Context Loss** - Manager agents need comprehensive system prompts
4. **Tool Selection** - Provide clear criteria for when to use each tool

### Debugging Tips
1. Test each sub-agent individually first
2. Verify tool connections with simple tasks
3. Monitor token usage with complex hierarchies
4. Use detailed logging in system prompts

## Example Implementations
See `/a0/flow_builder/builder_examples/` directory for complete working examples of hierarchical agent patterns.
