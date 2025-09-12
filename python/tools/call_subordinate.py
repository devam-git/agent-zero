from agent import Agent, UserMessage
from python.helpers.tool import Tool, Response
from initialize import initialize_agent
from python.extensions.hist_add_tool_result import _90_save_tool_call_file as save_tool_call_file
import os
from python.helpers import files
import re

class Delegation(Tool):

    async def execute(self, message="", reset="", **kwargs):
        # create subordinate agent using the data object on this agent and set superior agent to his data object
        if (
            self.agent.get_data(Agent.DATA_NAME_SUBORDINATE) is None
            or str(reset).lower().strip() == "true"
        ):
            # initialize default config
            config = initialize_agent()

            # set subordinate prompt profile if provided, if not, keep original
            agent_profile = kwargs.get("profile")
            if agent_profile:
                # Normalize profile name
                profile = agent_profile.lower().strip().replace(" ", "_")
                sub_agents_dir = files.get_abs_path("agents")
                profile_dir = os.path.join(sub_agents_dir, profile)
                
                # Create profile if it doesn't exist and not default
                if profile != "agent0" and not os.path.isdir(profile_dir):
                    try:
                        system_prompt = self.agent.read_prompt("sub_create.md")
                        llm_response = await self.agent.call_utility_model(
                            system=system_prompt,
                            message=f"Create a sub-agent profile for '{profile}'."
                        )
                        
                        # Clean markdown formatting
                        cleaned = re.sub(r'```(?:markdown)?\s*|\s*```', '', llm_response, flags=re.MULTILINE).strip()
                        
                        # Create profile directory and files
                        os.makedirs(profile_dir, exist_ok=True)
                        with open(os.path.join(profile_dir, "_context.md"), "w") as f:
                            f.write(f"# {profile}\n - agent specialised in {profile}")
                        os.makedirs(os.path.join(profile_dir, "prompts"), exist_ok=True)
                        with open(os.path.join(profile_dir, "prompts", "agent.system.main.role.md"), "w") as f:
                            f.write(cleaned) 
                        self.agent.context.log.log(type="util", content=f"Created profile '{profile}'")
                            
                    except Exception as e:
                        self.agent.context.log.log(type="warning", content=f"Failed to create profile '{profile}': {e}")
                        profile = "agent0"
                elif profile != "agent0":
                    self.agent.context.log.log(type="util", content=f"Using existing profile '{profile}'")
                
                config.profile = profile

            # create agent
            sub = Agent(self.agent.number + 1, config, self.agent.context)
            # register superior/subordinate
            sub.set_data(Agent.DATA_NAME_SUPERIOR, self.agent)
            self.agent.set_data(Agent.DATA_NAME_SUBORDINATE, sub)

        # add user message to subordinate agent
        subordinate: Agent = self.agent.get_data(Agent.DATA_NAME_SUBORDINATE)  # type: ignore
        subordinate.hist_add_user_message(UserMessage(message=message, attachments=[]))

        # run subordinate monologue
        result = await subordinate.monologue()

        # hint to use includes for long responses
        additional = None
        if len(result) >= save_tool_call_file.LEN_MIN:
            hint = self.agent.read_prompt("fw.hint.call_sub.md")
            if hint:
                additional = {"hint": hint}

        # result
        return Response(message=result, break_loop=False, additional=additional)

    def get_log_object(self):
        return self.agent.context.log.log(
            type="tool",
            heading=f"icon://communication {self.agent.agent_name}: Calling Subordinate Agent",
            content="",
            kvps=self.args,
        )
