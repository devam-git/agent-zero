#!/usr/bin/env python3
"""
chat_input_to_template_examples.py

Complete examples demonstrating how ChatInput components can feed their output
directly into dynamic prompt template variables using the enhanced LangflowBuilder.

This file creates multiple workflow examples showing:
1. Single ChatInput → Single Template Variable
2. Multiple ChatInputs → Multiple Template Variables  
3. Complex Expert Assistant with mixed input types
4. Real-world use cases and patterns

Prerequisites:
- Enhanced LangflowBuilder (builder.py)
- Updated component templates (component_templates.py)
- Python 3.7+

Usage:
    python chat_input_to_template_examples.py

Author: AI Assistant
Date: 2024
"""

import json
import os
from typing import Dict, Any
import sys

# Import the enhanced LangflowBuilder
try:
    from builder import LangflowBuilder
except ImportError:
    print("❌ Error: Enhanced LangflowBuilder not found!")
    print("Please ensure 'builder.py' with dynamic prompt support is in the same directory.")
    sys.exit(1)

def create_expert_consultant_workflow():
    """
    Create an expert consultant workflow where user questions flow into a sophisticated
    dynamic prompt template with multiple configuration options.
    
    Pattern: ChatInput.message → Prompt.user_question (+ manual config fields)
    """
    print("🔨 Creating Expert Consultant Workflow...")
    
    builder = LangflowBuilder(
        name="Expert Consultant Assistant",
        description="AI expert consultant that adapts its expertise and response style based on user questions and preferences"
    )
    
    # User Input Component
    builder.add_component("user_input", "ChatInput", {
        "input_value": "What are the main challenges facing renewable energy adoption in developing countries?",
        "sender": "User",
        "sender_name": "User",
        "should_store_message": True
    }, position=(100, 300))
    
    # Expert Consultant Prompt Template
    prompt_template = """You are a world-renowned {expert_field} with {experience_years} years of experience and {expertise_level} expertise.

EXPERTISE CONTEXT:
- Field: {expert_field}
- Experience: {experience_years} years
- Level: {expertise_level}
- Specialization: {specialization}

USER PROFILE:
- Background: {user_background}
- Knowledge Level: {user_knowledge_level}

USER QUESTION:
{user_question}

RESPONSE REQUIREMENTS:
- Style: {response_style}
- Detail Level: {detail_level}
- Include Examples: {include_examples}
- Tone: {response_tone}

Please provide a comprehensive response that:
1. Demonstrates your expertise in {expert_field}
2. Is appropriate for someone with {user_knowledge_level} knowledge
3. Uses a {response_style} approach with {detail_level} detail
4. Maintains a {response_tone} tone throughout

Your expert analysis:"""
    
    # Configure dynamic fields with rich options
    field_configs = {
        "user_question": {
            "display_name": "User Question",
            "info": "The main question from the user (automatically populated from ChatInput)",
            "placeholder": "User's question will appear here automatically when connected to ChatInput...",
            "required": True,
            "multiline": True
        },
        "expert_field": {
            "display_name": "Expert Field",
            "info": "What field should the AI expert specialize in?",
            "options": [
                "renewable energy", "environmental science", "sustainable development",
                "climate policy", "economics", "technology innovation", 
                "public policy", "international development", "engineering",
                "business strategy", "data science", "artificial intelligence"
            ],
            "default_value": "renewable energy"
        },
        "experience_years": {
            "display_name": "Years of Experience",
            "info": "How many years of experience should the expert have?",
            "options": ["5", "10", "15", "20", "25", "30+"],
            "default_value": "15"
        },
        "expertise_level": {
            "display_name": "Expertise Level",
            "info": "What level of expertise should the AI demonstrate?",
            "options": ["senior", "expert", "world-class", "pioneering", "legendary"],
            "default_value": "expert"
        },
        "specialization": {
            "display_name": "Specialization",
            "info": "Specific area of specialization within the expert field",
            "placeholder": "e.g., solar energy systems, policy implementation, market analysis",
            "multiline": False
        },
        "user_background": {
            "display_name": "User Background",
            "info": "Background information about the user asking the question",
            "placeholder": "e.g., graduate student, policy maker, business executive, researcher",
            "default_value": "interested professional"
        },
        "user_knowledge_level": {
            "display_name": "User Knowledge Level",
            "info": "User's knowledge level in the topic area",
            "options": ["beginner", "intermediate", "advanced", "expert"],
            "default_value": "intermediate"
        },
        "response_style": {
            "display_name": "Response Style",
            "info": "How should the response be structured and presented?",
            "options": ["analytical", "consultative", "educational", "strategic", "comprehensive"],
            "default_value": "consultative"
        },
        "detail_level": {
            "display_name": "Detail Level",
            "info": "How much detail should be included in the response?",
            "options": ["overview", "moderate", "detailed", "comprehensive", "exhaustive"],
            "default_value": "detailed"
        },
        "include_examples": {
            "display_name": "Include Examples",
            "info": "Should the response include specific examples and case studies?",
            "options": ["yes", "no", "when relevant"],
            "default_value": "yes"
        },
        "response_tone": {
            "display_name": "Response Tone",
            "info": "What tone should the expert use in their response?",
            "options": ["professional", "authoritative", "collaborative", "educational", "friendly"],
            "default_value": "professional"
        }
    }
    
    builder.add_dynamic_prompt("expert_prompt", prompt_template, field_configs, position=(500, 150))
    
    # Language Model
    builder.add_component("llm", "LanguageModel", {
        "provider": "OpenAI",
        "model_name": "gpt-4o",
        "temperature": 0.7,
        "api_key": ""
    }, position=(950, 300))
    
    # Output
    builder.add_component("output", "ChatOutput", {
        "sender": "Machine",
        "sender_name": "Expert Consultant",
        "should_store_message": True
    }, position=(1400, 300))
    
    # 🔗 KEY CONNECTION: ChatInput message flows into user_question template variable
    builder.connect("user_input", "expert_prompt", "message", "user_question")
    builder.connect("expert_prompt", "llm", "prompt", "input_value")
    builder.connect("llm", "output", "text_output", "input_value")
    
    # Documentation
    builder.add_note("""# Expert Consultant Assistant

## 🔗 Key Connection Pattern:
**ChatInput.message → Prompt.user_question**

## How It Works:
1. User types question in ChatInput
2. Question automatically flows into {user_question} template variable
3. AI combines user question with expert configuration
4. Language model processes the complete expert prompt
5. Professional consultant response delivered

## Dynamic Fields:
- ✅ **user_question**: Connected from ChatInput (automatic)
- ⚙️ **expert_field**: Manual dropdown selection
- ⚙️ **experience_years**: Manual dropdown selection
- ⚙️ **expertise_level**: Manual dropdown selection
- ⚙️ **specialization**: Manual text input
- ⚙️ **user_background**: Manual text input
- ⚙️ **user_knowledge_level**: Manual dropdown selection
- ⚙️ **response_style**: Manual dropdown selection
- ⚙️ **detail_level**: Manual dropdown selection
- ⚙️ **include_examples**: Manual dropdown selection
- ⚙️ **response_tone**: Manual dropdown selection

## Benefits:
- User input drives the conversation
- Highly configurable expert persona
- Professional, consultative responses
- Pre-compiled fields appear immediately upon import""", 
    position=(1500, 50), color="blue")
    
    return builder.build()

def create_content_analyzer_workflow():
    """
    Create a content analysis workflow with multiple ChatInputs feeding different
    template variables for comprehensive content analysis.
    
    Pattern: Multiple ChatInputs → Multiple Template Variables
    """
    print("🔨 Creating Content Analyzer Workflow...")
    
    builder = LangflowBuilder(
        name="Multi-Input Content Analyzer",
        description="Analyze content using multiple input sources feeding into different template variables"
    )
    
    # Multiple ChatInput components for different types of input
    builder.add_component("content_input", "ChatInput", {
        "input_value": "Artificial intelligence is rapidly transforming industries across the globe. From healthcare to finance, AI technologies are enabling unprecedented levels of automation and insight generation...",
        "sender": "User",
        "sender_name": "Content Provider"
    }, position=(50, 200))
    
    builder.add_component("context_input", "ChatInput", {
        "input_value": "This is for a technology blog aimed at business executives who want to understand AI's impact on their industries.",
        "sender": "User", 
        "sender_name": "Context Provider"
    }, position=(50, 400))
    
    builder.add_component("requirements_input", "ChatInput", {
        "input_value": "Focus on practical applications and ROI. Include specific industry examples. Keep the tone professional but accessible.",
        "sender": "User",
        "sender_name": "Requirements"
    }, position=(50, 600))
    
    # Content Analysis Prompt Template
    analysis_template = """CONTENT ANALYSIS REQUEST

CONTENT TO ANALYZE:
{content_text}

CONTEXT INFORMATION:
{context_info}

SPECIFIC REQUIREMENTS:
{analysis_requirements}

ANALYSIS PARAMETERS:
- Analysis Type: {analysis_type}
- Focus Areas: {focus_areas}
- Output Format: {output_format}
- Detail Level: {detail_level}

Please provide a comprehensive analysis that covers:
1. Content quality and clarity
2. Audience appropriateness
3. Key strengths and areas for improvement
4. Specific recommendations
5. Overall assessment and score

Analysis:"""
    
    # Field configurations for the content analyzer
    field_configs = {
        "content_text": {
            "display_name": "Content to Analyze",
            "info": "The main content that will be analyzed (connected from ChatInput)",
            "placeholder": "Content will be automatically populated from the Content Input...",
            "required": True,
            "multiline": True
        },
        "context_info": {
            "display_name": "Context Information",
            "info": "Background context about the content (connected from ChatInput)",
            "placeholder": "Context will be automatically populated from the Context Input...",
            "required": True,
            "multiline": True
        },
        "analysis_requirements": {
            "display_name": "Analysis Requirements",
            "info": "Specific requirements for the analysis (connected from ChatInput)",
            "placeholder": "Requirements will be automatically populated from the Requirements Input...",
            "multiline": True
        },
        "analysis_type": {
            "display_name": "Analysis Type",
            "info": "What type of analysis should be performed?",
            "options": ["comprehensive", "technical", "audience-focused", "style-focused", "strategic"],
            "default_value": "comprehensive"
        },
        "focus_areas": {
            "display_name": "Focus Areas",
            "info": "Specific areas to focus the analysis on",
            "placeholder": "e.g., readability, accuracy, engagement, technical depth",
            "multiline": True
        },
        "output_format": {
            "display_name": "Output Format",
            "info": "How should the analysis be formatted?",
            "options": ["structured report", "bullet points", "narrative", "scorecard", "detailed breakdown"],
            "default_value": "structured report"
        },
        "detail_level": {
            "display_name": "Detail Level",
            "info": "How detailed should the analysis be?",
            "options": ["summary", "standard", "detailed", "comprehensive"],
            "default_value": "detailed"
        }
    }
    
    builder.add_dynamic_prompt("analyzer_prompt", analysis_template, field_configs, position=(500, 350))
    
    # Language Model
    builder.add_component("llm", "LanguageModel", {
        "provider": "OpenAI",
        "model_name": "gpt-4o-mini",
        "temperature": 0.3
    }, position=(950, 400))
    
    # Output
    builder.add_component("output", "ChatOutput", {
        "sender": "Machine",
        "sender_name": "Content Analyzer"
    }, position=(1400, 400))
    
    # 🔗 MULTIPLE KEY CONNECTIONS: Different ChatInputs to different template variables
    builder.connect("content_input", "analyzer_prompt", "message", "content_text")
    builder.connect("context_input", "analyzer_prompt", "message", "context_info") 
    builder.connect("requirements_input", "analyzer_prompt", "message", "analysis_requirements")
    builder.connect("analyzer_prompt", "llm", "prompt", "input_value")
    builder.connect("llm", "output", "text_output", "input_value")
    
    # Documentation
    builder.add_note("""# Multi-Input Content Analyzer

## 🔗 Multiple Connection Pattern:
- **Content ChatInput.message → Prompt.content_text**
- **Context ChatInput.message → Prompt.context_info**
- **Requirements ChatInput.message → Prompt.analysis_requirements**

## Workflow:
1. User provides content in first ChatInput
2. User provides context in second ChatInput  
3. User provides requirements in third ChatInput
4. All inputs flow into respective template variables
5. Comprehensive analysis generated

## Advanced Pattern:
This demonstrates how multiple user inputs can feed into different parts of a single prompt template, enabling complex, multi-faceted AI workflows.""", 
    position=(1500, 100), color="green")
    
    return builder.build()

def create_simple_qa_workflow():
    """
    Create a simple Q&A workflow demonstrating the basic ChatInput → Template pattern.
    
    Pattern: Single ChatInput → Single Template Variable (minimal example)
    """
    print("🔨 Creating Simple Q&A Workflow...")
    
    builder = LangflowBuilder(
        name="Simple Q&A Assistant",
        description="Basic question-answering assistant with ChatInput feeding into template variable"
    )
    
    # Simple user input
    builder.add_component("question", "ChatInput", {
        "input_value": "Explain quantum computing in simple terms",
        "sender": "User",
        "sender_name": "User"
    }, position=(100, 300))
    
    # Simple dynamic prompt
    qa_template = """You are a helpful {assistant_role} with expertise in {subject_area}.

User's Question: {user_question}

Please provide a {response_length} explanation that is {complexity_level} and uses a {communication_style} approach.

Answer:"""
    
    # Simple field configuration
    field_configs = {
        "user_question": {
            "display_name": "User Question",
            "info": "The question asked by the user",
            "required": True,
            "multiline": True
        },
        "assistant_role": {
            "display_name": "Assistant Role",
            "info": "What type of assistant should this be?",
            "options": ["teacher", "tutor", "expert", "guide", "mentor"],
            "default_value": "teacher"
        },
        "subject_area": {
            "display_name": "Subject Area", 
            "info": "Primary area of expertise",
            "placeholder": "e.g., science, technology, history, literature",
            "default_value": "science and technology"
        },
        "response_length": {
            "display_name": "Response Length",
            "info": "How long should the response be?",
            "options": ["brief", "moderate", "detailed", "comprehensive"],
            "default_value": "moderate"
        },
        "complexity_level": {
            "display_name": "Complexity Level",
            "info": "How complex should the explanation be?",
            "options": ["very simple", "simple", "intermediate", "advanced"],
            "default_value": "simple"
        },
        "communication_style": {
            "display_name": "Communication Style",
            "info": "What communication style should be used?",
            "options": ["conversational", "formal", "friendly", "professional"],
            "default_value": "conversational"
        }
    }
    
    builder.add_dynamic_prompt("qa_prompt", qa_template, field_configs, position=(500, 300))
    
    # Language Model
    builder.add_component("llm", "LanguageModel", {
        "provider": "OpenAI",
        "model_name": "gpt-4o-mini",
        "temperature": 0.5
    }, position=(900, 300))
    
    # Output
    builder.add_component("output", "ChatOutput", {
        "sender": "Machine",
        "sender_name": "Q&A Assistant"
    }, position=(1300, 300))
    
    # 🔗 KEY CONNECTION: Simple ChatInput to Template Variable
    builder.connect("question", "qa_prompt", "message", "user_question")
    builder.connect("qa_prompt", "llm", "prompt", "input_value")
    builder.connect("llm", "output", "text_output", "input_value")
    
    # Simple documentation
    builder.add_note("""# Simple Q&A Assistant

## Basic Pattern:
**ChatInput.message → Prompt.user_question**

Perfect example of the fundamental ChatInput → Template Variable connection pattern.

User types question → Flows into template → AI processes → Response delivered""", 
    position=(1400, 200), color="yellow")
    
    return builder.build()

def create_feedback_analyzer_workflow():
    """
    Real-world example: Customer feedback analyzer with sentiment analysis and action recommendations.
    
    Pattern: ChatInput → Template Variable for practical business use case
    """
    print("🔨 Creating Feedback Analyzer Workflow...")
    
    builder = LangflowBuilder(
        name="Customer Feedback Analyzer",
        description="Analyze customer feedback and provide sentiment analysis with actionable recommendations"
    )
    
    # Customer feedback input
    builder.add_component("feedback_input", "ChatInput", {
        "input_value": "I've been using your software for 6 months now. While I love the user interface and the customer support is excellent, I'm really frustrated with the slow loading times and occasional crashes. The mobile app is also quite buggy. However, when it works, it's exactly what I need for my business.",
        "sender": "Customer",
        "sender_name": "Customer Feedback"
    }, position=(100, 300))
    
    # Feedback analysis template
    feedback_template = """CUSTOMER FEEDBACK ANALYSIS

FEEDBACK TO ANALYZE:
{customer_feedback}

ANALYSIS CONTEXT:
- Business Type: {business_type}
- Product Category: {product_category}
- Analysis Focus: {analysis_focus}
- Priority Level: {priority_level}

Please provide a comprehensive analysis including:

1. **SENTIMENT ANALYSIS**
   - Overall sentiment (Positive/Negative/Mixed)
   - Sentiment confidence score (1-10)
   - Emotional tone indicators

2. **KEY THEMES IDENTIFICATION**
   - Main positive points
   - Main concerns/issues
   - Feature requests or suggestions

3. **PRIORITY ASSESSMENT**
   - Critical issues requiring immediate attention
   - Medium priority improvements
   - Nice-to-have enhancements

4. **ACTIONABLE RECOMMENDATIONS**
   - Short-term actions (1-30 days)
   - Medium-term improvements (1-6 months)
   - Long-term strategic considerations

5. **RESPONSE STRATEGY**
   - Suggested customer response approach
   - Key points to address in follow-up
   - Escalation recommendations if needed

Analysis:"""
    
    # Feedback analyzer field configuration
    field_configs = {
        "customer_feedback": {
            "display_name": "Customer Feedback",
            "info": "The customer feedback text to analyze (from ChatInput)",
            "placeholder": "Customer feedback will be automatically populated...",
            "required": True,
            "multiline": True
        },
        "business_type": {
            "display_name": "Business Type",
            "info": "What type of business is this feedback for?",
            "options": ["SaaS/Software", "E-commerce", "Service Provider", "Manufacturing", "Healthcare", "Education", "Other"],
            "default_value": "SaaS/Software"
        },
        "product_category": {
            "display_name": "Product Category",
            "info": "What category of product/service?",
            "options": ["Software Application", "Web Platform", "Mobile App", "Physical Product", "Professional Service", "Other"],
            "default_value": "Software Application"
        },
        "analysis_focus": {
            "display_name": "Analysis Focus",
            "info": "What should the analysis focus on?",
            "options": ["Overall Experience", "Product Quality", "Customer Service", "Technical Issues", "Feature Requests", "Comprehensive"],
            "default_value": "Comprehensive"
        },
        "priority_level": {
            "display_name": "Priority Level",
            "info": "How should issues be prioritized?",
            "options": ["Customer Impact", "Business Critical", "Revenue Impact", "Strategic Importance"],
            "default_value": "Customer Impact"
        }
    }
    
    builder.add_dynamic_prompt("feedback_analyzer", feedback_template, field_configs, position=(500, 200))
    
    # Language Model with higher temperature for creative recommendations
    builder.add_component("llm", "LanguageModel", {
        "provider": "OpenAI", 
        "model_name": "gpt-4o",
        "temperature": 0.6
    }, position=(950, 300))
    
    # Output
    builder.add_component("output", "ChatOutput", {
        "sender": "Machine",
        "sender_name": "Feedback Analyzer"
    }, position=(1400, 300))
    
    # 🔗 KEY CONNECTION: Customer feedback flows into analysis template
    builder.connect("feedback_input", "feedback_analyzer", "message", "customer_feedback")
    builder.connect("feedback_analyzer", "llm", "prompt", "input_value")
    builder.connect("llm", "output", "text_output", "input_value")
    
    # Business-focused documentation
    builder.add_note("""# Customer Feedback Analyzer

## Business Use Case:
Transform raw customer feedback into actionable business insights.

## Connection Pattern:
**Customer Feedback Input → Analysis Template → AI Processing → Structured Recommendations**

## Key Features:
- Sentiment analysis with confidence scoring
- Priority-based issue categorization  
- Actionable short/medium/long-term recommendations
- Customer response strategy suggestions

## Real-World Application:
- Customer service teams can paste feedback and get structured analysis
- Product managers get prioritized feature requests
- Support teams get response guidance
- Management gets business impact assessment""", 
    position=(1500, 50), color="purple")
    
    return builder.build()

def save_workflow(name: str, workflow: Dict[str, Any], results_dir: str = "results") -> str:
    """Save a workflow to a JSON file with validation."""
    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)
    
    # Create filename
    filename = f"{name.lower().replace(' ', '_')}.json"
    filepath = os.path.join(results_dir, filename)
    
    # Validate JSON structure
    try:
        json_str = json.dumps(workflow, indent=2)
        json.loads(json_str)  # Validate by parsing
    except Exception as e:
        print(f"❌ JSON validation failed for {name}: {e}")
        return ""
    
    # Save to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"✅ Saved: {filename}")
        return filepath
    except Exception as e:
        print(f"❌ Failed to save {name}: {e}")
        return ""

def analyze_workflow_connections(workflow: Dict[str, Any], name: str):
    """Analyze and display the connections in a workflow."""
    print(f"\n🔗 Connections in {name}:")
    
    edges = workflow.get('data', {}).get('edges', [])
    if not edges:
        print("   No connections found")
        return
    
    for edge in edges:
        source_id = edge.get('source', 'Unknown')
        target_id = edge.get('target', 'Unknown')
        
        # Get connection details
        source_handle = edge.get('data', {}).get('sourceHandle', {})
        target_handle = edge.get('data', {}).get('targetHandle', {})
        
        source_output = source_handle.get('name', 'unknown')
        target_input = target_handle.get('fieldName', 'unknown')
        
        # Clean up IDs for display
        source_clean = source_id.split('-')[0] if '-' in source_id else source_id
        target_clean = target_id.split('-')[0] if '-' in target_id else target_id
        
        print(f"   {source_clean}.{source_output} → {target_clean}.{target_input}")

def display_dynamic_fields(workflow: Dict[str, Any], name: str):
    """Display the dynamic fields in prompt components."""
    print(f"\n🎯 Dynamic Fields in {name}:")
    
    nodes = workflow.get('data', {}).get('nodes', [])
    prompt_nodes = [node for node in nodes if node.get('data', {}).get('type') == 'Prompt']
    
    if not prompt_nodes:
        print("   No Prompt components found")
        return
    
    for i, node in enumerate(prompt_nodes, 1):
        node_data = node.get('data', {}).get('node', {})
        custom_fields = node_data.get('custom_fields', {}).get('template', [])
        
        if custom_fields:
            print(f"   Prompt {i}: {', '.join(custom_fields)}")
        else:
            print(f"   Prompt {i}: No dynamic fields")

def main():
    """Main function to generate all ChatInput → Template Variable examples."""
    print("🚀 Generating ChatInput → Template Variable Examples")
    print("=" * 60)
    
    # Create results directory
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    
    # Define all workflows to generate
    workflows = [
        ("Expert Consultant", create_expert_consultant_workflow),
        ("Content Analyzer", create_content_analyzer_workflow), 
        ("Simple Q&A", create_simple_qa_workflow),
        ("Feedback Analyzer", create_feedback_analyzer_workflow)
    ]
    
    # Generate each workflow
    generated_files = []
    for name, create_func in workflows:
        try:
            print(f"\n📋 Generating: {name}")
            workflow = create_func()
            
            # Save workflow
            filepath = save_workflow(name, workflow, results_dir)
            if filepath:
                generated_files.append((name, filepath, workflow))
                
            # Analyze connections
            analyze_workflow_connections(workflow, name)
            
            # Display dynamic fields
            display_dynamic_fields(workflow, name)
            
        except Exception as e:
            print(f"❌ Error generating {name}: {e}")
    
    # Summary
    print(f"\n🎉 Generation Complete!")
    print("=" * 60)
    print(f"Generated {len(generated_files)} workflows:")
    
    for name, filepath, workflow in generated_files:
        nodes_count = len(workflow.get('data', {}).get('nodes', []))
        edges_count = len(workflow.get('data', {}).get('edges', []))
        print(f"  📄 {name}: {nodes_count} components, {edges_count} connections")
        print(f"     File: {os.path.basename(filepath)}")
    
    print(f"\n📁 All files saved in: {os.path.abspath(results_dir)}")
    
    print("\n🔑 Key Pattern Demonstrated:")
    print("   ChatInput.message → Prompt.{template_variable}")
    print("   This enables direct user input into AI prompt templates!")
    
    print("\n✨ Benefits:")
    print("   ✅ Pre-compiled dynamic fields appear immediately upon import")
    print("   ✅ No build step required - ready to connect and use")
    print("   ✅ Professional UI with dropdowns and validation")
    print("   ✅ Real user interaction with AI workflows")
    print("   ✅ Configurable AI behavior and responses")

if __name__ == "__main__":
    main()