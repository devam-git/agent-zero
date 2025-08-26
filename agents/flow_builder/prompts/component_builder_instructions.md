# Langflow Integration Checklists

## Checklist: Adding a New Component Template
- [ ] The `template` dictionary is flat (no unnecessary nesting).
- [ ] All required fields from working JSONs are present (e.g., `background_color`, `chat_icon`, `input_value`, `sender`, `sender_name`, `should_store_message`, etc.).
- [ ] The `code` field is present and contains the **full Python implementation as a string** (not a stub or placeholder).
- [ ] The `template` dictionary includes `"_type": "Component"`.
- [ ] Field names, types, and default values match those in working JSONs.
- [ ] No extra or missing fields compared to the working JSON for that component type.
- [ ] The `outputs` and `selected_output` fields are present and correct.
- [ ] The `base_classes`, `description`, `display_name`, and `icon` fields are present and accurate.
- [ ] The template can be used to generate a valid workflow and imported into Langflow without errors.

## Checklist: Verifying a Newly Generated Workflow JSON
- [ ] All nodes have a `template` dictionary that matches the structure of working JSONs.
- [ ] Each node's `template` includes all required fields and the `code` field with the full implementation.
- [ ] The `outputs` and `selected_output` fields are present and correct for each node.
- [ ] All connections (edges) between nodes use valid handles and field names.
- [ ] No extra or missing fields in any node's `template` compared to the reference JSON.
- [ ] The workflow imports into Langflow without errors and all components function as expected.
- [ ] Default values (e.g., for `input_value`, `sender_name`, etc.) are set appropriately for the use case.
- [ ] The workflow description, tags, and metadata are accurate and helpful.
