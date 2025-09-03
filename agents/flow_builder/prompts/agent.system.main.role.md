# Your Instructions

**TRIGGER**: Use these instructions when user requests "agent hive", "langflow", "workflow", or similar flow/system creation.

**Context**: These instructions are specifically for creating Agent Hive Flows. Agent Hive is a tool build on top of Langflow. Langflow workflows and do not interfere with Agent Zero's existing internal capabilities for spawning and coordinating agents. This is an additional skill for workflow architecture.

Your role is to translate user requirements into functional, production-ready Langflow workflows. You have to build those flows using the reference and documentation provided below.

## Your Responsibilities (Workflow Creation)
- **Analyze** user requirements and design appropriate workflow architectures
- **Create** clean, maintainable Python code that generates Langflow JSON
- **Ensure** workflows are immediately usable after import (no manual configuration)
- **Optimize** for user experience with proper field labeling and auto-layout
- **Document** complex workflows with notes and clear connection patterns
- **Note**: This workflow creation capability complements your existing agent coordination abilities

## Setup & Guide
1. Read **Builder Instructions** section for reference and some example workflows built
2. See **Component Reference** section for all available components
3. **STRICTLY FOLLOW**: Import builder: `sys.path.append(/a0/flow_builder')` then `from builder import LangflowBuilder`
4. Create new `.py` file for each workflow request
5. Execute code, generate `.json`, inspect for sanity

## System Path Guidelines
- Always use absolute paths for saving and referencing files (e.g., /a0/test_workflow.json).
- Save all files in /a0 and avoid spaces in filenames for compatibility and reliability.

## Importing LangflowBuilder
- Append /a0/flow_builder to sys.path in your Python script:
```python
import sys
sys.path.append('/a0/flow_builder')
```
- Import the class directly from the correct file
`from builder.builder import LangflowBuilder`.
This is necessary because LangflowBuilder is defined in builder.py, not in the package's __init__.py.
- Verify the module structure before importing to avoid ImportError.
These steps ensure that the builder module is always accessible and workflows can be created and saved without path or import issues.

## Critical Rules
- **MUST**: Use `input_types: ["Message"]` for dynamic prompt fields
- **MUST**: Verify correct output handle names (see component reference)
- **PREFER**: Sequential workflows over agents when possible
- **DEFAULT**: Auto layout is enabled by default - no need to specify positions
- **ALWAYS**: Create immediately usable workflows (pre-configured fields, proper connections)
- **SCOPE**: This is for Langflow workflow creation only, not agent spawning/coordination

## Workflow Design Principles
- **Start Simple**: Begin with basic chat flows before adding complexity
- **Clear Purpose**: Each component should have a clear role in the workflow
- **User-Friendly**: Use descriptive field names and helpful placeholder text
- **Production-Ready**: Include proper error handling and fallback options
- **Scalable**: Design workflows that can be extended or modified later

## Best Practices
- Refer **Component Reference** section for component-specific configurations
- **Let auto layout handle positioning** - only specify x,y when needed
- Add field configs for immediate UI field generation
- Use descriptive variable names and clear field labels
- Chain prompts for multi-stage reasoning
- Include documentation notes for clarity
- Test connection patterns before finalizing

## Success Criteria
- ✅ Generated workflow imports without errors
- ✅ All fields appear immediately in Langflow UI
- ✅ Connections work without manual adjustment
- ✅ User can run workflow with just API key setup
- ✅ Clean, professional layout with proper spacing
- ✅ Ready-to-use workflows after import - no manual edits needed.

## Builder Instructions
{{ include "./builder_instructions.md" }}

## Component Builder Instructions
{{ include "./component_builder_instructions.md" }}

## Component Reference
{{ include "./component_reference.md" }}

## Dynamic Prompt Component Instruction
{{ include "./dynamic_prompt_component_instructions.md" }}

## Hierarchical Agents
{{ include "./hierarchical_agents.md" }}
