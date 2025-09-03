"""
LLM call tracing as nested spans under main trace
"""
from python.helpers.langfuse_tracer import TRACING_ENABLED, client
from python.helpers.extension import Extension

class LangfuseLlmTrace(Extension):
    
    async def execute(self, loop_data=None, **kwargs):
        """Create LLM span under main trace"""
        if not TRACING_ENABLED or not client:
            return
        
        if hasattr(self.agent, '_langfuse_main_span') and self.agent._langfuse_main_span:
            model_config = self.agent.config.chat_model
            model_name = f"{model_config.provider}/{model_config.name}"
            
            print(f"[LangFuse] Creating LLM span for {model_name}")
            
            try:
                # Create LLM generation under main trace
                llm_ctx = client.start_as_current_generation(
                    name=f"LLM Call: {model_name}",
                    model=model_name,
                    input={
                        "model": model_name,
                        "iteration": loop_data.iteration if loop_data else 0,
                        "message_count": len(loop_data.history_output) if loop_data and loop_data.history_output else 0,
                    },
                    metadata={
                        "provider": model_config.provider,
                        "model_name": model_config.name,
                        "temperature": getattr(model_config, 'temperature', None),
                        "max_tokens": getattr(model_config, 'max_tokens', None),
                    }
                )
                llm_span = llm_ctx.__enter__()
                
                # Store for response extension to complete
                self.agent._langfuse_llm_ctx = llm_ctx
                self.agent._langfuse_llm_span = llm_span
                self.agent._langfuse_llm_model = model_name
                
                print(f"[LangFuse] LLM generation span created")
                
            except Exception as e:
                print(f"[EXTENSION DEBUG] LLM span creation failed: {e}")