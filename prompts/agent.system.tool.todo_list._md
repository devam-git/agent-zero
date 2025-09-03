### To-Do List:
Manage tasks and subtasks in a simple txt-based to-do list for structured planning and progress tracking. Each agent has its own persistent file (todo.txt), with support for adding, completing, uncompleting, deleting, clearing, and listing tasks.

**When to use**:
- **Complex multi-step problems**: Break down into manageable tasks with clear tracking
- **Conversation start**: Use `bulk_add` to quickly establish all required tasks
- **Progress tracking**: Regular `update` calls to mark completion and add notes
- **Plan changes**: Use `delete` for obsolete tasks, `add` for new requirements

**Parameters**:
- action: str
Operations: "add", "update", "delete", "clear", "list", "bulk_add"

- title: str (required for add/update/delete)
Task title for individual operations

- description: str (optional)
Task details and context

- notes: str (optional)
Additional notes and progress logs

- parent: str (optional)
Parent task title for creating subtasks

- done: bool (optional)
Task completion status (true/false)

- todos: list (required for bulk_add)
List of tasks - can be strings or objects with {title, description, notes}

- clear_first: str (optional, default "true")
Whether to clear existing todos before bulk adding

- reset: str (optional)
"true" for new conversations/topics, "false" to continue existing work

**Actions**:
- **bulk_add**: Clear list and add multiple tasks at once. Use at conversation start.
- **add**: Single task creation. Use for new requirements during work.
- **update**: Mark done or add progress notes. Use frequently to track completion.
- **delete**: Remove obsolete tasks. Use when plans change.
- **clear**: Reset entire list. Use sparingly.
- **list**: View current todos. Use to stay oriented.

**Storage**:
Tasks are stored in a markdown file (todo.txt) inside an agent-specific directory under data/.

**Usage Examples**:

**Start conversation with multiple tasks:**
```json
{
    "tool_name": "todo_list",
    "tool_args": {
        "action": "bulk_add",
        "todos": [
            "Analyze user requirements",
            {"title": "Design database schema", "description": "Create tables for users and orders"},
            {"title": "Implement API endpoints", "notes": "Focus on authentication first"}
        ]
    }
}
```

**Add single task:**
```json
{
    "tool_name": "todo_list",
    "tool_args": {
        "action": "add",
        "title": "Fix login bug",
        "parent": "Implement API endpoints"
    }
}
```

**Mark task complete:**
```json
{
    "tool_name": "todo_list",
    "tool_args": {
        "action": "update",
        "title": "Analyze user requirements",
        "done": true,
        "notes": "Found 3 core features needed"
    }
}
```

**Best Practices**:
- **Start fast**: Use `bulk_add` at conversation beginning to establish all tasks
- **Stay current**: Mark tasks done immediately upon completion with progress notes
- **Adapt quickly**: Delete obsolete tasks when requirements change
- **Track progress**: Use notes field for important findings and context
- **Stay focused**: Regularly `list` to review objectives and remaining work