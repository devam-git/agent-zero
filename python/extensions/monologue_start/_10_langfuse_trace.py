"""
Start main conversation trace manually
"""
from python.helpers.langfuse_tracer import client, TRACING_ENABLED
from python.helpers.extension import Extension

class LangfuseTrace(Extension):
    
    async def execute(self, loop_data=None, **kwargs):
        """Start main conversation trace"""
        print(f"[EXTENSION DEBUG] Monologue start extension CALLED for {self.agent.agent_name}")
        print(f"[EXTENSION DEBUG] TRACING_ENABLED: {TRACING_ENABLED}, client: {client is not None}")
        
        if not TRACING_ENABLED or not client:
            print("[EXTENSION DEBUG] Skipping trace creation - not enabled or no client")
            return
        
        # Extract user message
        user_input = "No user message"
        if loop_data and loop_data.user_message and hasattr(loop_data.user_message, 'content'):
            content = loop_data.user_message.content
            if isinstance(content, dict):
                user_input = content.get('message', 'No message')
            else:
                user_input = str(content)
        
        print(f"[LangFuse] Starting main trace for: {user_input[:50]}...")
        
        # In SDK v3, create trace using context manager approach
        try:
            # Generate a trace ID for this conversation
            trace_id = client.create_trace_id(seed=f"{self.agent.agent_name}-{getattr(self.agent.context, 'id', 'unknown')}")
            
            # Start the main trace span
            trace_ctx = client.start_as_current_span(
                name="Agent Conversation",
                input={"user_message": user_input, "agent": self.agent.agent_name},
                trace_context={"trace_id": trace_id}
            )
            # Enter context so this becomes the active span
            trace_span = trace_ctx.__enter__()
            
            # Update trace metadata
            client.update_current_trace(
                user_id=getattr(self.agent.context, 'id', 'unknown'),
                session_id=getattr(self.agent.context, 'id', 'unknown'),
                tags=[self.agent.agent_name, "conversation"],
                metadata={
                    "agent_name": self.agent.agent_name,
                    "agent_number": getattr(self.agent, 'number', 0),
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                }
            )
            
            print(f"[EXTENSION DEBUG] Trace creation successful")
        except Exception as e:
            print(f"[EXTENSION DEBUG] Trace creation failed: {e}")
            return
        
        # Store trace context and span for other extensions to use
        self.agent._langfuse_main_ctx = trace_ctx
        self.agent._langfuse_main_span = trace_span
        self.agent._langfuse_user_input = user_input
        
        print(f"[LangFuse] Main trace created with ID: {trace_id}")