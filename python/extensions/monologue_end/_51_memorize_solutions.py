import asyncio
from python.helpers import settings
from python.helpers.extension import Extension
from python.helpers.memory import Memory
from python.helpers.dirty_json import DirtyJson
from agent import LoopData
from python.helpers.log import LogItem
from python.tools.memory_load import DEFAULT_THRESHOLD as DEFAULT_MEMORY_THRESHOLD


class MemorizeSolutions(Extension):

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        # try:

        set = settings.get_settings()

        if not set["memory_memorize_enabled"]:
            return
 
        # show full util message
        log_item = self.agent.context.log.log(
            type="util",
            heading="Memorizing succesful solutions...",
        )

        # memorize in background
        task = asyncio.create_task(self.memorize(loop_data, log_item))
        return task

    async def memorize(self, loop_data: LoopData, log_item: LogItem, **kwargs):

        set = settings.get_settings()

        db = await Memory.get(self.agent)

        # get system message and chat history for util llm
        system = self.agent.read_prompt("memory.solutions_sum.sys.md")
        msgs_text = self.agent.concat_messages(self.agent.history)

        # log query streamed by LLM
        async def log_callback(content):
            log_item.stream(content=content)

        # Set up Langfuse tracing for solution memorization
        span_context = None
        span = None
        try:
            from langfuse import get_client
            langfuse = get_client()
            span_context = langfuse.start_as_current_span(name="solution-memorization")
            span = span_context.__enter__()
            span.update(input=f"Analyzing conversation for solutions (length: {len(msgs_text)} chars)")
        except ImportError:
            pass
        except Exception:
            pass

        try:
            # call util llm to find solutions in history
            solutions_json = await self.agent.call_utility_model(
                system=system,
                message=msgs_text,
                callback=log_callback,
                background=True,
            )

            # validate and parse solutions response
            if not solutions_json or not isinstance(solutions_json, str):
                log_item.update(heading="No response from utility model.")
                if span and span_context:
                    span.update(output="No response from utility model")
                    span_context.__exit__(None, None, None)
                return

            solutions_json = solutions_json.strip()
            if not solutions_json:
                log_item.update(heading="Empty response from utility model.")
                if span and span_context:
                    span.update(output="Empty response from utility model")
                    span_context.__exit__(None, None, None)
                return

            try:
                solutions = DirtyJson.parse_string(solutions_json)
            except Exception as e:
                log_item.update(heading=f"Failed to parse solutions response: {str(e)}")
                if span and span_context:
                    span.update(output=f"Failed to parse solutions: {str(e)}")
                    span_context.__exit__(None, None, None)
                return

            # normalize to list format
            if solutions is None:
                log_item.update(heading="No valid solutions found in response.")
                if span and span_context:
                    span.update(output="No valid solutions found")
                    span_context.__exit__(None, None, None)
                return

            if not isinstance(solutions, list):
                if isinstance(solutions, (str, dict)):
                    solutions = [solutions]
                else:
                    log_item.update(heading="Invalid solutions format received.")
                    if span and span_context:
                        span.update(output="Invalid solutions format")
                        span_context.__exit__(None, None, None)
                    return

            if not solutions:
                log_item.update(heading="No successful solutions to memorize.")
                if span and span_context:
                    span.update(output="No solutions to memorize")
                    span_context.__exit__(None, None, None)
                return

            solutions_txt = "\n\n".join([str(solution) for solution in solutions]).strip()
            log_item.update(
                heading=f"{len(solutions)} successful solutions to memorize.", solutions=solutions_txt
            )

            # process and memorize solutions
            total_processed = 0
            total_consolidated = 0
            
            for solution in solutions:
                # convert solution to structured text
                if isinstance(solution, dict):
                    problem = solution.get('problem', 'Unknown problem')
                    solution_text = solution.get('solution', 'Unknown solution')
                    txt = f"# Problem\n {problem}\n# Solution\n {solution_text}"
                else:
                    txt = f"# Solution\n {str(solution)}"

                if set["memory_memorize_consolidation"]:
                    try:
                        from python.helpers.memory_consolidation import create_memory_consolidator
                        consolidator = create_memory_consolidator(
                            self.agent,
                            similarity_threshold=DEFAULT_MEMORY_THRESHOLD,
                            max_similar_memories=6,
                            max_llm_context_memories=3
                        )

                        result_obj = await consolidator.process_new_memory(
                            new_memory=txt,
                            area=Memory.Area.SOLUTIONS.value,
                            metadata={"area": Memory.Area.SOLUTIONS.value},
                            log_item=None
                        )

                        if result_obj.get("success"):
                            total_consolidated += 1
                        total_processed += 1

                    except Exception as e:
                        log_item.update(consolidation_error=str(e))
                        total_processed += 1
                else:
                    # simple memorization without consolidation
                    if set["memory_memorize_replace_threshold"] > 0:
                        await db.delete_documents_by_query(
                            query=txt,
                            threshold=set["memory_memorize_replace_threshold"],
                            filter=f"area=='{Memory.Area.SOLUTIONS.value}'",
                        )
                    await db.insert_text(text=txt, metadata={"area": Memory.Area.SOLUTIONS.value})

            # update final results
            if set["memory_memorize_consolidation"]:
                result_msg = f"{total_processed} solutions processed, {total_consolidated} intelligently consolidated"
                log_item.update(
                    heading=f"Solution memorization completed: {result_msg}",
                    result=result_msg,
                    solutions_processed=total_processed,
                    solutions_consolidated=total_consolidated,
                )
                if span and span_context:
                    span.update(output=f"Processed {total_processed} solutions, {total_consolidated} consolidated")
                    span_context.__exit__(None, None, None)
            else:
                result_msg = f"{len(solutions)} solutions memorized"
                log_item.update(heading=result_msg, result=result_msg)
                if span and span_context:
                    span.update(output=f"Memorized {len(solutions)} solutions: {solutions_txt[:200]}...")
                    span_context.__exit__(None, None, None)

        except Exception as e:
            # ensure span is closed even on error
            if span and span_context:
                span.update(output=f"Error during solution memorization: {str(e)}")
                span_context.__exit__(None, None, None)
            raise

