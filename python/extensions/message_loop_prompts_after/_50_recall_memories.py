import asyncio
from python.helpers.extension import Extension
from python.helpers.memory import Memory
from agent import LoopData
from python.tools.memory_load import DEFAULT_THRESHOLD as DEFAULT_MEMORY_THRESHOLD
from python.helpers import dirty_json, errors, settings, log 


DATA_NAME_TASK = "_recall_memories_task"
DATA_NAME_ITER = "_recall_memories_iter"


class RecallMemories(Extension):

    # INTERVAL = 3
    # HISTORY = 10000
    # MEMORIES_MAX_SEARCH = 12
    # SOLUTIONS_MAX_SEARCH = 8
    # MEMORIES_MAX_RESULT = 5
    # SOLUTIONS_MAX_RESULT = 3
    # THRESHOLD = DEFAULT_MEMORY_THRESHOLD

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):

        set = settings.get_settings()

        # turned off in settings?
        if not set["memory_recall_enabled"]:
            return

        # every X iterations (or the first one) recall memories
        if loop_data.iteration % set["memory_recall_interval"] == 0:

            # show util message right away
            log_item = self.agent.context.log.log(
                type="util",
                heading="Searching memories...",
            )

            # Create memory search task without tracing yet - we'll set up tracing inside with the actual query
            task = asyncio.create_task(
                self.search_memories(loop_data=loop_data, log_item=log_item, **kwargs)
            )
        else:
            task = None

        # set to agent to be able to wait for it
        self.agent.set_data(DATA_NAME_TASK, task)
        self.agent.set_data(DATA_NAME_ITER, loop_data.iteration)

    async def search_memories(self, log_item: log.LogItem, loop_data: LoopData, **kwargs):
        # cleanup previous memories/solutions
        extras = loop_data.extras_persistent
        if "memories" in extras:
            del extras["memories"]
        if "solutions" in extras:
            del extras["solutions"]

        set = settings.get_settings()

        # Set up Langfuse tracing at the start
        span_context = None
        span = None
        try:
            from langfuse import get_client
            langfuse = get_client()
            span_context = langfuse.start_as_current_span(name="memory-search")
            span = span_context.__enter__()
        except ImportError:
            pass
        except Exception:
            pass

        try:
            # get system message and chat history for util llm
            system = self.agent.read_prompt("memory.memories_query.sys.md")

            # log query streamed by LLM
            async def log_callback(content):
                log_item.stream(query=content)

            # prepare conversation context
            user_instruction = (
                loop_data.user_message.output_text() if loop_data.user_message else "None"
            )
            history = self.agent.history.output_text()[-set["memory_recall_history_len"]:]
            message = self.agent.read_prompt(
                "memory.memories_query.msg.md", history=history, message=user_instruction
            )

            # generate or use direct query
            if set["memory_recall_query_prep"]:
                try:
                    query = await self.agent.call_utility_model(
                        system=system,
                        message=message,
                        callback=log_callback,
                        background=True,
                    )
                    query = query.strip()
                except Exception as e:
                    err = errors.format_error(e)
                    self.agent.context.log.log(
                        type="error", heading="Recall memories extension error:", content=err
                    )
                    query = ""
            else:
                query = user_instruction + "\n\n" + history

            # Update span with input query (even if empty or just "-")
            if span:
                input_text = query[:200] + "..." if len(query) > 200 else query
                if not query or len(query) <= 3:
                    input_text = f"Query: '{query}' (too short for search)"
                span.update(input=input_text)

            # if there is no meaningful query, return early with trace
            if not query or len(query) <= 3:
                log_item.update(
                    query="No relevant memory query generated, skipping search",
                )
                if span and span_context:
                    span.update(output="No meaningful query generated - search skipped")
                    span_context.__exit__(None, None, None)
                return

            # get memory database and search
            db = await Memory.get(self.agent)

            # search for general memories and fragments
            memories = await db.search_similarity_threshold(
                query=query,
                limit=set["memory_recall_memories_max_search"],
                threshold=set["memory_recall_similarity_threshold"],
                filter=f"area == '{Memory.Area.MAIN.value}' or area == '{Memory.Area.FRAGMENTS.value}'",
            )

            # search for solutions
            solutions = await db.search_similarity_threshold(
                query=query,
                limit=set["memory_recall_solutions_max_search"],
                threshold=set["memory_recall_similarity_threshold"],
                filter=f"area == '{Memory.Area.SOLUTIONS.value}'",
            )

            if not memories and not solutions:
                log_item.update(heading="No memories or solutions found")
                if span and span_context:
                    span.update(output="No relevant memories or solutions found")
                    span_context.__exit__(None, None, None)
                return

            # optional post-filtering with AI validation
            if set["memory_recall_post_filter"]:
                mems_list = {i: memory.page_content for i, memory in enumerate(memories + solutions)}
                try:
                    filter = await self.agent.call_utility_model(
                        system=self.agent.read_prompt("memory.memories_filter.sys.md"),
                        message=self.agent.read_prompt(
                            "memory.memories_filter.msg.md",
                            memories=mems_list,
                            history=history,
                            message=user_instruction,
                        ),
                        background=True,
                    )
                    filter_inds = dirty_json.try_parse(filter)

                    # filter memories and solutions based on validated indices
                    if isinstance(filter_inds, list):
                        filtered_memories = []
                        filtered_solutions = []
                        mem_len = len(memories)
                        for idx in filter_inds:
                            if isinstance(idx, int):
                                if idx < mem_len:
                                    filtered_memories.append(memories[idx])
                                else:
                                    sol_idx = idx - mem_len
                                    if sol_idx < len(solutions):
                                        filtered_solutions.append(solutions[sol_idx])
                        memories = filtered_memories
                        solutions = filtered_solutions

                except Exception as e:
                    err = errors.format_error(e)
                    self.agent.context.log.log(
                        type="error", heading="Failed to filter relevant memories", content=err
                    )

            # limit final results
            memories = memories[: set["memory_recall_memories_max_result"]]
            solutions = solutions[: set["memory_recall_solutions_max_result"]]

            # prepare results
            memories_txt = "\n\n".join([mem.page_content for mem in memories]) if memories else ""
            solutions_txt = "\n\n".join([sol.page_content for sol in solutions]) if solutions else ""

            # update UI log
            log_item.update(heading=f"{len(memories)} memories and {len(solutions)} relevant solutions found")
            if memories_txt:
                log_item.update(memories=memories_txt)
            if solutions_txt:
                log_item.update(solutions=solutions_txt)

            # update Langfuse span with results
            if span and span_context:
                output_content = f"Found {len(memories)} memories and {len(solutions)} solutions"
                if memories_txt:
                    output_content += f"\n\nMEMORIES:\n{memories_txt[:300]}..."
                if solutions_txt:
                    output_content += f"\n\nSOLUTIONS:\n{solutions_txt[:200]}..."
                span.update(output=output_content)
                span_context.__exit__(None, None, None)

            # add to prompt context
            if memories_txt:
                extras["memories"] = self.agent.parse_prompt(
                    "agent.system.memories.md", memories=memories_txt
                )
            if solutions_txt:
                extras["solutions"] = self.agent.parse_prompt(
                    "agent.system.solutions.md", solutions=solutions_txt
                )

        except Exception as e:
            # ensure span is closed even on error
            if span and span_context:
                span.update(output=f"Error during memory search: {str(e)}")
                span_context.__exit__(None, None, None)
            raise
