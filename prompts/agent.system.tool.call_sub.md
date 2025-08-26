### call_subordinate

Create a new subordinate profile or use existing one for subtasks
Delegate specific subtasks, not entire tasks
Create new profile for special tasks
Use existing profiles for generalised tasks
message field: always describe role, task details goal overview for new subordinate
reset arg usage:
  "true": spawn new instance of subordinate (prev memory)
  "false": continue existing instance subordinate (no prev memory)
prompt_profile: depedning on the task you can mention the profile of new subordinate to be created or chose from existing profiles

**Important**: Be aware of your current agent profile and do NOT delegate to subordinates with the same profile as yourself. Choose different specialized profiles for subordinates.

example usage
```json
{
    "thoughts": [
        "The result seems to be ok but...",
        "I will create a financial analyst subordinate to...",
    ],
    "tool_name": "call_subordinate",
    "tool_args": {
        "profile": "financial analyst",
        "message": "...",
        "reset": "true"
    }
}
```

**available profiles:**
{{agent_profiles}}