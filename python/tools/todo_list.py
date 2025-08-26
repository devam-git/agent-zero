from pathlib import Path
from python.helpers.tool import Tool, Response

class Todo(Tool):
    def __init__(self, agent, name: str, method: str | None, args: dict[str,str], message: str, loop_data=None, **kwargs):
        super().__init__(agent, name, method, args, message, loop_data, **kwargs)
        self.base_dir = Path("a0/data") / f"{agent.number}_{agent.config.profile}"
        self.file = self.base_dir / "todo.txt"

        self.base_dir.mkdir(parents=True, exist_ok=True)
        if not self.file.exists():
            self.file.write_text("# To-Do List\n", encoding="utf-8")

    def _read(self) -> list[str]:
        return self.file.read_text(encoding="utf-8").splitlines()

    def _write(self, lines: list[str]):
        content = "\n".join(lines)
        self.file.write_text(content, encoding="utf-8")

    async def execute(self, **kwargs) -> Response:
        action = self.args.get("action", "list")
        reset = self.args.get("reset", "false").lower() == "true"
        
        if reset:
            self.clear()
            return Response(message="Todo list has been reset for new conversation.", break_loop=False)
        
        if action == "add":
            title = self.args.get("title", "")
            description = self.args.get("description", "")
            parent = self.args.get("parent", None)
            notes = self.args.get("notes", "")
            self.add_task(title, description, parent, notes)
            return Response(message=f"Added task. Here is the list:\n{self.print_list()}", break_loop=False)
            
        elif action == "delete":
            title = self.args.get("title", "")
            self.delete_task(title)
            return Response(message=f"Deleted task. Here is the list:\n{self.print_list()}", break_loop=False)
            
        elif action == "clear":
            self.clear()
            return Response(message="Cleared all tasks.", break_loop=False)

        elif action == "update":
            title = self.args.get("title", "")
            description = self.args.get("description", "")
            parent = self.args.get("parent", None)
            notes = self.args.get("notes", "")
            done = self.args.get("done", False)
            self.update_task(title, description, parent, notes, done)
            return Response(message=f"Updated task. Here is the list:\n{self.print_list()}", break_loop=False)
        
        elif action == "list":
            content = self.print_list()
            return Response(message=f"To-Do List:\n{content}", break_loop=False)

    def add_task(self, title: str, description: str = "", parent: str = None, notes: str = ""):
        lines = self._read()
        task_line = f"- [ ] {title}" + (f" — {description}" if description else "")
        if notes:
            task_line += f"\n  {notes}"

        if parent:
            new_lines = []
            inserted = False
            for line in lines:
                new_lines.append(line)
                if parent in line and line.strip().startswith("- ["):
                    new_lines.append(f"  {task_line}")
                    inserted = True
            lines = new_lines if inserted else lines + [task_line]
        else:
            lines.append(task_line)

        self._write(lines)

    def update_task(self, title: str, description: str = "", parent: str = None, notes: str = "", done: bool = False):
        lines = self._read()
        for i, line in enumerate(lines):
            if title in line and line.strip().startswith("- ["):
                # Build the new line with updated checkbox, title, and description
                checkbox = "- [x]" if done else "- [ ]"
                new_line = f"{checkbox} {title}"
                if description:
                    new_line += f" — {description}"
                if notes:
                    new_line += f"\n  {notes}"
                lines[i] = new_line
                break
        self._write(lines)

    def delete_task(self, title: str):
        lines = self._read()
        lines = [line for line in lines if title not in line]
        self._write(lines)

    def clear(self):
        self._write(["# To-Do List", ""])

    def print_list(self) -> str:
        return "\n".join(self._read())
