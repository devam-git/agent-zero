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

### 3. File Processing: Document Analysis Workflow

```python
# Document analysis workflow with file loading and processing
builder = LangflowBuilder("Document Analysis System", "Load and analyze documents with AI")

# File loader component
builder.add_component("doc_loader", "File", {
    "path": [],  # Files will be uploaded via UI
    "concurrency_multithreading": 2,  # Process 2 files in parallel
    "separator": "\n\n---\n\n"  # Separate multiple files clearly
})

# User instructions input
builder.add_component("user_input", "ChatInput", {
    "input_value": "Summarize key insights",
    "sender_name": "User"
})

# Analysis prompt with file content
analysis_template = """Analyze these documents and {instructions}:

Document Content:
{document_content}

Provide structured analysis with key findings."""

builder.add_dynamic_prompt("analysis_prompt", analysis_template, {
    "document_content": builder.create_compatible_field_config("Document Content", required=True, multiline=True),
    "instructions": builder.create_compatible_field_config("Analysis Instructions", required=True)
})

# LLM for analysis
builder.add_component("analyzer_llm", "OpenAIModel", {
    "model_name": "gpt-4o-mini",
    "api_key": "",  # Add your API key
    "temperature": 0.2,
    "max_tokens": 2000
})

# Output component
builder.add_component("analysis_output", "ChatOutput", {
    "sender_name": "Document Analyzer"
})

# Connections: File → Prompt → LLM → Output
builder.connect("doc_loader", "analysis_prompt", "message", "document_content")
builder.connect("user_input", "analysis_prompt", "message", "instructions")
builder.connect("analysis_prompt", "analyzer_llm")
builder.connect("analyzer_llm", "analysis_output")
```

**Key Patterns Demonstrated:**
- **Sequential Processing**: Linear workflow with step-by-step dependencies
- **Parallel Processing**: Multiple analysis paths that converge for synthesis
- **File Loading**: Using File component to load and process documents
- **Dynamic Prompts**: Advanced field configurations with dropdowns and validation
- **Mixed LLM Strategy**: Different models for different complexity levels (GPT-4o for planning/synthesis, GPT-4o-mini for analysis)
- **Flexible Connections**: Auto-detection and explicit handle specification
- **Helper Methods**: `create_compatible_field_config()` for guaranteed compatibility