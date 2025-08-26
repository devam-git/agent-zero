🧮 Calculator Tool Template Features:
1. Tool-Specific Properties

Category: "tools" - Identifies it as a tool component
Tool Mode: tool_mode: True in the input field
Base Classes: ["Data"] - Returns structured data
Icon: "calculator" - Calculator icon

2. Input Configuration

Expression Input:

Type: MessageTextInput
Tool-compatible: tool_mode: True
Example: "4*4*(33/22)+12-20"
Trace enabled for debugging


3. Output Structure

Name: "result"
Type: "Data"
Method: "evaluate_expression"
Tool Compatible: tool_mode: True

4. Key Differences from Chat Components

Base Classes: ["Data"] instead of ["Message"]
Output Type: "Data" for structured results
Tool Mode: Enabled for agent integration
Category: "tools" for organization

5. Connection Type
When connecting to agents:

Output: "Data" type
Connection: Uses "other" type (like ChatOutput)
Agent Input: "Tool" type in tools array

🔧 Usage in Builder:
python# Add to your component templates
NEW_COMPONENT_TEMPLATES["Calculator"] = CALCULATOR_TEMPLATE

# Use in workflow with agent
builder.add_component("calc", "Calculator", {
    "expression": "2+2"  # Default or placeholder
})

builder.add_component("agent", "Agent", {
    "system_prompt": "You can use calculator for math."
})

# Connect calculator as tool to agent
builder.connect("calc", "agent", "result", "tools")
The calculator will appear as an available tool that agents can use to perform mathematical calculations!