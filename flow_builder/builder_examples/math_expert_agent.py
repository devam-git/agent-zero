import os
import json
from builder import LangflowBuilder

# Example usage for math expert agent
def create_math_expert_agent():
    builder = LangflowBuilder(
        name="Math Expert Agent",
        description="Advanced mathematical problem solver that can handle various types of math problems including algebra, calculus, geometry, statistics, and more. Provides step-by-step solutions with clear explanations."
    )
    
    # Add components with config values that differ from template defaults
    builder.add_component("input", "ChatInput", {
        "input_value": "Solve for x: 2x² + 5x - 3 = 0. Please show all steps and verify the solution.",
        "sender": "User",
        "sender_name": "User",
        "should_store_message": True
    }, position=(100, 300))
    
    builder.add_component("prompt", "Prompt", {
        "template": "You are an expert mathematician and math tutor with deep knowledge across all areas of mathematics. Your task is to solve mathematical problems with clear, step-by-step explanations.\n\nWhen solving any math problem, please provide:\n\n1. **Problem Analysis**: Identify the type of problem and the mathematical concepts involved\n2. **Solution Method**: Explain which approach or formula you'll use and why\n3. **Step-by-Step Solution**: Break down the solution into clear, numbered steps\n4. **Calculations**: Show all mathematical work with proper notation\n5. **Verification**: Check your answer by substituting back or using alternative methods\n6. **Final Answer**: Clearly state the final result with appropriate units if applicable\n7. **Explanation**: Provide a brief explanation of key concepts used\n\nFor complex problems, include:\n- Relevant formulas and theorems\n- Graphs or diagrams when helpful (describe them clearly)\n- Alternative solution methods if applicable\n- Common mistakes to avoid\n\nAlways use proper mathematical notation and be precise with your calculations. If the problem is ambiguous, ask for clarification or state your assumptions."
    }, position=(100, 600))
    
    builder.add_component("llm", "LanguageModel", {
        "provider": "OpenAI",
        "model_name": "gpt-4o-mini",
        "api_key": "",
        "input_value": "",
        "system_message": "",
        "stream": False,
        "temperature": 0.1
    }, position=(450, 300))
    
    builder.add_component("output", "ChatOutput", {
        "sender": "Machine",
        "sender_name": "Math Expert",
        "should_store_message": True
    }, position=(800, 300))
    
    # Connect components
    builder.connect("prompt", "llm", "prompt", "system_message")
    builder.connect("input", "llm", "message", "input_value")
    builder.connect("llm", "output", "text_output", "input_value")
    
    # Add documentation
    builder.add_note("""# Math Expert Agent

This workflow provides expert-level mathematical problem solving with detailed explanations.

## Capabilities:
- **Algebra**: Linear/quadratic equations, systems, polynomials
- **Calculus**: Derivatives, integrals, limits, optimization
- **Geometry**: Area, volume, trigonometry, coordinate geometry
- **Statistics**: Probability, distributions, hypothesis testing
- **Linear Algebra**: Matrices, vectors, eigenvalues
- **Number Theory**: Prime numbers, modular arithmetic
- **Discrete Math**: Combinatorics, graph theory, logic

## Features:
- Step-by-step solutions with clear explanations
- Multiple solution methods when applicable
- Verification of answers
- Proper mathematical notation
- Concept explanations and key insights
- Error checking and common mistake identification

## Usage:
1. Add your API key to the Language Model component
2. Enter your math problem in the Chat Input
3. Run the workflow to get detailed solution

## Example Problems:
- "Solve: 3x² - 12x + 9 = 0"
- "Find the derivative of f(x) = x³sin(2x)"
- "Calculate the area under y = x² from x=0 to x=3"
- "Prove that √2 is irrational"
- "Find the probability of getting exactly 2 heads in 5 coin flips"

## Tips:
- Be specific about what you want (solve, simplify, prove, etc.)
- Include any constraints or conditions
- Specify the domain if relevant
- Ask for graphs or visual aids if helpful""", 
    position=(900, 100), color="green")
    
    return builder.build()

# Generate the workflow
if __name__ == "__main__":
    workflow_json = create_math_expert_agent()
    # Ensure results directory exists
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, "math_expert_agent.json")
    # Validate JSON before saving
    try:
        json_str = json.dumps(workflow_json, indent=2)
        json.loads(json_str)  # Validate
    except Exception as e:
        print(f"ERROR: Generated workflow is not valid JSON: {e}")
        exit(1)
    # Save to file
    with open(output_path, "w") as f:
        f.write(json_str)
    print("Math expert agent workflow generated!")
    print(f"Components: {len(workflow_json['data']['nodes']) - 1}")  # -1 for note
    print(f"Connections: {len(workflow_json['data']['edges'])}")
    print(f"Success! Workflow saved to: {os.path.abspath(output_path)}")
