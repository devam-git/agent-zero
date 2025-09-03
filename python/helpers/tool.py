from abc import abstractmethod
from dataclasses import dataclass
import functools

from agent import Agent, LoopData
from python.helpers.print_style import PrintStyle
from python.helpers.strings import sanitize_string
from python.helpers.langfuse_tracer import observe

@dataclass
class Response:
    message: str
    break_loop: bool

class Tool:

    def __init__(self, agent: Agent, name: str, method: str | None, args: dict[str,str], message: str, loop_data: LoopData | None, **kwargs) -> None:
        self.agent = agent
        self.name = name
        self.method = method
        self.args = args
        self.loop_data = loop_data
        self.message = message
        
        # Initialize tracing if not already set
        from python.helpers.langfuse_tracer import TRACING_ENABLED
        
        print(f"[TOOL DEBUG] Tool {self.name} created for {agent.agent_name}")
        print(f"[TOOL DEBUG] observe available: {observe is not None}")
        print(f"[TOOL DEBUG] TRACING_ENABLED: {TRACING_ENABLED}")
        print(f"[TOOL DEBUG] agent has _langfuse_enabled: {hasattr(agent, '_langfuse_enabled')}")
        
        if not hasattr(agent, '_langfuse_enabled'):
            agent._langfuse_enabled = TRACING_ENABLED
            print(f"[TOOL DEBUG] Set agent._langfuse_enabled = {TRACING_ENABLED}")
        
        print(f"[TOOL DEBUG] Final agent._langfuse_enabled: {getattr(agent, '_langfuse_enabled', 'NOT SET')}")
        
        # Wrap execute with tracing if available and enabled
        if observe and agent._langfuse_enabled:
            self._wrap_with_tracing()
            print(f"[TOOL DEBUG] Tool {self.name} wrapped with tracing")
        else:
            print(f"[TOOL DEBUG] Tool {self.name} NOT wrapped - observe:{observe is not None}, enabled:{agent._langfuse_enabled}")

    def _wrap_with_tracing(self):
        """Wrap execute method with LangFuse span under main trace"""
        original_execute = self.execute
        
        @functools.wraps(original_execute)
        async def traced_execute(**kwargs):
            # Check if we have a main span to attach to
            if hasattr(self.agent, '_langfuse_main_span') and self.agent._langfuse_main_span:
                from python.helpers.langfuse_tracer import client
                if client:
                    try:
                        # Create span under main trace using context manager
                        with client.start_as_current_span(
                            name=f"Tool: {self.name}",
                            input={
                                "tool_name": self.name,
                                "tool_method": self.method,
                                "args": {k: (str(v)[:200] if len(str(v)) > 200 else v) 
                                        for k, v in (self.args or {}).items()}
                            }
                        ) as span:
                            print(f"[LangFuse] Executing tool span: {self.name}")
                            result = await original_execute(**kwargs)
                            
                            # Update span with result
                            span.update(
                                output={
                                    "message": result.message[:500] if len(result.message) > 500 else result.message,
                                    "break_loop": result.break_loop,
                                    "success": True
                                }
                            )
                            print(f"[LangFuse] Tool span completed: {self.name}")
                            return result
                    except Exception as e:
                        print(f"[LangFuse] Tool span failed: {self.name} - {e}")
                        # Still execute the tool even if tracing fails
                        return await original_execute(**kwargs)
                else:
                    return await original_execute(**kwargs)
            else:
                return await original_execute(**kwargs)
        
        self.execute = traced_execute

    @abstractmethod
    async def execute(self, **kwargs) -> Response:
        pass

    async def before_execution(self, **kwargs):
        PrintStyle(font_color="#1B4F72", padding=True, background_color="white", bold=True).print(f"{self.agent.agent_name}: Using tool '{self.name}'")
        self.log = self.get_log_object()
        
        if self.args and isinstance(self.args, dict):
            for key, value in self.args.items():
                PrintStyle(font_color="#85C1E9", bold=True).stream(self.nice_key(key)+": ")
                PrintStyle(font_color="#85C1E9", padding=isinstance(value,str) and "\n" in value).stream(value)
                PrintStyle().print()

    async def after_execution(self, response: Response, **kwargs):
        text = sanitize_string(response.message.strip())
        self.agent.hist_add_tool_result(self.name, text)
        PrintStyle(font_color="#1B4F72", background_color="white", padding=True, bold=True).print(f"{self.agent.agent_name}: Response from tool '{self.name}'")
        PrintStyle(font_color="#85C1E9").print(text)
        self.log.update(content=text)

    def get_log_object(self):
        if self.method:
            heading = f"icon://construction {self.agent.agent_name}: Using tool '{self.name}:{self.method}'"
        else:
            heading = f"icon://construction {self.agent.agent_name}: Using tool '{self.name}'"
        return self.agent.context.log.log(type="tool", heading=heading, content="", kvps=self.args)

    def nice_key(self, key: str):
        words = key.split('_')
        words = [words[0].capitalize()] + [word.lower() for word in words[1:]]
        result = ' '.join(words)
        return result