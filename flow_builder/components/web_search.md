🔍 Web Search Tool Template Features:

## 1. Tool-Specific Properties

**Category:** "tools" - Identifies it as a tool component
**Tool Mode:** tool_mode: True in the search query input field
**Base Classes:** ["Data"] - Returns structured search data
**Icon:** "search" - Search magnifying glass icon

## 2. Input Configuration

**Search Query Input:**
- Type: MessageTextInput
- Tool-compatible: tool_mode: True
- Example: "latest AI developments 2024"
- Trace enabled for debugging

**Number of Results:**
- Type: IntInput
- Default: 5 results
- Range: 1-10 results maximum



## 3. Search Capabilities

**DuckDuckGo Integration:**
- Uses DuckDuckGo Instant Answer API
- No API key required
- Returns abstracts and related topics
- Handles errors gracefully

**Structured Results:**
- Rank, title, URL, snippet for each result
- Source attribution
- Timestamp and metadata
- Search summary

**Error Handling:**
- Empty query validation
- Network timeout protection
- Fallback search options
- Graceful error responses

## 4. Output Structure

**Result Format:**
```json
{
  "query": "search terms",
  "results": [
    {
      "rank": 1,
      "title": "Result Title",
      "url": "https://example.com",
      "snippet": "Description...",
      "source": "DuckDuckGo"
    }
  ],
  "summary": "Found X results for 'query'",
  "timestamp": "2024-01-01T12:00:00",
  "search_engine": "duckduckgo",
  "total_results": 5
}
```

## 5. Key Differences from Chat Components

**Base Classes:** ["Data"] instead of ["Message"]
**Output Type:** "Data" for structured search results
**Tool Mode:** Enabled for agent integration
**Category:** "tools" for organization
**Real-time Data:** Fetches current web information

## 6. Connection Type
When connecting to agents:
- **Output:** "Data" type
- **Connection:** Uses "component_as_tool" output
- **Agent Input:** "Tool" type in tools array

## 🔧 Usage in Builder:

```python
# Add to your component templates
NEW_COMPONENT_TEMPLATES["WebSearch"] = WEB_SEARCH_TEMPLATE

# Use in workflow with agent
builder.add_component("search", "WebSearch", {
    "query": "example search",  # Default or placeholder
    "num_results": 3,
    "search_engine": "duckduckgo"
})

builder.add_component("agent", "Agent", {
    "system_prompt": "You can search the web for current information."
})

# Connect web search as tool to agent
builder.connect("search", "agent", "component_as_tool", "tools")
```

## 🌐 Example Use Cases:

- **Research Assistant:** "Find recent studies on climate change"
- **News Updates:** "Latest news about artificial intelligence"  
- **Fact Checking:** "Current population of Tokyo Japan"
- **Product Research:** "Best smartphones 2024 reviews"
- **Academic Research:** "machine learning papers 2024"

The web search tool will appear as an available tool that agents can use to find current, real-time information from the web!

## 🔒 Privacy & Security:

- Uses DuckDuckGo by default (privacy-focused)
- No personal data stored
- Request timeout protection
- Error handling prevents data leaks
- Configurable result limits 