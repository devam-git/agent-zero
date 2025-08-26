# Dynamic Prompt Guide

⚠️ **CRITICAL**: Use `input_types: ["Message"]` for all dynamic prompt fields.

## Quick Start

```python
# Create dynamic prompt with variables
builder.add_dynamic_prompt("prompt", "Analyze: {user_text}", {
    "user_text": {"input_types": ["Message"], "required": True}
})

# Connect input → prompt → llm  
builder.connect("input", "prompt")  # message → user_text
builder.connect("prompt", "llm")    # prompt → input_value
```

## Keyword Style (NEW)

```python
builder.add_dynamic_prompt(
    id="prompt",
    template="You are a {role}. Analyze: {user_text}",
    fields={
        "user_text": {"input_types": ["Message"], "required": True},
        "role": {"options": ["teacher", "expert"], "default_value": "teacher"}
    },
    x=400, y=200
)
```

## Field Options

```python
fields = {
    "field_name": {
        "input_types": ["Message"],     # REQUIRED for connections
        "display_name": "User Label",
        "required": True,
        "multiline": True,
        "options": ["opt1", "opt2"],    # Creates dropdown
        "info": "Help tooltip",
        "placeholder": "Example text"
    }
}
```

## Connection Patterns

```
ChatInput.message → Prompt.{field} → LanguageModel.input_value → ChatOutput.input_value
```

## Helper Method

```python
# Use for guaranteed compatibility
field_config = LangflowBuilder.create_compatible_field_config(
    display_name="User Input",
        required=True
    )
```

## Common Mistakes

❌ Wrong: `"input_types": ["Message", "Text"]` - breaks connections  
✅ Correct: `"input_types": ["Message"]` - works with Language Models

❌ Wrong: Assuming field names = output handles  
✅ Correct: Check component definitions for actual output names

Variables auto-extracted from `{variable}` patterns in template.
