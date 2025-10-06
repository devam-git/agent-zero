# from langflow.field_typing import Data
from contextlib import AsyncExitStack
import asyncio
import httpx
import logging
from typing import Optional
from mcp import ClientSession, types
from mcp.client.sse import sse_client
from langchain_core.tools import StructuredTool

from langflow.base.mcp.util import create_tool_coroutine, create_tool_func, create_input_schema_from_json_schema
from langflow.custom import Component
from langflow.field_typing import Tool
from langflow.io import MessageTextInput, Output

logger = logging.getLogger(__name__)


class SSEOptimizedMCPClient:
    """MCP client optimized for SSE connection issues"""
    
    def __init__(self):
        # Connection state
        self.session: Optional[ClientSession] = None
        self.sse = None
        self.write = None
        self.exit_stack = AsyncExitStack()
        
        # Connection management
        self._connection_lock = asyncio.Lock()
        
        # Timeouts based on diagnostic results
        self.basic_timeout = 7      # Basic connectivity (5s + 2s safety)
        self.sse_timeout = 25       # SSE streaming needs more time
        self.operation_timeout = 10 # Individual operations
        self.retry_delay = 2        # Delay between retries

    async def _wait_for_server_ready(self, url: str) -> bool:
        """Wait for server to be ready before attempting SSE"""
        logger.debug("Checking if server is ready for SSE connection")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient(timeout=self.basic_timeout) as client:
                    response = await client.head(url)
                    if response.status_code == 200:
                        logger.debug(f"Server ready on attempt {attempt + 1}")
                        return True
            except Exception as e:
                logger.debug(f"Server readiness check {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)  # Brief wait between checks
        
        return False

    async def _create_sse_connection_with_retries(self, url: str, headers: Optional[dict[str, str]] = None) -> list[types.Tool]:
        """Create SSE connection with specific retry strategy for SSE issues"""
        if headers is None:
            headers = {}
        
        logger.info(f"Creating SSE connection with retries to: {url}")
        await self._cleanup_connection()
        
        # Wait for server to be ready first
        if not await self._wait_for_server_ready(url):
            raise ValueError("Server not responding to readiness checks")
        
        # Try SSE connection with progressive timeouts
        sse_timeouts = [15, 25, 35]  # Progressive SSE timeouts
        
        for attempt, sse_timeout in enumerate(sse_timeouts):
            try:
                logger.info(f"SSE attempt {attempt + 1}/{len(sse_timeouts)} with {sse_timeout}s timeout")
                
                async with asyncio.timeout(sse_timeout + 5):  # Add buffer to asyncio timeout
                    # Create SSE client with current timeout
                    sse_transport = await self.exit_stack.enter_async_context(
                        sse_client(url, headers, self.basic_timeout, sse_timeout)
                    )
                    self.sse, self.write = sse_transport
                    logger.debug(f"SSE transport created with {sse_timeout}s timeout")
                    
                    # Create and initialize session quickly
                    async with asyncio.timeout(self.operation_timeout):
                        self.session = await self.exit_stack.enter_async_context(
                            ClientSession(self.sse, self.write)
                        )
                        await self.session.initialize()
                        logger.debug("Session initialized successfully")
                    
                    # Get tools quickly
                    async with asyncio.timeout(self.operation_timeout):
                        response = await self.session.list_tools()
                        logger.info(f"Successfully connected with {sse_timeout}s timeout, found {len(response.tools)} tools")
                        return response.tools
                
            except asyncio.TimeoutError:
                logger.warning(f"SSE attempt {attempt + 1} timed out after {sse_timeout}s")
                await self._cleanup_connection()
                if attempt < len(sse_timeouts) - 1:
                    logger.info(f"Waiting {self.retry_delay}s before next attempt")
                    await asyncio.sleep(self.retry_delay)
                continue
                
            except Exception as e:
                logger.warning(f"SSE attempt {attempt + 1} failed: {str(e)}")
                await self._cleanup_connection()
                if attempt < len(sse_timeouts) - 1:
                    # For non-timeout errors, wait a bit longer
                    wait_time = self.retry_delay * (attempt + 1)
                    logger.info(f"Waiting {wait_time}s before next attempt")
                    await asyncio.sleep(wait_time)
                continue
        
        # All attempts failed
        raise ValueError("All SSE connection attempts failed - server may be overloaded")

    async def _cleanup_connection(self):
        """Clean up connection resources"""
        try:
            if self.exit_stack:
                await asyncio.wait_for(self.exit_stack.aclose(), timeout=5)
        except Exception as e:
            logger.debug(f"Cleanup error (ignored): {e}")
        finally:
            self.session = None
            self.sse = None
            self.write = None
            self.exit_stack = AsyncExitStack()

    async def _is_session_healthy(self) -> bool:
        """Quick health check"""
        if not self.session:
            return False
        try:
            async with asyncio.timeout(5):
                await self.session.list_tools()
                return True
        except Exception:
            return False

    async def get_tools_optimized(self, url: str, headers: Optional[dict[str, str]] = None) -> list[types.Tool]:
        """Get tools with SSE optimization"""
        async with self._connection_lock:
            try:
                # Check if existing session is healthy
                if self.session and await self._is_session_healthy():
                    logger.debug("Using existing healthy session")
                    async with asyncio.timeout(self.operation_timeout):
                        response = await self.session.list_tools()
                        return response.tools
                
                # Need new connection
                logger.info("Creating new SSE-optimized connection")
                return await self._create_sse_connection_with_retries(url, headers)
                
            except Exception as e:
                await self._cleanup_connection()
                raise ValueError(f"Optimized connection failed: {str(e)}")

    async def close(self):
        """Close connection"""
        async with self._connection_lock:
            await self._cleanup_connection()

    async def run_tool(self, tool_name: str, arguments: dict) -> str:
        """Run a tool with the given arguments."""
        if not self.session:
            raise ValueError("Session not initialized. Call get_tools_optimized first.")
        
        try:
            result = await self.session.call_tool(tool_name, arguments=arguments)
            return str(result)
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {e}")
            raise ValueError(f"Tool '{tool_name}' execution failed: {e}") from e


class QpiAIMCPSse(Component):
    display_name = "QpiAI MCP Tools"
    description = "Connects to QpiAI hosted remote MCP servers with SSE optimization."
    icon = "QpiAI"
    name = "QpiAI MCP Tools"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = SSEOptimizedMCPClient()
        self.tools = []
        self.tool_names = []

    inputs = [
        MessageTextInput(
            name="tool_api_url",
            display_name="tool_api_url",
            info="sse url",
            value="",
            tool_mode=False,
        ),
        MessageTextInput(
            name="tool_api_credentials",
            display_name="tool_api_credentials",
            info="sse url", 
            value="",
            tool_mode=False,
        ),
        MessageTextInput(
            name="tool_name",
            display_name="tool_name",
            info="sse url",
            value="gmail",
            tool_mode=False,
        ),
    ]

    outputs = [
        Output(display_name="Tools", name="tools", method="build_output"),
    ]

    async def build_output(self) -> list[Tool]:
        """Build tools with SSE-optimized connection"""
        
        async def _build_with_sse_optimization():
            try:
                url = f"{self.tool_api_url}/{self.tool_name}/{self.tool_api_credentials}"
                logger.info(f"Building tools for {self.tool_name} service")
                logger.info(f"Using SSE-optimized timeouts: basic={self.client.basic_timeout}s, sse={self.client.sse_timeout}s")
                
                # Get tools with SSE optimization
                self.tools = await self.client.get_tools_optimized(url)
                
                if not self.tools:
                    raise ValueError("No tools returned from server")
                
                # Create Langflow tools
                tool_list = []
                for mcp_tool in self.tools:
                    try:
                        args_schema = create_input_schema_from_json_schema(mcp_tool.inputSchema)
                        
                        langflow_tool = StructuredTool(
                            name=mcp_tool.name,
                            description=mcp_tool.description,
                            coroutine=create_tool_coroutine(mcp_tool.name, args_schema, self.client),
                            func=create_tool_func(mcp_tool.name, args_schema, self.client),
                            args_schema=args_schema,
                            handle_tool_error=True
                        )
                        tool_list.append(langflow_tool)
                        logger.debug(f"Created tool: {mcp_tool.name}")
                        
                    except Exception as e:
                        logger.error(f"Failed to create tool {mcp_tool.name}: {e}")
                        continue
                
                if not tool_list:
                    raise ValueError("No tools were successfully created")
                
                self.tool_names = [tool.name for tool in self.tools]
                logger.info(f"Successfully created {len(tool_list)} tools: {self.tool_names}")
                return tool_list
                
            except Exception as e:
                logger.error(f"SSE-optimized build failed: {e}")
                raise ValueError(f"Build failed: {str(e)}")
        
        # Shield the build process with generous timeout for SSE issues
        try:
            return await asyncio.wait_for(
                asyncio.shield(_build_with_sse_optimization()),
                timeout=90  # Allow time for SSE retries (3 attempts × 35s max + buffer)
            )
        except asyncio.TimeoutError:
            error_msg = "Build timed out after 90s - SSE connection issues persist"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except asyncio.CancelledError:
            error_msg = "Build cancelled by Langflow"
            logger.warning(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Build failed: {str(e)}"
            logger.error(error_msg) 
            raise ValueError(error_msg)

    async def cleanup(self):
        """Cleanup for Langflow"""
        try:
            await self.client.close()
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")