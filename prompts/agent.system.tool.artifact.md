### Artifact Storage:
Context-efficient storage for large generated content. Prevents context pollution while maintaining access to important outputs like research documents, code, datasets, and documentation.

**When to use**:
- **Large content**: Generated reports, research documents, extensive code
- **Reusable assets**: Templates, configurations, datasets for future reference  
- **Context management**: Keep conversation focused while preserving important outputs
- **Collaboration**: Store outputs that subordinates or future sessions may need

**Parameters**:
- action: str
Operations: "create", "update", "get", "list", "delete", "search"

- title: str (required for create)
Descriptive name for the artifact

- content: str (required for create, optional for update)
The actual content to store

- description: str (optional)
Brief explanation of artifact purpose and contents

- type: str (optional) 
Content type: "code", "document", "data", "text" (auto-detected if not provided)

- id: str (required for update/get/delete)
Unique artifact identifier returned during creation


- query: str (required for search)
Search term for finding artifacts by title/description

**Actions**:
- **create**: Store new content as artifact. Returns ID for future reference. Auto-saves to vector DB.
- **get**: Retrieve full artifact content and metadata.
- **update**: Modify existing artifact content or metadata. Auto-updates vector DB.
- **list**: View all artifacts with descriptions and metadata.
- **search**: Find artifacts by keyword or type filter.
- **delete**: Remove artifact and its content file. Auto-removes from vector DB.

**Best Practices**:
- **Create early**: Store large outputs immediately to avoid context bloat
- **Descriptive info**: Use clear titles and descriptions for easy search and retrieval
- **Type tagging**: Specify type for better organization and filtering
- **Clean up**: Delete obsolete artifacts to maintain organization
- **Vector search**: Artifacts automatically indexed in vector DB for intelligent search

**Usage Examples**:

**Store research document:**
```json
{
    "tool_name": "artifact",
    "tool_args": {
        "action": "create",
        "title": "Market Analysis Report Q3",
        "content": "[Long research content...]",
        "description": "Comprehensive market analysis with competitor data",
        "type": "document"
    }
}
```

**Retrieve full artifact:**
```json
{
    "tool_name": "artifact",
    "tool_args": {
        "action": "get",
        "id": "a1b2c3d4"
    }
}
```

**Search for code artifacts:**
```json
{
    "tool_name": "artifact",
    "tool_args": {
        "action": "search",
        "query": "api",
        "type": "code"
    }
}
```

**Storage**:
- **Files**: Agent-specific directory `data/{agent_id}_{profile}/artifacts/` with metadata.json index and individual content files
- **Vector DB**: Title and description automatically indexed in vector database for intelligent search and memory integration