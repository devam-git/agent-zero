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

**CRITICAL RULE**: 
- **YOUR CURRENT PROFILE: {{profile}}**
- **NEVER delegate to subordinates with profile "{{profile}}" - this will cause infinite recursion**
- **ALWAYS choose a DIFFERENT specialized profile for subordinates**
- **If task matches your current specialization, handle it yourself instead of delegating**

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
**Current Agent Info**:
Agent Number: {{number}}
Profile: {{profile}}

**Available profiles:**
{{agent_profiles}}