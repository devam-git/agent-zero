from builder import LangflowBuilder
import json

builder = LangflowBuilder(
    name="AgentHive Sequential Support Ticket Email Workflow (Corrected)",
    description="Sequential workflow: analyzes support tickets and drafts a suitable email reply using chained LLM prompts. All connections use correct output handle names."
)

# 1. ChatInput for support ticket
builder.add_component("ticket_in", "ChatInput", {
    "input_value": "Paste support ticket text here",
    "sender": "User",
    "sender_name": "Support Agent",
    "should_store_message": True
}, position=(100, 200))

# 2. Dynamic Prompt: Analyze ticket
analyze_template = """Analyze the following support ticket and extract the key issue, sentiment, and any important details.\n\nSupport Ticket:\n{ticket_text}\n\nRespond with a structured summary."""
field_configs1 = {
    "ticket_text": builder.create_compatible_field_config(
        display_name="Support Ticket Text",
        info="The full text of the support ticket.",
        placeholder="Paste the ticket here...",
        required=True
    )
}
builder.add_dynamic_prompt("analyze_prompt", analyze_template, field_configs1, position=(300, 200))

# 3. LLM for analysis
builder.add_component("llm_analyze", "LanguageModel", {
    "provider": "OpenAI",
    "model_name": "gpt-4o-mini",
    "temperature": 0.2,
    "stream": False
}, position=(500, 200))

# 4. Dynamic Prompt: Draft email
email_template = """Based on the following support ticket analysis, draft a professional and empathetic email reply to the customer.\n\nTicket Analysis:\n{ticket_analysis}\n\nThe email should address the issue, acknowledge the sentiment, and offer a clear next step or resolution."""
field_configs2 = {
    "ticket_analysis": builder.create_compatible_field_config(
        display_name="Ticket Analysis",
        info="Structured summary of the support ticket (from previous step).",
        placeholder="Analysis output will appear here...",
        required=True
    )
}
builder.add_dynamic_prompt("email_prompt", email_template, field_configs2, position=(700, 200))

# 5. LLM for email drafting
builder.add_component("llm_email", "LanguageModel", {
    "provider": "OpenAI",
    "model_name": "gpt-4o-mini",
    "temperature": 0.2,
    "stream": False
}, position=(900, 200))

# 6. ChatOutput for final email
builder.add_component("email_out", "ChatOutput", {
    "sender": "Machine",
    "sender_name": "Support Email Draft",
    "should_store_message": True
}, position=(1100, 200))

# Corrected Connections
# ChatInput output is 'message', connect to analyze_prompt 'ticket_text'
builder.connect("ticket_in", "analyze_prompt", "message", "ticket_text")
# LLM output is 'text_output', connect to email_prompt 'ticket_analysis'
builder.connect("analyze_prompt", "llm_analyze")
builder.connect("llm_analyze", "email_prompt", "text_output", "ticket_analysis")
builder.connect("email_prompt", "llm_email")
builder.connect("llm_email", "email_out")

# Documentation note
builder.add_note("""
# Sequential Support Ticket Email Workflow (AgentHive, FIXED)

**✅ FIXED: Input Type Compatibility Issue**
- All dynamic prompt fields now use input_types: ["Message"]  
- Connections work properly in Langflow UI
- Uses create_compatible_field_config() helper method

## Workflow Steps:
- Step 1: User pastes a support ticket (ChatInput)
- Step 2: LLM analyzes the ticket and summarizes key issues and sentiment (Dynamic Prompt + LLM)
- Step 3: LLM drafts a professional, empathetic email reply based on the analysis (Dynamic Prompt + LLM)
- Step 4: Final email draft is shown to the user (ChatOutput)

## Technical Details:
- All connections use correct output handle names per latest dynamic prompt instructions
- Built with LangflowBuilder and latest best practices for agent-hive
- Dynamic fields auto-connect to Language Model outputs properly
- No manual connection fixes needed in UI

## Key Lesson:
**Always use input_types: ["Message"] for dynamic prompt fields!**
This ensures compatibility with Language Model text_output handles.
""", position=(1300, 100))

workflow = builder.build()
with open("support_ticket_flow.json", "w") as f:
    json.dump(workflow, f, indent=2)
print("Workflow saved to support_ticket_flow.json")