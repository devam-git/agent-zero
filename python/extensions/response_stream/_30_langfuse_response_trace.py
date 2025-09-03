"""
Complete LLM span with response
"""
from python.helpers.langfuse_tracer import TRACING_ENABLED
from python.helpers.extension import Extension

class LangfuseResponseTrace(Extension):
    
    async def execute(self, loop_data=None, text="", parsed=None, **kwargs):
        """Complete LLM span with response"""
        if not TRACING_ENABLED:
            return
        
        # Complete LLM span if it exists
        if hasattr(self.agent, '_langfuse_llm_span') and self.agent._langfuse_llm_span and len(text) > 100:
            
            try:
                # Parse tool requests if available
                tool_request = None
                if parsed and isinstance(parsed, dict):
                    tool_request = {
                        "tool_name": parsed.get("tool_name", ""),
                        "has_tool_call": True,
                    }
                
                # Update the LLM generation with output
                self.agent._langfuse_llm_span.update(
                    output={
                        "response": text[:1000] if len(text) > 1000 else text,
                        "response_length": len(text),
                        "tool_request": tool_request,
                        "iteration": loop_data.iteration if loop_data else 0,
                    }
                )
                
                # End the generation span context
                self.agent._langfuse_llm_span.__exit__(None, None, None)
                print(f"[LangFuse] LLM span completed: {len(text)} chars, has_tool: {tool_request is not None}")
                
                # Clear the span
                self.agent._langfuse_llm_span = None
                
            except Exception as e:
                print(f"[EXTENSION DEBUG] LLM span completion failed: {e}")
        
        # Store final response for main trace completion
        if len(text) > 100:
            self.agent._langfuse_response = text[:500]