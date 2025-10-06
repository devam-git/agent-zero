# Component Summary

Quick reference for component selection. For detailed API specs (handles, configs), use document_query tool on `/a0/flow_builder/component_registry.md`.

| Component | Category | Purpose | Use For |
|-----------|----------|---------|---------|
| ChatInput | I/O | User chat input | chat flows, user interaction, getting user input |
| ChatOutput | I/O | Display chat responses | chat flows, showing results, displaying responses |
| TextInput | I/O | Simple text input | basic text input, simple forms |
| TextOutput | I/O | Display text output | showing text results, simple displays |
| File | I/O | Load files as DataFrame or Message (outputs: dataframe, message) | file loading, document processing, data ingestion, reading files |
| Type_Convert | Utilities | Convert between Message/Data/DataFrame (input: input_data, outputs: message_output/data_output/dataframe_output) | type conversion, converting between data types |
| LanguageModel | AI Models | Generic LLM processing | text generation, analysis, AI responses |
| OpenAIModel | AI Models | OpenAI specific model | OpenAI GPT models, specific API features |
| Prompt | Templates | Dynamic Template prompts with {variables} | templated text, user input processing, prompt engineering |
| Agent | Advanced | AI agent with tools | complex tasks, tool usage, multi-step reasoning |
| Calculator | Tools | Mathematical calculations | math operations, calculations, numerical tasks |
| WebSearch | Tools | Web search functionality | research, information gathering, web queries |
| MCPTools | Tools | General MCP server connection | any remote MCP servers, custom MCP tools, third-party MCP services. To use with Agent |
| MCPNode | Tools | Direct MCP tool execution | specific MCP tool execution in workflow, dynamic tool integration. To use without Agent |
| QpiAIMCPTools | Tools | QpiAI hosted MCP tools | QpiAI services, Gmail, Slack, Calendar, Drive, Sheets |
| If_Else | Control Flow | Conditional routing | branching logic, conditional workflows, decision making, text comparison |

**Note**: MCP components can be used in different ways:
Unless specified, use MCPTools.
1. **All tools** - Use MCPTools in static way to expose all server tools to agents
2. **Known specific tool** - Use a specific tool from the MCPTools if you know the exact tool name
3. **Direct execution** - Use MCPNode to execute specific MCP actions directly in workflow without agent (ONLY IF USER MENTIONS)
4. **Unknown/explore tools** - Use dynamic discovery to explore available tools first, then schemas

## QpiAI MCP Tools Available

| Tool Name | Service | Purpose | Use For |
|-----------|---------|---------|---------|
| gmail | Gmail | Email operations | send emails, read emails, search emails, manage inbox |
| slack | Slack | Team communication | send messages, read channels, manage workspace |
| calendar | Calendar | Schedule management | create events, check availability, manage appointments |
| drive | Google Drive | File operations | upload files, download files, share documents |
| sheets | Google Sheets | Spreadsheet operations | read data, write data, create sheets, calculations |

**Note**: QpiAI MCP tools are dynamic - specific schemas and parameters are discovered at runtime by the discovery agent.

## Connection Patterns
- **Basic Chat**: ChatInput.message → Prompt.{field} → LanguageModel.input_value → ChatOutput.input_value
- **File Loading**: File.message → Prompt.{field} OR File.dataframe → Component.data_input
- **Agent with Tools**: ChatInput.message → Agent.input_value + Calculator.component_as_tool → Agent.tools + MCPTools.component_as_tool → Agent.tools + WebSearch.component_as_tool → Agent.tools → Agent.response → ChatOutput.input_value
- **Direct MCP Execution**: ChatInput.message → MCPNode.{dynamic_inputs} → MCPNode.result → ChatOutput.input_value
- **Multi-stage**: ChatInput.message → Prompt1.{field} → LanguageModel1.input_value → Prompt2.{field} → LanguageModel2.input_value → ChatOutput.input_value
- **Conditional Routing**: ChatInput.message → If_Else.input_text + TextInput.text → If_Else.match_text → If_Else.true_result → Component1 + If_Else.false_result → Component2

## Best Practices
1. **Always use `input_types: ["Message"]`** for dynamic prompt fields
2. **Verify output handle names** - they vary by component type
3. **Chain components logically** following the connection patterns