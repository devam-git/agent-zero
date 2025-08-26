import json
from typing import Dict, Any
from builder import LangflowBuilder

def create_web_search_resource_agent():
    """
    Creates a web search agent that searches for resources on any topic 
    and provides a structured list of valuable resources to check.
    
    The agent will:
    - Perform comprehensive web searches on the given topic
    - Identify high-quality, diverse sources
    - Provide a curated list of resources with descriptions
    - Include different types of sources (articles, guides, videos, tools, etc.)
    """
    
    builder = LangflowBuilder(
        name="Web Search Resource Agent",
        description="An AI agent that searches the web for any topic and provides a curated list of valuable resources to explore."
    )
    
    # Add Web Search Tool
    builder.add_component("web_search", "WebSearch", {
        "query": "example search query",
        "max_results": 10
    }, position=(100, 400))
    
    # Add Resource Curation Agent
    builder.add_component("resource_agent", "Agent", {
        "system_prompt": """You are a professional research librarian and resource curator. Your specialty is finding and organizing the best resources on any topic for people who want to learn or research.

When someone asks for resources on a topic, follow this process:

1. **Search Strategy**:
   - Perform multiple targeted web searches with different angles
   - Look for authoritative sources, tutorials, guides, and tools
   - Search for both beginner-friendly and advanced resources
   - Include recent and foundational content

2. **Resource Categories to Find**:
   - Official documentation and websites
   - Comprehensive guides and tutorials
   - Expert articles and blog posts
   - Educational videos and courses
   - Tools, software, and platforms
   - Research papers and case studies
   - Community forums and discussions
   - Books and publications

3. **Output Format**:
   Present your findings as a well-organized list with these sections:

   ## 📚 Essential Resources for [Topic]

   ### 🏛️ Official & Authoritative Sources
   - **[Resource Name]** - [URL]
     Brief description of what this resource offers and why it's valuable.

   ### 📖 Comprehensive Guides & Tutorials  
   - **[Resource Name]** - [URL]
     Brief description focusing on what you'll learn.

   ### 🔧 Tools & Platforms
   - **[Resource Name]** - [URL]
     Description of the tool and its use cases.

   ### 📰 Latest News & Articles
   - **[Resource Name]** - [URL]  
     Brief summary of key insights.

   ### 🎓 Learning Resources
   - **[Resource Name]** - [URL]
     Description of content level and format.

   ### 💬 Communities & Forums
   - **[Resource Name]** - [URL]
     Description of the community and discussion topics.

4. **Quality Criteria**:
   - Prioritize credible, well-established sources
   - Include both free and premium resources when relevant
   - Balance different formats (text, video, interactive)
   - Ensure resources are current and actively maintained
   - Provide diverse perspectives and approaches

5. **Additional Tips**:
   - Add a brief note about which resources are best for beginners vs. advanced users
   - Mention if any resources require subscriptions or payment
   - Include estimated time commitments for courses/tutorials
   - Suggest a learning path or reading order when appropriate

Always search multiple times with different queries to ensure you find the most comprehensive and diverse set of resources. Be thorough and helpful!""",
        
        "agent_llm": "OpenAI",
        "model_name": "gpt-4o-mini",
        "temperature": 0.1,
        "max_iterations": 15,
        "handle_parsing_errors": True
    }, position=(400, 300))
    
    # Add Topic Input
    builder.add_component("topic_input", "ChatInput", {
        "input_value": "I want to learn about machine learning. Can you provide me with a comprehensive list of resources to get started and advance my knowledge?",
        "sender": "User",
        "sender_name": "User", 
        "should_store_message": True,
        "background_color": "#1f77b4",
        "chat_icon": "🔍",
        "text_color": "#ffffff"
    }, position=(100, 200))
    
    # Add Resource List Output
    builder.add_component("resource_output", "ChatOutput", {
        "sender": "Machine",
        "sender_name": "Resource Curator",
        "should_store_message": True,
        "data_template": "{input_value}",
        "background_color": "#2ca02c", 
        "chat_icon": "📚",
        "text_color": "#ffffff"
    }, position=(700, 300))
    
    # Connect components - Web search tool to agent
    builder.connect("web_search", "resource_agent", "component_as_tool", "tools")
    
    # Connect input to agent
    builder.connect("topic_input", "resource_agent", "message", "input_value")
    
    # Connect agent to output
    builder.connect("resource_agent", "resource_output", "response", "input_value")
    
    # Add helpful documentation
    builder.add_note("""
# 🔍 Web Search Resource Agent

## What This Agent Does
- Searches the web for comprehensive resources on any topic
- Curates and organizes findings by category
- Provides structured lists with descriptions and URLs
- Focuses on high-quality, diverse sources

## How to Use
1. Enter your topic of interest in the input
2. The agent will perform multiple web searches
3. Receive a curated list organized by resource type
4. Follow up with specific questions to refine results

## Example Topics
- "Python programming for beginners"
- "Digital marketing strategies 2024" 
- "Sustainable energy solutions"
- "Machine learning fundamentals"
- "Starting a small business"

## Resource Categories
- Official documentation
- Tutorials and guides  
- Tools and platforms
- Latest articles and news
- Learning courses
- Community forums
- Books and publications

## Tips for Best Results
- Be specific about your learning level
- Mention particular aspects you're interested in
- Ask for resources in specific formats (video, text, interactive)
- Request beginner vs. advanced materials
""", position=(750, 50), color="blue")
    
    return builder.build()

def save_workflow_to_file(workflow: Dict[str, Any], filename: str):
    """Save the generated workflow to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(workflow, f, indent=2)
    print(f"Workflow saved to {filename}")

def main():
    """Generate and save the web search resource agent workflow."""
    workflow = create_web_search_resource_agent()
    save_workflow_to_file(workflow, "results/web_search_resource_agent.json")
    print("✨ Web Search Resource Agent created successfully!")
    print("\n📋 Workflow Features:")
    print("- Web search capabilities for any topic")
    print("- Structured resource organization")
    print("- Multiple search strategies")
    print("- Quality source curation")
    print("- User-friendly categorization")
    
    return workflow

if __name__ == "__main__":
    main()
