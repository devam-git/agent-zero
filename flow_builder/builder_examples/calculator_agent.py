from builder import LangflowBuilder
import json
def create_calculator_agent():
    """
    Creates an AI agent with calculator capabilities for mathematical problem solving.
    
    Returns:
        dict: Complete Langflow workflow configuration
    """
    builder = LangflowBuilder(
        name="Calculator Agent",
        description="AI agent with calculator tool for solving mathematical problems step-by-step."
    )
    
    # Add calculator tool
    builder.add_component("calculator", "Calculator")
    
    # Add agent with mathematical problem-solving instructions
    builder.add_component("agent", "Agent", {
        "system_prompt": """You are a helpful mathematical assistant with access to a calculator tool.

When users ask mathematical questions:
1. Use the calculator tool for all arithmetic operations and complex calculations
2. Break down complex problems into step-by-step solutions
3. Show your work clearly and explain each step
4. Verify your calculations using the calculator
5. Provide the final answer clearly

You can handle:
- Basic arithmetic (addition, subtraction, multiplication, division)
- Advanced mathematics (powers, roots, trigonometry)
- Complex expressions and multi-step problems
- Percentage calculations
- Algebraic expressions

Always use the calculator tool rather than doing mental math to ensure accuracy.""",
    
    })
    
    # Add input component
    builder.add_component("input", "ChatInput", {
        "input_value": "Calculate: What is 15% of 250 plus the square root of 144?",
        "sender": "User",
        "sender_name": "User",
        "should_store_message": True
    })
    
    # Add output component
    builder.add_component("output", "ChatOutput", {
        "sender": "Machine",
        "sender_name": "Calculator Agent",
        "should_store_message": True
    })
    
    # Connect calculator tool to agent
    builder.connect("calculator", "agent", "component_as_tool", "tools")
    
    # Connect the main flow: input -> agent -> output
    builder.connect("input", "agent", "message", "input_value")
    builder.connect("agent", "output", "response", "input_value")
    
    # Add helpful documentation
    builder.add_note("""
# Calculator Agent

## Capabilities
- Arithmetic operations (+, -, *, /)
- Advanced math (powers, roots, trig)
- Multi-step problem solving
- Percentage calculations
- Complex expressions

## Example Queries
- "What is 15% of 250?"
- "Calculate (25 + 30) * 4 / 2"
- "Find the area of a circle with radius 7"
- "What is 2^10 - 500?"

The agent will use the calculator tool to ensure accurate results!
""", position=(750, 100))
    
    return builder.build()

# Create and return the workflow
if __name__ == "__main__":
    workflow = create_calculator_agent()
    json_workflow = json.dumps(workflow, indent=4)
    with open("calculator_agent.json", "w") as f:
        f.write(json_workflow)
    print("Calculator Agent workflow created successfully!")
    print(f"Components: {len(workflow['data']['nodes'])}")
    print(f"Connections: {len(workflow['data']['edges'])}")
