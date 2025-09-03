"""
Complete main trace when conversation ends
"""
from python.helpers.langfuse_tracer import flush, TRACING_ENABLED, client
from python.helpers.extension import Extension

class LangfuseTraceComplete(Extension):
    
    async def execute(self, loop_data=None, **kwargs):
        """Complete main trace and flush"""
        if not TRACING_ENABLED or not client:
            return
        
        # Complete main trace if it exists
        if hasattr(self.agent, '_langfuse_main_span') and self.agent._langfuse_main_span:
            
            try:
                # Gather final output
                final_output = {
                    "user_input": getattr(self.agent, '_langfuse_user_input', 'Unknown'),
                    "final_response": getattr(self.agent, '_langfuse_response', 'No response'),
                    "iterations": loop_data.iteration if loop_data and hasattr(loop_data, 'iteration') else 0,
                    "message_count": len(self.agent.history.current.messages) if hasattr(self.agent, 'history') else 0,
                }
                
                # Update trace with final output and metadata
                client.update_current_trace(
                    output=final_output,
                    metadata={
                        "completion_status": "success",
                        "total_iterations": loop_data.iteration if loop_data and hasattr(loop_data, 'iteration') else 0,
                        "agent_name": self.agent.agent_name,
                        "completion_time": __import__('datetime').datetime.now().isoformat()
                    }
                )
                
                # End the main trace span context
                self.agent._langfuse_main_span.__exit__(None, None, None)
                
                print(f"[LangFuse] Main trace completed for conversation")
                
                # Clear trace references
                self.agent._langfuse_main_span = None
                self.agent._langfuse_response = None
                self.agent._langfuse_user_input = None
                
            except Exception as e:
                print(f"[EXTENSION DEBUG] Trace completion failed: {e}")
        
        print("[LangFuse] Flushing all traces...")
        flush()
        print("[LangFuse] All traces sent to LangFuse")