import json
from typing import Dict, Any, Tuple
from builder import LangflowBuilder

def create_research_agent_with_web_search():
    """
    Creates a comprehensive research agent with web search capabilities.
    
    This agent can:
    - Perform web searches on any topic
    - Analyze and synthesize information from multiple sources
    - Provide detailed research reports
    - Handle follow-up questions and refinements
    """
    
    builder = LangflowBuilder(
        name="Research Agent with Web Search",
        description="An AI research assistant that can search the web and provide comprehensive analysis on any topic with citations and detailed findings."
    )
    
    # Add Web Search Tool
    builder.add_component("web_search", "WebSearch", {
        "max_results": 10,
    }, position=(100, 400))
    
    # Add Research Agent with comprehensive instructions
    builder.add_component("research_agent", "Agent", {
        "system_prompt": """You are an expert research analyst with access to web search capabilities. Your role is to conduct thorough research and provide comprehensive, well-structured reports.

When conducting research:

1. **Search Strategy**:
   - Use specific, targeted search queries
   - Perform multiple searches from different angles
   - Search for recent and authoritative sources
   - Look for diverse perspectives on the topic

2. **Analysis Framework**:
   - Summarize key findings clearly
   - Identify main themes and patterns
   - Note conflicting information or debates
   - Assess credibility of sources
   - Provide relevant statistics and data points

3. **Report Structure**:
   - Executive Summary (2-3 sentences)
   - Key Findings (organized by themes)
   - Supporting Evidence (with source citations)
   - Implications and Conclusions
   - Recommendations for further research

4. **Citation Format**:
   - Always include source URLs
   - Mention publication dates when available
   - Note the type of source (news, academic, official, etc.)

5. **Quality Standards**:
   - Fact-check information across multiple sources
   - Distinguish between facts and opinions
   - Acknowledge limitations or gaps in available information
   - Provide balanced perspectives on controversial topics

Be thorough, accurate, and objective in your research. If you need to search for additional information to provide a complete answer, use the web search tool multiple times with different queries.""",
        
        "agent_llm": "OpenAI",
        "model_name": "gpt-4o",  # Using GPT-4 for better analysis capabilities
        "temperature": 0.2,  # Lower temperature for more consistent, factual responses
        "max_iterations": 20,  # Allow multiple search iterations for thorough research
        "handle_parsing_errors": True,
        "memory_enabled": True,
        "memory_window_size": 15  # Remember previous searches in the conversation
    }, position=(400, 300))
    
    # Add Chat Input for research queries
    builder.add_component("research_input", "ChatInput", {
        "input_value": "Research the latest developments in artificial intelligence and their potential impact on the job market in 2024. Include recent studies, expert opinions, and specific examples of AI implementations in various industries.",
        "sender": "User",
        "sender_name": "Researcher",
        "should_store_message": True,
        "background_color": "#1f77b4",
        "chat_icon": "🔍",
        "text_color": "#ffffff"
    }, position=(100, 200))
    
    # Add Research Output
    builder.add_component("research_output", "ChatOutput", {
        "sender": "Machine",
        "sender_name": "Research Agent",
        "should_store_message": True,
        "data_template": "{input_value}",
        "background_color": "#2ca02c",
        "chat_icon": "📊",
        "text_color": "#ffffff"
    }, position=(700, 300))
    
    # Connect the web search tool to the agent
    builder.connect("web_search", "research_agent", "component_as_tool", "tools")
    
    # Connect the input to the agent
    builder.connect("research_input", "research_agent", "message", "input_value")
    
    # Connect the agent to the output
    builder.connect("research_agent", "research_output", "response", "input_value")
    
    # Add documentation note
    builder.add_note("""
# Research Agent with Web Search

## Capabilities
- Web search across multiple search engines
- Multi-source information synthesis
- Comprehensive research reports
- Citation and source tracking
- Follow-up question handling

## Example Research Topics
- Technology trends and market analysis
- Scientific developments and breakthroughs
- Policy changes and regulatory updates
- Industry analysis and competitive intelligence
- Academic research and literature reviews

## Search Features
- Multiple search queries per topic
- Source diversity and credibility assessment
- Real-time information access
- Snippet extraction and analysis
- Metadata collection

## Output Format
- Executive summaries
- Structured findings
- Source citations
- Balanced perspectives
- Actionable insights

## Best Practices
- Ask specific, focused questions
- Request particular angles or perspectives
- Specify time frames for current events
- Ask for source types (academic, news, official)
- Request follow-up searches for deeper analysis
""", position=(750, 50), color="blue")
    
    return builder.build()


def create_specialized_research_workflows():
    """
    Creates additional specialized research workflows for different use cases.
    """
    
    # Academic Research Agent
    def create_academic_research_agent():
        builder = LangflowBuilder(
            name="Academic Research Agent",
            description="Specialized agent for academic and scientific research with citation standards."
        )
        
        builder.add_component("academic_search", "SearchTool", {
            "api_key": "",
            "search_engine": "google_scholar",  # If available
            "max_results": 15,
            "include_snippets": True,
            "filter_academic": True
        }, position=(100, 400))
        
        builder.add_component("academic_agent", "Agent", {
            "system_prompt": """You are an academic research specialist. Focus on:
            - Peer-reviewed sources and academic publications
            - Proper academic citation formats (APA, MLA, Chicago)
            - Literature reviews and systematic analysis
            - Methodology assessment and research quality
            - Gap identification in current research
            - Theoretical frameworks and conceptual models
            
            Always prioritize scholarly sources and provide proper academic citations.""",
            
            "agent_llm": "OpenAI",
            "model_name": "gpt-4o",
            "temperature": 0.1,
            "max_iterations": 15
        }, position=(400, 300))
        
        # Connect components
        builder.connect("academic_search", "academic_agent", "component_as_tool", "tools")
        
        return builder.build()
    
    # Market Research Agent
    def create_market_research_agent():
        builder = LangflowBuilder(
            name="Market Research Agent",
            description="Specialized agent for business and market intelligence research."
        )
        
        builder.add_component("market_search", "SearchTool", {
            "api_key": "",
            "max_results": 12,
            "include_metadata": True,
            "focus_domains": ["business", "finance", "market"]
        }, position=(100, 400))
        
        builder.add_component("market_agent", "Agent", {
            "system_prompt": """You are a market research analyst. Focus on:
            - Market trends and forecasts
            - Competitive analysis and positioning
            - Industry reports and data
            - Consumer behavior and preferences
            - Financial performance metrics
            - SWOT analysis frameworks
            - Market size and growth projections
            
            Provide actionable business insights with supporting data.""",
            
            "agent_llm": "OpenAI",
            "model_name": "gpt-4o-mini",
            "temperature": 0.3,
            "max_iterations": 12
        }, position=(400, 300))
        
        builder.connect("market_search", "market_agent", "component_as_tool", "tools")
        
        return builder.build()
    
    return {
        "academic_research": create_academic_research_agent(),
        "market_research": create_market_research_agent()
    }


def save_workflow_to_file(workflow: Dict[str, Any], filename: str):
    """Save workflow JSON to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    print(f"Workflow saved to {filename}")


def main():
    """
    Main function to create and save research agent workflows
    """
    print("Creating Research Agent with Web Search...")
    
    # Create the main research agent workflow
    research_workflow = create_research_agent_with_web_search()
    
    # Save the workflow
    save_workflow_to_file(research_workflow, "research_agent_workflow.json")
    
    # Create specialized workflows
    print("\nCreating specialized research workflows...")
    specialized_workflows = create_specialized_research_workflows()
    
    # Save specialized workflows
    for name, workflow in specialized_workflows.items():
        filename = f"{name}_workflow.json"
        save_workflow_to_file(workflow, filename)
    
    print("\n✅ Research Agent Creation Complete!")
    print("\nGenerated Workflows:")
    print("1. research_agent_workflow.json - Main research agent with web search")
    print("2. academic_research_workflow.json - Academic research specialist")
    print("3. market_research_workflow.json - Market research analyst")
    
    print("\n🔧 Setup Instructions:")
    print("1. Set your search API key: export SEARCH_API_KEY='your-api-key'")
    print("2. Set your OpenAI API key: export OPENAI_API_KEY='your-openai-key'")
    print("3. Import the JSON files into Langflow")
    print("4. Connect and test the workflows")
    
    print("\n💡 Usage Tips:")
    print("- Ask specific, focused research questions")
    print("- Request particular time frames or source types")
    print("- Use follow-up questions to drill down into specific aspects")
    print("- Ask for comparisons between different sources or perspectives")
    
    return research_workflow


if __name__ == "__main__":
    workflow = main()
