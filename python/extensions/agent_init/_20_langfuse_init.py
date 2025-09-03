"""
Initialize LangFuse tracing when agent starts
"""
from python.helpers.langfuse_tracer import TRACING_ENABLED
from python.helpers.extension import Extension

class LangfuseInit(Extension):
    
    async def execute(self, **kwargs):
        """Initialize tracing for this agent"""
        print(f"[EXTENSION DEBUG] Agent init extension CALLED for {self.agent.agent_name}")
        print(f"[EXTENSION DEBUG] TRACING_ENABLED: {TRACING_ENABLED}")
        
        if TRACING_ENABLED:
            self.agent._langfuse_enabled = True
            print(f"[LangFuse] Agent {self.agent.agent_name} tracing enabled")
            print(f"[EXTENSION DEBUG] Set agent._langfuse_enabled = {self.agent._langfuse_enabled}")
        else:
            self.agent._langfuse_enabled = False
            print(f"[LangFuse] Agent {self.agent.agent_name} tracing disabled")