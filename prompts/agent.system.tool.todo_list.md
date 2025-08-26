### To-Do List:
Manage tasks and subtasks in a simple txt-based to-do list for structured planning and progress tracking. Each agent has its own persistent file (todo.txt), with support for adding, completing, uncompleting, deleting, clearing, and listing tasks.

**When to use**:
Use this tool when you are solving a complex problem with structured planning. Keep creatinf=g, managing and updating tasks (parent/subtask).
And keep refering to the list to keep track of your objectives.

**Parameters**:
- action: str
The operation to perform. Possible values are: "add", "update", "delete", "clear", "list".

- title: str (optional but usually required)
The title of the task to add, complete, uncomplete, or delete.

- description: str (optional)
Details for a task when creating it.

- notes: str (optional)
Additonal notes about a task and its solving.

- parent: str (optional)
The title of an existing task to nest a new subtask under.

- done: bool
status of the task, "true" if completed, "else" false.

- reset: str (optional)
"true" if you want to use a fresh new todo list (for new topics/conversations)
"false" if you want to use the same existing list (for same topics/conversations)

Strictly set reset="true" for a new conversation or a conversation on a seperate topic

**Actions**:
- add: Creates a new top-level task, or a subtask if parent is provided. Requires title.
- update: Update the status or add any logs/notes to the task. Requires title.
- delete: Removes a task (and any subtasks under it). Requires title.
- clear: Clears all tasks from the list. No parameters required.
- list: Returns the full to-do list as text. No parameters required.

**Storage**:
Tasks are stored in a markdown file (todo.txt) inside an agent-specific directory under data/.

**Usage**:
```json
{
    "thoughts": [
        "This looks like a new project, so I should add a main task."
    ],
    "headline": "Adding a top-level task",
    "tool_name": "todo_list",
    "tool_args": {
        "action": "add",
        "title": "Prepare quarterly business report",
        "description": "Compile and analyze revenue and expense data"
    }
}
{
    "thoughts": [
        "Now I'll add a subtask under the report task."
    ],
    "headline": "Adding a subtask",
    "tool_name": "todo_list",
    "tool_args": {
        "action": "add",
        "parent": "Prepare quarterly business report",
        "title": "Collect revenue data",
        "description": "Gather revenue figures from all departments"
    }
}
{
    "thoughts": [
        "The first subtask is complete, I should mark it as done."
    ],
    "headline": "Completing a subtask",
    "tool_name": "todo_list",
    "tool_args": {
        "action": "update",
        "title": "Collect revenue data",
        "done" : true
    }
}
```

**Tips**:
- Complete all to-dos in the list for success criteria
- Can change the list if you find a better plan/approach or stuck on one problem
- Regularly refer the to-do for objectives and keep updating the status 
- Use the notes field for important content regarding that task