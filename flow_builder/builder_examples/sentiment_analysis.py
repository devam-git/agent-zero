import os
import json
from builder import LangflowBuilder

# Example usage for sentiment analyzer
def create_sentiment_analyzer():
    builder = LangflowBuilder(
        name="Sentiment Analyzer",
        description="Comprehensive sentiment analysis workflow that classifies text as positive, negative, or neutral with detailed analysis including confidence scores and key indicators."
    )
    
    # Add components with config values that differ from template defaults
    builder.add_component("input", "ChatInput", {
        "input_value": "I absolutely love this new product! It has exceeded all my expectations and made my life so much easier.",
        "sender": "User",
        "sender_name": "User",
        "should_store_message": True
    }, position=(100, 300))
    
    builder.add_component("prompt", "Prompt", {
        "template": "You are a professional sentiment analysis expert. Your task is to analyze the sentiment of the given text and provide a comprehensive analysis.\n\nPlease analyze the sentiment of the text and respond with:\n\n1. **Overall Sentiment**: Classify as Positive, Negative, or Neutral\n2. **Confidence Score**: Rate your confidence from 1-10 (10 being most confident)\n3. **Key Indicators**: List the specific words, phrases, or expressions that led to your sentiment classification\n4. **Emotional Tone**: Describe the emotional tone (e.g., excited, frustrated, content, angry, happy, etc.)\n5. **Brief Explanation**: Provide a 1-2 sentence explanation of your analysis\n\nFormat your response clearly with these sections. Be objective and thorough in your analysis."
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
        "sender_name": "Sentiment Analyzer",
        "should_store_message": True
    }, position=(800, 300))
    
    # Connect components
    builder.connect("prompt", "llm", "prompt", "system_message")
    builder.connect("input", "llm", "message", "input_value")
    builder.connect("llm", "output", "text_output", "input_value")
    
    # Add documentation
    builder.add_note("""# Sentiment Analyzer

This workflow performs comprehensive sentiment analysis on text input.

## How it works:
1. **Input**: Enter any text you want to analyze
2. **Analysis**: The AI analyzes sentiment with detailed breakdown
3. **Output**: Get sentiment classification, confidence score, and explanation

## Features:
- Overall sentiment classification (Positive/Negative/Neutral)
- Confidence scoring (1-10 scale)
- Key indicator identification
- Emotional tone analysis
- Detailed explanations

## Usage:
1. Add your API key to the Language Model component
2. Enter text in the Chat Input
3. Run the workflow to get detailed sentiment analysis

## Examples:
- Product reviews
- Customer feedback
- Social media posts
- Survey responses
- Support tickets""", 
    position=(900, 100), color="blue")
    
    return builder.build()

# Generate the workflow
if __name__ == "__main__":
    workflow_json = create_sentiment_analyzer()
    # Ensure results directory exists
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, "sentiment_analyzer.json")
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
    print("Sentiment analyzer workflow generated!")
    print(f"Components: {len(workflow_json['data']['nodes']) - 1}")  # -1 for note
    print(f"Connections: {len(workflow_json['data']['edges'])}")
    print(f"Success! Workflow saved to: {os.path.abspath(output_path)}")