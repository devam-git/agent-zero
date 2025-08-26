import json
import uuid
import re
from typing import Dict, List, Any, Tuple, Optional

# Add import for new component templates
from component_templates import NEW_COMPONENT_TEMPLATES
import os

class LangflowBuilder:
    """
    Create Langflow workflows programmatically with proper connection handling.
    
    ⚠️ CRITICAL: Dynamic prompt fields MUST use input_types: ["Message"] for connections to work.
    
    Usage:
        builder = LangflowBuilder("Workflow Name", "Description")
        builder.add_component("input", "ChatInput", {"input_value": "Hello"})
        builder.add_dynamic_prompt("prompt", "Analyze: {user_text}", {
            "user_text": {"input_types": ["Message"], "required": True}
        })
        builder.add_component("llm", "LanguageModel", {"provider": "OpenAI"})
        builder.connect("input", "prompt")  # message → user_text
        builder.connect("prompt", "llm")    # prompt → input_value
        workflow = builder.build()
    
    Auto Layout (DEFAULT):
        # Components are automatically positioned left-to-right
        builder = LangflowBuilder("Test")  # auto_position=True by default
        # Override if needed: LangflowBuilder("Test", auto_position=False)
    
    Keyword Arguments:
        # All methods support keyword args for cleaner code
        builder = LangflowBuilder(workflow_name="Test", spacing=800)
        builder.add_component(id="input", component_type="ChatInput", x=100, y=200)
        builder.connect(source="input", target="prompt")
    
    Connection Patterns:
        ChatInput.message → Prompt.{field} → LanguageModel.input_value → ChatOutput.input_value
    """
    def __init__(self, name: str = None, description: str = "", **kwargs):
        """
        Initialize LangflowBuilder.
        
        Args:
            name: Workflow name (or use workflow_name in kwargs)
            description: Workflow description (or use workflow_description in kwargs)
            **kwargs: auto_position=True (default), spacing=650, etc.
        """
        # Handle name from kwargs if not provided as positional arg
        if name is None:
            name = kwargs.get('workflow_name', kwargs.get('name', 'Untitled Workflow'))
        
        # Handle description from kwargs if needed
        if not description and 'workflow_description' in kwargs:
            description = kwargs.get('workflow_description', '')
        elif 'description' in kwargs and not description:
            description = kwargs.get('description', '')
        
        self.name = name
        self.description = description
        self.components = []
        self.connections = []
        self.notes = []
        self.node_counter = {}
        self.node_id_map = {}  # Map logical name to generated ID
        
        # Handle additional kwargs - AUTO LAYOUT IS NOW DEFAULT
        self.auto_position = kwargs.get('auto_position', True)  # ✅ DEFAULT TO TRUE
        self.spacing = kwargs.get('spacing', 350)
        
    def _generate_node_id(self, type_name: str) -> str:
        # Use a short prefix and incrementing number for each type
        prefix_map = {
            "ChatInput": "ChatInput-SA",
            "Prompt": "Prompt-SA",
            "LanguageModel": "LanguageModelComponent-SA",
            "LanguageModelComponent": "LanguageModelComponent-SA",
            "ChatOutput": "ChatOutput-SA",
            "note": "note-SA",
            "noteNode": "note-SA"
        }
        prefix = prefix_map.get(type_name, f"{type_name}-SA")
        self.node_counter.setdefault(type_name, 0)
        self.node_counter[type_name] += 1
        return f"{prefix}{self.node_counter[type_name]:03d}"
    
    def extract_variables_from_template(self, template: str) -> List[str]:
        """Extract {variable} patterns from prompt template"""
        pattern = r'\{([^}]+)\}'
        variables = re.findall(pattern, template)
        return list(set(variables))  # Remove duplicates
    
    def generate_dynamic_field_definition(self, 
                                        variable_name: str, 
                                        display_name: Optional[str] = None,
                                        field_type: str = "str",
                                        input_types: List[str] = None,
                                        advanced: bool = False,
                                        required: bool = False,
                                        multiline: bool = True,
                                        info: str = "",
                                        placeholder: str = "",
                                        options: List[str] = None,
                                        default_value: str = "") -> Dict[str, Any]:
        """Generate field definition for dynamic prompt variable"""
        
        if display_name is None:
            display_name = variable_name.replace("_", " ").title()
            
        if input_types is None:
            input_types = ["Message"]  # ✅ DEFAULT TO COMPATIBLE TYPE
        
        # Base field definition
        field_def = {
            "advanced": advanced,
            "display_name": display_name,
            "dynamic": False,  # Set to False since we're pre-configuring
            "field_type": field_type,
            "fileTypes": [],
            "file_path": "",
            "info": info,
            "input_types": input_types,
            "list": False,
            "load_from_db": False,
            "multiline": multiline,
            "name": variable_name,
            "placeholder": placeholder,
            "required": required,
            "show": True,
            "title_case": False,
            "trace_as_input": True,
            "trace_as_metadata": True,
            "type": field_type,
            "value": default_value
        }
        
        # Add dropdown-specific fields if options are provided
        if options:
            field_def["_input_type"] = "DropdownInput"
            field_def["options"] = options
            field_def["value"] = options[0] if options and not default_value else default_value
        
        return field_def
    
    @staticmethod
    def create_compatible_field_config(display_name: str, 
                                     info: str = "", 
                                     placeholder: str = "",
                                     required: bool = True,
                                     multiline: bool = True,
                                     options: List[str] = None) -> Dict[str, Any]:
        """
        Helper method to create Langflow-compatible field configurations.
        
        This ensures input_types is set to ["Message"] for proper Language Model connections.
        
        Args:
            display_name: Human-readable field label
            info: Tooltip description  
            placeholder: Input placeholder text
            required: Whether field is mandatory
            multiline: Allow multi-line text input
            options: For dropdown fields (optional)
            
        Returns:
            Field configuration dict ready for use in field_configs
            
        Example:
            field_configs = {
                "user_input": LangflowBuilder.create_compatible_field_config(
                    display_name="User Input",
                    info="Enter the text to analyze",
                    placeholder="Type your message here...",
                    required=True
                )
            }
        """
        config = {
            "display_name": display_name,
            "info": info,
            "placeholder": placeholder,
            "required": required,
            "multiline": multiline,
            "input_types": ["Message"],  # ✅ ALWAYS COMPATIBLE WITH LANGUAGE MODELS
            "type": "str",
            "_input_type": "MessageTextInput"
        }
        
        if options:
            config["_input_type"] = "DropdownInput"
            config["options"] = options
            config["multiline"] = False  # Dropdowns are single-line
            
        return config
    
    def add_component(self, logical_id: str = None, type: str = None, config: Dict[str, Any] = None, position: Tuple[int, int] = None, dynamic_fields: Dict[str, Dict[str, Any]] = None, **kwargs):
        """Add a component with logical name for reference.
        
        Args:
            logical_id: Logical name (or use id/name in kwargs)
            type: Component type (or use component_type in kwargs)
            config: Configuration dict (or pass config fields directly as kwargs)
            position: Position (x,y) (or use pos/x/y in kwargs)
        """
        # Handle logical_id from kwargs
        if logical_id is None:
            logical_id = kwargs.get('id', kwargs.get('name'))
            if logical_id is None:
                raise ValueError("logical_id must be provided either as positional arg or via 'id'/'name' kwargs")
        
        # Handle type from kwargs
        if type is None:
            type = kwargs.get('component_type', kwargs.get('type'))
            if type is None:
                raise ValueError("type must be provided either as positional arg or via 'component_type'/'type' kwargs")
        
        # Handle config from kwargs
        if config is None:
            config = kwargs.get('configuration', kwargs.get('config', {}))
        else:
            config = config.copy()  # Make a copy to avoid modifying original
        
        # Handle position from kwargs
        if position is None:
            if 'pos' in kwargs:
                position = kwargs['pos']
            elif 'x' in kwargs or 'y' in kwargs:
                x = kwargs.get('x', 0)
                y = kwargs.get('y', 0)
                position = (x, y)
        
        # Add any direct config kwargs to config dict
        config_kwargs = {k: v for k, v in kwargs.items() 
                        if k not in ['id', 'name', 'component_type', 'type', 'configuration', 'config', 'pos', 'x', 'y']}
        config.update(config_kwargs)
        
        node_type = type if type != "LanguageModel" else "LanguageModelComponent"
        node_id = self._generate_node_id(node_type)
        self.node_id_map[logical_id] = node_id
        
        # Get full template and merge config
        templates = self._get_component_templates()
        import copy
        template = copy.deepcopy(templates.get(type, {}))  # DEEP copy to avoid shared references
        full_config = {}
        
        if "template" in template:
            # Start with a deep copy of the template
            full_config = copy.deepcopy(template["template"])
            
            # Handle dynamic prompts
            if type == "Prompt" and config and "template" in config:
                prompt_template = config["template"]
                variables = self.extract_variables_from_template(prompt_template)
                
                # Set up custom_fields.template array (now on the deep copied template)
                if "custom_fields" not in template:
                    template["custom_fields"] = {}
                template["custom_fields"]["template"] = variables
                
                # Generate field definitions
                if variables:
                    for var in variables:
                        if dynamic_fields and var in dynamic_fields:
                            # Use provided field definition
                            full_config[var] = dynamic_fields[var]
                        else:
                            # Generate default field definition
                            full_config[var] = self.generate_dynamic_field_definition(var)
            
            # Overwrite with user config
            if config:
                for k, v in config.items():
                    if k in full_config:
                        if isinstance(full_config[k], dict) and "value" in full_config[k]:
                            full_config[k]["value"] = v
                        else:
                            full_config[k] = v
                    # Handle template field specially
                    elif k == "template" and type == "Prompt":
                        full_config["template"]["value"] = v
        
        component = {
            "id": node_id,
            "type": type,
            "config": full_config,
            "position": position or (0, 0),
            "template_metadata": template  # Store template metadata
        }
        self.components.append(component)
        return self
    
    def add_dynamic_prompt(self, logical_id: str = None, template: str = None, field_configs: Dict[str, Dict[str, Any]] = None, position: Tuple[int, int] = None, **kwargs):
        """Add a prompt with dynamic {variables} fields.
        
        Args:
            logical_id: Logical name (or use id/name in kwargs)
            template: Prompt template with {variables} (or use prompt_template in kwargs)
            field_configs: Field configs for variables (or use fields in kwargs)
            position: Position (x,y) (or use pos/x/y in kwargs)
        """
        # Handle logical_id from kwargs
        if logical_id is None:
            logical_id = kwargs.get('id', kwargs.get('name'))
            if logical_id is None:
                raise ValueError("logical_id must be provided either as positional arg or via 'id'/'name' kwargs")
        
        # Handle template from kwargs
        if template is None:
            template = kwargs.get('prompt_template', kwargs.get('template'))
            if template is None:
                raise ValueError("template must be provided either as positional arg or via 'prompt_template'/'template' kwargs")
        
        # Handle field_configs from kwargs
        if field_configs is None:
            field_configs = kwargs.get('fields', kwargs.get('field_configs'))
        
        # Handle position from kwargs
        if position is None:
            if 'pos' in kwargs:
                position = kwargs['pos']
            elif 'x' in kwargs or 'y' in kwargs:
                x = kwargs.get('x', 0)
                y = kwargs.get('y', 0)
                position = (x, y)
        
        variables = self.extract_variables_from_template(template)
        dynamic_fields = {}
        
        for var in variables:
            if field_configs and var in field_configs:
                # Merge provided config with default
                field_def = self.generate_dynamic_field_definition(var)
                field_def.update(field_configs[var])
                dynamic_fields[var] = field_def
            else:
                dynamic_fields[var] = self.generate_dynamic_field_definition(var)
        
        return self.add_component(
            logical_id=logical_id,
            type="Prompt", 
            config={"template": template},
            position=position,
            dynamic_fields=dynamic_fields
        )
    
    def connect(self, from_logical: str = None, to_logical: str = None, from_output: str = None, to_input: str = None, **kwargs):
        """Connect two components by logical name.
        
        Args:
            from_logical: Source component ID (or use source/from_id in kwargs)
            to_logical: Target component ID (or use target/to_id in kwargs)
            from_output: Source output handle (or use source_output/output in kwargs)
            to_input: Target input handle (or use target_input/input in kwargs)
        """
        # Handle from_logical from kwargs
        if from_logical is None:
            from_logical = kwargs.get('source', kwargs.get('from_id'))
            if from_logical is None:
                raise ValueError("from_logical must be provided either as positional arg or via 'source'/'from_id' kwargs")
        
        # Handle to_logical from kwargs
        if to_logical is None:
            to_logical = kwargs.get('target', kwargs.get('to_id'))
            if to_logical is None:
                raise ValueError("to_logical must be provided either as positional arg or via 'target'/'to_id' kwargs")
        
        # Handle from_output from kwargs
        if from_output is None:
            from_output = kwargs.get('source_output', kwargs.get('output'))
        
        # Handle to_input from kwargs
        if to_input is None:
            to_input = kwargs.get('target_input', kwargs.get('input'))
        
        connection = {
            "from": self.node_id_map[from_logical],
            "to": self.node_id_map[to_logical],
            "from_output": from_output,
            "to_input": to_input
        }
        self.connections.append(connection)
        return self
    
    def add_note(self, content: str = None, position: Tuple[int, int] = None, color: str = "blue", **kwargs):
        """Add a documentation note.
        
        Args:
            content: Note text (or use text in kwargs)
            position: Position (x,y) (or use pos/x/y in kwargs)
            color: Note color (default: "blue")
        """
        # Handle content from kwargs
        if content is None:
            content = kwargs.get('text', kwargs.get('note_text'))
            if content is None:
                raise ValueError("content must be provided either as positional arg or via 'text'/'note_text' kwargs")
        
        # Handle position from kwargs
        if position is None:
            if 'pos' in kwargs:
                position = kwargs['pos']
            elif 'x' in kwargs or 'y' in kwargs:
                x = kwargs.get('x', 0)
                y = kwargs.get('y', 0)
                position = (x, y)
            else:
                position = (0, 0)
        
        # Handle color from kwargs
        if 'note_color' in kwargs:
            color = kwargs['note_color']
        elif 'color' in kwargs:
            color = kwargs['color']
        
        note_id = self._generate_node_id("noteNode")
        note = {
            "id": note_id,
            "content": content,
            "position": position,
            "color": color
        }
        self.notes.append(note)
        return self
    
    def build(self) -> Dict[str, Any]:
        """Generate the full Langflow JSON"""
        nodes = []
        edges = []
        
        # Auto-position components if not specified
        self._auto_position()
        
        # Generate nodes
        for i, comp in enumerate(self.components):
            node = self._create_node(comp, i)
            nodes.append(node)
        
        # Generate notes
        for i, note in enumerate(self.notes):
            note_node = self._create_note(note, len(self.components) + i)
            nodes.append(note_node)
        
        # Generate edges
        for conn in self.connections:
            edge = self._create_edge(conn)
            edges.append(edge)
        
        return {
            "data": {
                "edges": edges,
                "nodes": nodes,
                "viewport": {"x": 0, "y": 0, "zoom": 1}
            },
            "description": self.description,
            "endpoint_name": None,
            "id": "sentiment-analyzer-001",  # Use a string ID for compatibility
            "is_component": False,
            "last_tested_version": "1.4.3",
            "name": self.name,
            "tags": self._extract_tags()
        }
    
    def _auto_position(self):
        """Auto-position components in a left-to-right flow"""
        if not self.auto_position:
            return
            
        x_spacing = self.spacing
        y_spacing = 100
        
        for i, comp in enumerate(self.components):
            if comp["position"] == (0, 0):  # No position specified
                comp["position"] = (100 + i * x_spacing, 300)
        
        # Auto-position notes that don't have explicit positions
        for i, note in enumerate(self.notes):
            if note["position"] == (0, 0):
                # Position notes at the top, offset from components
                note["position"] = (100 + i * 400, 50)
    
    def _create_node(self, comp: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Create a node from component definition, using full template and correct node type."""
        templates = self._get_component_templates()
        base_template = templates.get(comp["type"], {})
        template_metadata = comp.get("template_metadata", base_template)
        node_type = comp["type"]
        
        # Fix: Use correct selected_output based on component type
        selected_output_map = {
            "ChatInput": "message",
            "Prompt": "prompt", 
            "LanguageModel": "text_output",
            "LanguageModelComponent": "text_output",
            "ChatOutput": "message",
            "Agent": "response",
            "Calculator": "component_as_tool",
            "WebSearch": "component_as_tool" 
        }
        
        selected_output = selected_output_map.get(comp["type"], "message")
        
        # Build the template structure properly
        final_template = comp["config"].copy()
        
        # Add the _type field and code field
        final_template["_type"] = "Component"
        if "code" in base_template.get("template", {}):
            final_template["code"] = base_template["template"]["code"]
        
        # Use correct node type for output
        node_output_type = "genericNode" if node_type not in ("noteNode", "note") else "noteNode"
        
        node = {
            "data": {
                "description": template_metadata.get("description", ""),
                "display_name": template_metadata.get("display_name", comp["type"]),
                "id": comp["id"],
                "node": {
                    "base_classes": template_metadata.get("base_classes", ["Message"]),
                    "beta": False,
                    "conditional_paths": [],
                    "custom_fields": template_metadata.get("custom_fields", {}),
                    "description": template_metadata.get("description", ""),
                    "display_name": template_metadata.get("display_name", comp["type"]),
                    "documentation": "",
                    "edited": False,
                    "field_order": template_metadata.get("field_order", []),
                    "frozen": False,
                    "icon": template_metadata.get("icon", "MessagesSquare"),
                    "legacy": False,
                    "lf_version": "1.4.3",
                    "metadata": template_metadata.get("metadata", {}),
                    "output_types": [],
                    "outputs": template_metadata.get("outputs", []),
                    "pinned": False,
                    "template": final_template,
                    "tool_mode": False,
                    # Add optional fields if present in template
                    "showNode": template_metadata.get("showNode", True),
                    "priority": template_metadata.get("priority", 0),
                    "group_outputs": template_metadata.get("group_outputs", False),
                },
                "type": node_type,
                "selected_output": selected_output  # ✅ Use correct output name
            },
            "dragging": False,
            "height": 320 if comp["type"] == "Prompt" else 234,  # Taller height for prompts with dynamic fields
            "id": comp["id"],
            "measured": {"height": 320 if comp["type"] == "Prompt" else 234, "width": 320},
            "position": {"x": comp["position"][0], "y": comp["position"][1]},
            "positionAbsolute": {"x": comp["position"][0], "y": comp["position"][1]},
            "selected": False,
            "type": node_output_type,
            "width": 320
        }
        
        # For noteNode, add extra fields
        if node_output_type == "noteNode":
            node["resizing"] = False
            node["style"] = {"height": 400, "width": 350}
            node["width"] = 350
            node["height"] = 400
        
        return node
    
    def _create_note(self, note: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Create a note node"""
        note_id = note["id"]
        return {
            "data": {
                "id": note_id,
                "node": {
                    "description": note["content"],
                    "display_name": "README",
                    "documentation": "",
                    "template": {"backgroundColor": note["color"]}
                },
                "type": "note"
            },
            "dragging": False,
            "height": 400,
            "id": note_id,
            "measured": {"height": 400, "width": 350},
            "position": {"x": note["position"][0], "y": note["position"][1]},
            "positionAbsolute": {"x": note["position"][0], "y": note["position"][1]},
            "resizing": False,
            "selected": False,
            "style": {"height": 400, "width": 350},
            "type": "noteNode",
            "width": 350
        }
    
    def _create_edge(self, conn: Dict[str, Any]) -> Dict[str, Any]:
        """Create an edge from connection definition with proper type handling"""
        # Auto-detect common connection patterns
        output_map = {
            "ChatInput": "message",
            "Prompt": "prompt", 
            "LanguageModel": "text_output",
            "LanguageModelComponent": "text_output",
            "OpenAI": "text_output",
            "Agent": "response",
            "Calculator": "component_as_tool",
            "WebSearch": "component_as_tool"
        }
        
        input_map = {
            "LanguageModel": {"message": "input_value", "prompt": "input_value"},
            "LanguageModelComponent": {"message": "input_value", "prompt": "input_value"},
            "ChatOutput": {"message": "input_value", "text_output": "input_value", "response": "input_value"},
            "Agent": {"message": "input_value", "component_as_tool": "tools"}
        }
        
        # 🔧 ADD: Dynamic output type mapping
        output_type_map = {
            "component_as_tool": ["Tool"],  # Tools output Tool type
            "message": ["Message"],
            "prompt": ["Message"],
            "text_output": ["Message"],
            "response": ["Message"]
        }
        
        from_output = conn["from_output"] or output_map.get(self._get_component_type(conn["from"]), "message")
        
        # 🚀 NEW: Enhanced input resolution with Prompt component support
        target_component_type = self._get_component_type(conn["to"])
        
        if conn["to_input"]:
            # Explicit target input provided - use as is
            to_input = conn["to_input"]
        elif target_component_type == "Prompt":
            # 🎯 DYNAMIC PROMPT INPUT RESOLUTION
            to_input = self._resolve_prompt_input(conn["to"], from_output)
        else:
            # Standard input mapping for other components
            to_input = input_map.get(target_component_type, {}).get(from_output, "input_value")
        
        # 🔧 FIX: Get correct output types dynamically
        source_output_types = output_type_map.get(from_output, ["Message"])
        
        # 🔧 FIX: Determine correct target type based on component and input
        target_type = "other" if (target_component_type == "ChatOutput" and to_input == "input_value") else "str"
        
        # Special handling for Agent tools input
        if target_component_type == "Agent" and to_input == "tools":
            target_type = "other"
        
        # Handle input types for different target components
        if target_type == "other":
            if target_component_type == "ChatOutput":
                input_types = ["Data", "DataFrame", "Message"]
            elif target_component_type == "Agent" and to_input == "tools":
                input_types = ["Tool"]
            else:
                input_types = ["Message"]
        else:
            input_types = ["Message"]
        
        # 🔧 FIX: Use dynamic output types in edge ID
        edge_id = f"xy-edge__{conn['from']}{{œdataTypeœ:œ{self._get_component_type(conn['from'])}œ,œidœ:œ{conn['from']}œ,œnameœ:œ{from_output}œ,œoutput_typesœ:{json.dumps(source_output_types)}}}-{conn['to']}{{œfieldNameœ:œ{to_input}œ,œidœ:œ{conn['to']}œ,œinputTypesœ:{json.dumps(input_types)},œtypeœ:œ{target_type}œ}}"
        
        return {
            "animated": False,
            "className": "",
            "data": {
                "sourceHandle": {
                    "dataType": self._get_component_type(conn["from"]),
                    "id": conn["from"],
                    "name": from_output,
                    "output_types": source_output_types  # 🔧 FIX: Use dynamic types
                },
                "targetHandle": {
                    "fieldName": to_input,
                    "id": conn["to"],
                    "inputTypes": input_types,
                    "type": target_type
                }
            },
            "id": edge_id,
            "selected": False,
            "source": conn["from"],
            "sourceHandle": f"{{œdataTypeœ: œ{self._get_component_type(conn['from'])}œ, œidœ: œ{conn['from']}œ, œnameœ: œ{from_output}œ, œoutput_typesœ: {json.dumps(source_output_types)}}}",  # 🔧 FIX: Use dynamic types
            "target": conn["to"],
            "targetHandle": f"{{œfieldNameœ: œ{to_input}œ, œidœ: œ{conn['to']}œ, œinputTypesœ: {json.dumps(input_types)}, œtypeœ: œ{target_type}œ}}"
        }
    
    def _resolve_prompt_input(self, prompt_comp_id: str, from_output: str) -> str:
        """Resolve the appropriate input field for a Prompt component.
        
        Args:
            prompt_comp_id: The ID of the target Prompt component
            from_output: The output handle from the source component
            
        Returns:
            The appropriate input field name for the Prompt component
        """
        # Find the Prompt component
        prompt_component = None
        for comp in self.components:
            if comp["id"] == prompt_comp_id and comp["type"] == "Prompt":
                prompt_component = comp
                break
        
        if not prompt_component:
            return "input_value"  # Fallback
        
        # Get template variables from the component's template metadata
        template_metadata = prompt_component.get("template_metadata", {})
        custom_fields = template_metadata.get("custom_fields", {})
        template_variables = custom_fields.get("template", [])
        
        if not template_variables:
            return "input_value"  # Fallback if no template variables
        
        # 🎯 INTELLIGENT INPUT MATCHING
        # Try to match common patterns between output types and variable names
        input_matching_patterns = {
            "message": ["user_question", "user_input", "question", "input", "message", "user_message", "text", "content"],
            "text_output": ["analysis", "result", "output", "response", "answer", "summary", "feedback", "ticket_analysis", "analysis_result"],
            "response": ["previous_response", "context", "history", "prior_result"]
        }
        
        # Get potential variable names for this output type
        potential_vars = input_matching_patterns.get(from_output, [])
        
        # Try to find a matching variable name
        for pattern in potential_vars:
            for var in template_variables:
                if pattern in var.lower() or var.lower() in pattern:
                    return var
        
        # If no smart match found, return the first template variable
        # This handles cases where user wants to connect to the primary input
        return template_variables[0] if template_variables else "input_value"
    
    def _get_component_type(self, comp_id: str) -> str:
        """Get component type by ID"""
        for comp in self.components:
            if comp["id"] == comp_id:
                return comp["type"]
        for note in self.notes:
            if note["id"] == comp_id:
                return "noteNode"
        return "Unknown"
    
    def _extract_tags(self) -> List[str]:
        """Extract relevant tags based on components and description"""
        tags = []
        if "sentiment" in self.name.lower() or "sentiment" in self.description.lower():
            tags.extend(["sentiment", "analysis", "nlp", "classification"])
        if "chat" in self.name.lower():
            tags.append("chatbot")
        if any(comp["type"] in ("LanguageModel", "LanguageModelComponent") for comp in self.components):
            tags.append("llm")
        
        # Add dynamic prompts tag if any prompts have dynamic fields
        for comp in self.components:
            if comp["type"] == "Prompt" and comp.get("template_metadata", {}).get("custom_fields", {}).get("template"):
                tags.append("dynamic-prompts")
                break
        
        return list(dict.fromkeys(tags))  # Remove duplicates, preserve order
    
    def _get_component_templates(self) -> Dict[str, Dict[str, Any]]:
        """Component templates with essential configurations"""
        # Return a copy to avoid accidental mutation
        return dict(NEW_COMPONENT_TEMPLATES)


# Enhanced example usage for sentiment analyzer with dynamic prompts
def create_enhanced_sentiment_analyzer():
    builder = LangflowBuilder(
        name="Enhanced Sentiment Analyzer (Dynamic Prompts)",
        description="Advanced sentiment analysis workflow with pre-compiled dynamic prompt fields - ready to use immediately upon import."
    )
    
    # Add ChatInput
    builder.add_component("input", "ChatInput", {
        "input_value": "I absolutely love this new product! It has exceeded all my expectations.",
        "sender": "User",
        "sender_name": "User"
    }, position=(100, 300))
    
    # Add dynamic prompt with pre-compiled fields
    prompt_template = """You are an expert sentiment analysis AI. Analyze the sentiment of the following text with {analysis_depth} detail.

Text to analyze: {text_to_analyze}

Provide your analysis in {output_format} format:
- Sentiment: [Positive/Negative/Neutral]
- Confidence: [High/Medium/Low]  
- Key indicators: [List main words/phrases that influenced the sentiment]
- Brief explanation: [2-3 sentences explaining your reasoning]

Analysis:"""
    
    # Configure the dynamic fields
    field_configs = {
        "text_to_analyze": {
            "display_name": "Text to Analyze",
            "info": "The text content that will be analyzed for sentiment",
            "placeholder": "Enter the text you want to analyze for sentiment...",
            "required": True,
            "multiline": True
        },
        "analysis_depth": {
            "display_name": "Analysis Depth",
            "info": "How detailed should the sentiment analysis be?",
            "options": ["basic", "detailed", "comprehensive"],
            "default_value": "detailed"
        },
        "output_format": {
            "display_name": "Output Format",
            "info": "Format for the analysis results",
            "options": ["structured", "conversational", "bullet-points", "JSON"],
            "default_value": "structured"
        }
    }
    
    builder.add_dynamic_prompt("prompt", prompt_template, field_configs, position=(500, 250))
    
    # Add Language Model
    builder.add_component("llm", "LanguageModel", {
        "provider": "OpenAI",
        "model_name": "gpt-4o-mini",
        "temperature": 0.1
    }, position=(900, 300))
    
    # Add ChatOutput
    builder.add_component("output", "ChatOutput", {
        "sender": "Machine",
        "sender_name": "Sentiment Analyzer"
    }, position=(1300, 300))
    
    # Connect components
    builder.connect("input", "prompt", "message", "text_to_analyze")
    builder.connect("prompt", "llm", "prompt", "input_value")
    builder.connect("llm", "output", "text_output", "input_value")
    
    # Add documentation
    builder.add_note("""# Enhanced Sentiment Analyzer

This workflow features **pre-compiled dynamic prompt fields** that appear immediately upon import - no build step required!

## Dynamic Features:
- **Text to Analyze**: Main input field (connects to ChatInput)
- **Analysis Depth**: Choose basic, detailed, or comprehensive
- **Output Format**: Select structured, conversational, bullet-points, or JSON

## Immediate Workflow:
1. Import → Fields visible instantly
2. Connect inputs → No build needed first
3. Add API key → Run immediately

## Professional Benefits:
- Clean, labeled input fields
- Dropdown selections for consistency  
- Built-in documentation and placeholders
- Production-ready workflow structure

This demonstrates the power of pre-compiled dynamic prompts in Langflow!""", 
    position=(1400, 50), color="blue")
    
    return builder.build()

# Generate the enhanced workflow
if __name__ == "__main__":
    workflow_json = create_enhanced_sentiment_analyzer()
    
    # Ensure results directory exists
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, "enhanced_sentiment_analyzer.json")
    
    # Validate JSON before saving
    try:
        json_str = json.dumps(workflow_json, indent=2)
        json.loads(json_str)  # Validate
    except Exception as e:
        print(f"ERROR: Generated workflow is not valid JSON: {e}")
        exit(1)
    
    # Save to file
    with open(output_path, "w") as f:
        f.write(json_str)
    
    print("Enhanced sentiment analyzer workflow generated!")
    print(f"Components: {len(workflow_json['data']['nodes']) - 1}")  # -1 for note
    print(f"Connections: {len(workflow_json['data']['edges'])}")
    print(f"Success! Workflow saved to: {os.path.abspath(output_path)}")
    
    # Show dynamic fields that were created
    prompt_node = None
    for node in workflow_json['data']['nodes']:
        if node['data']['type'] == 'Prompt':
            prompt_node = node
            break
    
    if prompt_node:
        custom_fields = prompt_node['data']['node']['custom_fields']['template']
        print(f"\nPre-compiled dynamic fields: {custom_fields}")
        print("✅ These fields will appear immediately upon import!")