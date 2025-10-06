# Builder Checklists

## Checklist: Verifying a Newly Generated Workflow JSON
- [ ] All nodes have a `template` dictionary that matches the structure of working JSONs.
- [ ] Each node's `template` includes all required fields and the `code` field with the full implementation.
- [ ] The `outputs` and `selected_output` fields are present and correct for each node.
- [ ] All connections (edges) between nodes use valid handles and field names.
- [ ] No extra or missing fields in any node's `template` compared to the reference JSON.
- [ ] The workflow imports into Langflow without errors and all components function as expected.
- [ ] Default values (e.g., for `input_value`, `sender_name`, etc.) are set appropriately for the use case.
- [ ] The workflow description, tags, and metadata are accurate and helpful.
- [ ] Edge IDs contain raw `œ` characters (not `\u0153`) for proper Langflow connections.