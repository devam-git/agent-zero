# Langflow Builder Reference

**CRITICAL**: 
1. Dynamic prompt fields MUST use `input_types: ["Message"]` for connections.
2. There can be only one Chat Input and Chat Output Component.
3. Always prefer Chat input/output over Text Input/Output.

## Core Code

```python
from builder import LangflowBuilder

# Initialize (auto layout enabled by default)
builder = LangflowBuilder("Workflow Name", "Description")
# OR with kwargs: LangflowBuilder(workflow_name="Test", spacing=800)
# Disable auto layout: LangflowBuilder("Test", auto_position=False)

# Add components (positions auto-calculated unless specified)
builder.add_component("input", "ChatInput", {"input_value": "Hello"})
# OR with kwargs: builder.add_component(id="input", component_type="ChatInput", x=100, y=200)

# Add dynamic prompts
builder.add_dynamic_prompt("prompt", "Analyze: {user_text}", {
    "user_text": {"input_types": ["Message"], "required": True}
})

# Connect components  
builder.connect("input", "prompt")  # Auto-detects handles
# OR explicit: builder.connect("input", "prompt", "message", "user_text")
# OR with kwargs: builder.connect(source="input", target="prompt")

# Build workflow
workflow = builder.build()


# Save workflow JSON to file
import json
with open("workflow.json", "w") as f:
    json.dump(workflow, f, indent=2)

# OR save with custom filename
builder.save("custom_workflow.json")

```

## Component Reference

📖 **See "Component Reference" section for complete component documentation** including:
- All available component types and configurations
- Input/output handles and types  
- Connection patterns and examples
- Best practices for each component

## Complex Workflow Examples

### 1. Sequential Processing: Support Ticket Analysis

```python
# Sequential workflow for support ticket analysis and email drafting
builder = LangflowBuilder("Support Ticket Email Workflow", "Analyze tickets and draft replies")

# Input: Support ticket
builder.add_component("ticket_input", "ChatInput", {
    "input_value": "Customer complaint about login issues...",
    "sender_name": "Support Agent"
})

# Dynamic prompt: Analyze ticket
analyze_template = """Analyze this support ticket and extract key issues:
{ticket_text}

Provide structured summary with sentiment and priority."""

builder.add_dynamic_prompt("ticket_analyzer", analyze_template, {
    "ticket_text": builder.create_compatible_field_config("Ticket Text", required=True)
})

# LLM for analysis
builder.add_component("analysis_llm", "LanguageModel", {
    "model_name": "gpt-4o-mini",
    "temperature": 0.2
})

# Dynamic prompt: Draft email reply
email_template = """Based on this ticket analysis, draft a professional reply:
{analysis_result}

Include empathy, solution steps, and next actions."""

builder.add_dynamic_prompt("email_drafter", email_template, {
    "analysis_result": builder.create_compatible_field_config("Analysis Result", required=True)
})

# LLM for email drafting
builder.add_component("email_llm", "LanguageModel", {
    "model_name": "gpt-4o-mini", 
    "temperature": 0.3
})

# Output: Draft email
builder.add_component("email_output", "ChatOutput", {
    "sender_name": "Email Draft"
})

# Sequential connections: Input → Analysis → Email → Output
builder.connect("ticket_input", "ticket_analyzer", "message", "ticket_text")
builder.connect("ticket_analyzer", "analysis_llm")
builder.connect("analysis_llm", "email_drafter", "text_output", "analysis_result") 
builder.connect("email_drafter", "email_llm")
builder.connect("email_llm", "email_output")
```

### 2. Parallel Processing: Multi-Agent Research Pipeline

```python
# Complex research workflow with parallel analysis and synthesis
builder = LangflowBuilder(
    workflow_name="Research Analysis Pipeline",
    workflow_description="Multi-agent research with parallel processing",
    spacing=400
)

# Inputs
builder.add_component("topic_input", "ChatInput", {
    "input_value": "AI impact on education",
    "sender_name": "Researcher"
})

builder.add_component("requirements_input", "ChatInput", {
    "input_value": "Focus on pedagogy, outcomes, ethics",
    "sender_name": "Research Director"
})

# Research planner with advanced dynamic prompt
planning_template = """Create research plan for: {research_topic}
Requirements: {research_requirements}
Depth: {analysis_depth}

Provide structured plan with questions, methodology, deliverables."""

builder.add_dynamic_prompt("research_planner", planning_template, {
    "research_topic": {"display_name": "Topic", "required": True, "multiline": True},
    "research_requirements": {"display_name": "Requirements", "required": True, "multiline": True},
    "analysis_depth": {
        "display_name": "Analysis Depth",
        "options": ["Surface-level", "Moderate", "Deep-dive", "Comprehensive"],
        "default_value": "Comprehensive"
    }
})

builder.add_component("planner_llm", "LanguageModel", {
    "model_name": "gpt-4o",
    "temperature": 0.3
})

# Parallel analysis agents
technical_template = """Technical analysis of: {research_plan}
Style: {analysis_style}

Focus on implementation, infrastructure, tech challenges."""

builder.add_dynamic_prompt("technical_analyst", technical_template, {
    "research_plan": {"display_name": "Research Plan", "required": True, "multiline": True},
    "analysis_style": {
        "options": ["Practical", "Theoretical", "Hybrid"],
        "default_value": "Hybrid"
    }
})

social_template = """Social impact analysis of: {research_plan}
Perspective: {perspective}

Cover stakeholders, benefits, risks, community impact."""

builder.add_dynamic_prompt("social_analyst", social_template, {
    "research_plan": {"display_name": "Research Plan", "required": True, "multiline": True},
    "perspective": {
        "options": ["Conservative", "Progressive", "Balanced", "Critical"],
        "default_value": "Balanced"
    }
})

# Parallel LLMs
builder.add_component("technical_llm", "LanguageModel", {"model_name": "gpt-4o-mini"})
builder.add_component("social_llm", "LanguageModel", {"model_name": "gpt-4o-mini"})

# Synthesis agent
synthesis_template = """Synthesize research findings:
Technical: {technical_findings}
Social: {social_findings}

Create unified analysis with themes, conclusions, recommendations."""

builder.add_dynamic_prompt("synthesis_agent", synthesis_template, {
    "technical_findings": builder.create_compatible_field_config("Technical Analysis"),
    "social_findings": builder.create_compatible_field_config("Social Analysis")
})

builder.add_component("synthesis_llm", "LanguageModel", {"model_name": "gpt-4o"})
builder.add_component("final_output", "ChatOutput", {"sender_name": "Research System"})

# Connection flow
# Inputs to planner
builder.connect("topic_input", "research_planner", "message", "research_topic")
builder.connect("requirements_input", "research_planner", "message", "research_requirements")
builder.connect("research_planner", "planner_llm")

# Parallel distribution to analysts
builder.connect("planner_llm", "technical_analyst", "text_output", "research_plan")
builder.connect("planner_llm", "social_analyst", "text_output", "research_plan")

# Parallel analysis
builder.connect("technical_analyst", "technical_llm")
builder.connect("social_analyst", "social_llm")

# Synthesis convergence
builder.connect("technical_llm", "synthesis_agent", "text_output", "technical_findings")
builder.connect("social_llm", "synthesis_agent", "text_output", "social_findings")
builder.connect("synthesis_agent", "synthesis_llm")
builder.connect("synthesis_llm", "final_output")
```

**Key Patterns Demonstrated:**
- **Sequential Processing**: Linear workflow with step-by-step dependencies
- **Parallel Processing**: Multiple analysis paths that converge for synthesis
- **Dynamic Prompts**: Advanced field configurations with dropdowns and validation
- **Mixed LLM Strategy**: Different models for different complexity levels (GPT-4o for planning/synthesis, GPT-4o-mini for analysis)
- **Flexible Connections**: Auto-detection and explicit handle specification
- **Helper Methods**: `create_compatible_field_config()` for guaranteed compatibility

## Core Methods

### `LangflowBuilder(name, description, **kwargs)`
- **Args**: `name` (str), `description` (str)
- **Kwargs**: `workflow_name`, `auto_position=True` (default), `spacing=650`

### `add_component(id, type, config, position, **kwargs)`
- **Args**: `id` (str), `type` (str), `config` (dict), `position` (tuple, optional)
- **Kwargs**: `component_type`, `x`, `y`, `pos`, direct config fields
- **Auto Layout**: Position calculated automatically if not specified

### `add_dynamic_prompt(id, template, field_configs, position, **kwargs)`
- **Args**: `id` (str), `template` (str), `field_configs` (dict), `position` (tuple, optional)  
- **Kwargs**: `prompt_template`, `fields`, `x`, `y`, `pos`
- **Auto Layout**: Position calculated automatically if not specified

### `connect(from_id, to_id, from_output, to_input, **kwargs)`
- **Args**: `from_id` (str), `to_id` (str), `from_output` (str), `to_input` (str)
- **Kwargs**: `source`, `target`, `source_output`, `target_input`

### `add_note(content, position, color, **kwargs)`
- **Args**: `content` (str), `position` (tuple, optional), `color` (str)
- **Kwargs**: `text`, `note_text`, `x`, `y`, `pos`, `note_color`
- **Auto Layout**: Position calculated automatically if not specified

### `build() -> dict`
Returns complete Langflow JSON workflow.

## Auto Layout (Default Behavior)

The builder automatically positions components left-to-right with smart spacing:
- **Default**: `auto_position=True`, `spacing=650`
- **Components**: Positioned horizontally at y=300
- **Notes**: Positioned at top (y=50) to avoid overlap
- **Override**: Set explicit `x`, `y` coordinates to override auto-positioning
- **Disable**: Set `auto_position=False` for manual positioning only

## Field Config Options

```python
field_configs = {
    "variable_name": {
        "input_types": ["Message"],  # CRITICAL
        "display_name": "User Label",
        "required": True,
        "multiline": True,
        "options": ["opt1", "opt2"],  # For dropdowns
        "info": "Help text",
        "placeholder": "Example..."
    }
}
```

## Helper Methods

### `create_compatible_field_config(display_name, **kwargs)`
Creates guaranteed-compatible field configurations:
```python
field_config = LangflowBuilder.create_compatible_field_config(
    display_name="User Input",
    info="Help text",
    required=True,
    options=["opt1", "opt2"]  # Optional dropdown
)
```

## Keyword Arguments

All methods support kwargs for cleaner code:
- Use `id`/`name` instead of positional logical_id
- Use `component_type` instead of positional type  
- Use `x`, `y` for positioning (overrides auto layout)
- Use `source`/`target` for connections
- Pass config fields directly as kwargs

## Connection Patterns

```
ChatInput.message → Prompt.{field} → LanguageModel.input_value → ChatOutput.input_value
```

📖 **For detailed component specifications, see "Component Reference" section.**
