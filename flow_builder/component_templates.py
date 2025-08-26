# New component templates extracted from Youtube Analysis.json


BATCH_RUN_COMPONENT_TEMPLATE = {
    "description": "Runs an LLM on each row of a DataFrame column. If no column is specified, all columns are used.",
    "display_name": "Batch Run",
    "icon": "List",
    "base_classes": ["DataFrame"],
    "outputs": [{
        "allows_loop": False,
        "cache": True,
        "display_name": "LLM Results",
        "method": "run_batch",
        "name": "batch_results",
        "selected": "DataFrame",
        "types": ["DataFrame"]
    }],
    "selected_output": "batch_results",
    "field_order": [
        "df",
        "column_name",
        "model",
        "system_message",
        "output_column_name",
        "enable_metadata",
        "code"
    ],
    "template": {
        "df": {
            "_input_type": "DataFrameInput",
            "display_name": "DataFrame",
            "type": "other",
            "input_types": ["DataFrame"],
            "required": True,
            "value": ""
        },
        "column_name": {
            "_input_type": "StrInput",
            "display_name": "Column Name",
            "type": "str",
            "value": "text"
        },
        "model": {
            "_input_type": "HandleInput",
            "display_name": "Language Model",
            "type": "other",
            "input_types": ["LanguageModel"],
            "required": True,
            "value": ""
        },
        "system_message": {
            "_input_type": "MultilineInput",
            "display_name": "Instructions",
            "type": "str",
            "value": ""
        },
        "output_column_name": {
            "_input_type": "MessageTextInput",
            "display_name": "Output Column Name",
            "type": "str",
            "value": "model_response"
        },
        "enable_metadata": {
            "_input_type": "BoolInput",
            "display_name": "Enable Metadata",
            "type": "bool",
            "value": True
        },
        "code": {
            "_input_type": "code",
            "display_name": "Code",
            "type": "code",
            "value": "from langflow.base.data.utils import get_column_names\nfrom langflow.base.io.dataframe import DataFrameComponent\nfrom langflow.inputs.inputs import BoolInput\nfrom langflow.io import DataFrameInput, DropdownInput, MessageTextInput, MultilineInput, Output\nfrom langflow.schema.dataframe import DataFrame\nfrom langflow.schema.message import Message\n\nclass BatchRunComponent(DataFrameComponent):\n    display_name = \"Batch Run\"\n    description = \"Runs an LLM on each row of a DataFrame column. If no column is specified, all columns are used.\"\n    icon = \"List\"\n    name = \"BatchRunComponent\"\n    minimized = True\n\n    inputs = [\n        DataFrameInput(\n            name=\"df\",\n            display_name=\"DataFrame\",\n            input_types=[\"DataFrame\"],\n            required=True,\n        ),\n        MessageTextInput(\n            name=\"column_name\",\n            display_name=\"Column Name\",\n            value=\"text\",\n        ),\n        DropdownInput(\n            name=\"model\",\n            display_name=\"Language Model\",\n            input_types=[\"LanguageModel\"],\n            required=True,\n        ),\n        MultilineInput(\n            name=\"system_message\",\n            display_name=\"Instructions\",\n        ),\n        MessageTextInput(\n            name=\"output_column_name\",\n            display_name=\"Output Column Name\",\n            value=\"model_response\",\n        ),\n        BoolInput(\n            name=\"enable_metadata\",\n            display_name=\"Enable Metadata\",\n            value=True,\n        ),\n    ]\n    outputs = [\n        Output(display_name=\"LLM Results\", name=\"batch_results\", method=\"run_batch\"),\n    ]\n\n    async def run_batch(self) -> DataFrame:\n        # Implement batch LLM run logic here\n        pass"
        }
    }
}

YOUTUBE_COMMENTS_COMPONENT_TEMPLATE = {
    "description": "Retrieves and analyzes comments from YouTube videos.",
    "display_name": "YouTube Comments",
    "icon": "YouTube",
    "base_classes": ["DataFrame"],
    "outputs": [{
        "allows_loop": False,
        "cache": True,
        "display_name": "Comments",
        "method": "get_video_comments",
        "name": "comments",
        "selected": "DataFrame",
        "types": ["DataFrame"]
    }],
    "selected_output": "comments",
    "field_order": [
        "video_url",
        "api_key",
        "include_metrics",
        "include_replies",
        "max_results",
        "sort_by",
        "code"
    ],
    "template": {
        "video_url": {
            "_input_type": "MessageTextInput",
            "display_name": "Video URL",
            "type": "str",
            "required": True,
            "value": ""
        },
        "api_key": {
            "_input_type": "SecretStrInput",
            "display_name": "YouTube API Key",
            "type": "str",
            "required": True,
            "value": "YOUTUBE_API_KEY"
        },
        "include_metrics": {
            "_input_type": "BoolInput",
            "display_name": "Include Metrics",
            "type": "bool",
            "value": True
        },
        "include_replies": {
            "_input_type": "BoolInput",
            "display_name": "Include Replies",
            "type": "bool",
            "value": False
        },
        "max_results": {
            "_input_type": "IntInput",
            "display_name": "Max Results",
            "type": "int",
            "value": 10
        },
        "sort_by": {
            "_input_type": "DropdownInput",
            "display_name": "Sort By",
            "type": "str",
            "options": ["time", "relevance"],
            "value": "relevance"
        },
        "code": {
            "_input_type": "code",
            "display_name": "Code",
            "type": "code",
            "value": "from langflow.base.io.dataframe import DataFrameComponent\nfrom langflow.inputs.inputs import BoolInput\nfrom langflow.io import DropdownInput, IntInput, MessageTextInput, Output, SecretStrInput\nfrom langflow.schema.dataframe import DataFrame\n\nclass YouTubeCommentsComponent(DataFrameComponent):\n    display_name = \"YouTube Comments\"\n    description = \"Retrieves and analyzes comments from YouTube videos.\"\n    icon = \"YouTube\"\n    name = \"YouTubeCommentsComponent\"\n    minimized = True\n\n    inputs = [\n        MessageTextInput(\n            name=\"video_url\",\n            display_name=\"Video URL\",\n            required=True,\n        ),\n        SecretStrInput(\n            name=\"api_key\",\n            display_name=\"YouTube API Key\",\n            required=True,\n        ),\n        BoolInput(\n            name=\"include_metrics\",\n            display_name=\"Include Metrics\",\n            value=True,\n        ),\n        BoolInput(\n            name=\"include_replies\",\n            display_name=\"Include Replies\",\n            value=False,\n        ),\n        IntInput(\n            name=\"max_results\",\n            display_name=\"Max Results\",\n            value=10,\n        ),\n        DropdownInput(\n            name=\"sort_by\",\n            display_name=\"Sort By\",\n            options=[\"time\", \"relevance\"],\n            value=\"relevance\",\n        ),\n    ]\n    outputs = [\n        Output(display_name=\"Comments\", name=\"comments\", method=\"get_video_comments\"),\n    ]\n\n    async def get_video_comments(self) -> DataFrame:\n        # Implement YouTube comments retrieval logic here\n        pass\n"
        }
    }
}

OPENAI_MODEL_TEMPLATE = {
    "description": "Generates text using OpenAI LLMs.",
    "display_name": "OpenAI",
    "icon": "OpenAI",
    "base_classes": ["LanguageModel", "Message"],
    "outputs": [
        {
            "display_name": "Model Response",
            "method": "text_response",
            "name": "text_output",
            "selected": "Message",
            "types": ["Message"]
        },
        {
            "display_name": "Language Model",
            "method": "build_model",
            "name": "model_output",
            "selected": "LanguageModel",
            "types": ["LanguageModel"]
        }
    ],
    "selected_output": "model_output",
    "field_order": [
        "api_key",
        "input_value",
        "json_mode",
        "max_retries",
        "max_tokens",
        "model_kwargs",
        "model_name",
        "openai_api_base",
        "seed",
        "stream",
        "system_message",
        "temperature",
        "timeout",
        "code"
    ],
    "template": {
        "api_key": {
            "_input_type": "SecretStrInput",
            "display_name": "OpenAI API Key",
            "type": "str",
            "required": True,
            "value": "OPENAI_API_KEY"
        },
        "input_value": {
            "_input_type": "MessageTextInput",
            "display_name": "Input",
            "type": "str",
            "value": ""
        },
        "json_mode": {
            "_input_type": "BoolInput",
            "display_name": "JSON Mode",
            "type": "bool",
            "value": False
        },
        "max_retries": {
            "_input_type": "IntInput",
            "display_name": "Max Retries",
            "type": "int",
            "value": 5
        },
        "max_tokens": {
            "_input_type": "IntInput",
            "display_name": "Max Tokens",
            "type": "int",
            "value": ""
        },
        "model_kwargs": {
            "_input_type": "DictInput",
            "display_name": "Model Kwargs",
            "type": "dict",
            "value": {}
        },
        "model_name": {
            "_input_type": "DropdownInput",
            "display_name": "Model Name",
            "type": "str",
            "options": ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4.5-preview", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo", "o1"],
            "value": "gpt-4.1-mini"
        },
        "openai_api_base": {
            "_input_type": "StrInput",
            "display_name": "OpenAI API Base",
            "type": "str",
            "value": ""
        },
        "seed": {
            "_input_type": "IntInput",
            "display_name": "Seed",
            "type": "int",
            "value": 1
        },
        "stream": {
            "_input_type": "BoolInput",
            "display_name": "Stream",
            "type": "bool",
            "value": False
        },
        "system_message": {
            "_input_type": "MultilineInput",
            "display_name": "System Message",
            "type": "str",
            "value": ""
        },
        "temperature": {
            "_input_type": "SliderInput",
            "display_name": "Temperature",
            "type": "slider",
            "value": 0.1
        },
        "timeout": {
            "_input_type": "IntInput",
            "display_name": "Timeout",
            "type": "int",
            "value": 700
        },
        "code": {
            "_input_type": "code",
            "display_name": "Code",
            "type": "code",
            "value": "from langchain_openai import ChatOpenAI\nfrom langflow.base.models.model import LCModelComponent\nfrom langflow.inputs.inputs import BoolInput\nfrom langflow.io import DropdownInput, MessageTextInput, MultilineInput, SecretStrInput, SliderInput, IntInput, DictInput\nfrom langflow.schema.dotdict import dotdict\n\nclass OpenAIModelComponent(LCModelComponent):\n    display_name = \"OpenAI\"\n    description = \"Generates text using OpenAI LLMs.\"\n    icon = \"OpenAI\"\n    name = \"OpenAIModel\"\n    minimized = True\n\n    inputs = [\n        SecretStrInput(\n            name=\"api_key\",\n            display_name=\"OpenAI API Key\",\n            required=True,\n        ),\n        MessageTextInput(\n            name=\"input_value\",\n            display_name=\"Input\",\n        ),\n        BoolInput(\n            name=\"json_mode\",\n            display_name=\"JSON Mode\",\n            value=False,\n        ),\n        IntInput(\n            name=\"max_retries\",\n            display_name=\"Max Retries\",\n            value=5,\n        ),\n        IntInput(\n            name=\"max_tokens\",\n            display_name=\"Max Tokens\",\n        ),\n        DictInput(\n            name=\"model_kwargs\",\n            display_name=\"Model Kwargs\",\n        ),\n        DropdownInput(\n            name=\"model_name\",\n            display_name=\"Model Name\",\n            options=[\"gpt-4o-mini\", \"gpt-4o\", \"gpt-4.1\", \"gpt-4.1-mini\", \"gpt-4.1-nano\", \"gpt-4.5-preview\", \"gpt-4-turbo\", \"gpt-4-turbo-preview\", \"gpt-4\", \"gpt-3.5-turbo\", \"o1\"],\n            value=\"gpt-4.1-mini\",\n        ),\n        MessageTextInput(\n            name=\"openai_api_base\",\n            display_name=\"OpenAI API Base\",\n        ),\n        IntInput(\n            name=\"seed\",\n            display_name=\"Seed\",\n            value=1,\n        ),\n        BoolInput(\n            name=\"stream\",\n            display_name=\"Stream\",\n            value=False,\n        ),\n        MultilineInput(\n            name=\"system_message\",\n            display_name=\"System Message\",\n        ),\n        SliderInput(\n            name=\"temperature\",\n            display_name=\"Temperature\",\n            value=0.1,\n        ),\n        IntInput(\n            name=\"timeout\",\n            display_name=\"Timeout\",\n            value=700,\n        ),\n    ]\n\n    def build_model(self):\n        return ChatOpenAI(\n            model_name=self.model_name,\n            temperature=self.temperature,\n            streaming=self.stream,\n            openai_api_key=self.api_key,\n        )\n"
        }
    }
}

AGENT_TEMPLATE = {
    "description": "Define the agent's instructions, then enter a task to complete using tools.",
    "display_name": "YT-Insight",
    "icon": "bot",
    "base_classes": ["Message"],
    "outputs": [{
        "display_name": "Response",
        "method": "message_response",
        "name": "response",
        "selected": "Message",
        "types": ["Message"]
    }],
    "selected_output": "response",
    "field_order": [
        "agent_llm",
        "model_name",
        "api_key",
        "input_value",
        "system_prompt",
        "tools",
        "add_current_date_tool",
        "handle_parsing_errors",
        "json_mode",
        "max_iterations",
        "max_retries",
        "max_tokens",
        "memory",
        "message",
        "sender",
        "sender_name",
        "verbose",
        "code"
    ],
    "template": {
        "agent_llm": {
            "_input_type": "DropdownInput",
            "display_name": "Model Provider",
            "type": "str",
            "options": ["Amazon Bedrock", "Anthropic", "Azure OpenAI", "Google Generative AI", "Groq", "NVIDIA", "OpenAI", "SambaNova", "Custom"],
            "value": "OpenAI"
        },
        "model_name": {
            "_input_type": "DropdownInput",
            "display_name": "Model Name",
            "type": "str",
            "options": ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4.5-preview", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo", "o1"],
            "value": "gpt-4.1-mini"
        },
        "api_key": {
            "_input_type": "SecretStrInput",
            "display_name": "OpenAI API Key",
            "type": "str",
            "required": True,
            "value": "OPENAI_API_KEY"
        },
        "input_value": {
            "_input_type": "MessageTextInput",
            "display_name": "Input",
            "type": "str",
            "value": ""
        },
        "system_prompt": {
            "_input_type": "MultilineInput",
            "display_name": "Agent Instructions",
            "type": "str",
            "value": "You are a helpful assistant that can use tools to answer questions and perform tasks."
        },
        "tools": {
            "_input_type": "HandleInput",
            "display_name": "Tools",
            "type": "other",
            "input_types": ["Tool"],
            "value": ""
        },
        "add_current_date_tool": {
            "_input_type": "BoolInput",
            "display_name": "Current Date",
            "type": "bool",
            "value": True
        },
        "handle_parsing_errors": {
            "_input_type": "BoolInput",
            "display_name": "Handle Parse Errors",
            "type": "bool",
            "value": True
        },
        "json_mode": {
            "_input_type": "BoolInput",
            "display_name": "JSON Mode",
            "type": "bool",
            "value": False
        },
        "max_iterations": {
            "_input_type": "IntInput",
            "display_name": "Max Iterations",
            "type": "int",
            "value": 15
        },
        "max_retries": {
            "_input_type": "IntInput",
            "display_name": "Max Retries",
            "type": "int",
            "value": 5
        },
        "max_tokens": {
            "_input_type": "IntInput",
            "display_name": "Max Tokens",
            "type": "int",
            "value": ""
        },
        "memory": {
            "_input_type": "HandleInput",
            "display_name": "External Memory",
            "type": "other",
            "input_types": ["Memory"],
            "value": ""
        },
        "message": {
            "_input_type": "MessageTextInput",
            "display_name": "Message",
            "type": "str",
            "value": ""
        },
        "sender": {
            "_input_type": "DropdownInput",
            "display_name": "Sender Type",
            "type": "str",
            "options": ["Machine", "User"],
            "value": "Machine"
        },
        "sender_name": {
            "_input_type": "MessageTextInput",
            "display_name": "Sender Name",
            "type": "str",
            "value": "AI"
        },
        "verbose": {
            "_input_type": "BoolInput",
            "display_name": "Verbose",
            "type": "bool",
            "value": False
        },
        "code": {
            "_input_type": "code",
            "display_name": "Code",
            "type": "code",
            "value": "from langflow.base.io.agent import AgentComponent\nfrom langflow.inputs.inputs import BoolInput\nfrom langflow.io import DropdownInput, HandleInput, IntInput, MessageTextInput, MultilineInput, Output, SecretStrInput\n\nclass Agent(AgentComponent):\n    display_name = \"YT-Insight\"\n    description = \"Define the agent's instructions, then enter a task to complete using tools.\"\n    icon = \"bot\"\n    name = \"Agent\"\n    minimized = True\n\n    inputs = [\n        DropdownInput(\n            name=\"agent_llm\",\n            display_name=\"Model Provider\",\n            options=[\"Amazon Bedrock\", \"Anthropic\", \"Azure OpenAI\", \"Google Generative AI\", \"Groq\", \"NVIDIA\", \"OpenAI\", \"SambaNova\", \"Custom\"],\n            value=\"OpenAI\",\n        ),\n        DropdownInput(\n            name=\"model_name\",\n            display_name=\"Model Name\",\n            options=[\"gpt-4o-mini\", \"gpt-4o\", \"gpt-4.1\", \"gpt-4.1-mini\", \"gpt-4.1-nano\", \"gpt-4.5-preview\", \"gpt-4-turbo\", \"gpt-4-turbo-preview\", \"gpt-4\", \"gpt-3.5-turbo\", \"o1\"],\n            value=\"gpt-4.1-mini\",\n        ),\n        SecretStrInput(\n            name=\"api_key\",\n            display_name=\"OpenAI API Key\",\n            required=True,\n        ),\n        MessageTextInput(\n            name=\"input_value\",\n            display_name=\"Input\",\n        ),\n        MultilineInput(\n            name=\"system_prompt\",\n            display_name=\"Agent Instructions\",\n            value=\"You are a helpful assistant that can use tools to answer questions and perform tasks.\",\n        ),\n        HandleInput(\n            name=\"tools\",\n            display_name=\"Tools\",\n            input_types=[\"Tool\"],\n        ),\n        BoolInput(\n            name=\"add_current_date_tool\",\n            display_name=\"Current Date\",\n            value=True,\n        ),\n        BoolInput(\n            name=\"handle_parsing_errors\",\n            display_name=\"Handle Parse Errors\",\n            value=True,\n        ),\n        BoolInput(\n            name=\"json_mode\",\n            display_name=\"JSON Mode\",\n            value=False,\n        ),\n        IntInput(\n            name=\"max_iterations\",\n            display_name=\"Max Iterations\",\n            value=15,\n        ),\n        IntInput(\n            name=\"max_retries\",\n            display_name=\"Max Retries\",\n            value=5,\n        ),\n        IntInput(\n            name=\"max_tokens\",\n            display_name=\"Max Tokens\",\n        ),\n        HandleInput(\n            name=\"memory\",\n            display_name=\"External Memory\",\n            input_types=[\"Memory\"],\n        ),\n        MessageTextInput(\n            name=\"message\",\n            display_name=\"Message\",\n        ),\n        DropdownInput(\n            name=\"sender\",\n            display_name=\"Sender Type\",\n            options=[\"Machine\", \"User\"],\n            value=\"Machine\",\n        ),\n        MessageTextInput(\n            name=\"sender_name\",\n            display_name=\"Sender Name\",\n            value=\"AI\",\n        ),\n        BoolInput(\n            name=\"verbose\",\n            display_name=\"Verbose\",\n            value=False,\n        ),\n    ]\n    outputs = [\n        Output(display_name=\"Response\", name=\"response\", method=\"message_response\"),\n    ]\n\n    async def message_response(self):\n        # Implement agent response logic here\n        pass"
        }
    }
}

CHAT_INPUT_TEMPLATE = {
    "description": "Get chat inputs from the Playground.",
    "display_name": "Chat Input",
    "icon": "MessagesSquare",
    "base_classes": ["Message"],
    "beta": False,
    "conditional_paths": [],
    "custom_fields": {},
    "documentation": "",
    "edited": False,
    "field_order": [
        "input_value",
        "should_store_message",
        "sender",
        "sender_name",
        "session_id",
        "files",
        "background_color",
        "chat_icon",
        "text_color",
        "code"
    ],
    "frozen": False,
    "legacy": False,
    "lf_version": "1.4.3",
    "metadata": {},
    "output_types": [],
    "outputs": [{
        "allows_loop": False,
        "cache": True,
        "display_name": "Chat Message",
        "method": "message_response",
        "name": "message",
        "selected": "Message",
        "types": ["Message"]
    }],
    "pinned": False,
    "selected_output": "message",
    "tool_mode": False,
    "showNode": True,
    "priority": 0,
    "group_outputs": False,
    "template": {
        "_type": "Component",
        "background_color": {
            "_input_type": "MessageTextInput",
            "advanced": True,
            "display_name": "Background Color",
            "dynamic": False,
            "info": "The background color of the icon.",
            "input_types": ["Message"],
            "list": False,
            "list_add_label": "Add More",
            "load_from_db": False,
            "name": "background_color",
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "tool_mode": False,
            "trace_as_input": True,
            "trace_as_metadata": True,
            "type": "str",
            "value": ""
        },
        "chat_icon": {
            "_input_type": "MessageTextInput",
            "advanced": True,
            "display_name": "Icon",
            "dynamic": False,
            "info": "The icon of the message.",
            "input_types": ["Message"],
            "list": False,
            "list_add_label": "Add More",
            "load_from_db": False,
            "name": "chat_icon",
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "tool_mode": False,
            "trace_as_input": True,
            "trace_as_metadata": True,
            "type": "str",
            "value": ""
        },
        "input_value": {
            "_input_type": "MultilineInput",
            "advanced": False,
            "copy_field": False,
            "display_name": "Input Text",
            "dynamic": False,
            "info": "Message to be passed as input.",
            "input_types": [],
            "list": False,
            "list_add_label": "Add More",
            "load_from_db": False,
            "multiline": True,
            "name": "input_value",
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "tool_mode": False,
            "trace_as_input": True,
            "trace_as_metadata": True,
            "type": "str",
            "value": "I absolutely love this new product! It has exceeded all my expectations and made my life so much easier."
        },
        "sender": {
            "_input_type": "DropdownInput",
            "advanced": True,
            "combobox": False,
            "dialog_inputs": {},
            "display_name": "Sender Type",
            "dynamic": False,
            "info": "Type of sender.",
            "name": "sender",
            "options": ["Machine", "User"],
            "options_metadata": [],
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "toggle": False,
            "tool_mode": False,
            "trace_as_metadata": True,
            "type": "str",
            "value": "User"
        },
        "sender_name": {
            "_input_type": "MessageTextInput",
            "advanced": True,
            "display_name": "Sender Name",
            "dynamic": False,
            "info": "Name of the sender.",
            "input_types": ["Message"],
            "list": False,
            "list_add_label": "Add More",
            "load_from_db": False,
            "name": "sender_name",
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "tool_mode": False,
            "trace_as_input": True,
            "trace_as_metadata": True,
            "type": "str",
            "value": "User"
        },
        "should_store_message": {
            "_input_type": "BoolInput",
            "advanced": True,
            "display_name": "Store Messages",
            "dynamic": False,
            "info": "Store the message in the history.",
            "list": False,
            "list_add_label": "Add More",
            "name": "should_store_message",
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "tool_mode": False,
            "trace_as_metadata": True,
            "type": "bool",
            "value": True
        },
        "session_id": {
            "_input_type": "MessageTextInput",
            "advanced": True,
            "display_name": "Session ID",
            "dynamic": False,
            "info": "The session ID of the chat. If empty, the current session ID parameter will be used.",
            "input_types": ["Message"],
            "list": False,
            "list_add_label": "Add More",
            "load_from_db": False,
            "name": "session_id",
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "tool_mode": False,
            "trace_as_input": True,
            "trace_as_metadata": True,
            "type": "str",
            "value": ""
        },
        "files": {
            "_input_type": "FileInput",
            "advanced": True,
            "display_name": "Files",
            "dynamic": False,
            "info": "Files to be sent with the message.",
            "input_types": ["Message"],
            "is_list": True,
            "list": True,
            "list_add_label": "Add More",
            "load_from_db": False,
            "name": "files",
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "tool_mode": False,
            "trace_as_input": True,
            "trace_as_metadata": True,
            "type": "file",
            "value": ""
        },
        "text_color": {
            "_input_type": "MessageTextInput",
            "advanced": True,
            "display_name": "Text Color",
            "dynamic": False,
            "info": "The text color of the name",
            "input_types": ["Message"],
            "list": False,
            "list_add_label": "Add More",
            "load_from_db": False,
            "name": "text_color",
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "tool_mode": False,
            "trace_as_input": True,
            "trace_as_metadata": True,
            "type": "str",
            "value": ""
        },
        "code": {
            "advanced": True,
            "dynamic": True,
            "fileTypes": [],
            "file_path": "",
            "info": "",
            "list": False,
            "load_from_db": False,
            "multiline": True,
            "name": "code",
            "password": False,
            "placeholder": "",
            "required": True,
            "show": True,
            "title_case": False,
            "type": "code",
            "value": "from langflow.base.data.utils import IMG_FILE_TYPES, TEXT_FILE_TYPES\nfrom langflow.base.io.chat import ChatComponent\nfrom langflow.inputs.inputs import BoolInput\nfrom langflow.io import (\n    DropdownInput,\n    FileInput,\n    MessageTextInput,\n    MultilineInput,\n    Output,\n)\nfrom langflow.schema.message import Message\nfrom langflow.utils.constants import (\n    MESSAGE_SENDER_AI,\n    MESSAGE_SENDER_NAME_USER,\n    MESSAGE_SENDER_USER,\n)\n\n\nclass ChatInput(ChatComponent):\n    display_name = \"Chat Input\"\n    description = \"Get chat inputs from the Playground.\"\n    icon = \"MessagesSquare\"\n    name = \"ChatInput\"\n    minimized = True\n\n    inputs = [\n        MultilineInput(\n            name=\"input_value\",\n            display_name=\"Input Text\",\n            value=\"\",\n            info=\"Message to be passed as input.\",\n            input_types=[],\n        ),\n        BoolInput(\n            name=\"should_store_message\",\n            display_name=\"Store Messages\",\n            info=\"Store the message in the history.\",\n            value=True,\n            advanced=True,\n        ),\n        DropdownInput(\n            name=\"sender\",\n            display_name=\"Sender Type\",\n            options=[MESSAGE_SENDER_AI, MESSAGE_SENDER_USER],\n            value=MESSAGE_SENDER_USER,\n            info=\"Type of sender.\",\n            advanced=True,\n        ),\n        MessageTextInput(\n            name=\"sender_name\",\n            display_name=\"Sender Name\",\n            info=\"Name of the sender.\",\n            value=MESSAGE_SENDER_NAME_USER,\n            advanced=True,\n        ),\n        MessageTextInput(\n            name=\"session_id\",\n            display_name=\"Session ID\",\n            info=\"The session ID of the chat. If empty, the current session ID parameter will be used.\",\n            advanced=True,\n        ),\n        FileInput(\n            name=\"files\",\n            display_name=\"Files\",\n            file_types=TEXT_FILE_TYPES + IMG_FILE_TYPES,\n            info=\"Files to be sent with the message.\",\n            advanced=True,\n            is_list=True,\n            temp_file=True,\n        ),\n        MessageTextInput(\n            name=\"background_color\",\n            display_name=\"Background Color\",\n            info=\"The background color of the icon.\",\n            advanced=True,\n        ),\n        MessageTextInput(\n            name=\"chat_icon\",\n            display_name=\"Icon\",\n            info=\"The icon of the message.\",\n            advanced=True,\n        ),\n        MessageTextInput(\n            name=\"text_color\",\n            display_name=\"Text Color\",\n            info=\"The text color of the name\",\n            advanced=True,\n        ),\n    ]\n    outputs = [\n        Output(display_name=\"Chat Message\", name=\"message\", method=\"message_response\"),\n    ]\n\n    async def message_response(self) -> Message:\n        background_color = self.background_color\n        text_color = self.text_color\n        icon = self.chat_icon\n\n        message = await Message.create(\n            text=self.input_value,\n            sender=self.sender,\n            sender_name=self.sender_name,\n            session_id=self.session_id,\n            files=self.files,\n            properties={\n                \"background_color\": background_color,\n                \"text_color\": text_color,\n                \"icon\": icon,\n            },\n        )\n        if self.session_id and isinstance(message, Message) and self.should_store_message:\n            stored_message = await self.send_message(\n                message,\n            )\n            self.message.value = stored_message\n            message = stored_message\n\n        self.status = message\n        return message\n"
        }
    }
}

PROMPT_TEMPLATE_OLD = {
    "description": "Create a prompt template with dynamic variables.",
    "display_name": "Prompt",
    "icon": "braces",
    "base_classes": ["Message"],
    "beta": False,
    "conditional_paths": [],
    "custom_fields": {},
    "documentation": "",
    "edited": False,
    "field_order": [
        "template",
        "tool_placeholder",
        "code"
    ],
    "frozen": False,
    "legacy": False,
    "lf_version": "1.4.3",
    "metadata": {},
    "output_types": [],
    "outputs": [{
        "display_name": "Prompt",
        "method": "build_prompt",
        "name": "prompt",
        "selected": "Message",
        "types": ["Message"]
    }],
    "pinned": False,
    "selected_output": "prompt",
    "tool_mode": False,
    "showNode": True,
    "priority": 0,
    "group_outputs": False,
    "template": {
        "_type": "Component",
        "template": {
            "_input_type": "PromptInput",
            "advanced": False,
            "display_name": "Template",
            "dynamic": False,
            "info": "",
            "list": False,
            "list_add_label": "Add More",
            "load_from_db": False,
            "name": "template",
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "tool_mode": False,
            "trace_as_input": True,
            "type": "prompt",
            "value": "You are a professional sentiment analysis expert. Your task is to analyze the sentiment of the given text and provide a comprehensive analysis.\n\nPlease analyze the sentiment of the text and respond with:\n\n1. **Overall Sentiment**: Classify as Positive, Negative, or Neutral\n2. **Confidence Score**: Rate your confidence from 1-10 (10 being most confident)\n3. **Key Indicators**: List the specific words, phrases, or expressions that led to your sentiment classification\n4. **Emotional Tone**: Describe the emotional tone (e.g., excited, frustrated, content, angry, happy, etc.)\n5. **Brief Explanation**: Provide a 1-2 sentence explanation of your analysis\n\nFormat your response clearly with these sections. Be objective and thorough in your analysis."
        },
        "tool_placeholder": {
            "_input_type": "MessageTextInput",
            "advanced": True,
            "display_name": "Tool Placeholder",
            "dynamic": False,
            "info": "A placeholder input for tool mode.",
            "input_types": ["Message"],
            "list": False,
            "list_add_label": "Add More",
            "load_from_db": False,
            "name": "tool_placeholder",
            "placeholder": "",
            "required": False,
            "show": True,
            "title_case": False,
            "tool_mode": True,
            "trace_as_input": True,
            "trace_as_metadata": True,
            "type": "str",
            "value": ""
        },
        "code": {
            "_input_type": "code",
            "display_name": "Code",
            "type": "code",
            "value": "from langflow.base.prompts.api_utils import process_prompt_template\nfrom langflow.custom.custom_component.component import Component\nfrom langflow.inputs.inputs import DefaultPromptField\nfrom langflow.io import MessageTextInput, Output, PromptInput\nfrom langflow.schema.message import Message\nfrom langflow.template.utils import update_template_values\n\nclass PromptComponent(Component):\n    display_name: str = \"Prompt\"\n    description: str = \"Create a prompt template with dynamic variables.\"\n    icon = \"braces\"\n    trace_type = \"prompt\"\n    name = \"Prompt\"\n\n    inputs = [\n        PromptInput(name=\"template\", display_name=\"Template\"),\n        MessageTextInput(\n            name=\"tool_placeholder\",\n            display_name=\"Tool Placeholder\",\n            tool_mode=True,\n            advanced=True,\n            info=\"A placeholder input for tool mode.\",\n        ),\n    ]\n\n    outputs = [\n        Output(display_name=\"Prompt\", name=\"prompt\", method=\"build_prompt\"),\n    ]\n\n    async def build_prompt(self) -> Message:\n        prompt = Message.from_template(**self._attributes)\n        self.status = prompt.text\n        return prompt\n\n    def _update_template(self, frontend_node: dict):\n        prompt_template = frontend_node[\"template\"][\"template\"][\"value\"]\n        custom_fields = frontend_node[\"custom_fields\"]\n        frontend_node_template = frontend_node[\"template\"]\n        _ = process_prompt_template(\n            template=prompt_template,\n            name=\"template\",\n            custom_fields=custom_fields,\n            frontend_node_template=frontend_node_template,\n        )\n        return frontend_node\n\n    async def update_frontend_node(self, new_frontend_node: dict, current_frontend_node: dict):\n        \"\"\"This function is called after the code validation is done.\"\"\"\n        frontend_node = await super().update_frontend_node(new_frontend_node, current_frontend_node)\n        template = frontend_node[\"template\"][\"template\"][\"value\"]\n        # Kept it duplicated for backwards compatibility\n        _ = process_prompt_template(\n            template=template,\n            name=\"template\",\n            custom_fields=frontend_node[\"custom_fields\"],\n            frontend_node_template=frontend_node[\"template\"],\n        )\n        # Now that template is updated, we need to grab any values that were set in the current_frontend_node\n        # and update the frontend_node with those values\n        update_template_values(new_template=frontend_node, previous_template=current_frontend_node[\"template\"])\n        return frontend_node\n\n    def _get_fallback_input(self, **kwargs):\n        return DefaultPromptField(**kwargs)\n"
        }
    }
}

LANGUAGE_MODEL_TEMPLATE_OLD = {
    "description": "Runs a language model given a specified provider. ",
    "display_name": "Language Model",
    "icon": "brain-circuit",
    "base_classes": ["LanguageModel", "Message"],
    "beta": False,
    "conditional_paths": [],
    "custom_fields": {},
    "documentation": "",
    "edited": False,
    "field_order": [
        "provider",
        "model_name",
        "api_key",
        "input_value",
        "system_message",
        "stream",
        "temperature",
        "code"
    ],
    "frozen": False,
    "legacy": False,
    "lf_version": "1.4.3",
    "metadata": {},
    "output_types": [],
    "outputs": [{
        "display_name": "Model Response",
        "method": "text_response",
        "name": "text_output",
        "selected": "Message",
        "types": ["Message"]
    }],
    "pinned": False,
    "selected_output": "text_output",
    "tool_mode": False,
    "showNode": True,
    "priority": 0,
    "group_outputs": False,
    "template": {
        "_type": "Component",
        "code": {
            "_input_type": "code",
            "display_name": "Code",
            "type": "code",
            "value": "from typing import Any\n\nfrom langchain_anthropic import ChatAnthropic\nfrom langchain_google_genai import ChatGoogleGenerativeAI\nfrom langchain_openai import ChatOpenAI\n\nfrom langflow.base.models.anthropic_constants import ANTHROPIC_MODELS\nfrom langflow.base.models.google_generative_ai_constants import GOOGLE_GENERATIVE_AI_MODELS\nfrom langflow.base.models.model import LCModelComponent\nfrom langflow.base.models.openai_constants import OPENAI_MODEL_NAMES\nfrom langflow.field_typing import LanguageModel\nfrom langflow.field_typing.range_spec import RangeSpec\nfrom langflow.inputs.inputs import BoolInput\nfrom langflow.io import DropdownInput, MessageInput, MultilineInput, SecretStrInput, SliderInput\nfrom langflow.schema.dotdict import dotdict\n\n\nclass LanguageModelComponent(LCModelComponent):\n    display_name = \"Language Model\"\n    description = \"Runs a language model given a specified provider. \"\n    icon = \"brain-circuit\"\n    category = \"models\"\n    priority = 0  # Set priority to 0 to make it appear first\n\n    inputs = [\n        DropdownInput(\n            name=\"provider\",\n            display_name=\"Model Provider\",\n            options=[\"OpenAI\", \"Anthropic\", \"Google\"],\n            value=\"OpenAI\",\n            info=\"Select the model provider\",\n            real_time_refresh=True,\n            options_metadata=[{\"icon\": \"OpenAI\"}, {\"icon\": \"Anthropic\"}, {\"icon\": \"Google\"}],\n        ),\n        DropdownInput(\n            name=\"model_name\",\n            display_name=\"Model Name\",\n            options=OPENAI_MODEL_NAMES,\n            value=OPENAI_MODEL_NAMES[0],\n            info=\"Select the model to use\",\n        ),\n        SecretStrInput(\n            name=\"api_key\",\n            display_name=\"OpenAI API Key\",\n            info=\"Model Provider API key\",\n            required=False,\n            show=True,\n            real_time_refresh=True,\n        ),\n        MessageInput(\n            name=\"input_value\",\n            display_name=\"Input\",\n            info=\"The input text to send to the model\",\n        ),\n        MultilineInput(\n            name=\"system_message\",\n            display_name=\"System Message\",\n            info=\"A system message that helps set the behavior of the assistant\",\n            advanced=True,\n        ),\n        BoolInput(\n            name=\"stream\",\n            display_name=\"Stream\",\n            info=\"Whether to stream the response\",\n            value=False,\n            advanced=True,\n        ),\n        SliderInput(\n            name=\"temperature\",\n            display_name=\"Temperature\",\n            value=0.1,\n            info=\"Controls randomness in responses\",\n            range_spec=RangeSpec(min=0, max=1, step=0.01),\n            advanced=True,\n        ),\n    ]\n\n    def build_model(self) -> LanguageModel:\n        provider = self.provider\n        model_name = self.model_name\n        temperature = self.temperature\n        stream = self.stream\n\n        if provider == \"OpenAI\":\n            if not self.api_key:\n                msg = \"OpenAI API key is required when using OpenAI provider\"\n                raise ValueError(msg)\n            return ChatOpenAI(\n                model_name=model_name,\n                temperature=temperature,\n                streaming=stream,\n                openai_api_key=self.api_key,\n            )\n        if provider == \"Anthropic\":\n            if not self.api_key:\n                msg = \"Anthropic API key is required when using Anthropic provider\"\n                raise ValueError(msg)\n            return ChatAnthropic(\n                model=model_name,\n                temperature=temperature,\n                streaming=stream,\n                anthropic_api_key=self.api_key,\n            )\n        if provider == \"Google\":\n            if not self.api_key:\n                msg = \"Google API key is required when using Google provider\"\n                raise ValueError(msg)\n            return ChatGoogleGenerativeAI(\n                model=model_name,\n                temperature=temperature,\n                streaming=stream,\n                google_api_key=self.api_key,\n            )\n        msg = f\"Unknown provider: {provider}\"\n        raise ValueError(msg)\n\n    def update_build_config(self, build_config: dotdict, field_value: Any, field_name: str | None = None) -> dotdict:\n        if field_name == \"provider\":\n            if field_value == \"OpenAI\":\n                build_config[\"model_name\"][\"options\"] = OPENAI_MODEL_NAMES\n                build_config[\"model_name\"][\"value\"] = OPENAI_MODEL_NAMES[0]\n                build_config[\"api_key\"][\"display_name\"] = \"OpenAI API Key\"\n            elif field_value == \"Anthropic\":\n                build_config[\"model_name\"][\"options\"] = ANTHROPIC_MODELS\n                build_config[\"model_name\"][\"value\"] = ANTHROPIC_MODELS[0]\n                build_config[\"api_key\"][\"display_name\"] = \"Anthropic API Key\"\n            elif field_value == \"Google\":\n                build_config[\"model_name\"][\"options\"] = GOOGLE_GENERATIVE_AI_MODELS\n                build_config[\"model_name\"][\"value\"] = GOOGLE_GENERATIVE_AI_MODELS[0]\n                build_config[\"api_key\"][\"display_name\"] = \"Google API Key\"\n        return build_config\n"
        },
        "api_key": {
            "_input_type": "SecretStrInput",
            "display_name": "OpenAI API Key",
            "type": "str",
            "required": True,
            "value": ""
        },
        "input_value": {
            "_input_type": "MessageTextInput",
            "display_name": "Input",
            "type": "str",
            "value": ""
        },
        "model_name": {
            "_input_type": "DropdownInput",
            "display_name": "Model Name",
            "type": "str",
            "options": ["gpt-4o-mini", "gpt-4o"],
            "value": "gpt-4o-mini"
        },
        "provider": {
            "_input_type": "DropdownInput",
            "display_name": "Model Provider",
            "type": "str",
            "options": ["OpenAI", "Anthropic", "Google"],
            "options_metadata": [
                {"icon": "OpenAI"},
                {"icon": "Anthropic"},
                {"icon": "Google"}
            ],
            "placeholder": "",
            "real_time_refresh": True,
            "required": False,
            "show": True,
            "title_case": False,
            "toggle": False,
            "tool_mode": False,
            "trace_as_metadata": True,
            "value": "OpenAI"
        },
        "stream": {
            "_input_type": "BoolInput",
            "display_name": "Stream",
            "type": "bool",
            "value": False
        },
        "system_message": {
            "_input_type": "MultilineInput",
            "display_name": "System Message",
            "type": "str",
            "value": ""
        },
        "temperature": {
            "_input_type": "SliderInput",
            "display_name": "Temperature",
            "type": "slider",
            "value": 0.1
        }
    }
}

CHAT_OUTPUT_TEMPLATE_OLD = {
    "description": "Display a chat message in the Playground.",
    "display_name": "Chat Output",
    "icon": "monitor-speaker",
    "base_classes": ["CustomComponent"],
    "beta": False,
    "conditional_paths": [],
    "custom_fields": {},
    "documentation": "",
    "edited": False,
    "field_order": [
        "input_value",
        "sender",
        "sender_name",
        "session_id",
        "data_template",
        "should_store_message",
        "code"
    ],
    "frozen": False,
    "legacy": False,
    "lf_version": "1.4.3",
    "metadata": {},
    "output_types": [],
    "outputs": [{
        "display_name": "Chat Output",
        "method": "chat_output",
        "name": "message",
        "selected": "Message",
        "types": ["Message"]
    }],
    "pinned": False,
    "selected_output": "message",
    "tool_mode": False,
    "showNode": True,
    "priority": 0,
    "group_outputs": False,
    "template": {
        "_type": "Component",
        "code": {
            "_input_type": "code",
            "display_name": "Code",
            "type": "code",
            "value": "from typing import Any, List\n\nfrom pydantic import BaseModel\n\nfrom langflow.base.io.chat import ChatComponent\nfrom langflow.io import BoolInput, DataInput, MessageTextInput, StrInput\nfrom langflow.schema import Data\nfrom langflow.schema.message import Message\n\n\nclass ChatOutputComponent(ChatComponent):\n    display_name = \"Chat Output\"\n    description = \"Display a chat message in the Playground.\"\n    icon = \"monitor-speaker\"\n\n    inputs = [\n        MessageTextInput(\n            name=\"input_value\",\n            display_name=\"Text\",\n            info=\"Text to be passed as output.\",\n        ),\n        StrInput(\n            name=\"sender\",\n            display_name=\"Sender Type\",\n            options=[\"Machine\", \"User\", \"System\"],\n            value=\"Machine\",\n            info=\"The sender type for this message.\",\n            advanced=True,\n        ),\n        StrInput(\n            name=\"sender_name\",\n            display_name=\"Sender Name\",\n            info=\"The sender name for this message.\",\n            value=\"LangFlow\",\n            advanced=True,\n        ),\n        StrInput(\n            name=\"session_id\",\n            display_name=\"Session ID\",\n            info=\"The session ID for this message.\",\n            advanced=True,\n        ),\n        DataInput(\n            name=\"data_template\",\n            display_name=\"Data Template\",\n            info=\"Template to convert Data to Text. If left empty, it will be dynamically set to the Data's text key.\",\n            tool_mode=True,\n        ),\n        BoolInput(\n            name=\"should_store_message\",\n            display_name=\"Store Message\",\n            info=\"Whether to store the message in the memory.\",\n            value=True,\n            advanced=True,\n        ),\n    ]\n\n    def chat_output(self) -> Message:\n        sender_name = self.sender_name or \"LangFlow\"\n        sender = self.sender or \"Machine\"\n        session_id = self.session_id or \"\"\n        should_store_message = self.should_store_message\n\n        if hasattr(self.input_value, \"data\") and isinstance(self.input_value.data, dict):\n            # Check if it's a Data object that should be processed\n            data_obj: Data = Data(data=self.input_value.data)\n            if hasattr(data_obj, \"get_text\"):\n                content = data_obj.get_text(template=self.data_template)\n            else:\n                content = str(data_obj.data)\n        elif isinstance(self.input_value, Data):\n            content = self.input_value.get_text(template=self.data_template)\n        elif isinstance(self.input_value, BaseModel):\n            content = self.input_value.model_dump_json(exclude_none=True)\n        elif isinstance(self.input_value, Message):\n            content = self.input_value.text\n        else:\n            content = str(self.input_value)\n\n        message = Message(\n            text=content,\n            sender=sender,\n            sender_name=sender_name,\n            session_id=session_id,\n        )\n\n        # Store the message if needed\n        if should_store_message:\n            self.send_message(message)\n\n        return message\n"
        },
        "data_template": {
            "_input_type": "DataInput",
            "display_name": "Data Template",
            "type": "str",
            "value": ""
        },
        "input_value": {
            "_input_type": "MessageTextInput",
            "display_name": "Text",
            "type": "str",
            "value": ""
        },
        "sender": {
            "_input_type": "StrInput",
            "display_name": "Sender Type",
            "type": "str",
            "options": ["Machine", "User", "System"],
            "value": "Machine"
        },
        "sender_name": {
            "_input_type": "StrInput",
            "display_name": "Sender Name",
            "type": "str",
            "value": "LangFlow"
        },
        "session_id": {
            "_input_type": "StrInput",
            "display_name": "Session ID",
            "type": "str",
            "value": ""
        },
        "should_store_message": {
            "_input_type": "BoolInput",
            "display_name": "Store Message",
            "type": "bool",
            "value": True
        }
    }
}

from components import (
    CHAT_INPUT_TEMPLATE,
    CHAT_OUTPUT_TEMPLATE,
    LANGUAGE_MODEL_TEMPLATE,
    PROMPT_TEMPLATE,
    AGENT_TEMPLATE,
    CALCULATOR_TEMPLATE,
    WEB_SEARCH_TEMPLATE,
    TEXT_INPUT_TEMPLATE,
    TEXT_OUTPUT_TEMPLATE
)

NEW_COMPONENT_TEMPLATES = {
    "BatchRunComponent": BATCH_RUN_COMPONENT_TEMPLATE,
    "YouTubeCommentsComponent": YOUTUBE_COMMENTS_COMPONENT_TEMPLATE,
    "OpenAIModel": OPENAI_MODEL_TEMPLATE,
    "Agent": AGENT_TEMPLATE,
    "ChatInput": CHAT_INPUT_TEMPLATE,
    "Prompt": PROMPT_TEMPLATE,
    "LanguageModel": LANGUAGE_MODEL_TEMPLATE,
    "ChatOutput": CHAT_OUTPUT_TEMPLATE,
    "Agent": AGENT_TEMPLATE,
    "Calculator": CALCULATOR_TEMPLATE,
    "WebSearch": WEB_SEARCH_TEMPLATE,
    "TextInput": TEXT_INPUT_TEMPLATE,
    "TextOutput": TEXT_OUTPUT_TEMPLATE
}
