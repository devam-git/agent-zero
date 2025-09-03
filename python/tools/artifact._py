import json
import uuid
from datetime import datetime
from pathlib import Path
from python.helpers.tool import Tool, Response
from python.helpers.memory import Memory
from langchain_core.documents import Document

class Artifact(Tool):
    def __init__(self, agent, name: str, method: str | None, args: dict[str, str], message: str, loop_data=None, **kwargs):
        super().__init__(agent, name, method, args, message, loop_data, **kwargs)
        self.base_dir = Path("a0/data") / f"{agent.number}_{agent.config.profile}" / "artifacts"
        self.metadata_file = self.base_dir / "metadata.json"
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        if not self.metadata_file.exists():
            self._save_metadata({})

    def _load_metadata(self) -> dict:
        try:
            return json.loads(self.metadata_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_metadata(self, metadata: dict):
        self.metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    def _generate_id(self) -> str:
        return str(uuid.uuid4())[:8]

    def _detect_type(self, content: str) -> str:
        content_lower = content.lower().strip()
        
        # Code detection
        if any(lang in content_lower for lang in ['def ', 'function ', 'class ', 'import ', '#include', 'console.log', 'SELECT', 'CREATE TABLE']):
            return "code"
        
        # Data detection
        if content_lower.startswith('{') or content_lower.startswith('[') or ',' in content and '\n' in content:
            return "data"
        
        # Documentation detection  
        if any(marker in content for marker in ['# ', '## ', '### ', '**', '*', '- ', '1. ']):
            return "document"
        
        return "text"


    async def execute(self, **kwargs) -> Response:
        action = self.args.get("action", "list")
        
        if action == "create":
            return await self._create_artifact()
        elif action == "update":
            return await self._update_artifact()
        elif action == "get":
            return await self._get_artifact()
        elif action == "list":
            return await self._list_artifacts()
        elif action == "delete":
            return await self._delete_artifact()
        elif action == "search":
            return await self._search_artifacts()
        else:
            return Response(message="Invalid action. Use: create, update, get, list, delete, search", break_loop=False)

    async def _create_artifact(self) -> Response:
        title = self.args.get("title", "").strip()
        content = self.args.get("content", "").strip()
        description = self.args.get("description", "").strip()
        artifact_type = self.args.get("type", "").strip()
        
        if not title or not content:
            return Response(message="Title and content are required for creating artifacts", break_loop=False)
        
        artifact_id = self._generate_id()
        
        # Auto-detect type if not provided
        if not artifact_type:
            artifact_type = self._detect_type(content)
        
        # Save content to file
        content_file = self.base_dir / f"{artifact_id}.txt"
        content_file.write_text(content, encoding="utf-8")
        
        # Update metadata
        metadata = self._load_metadata()
        metadata[artifact_id] = {
            "title": title,
            "description": description,
            "type": artifact_type,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "size": len(content)
        }
        self._save_metadata(metadata)
        
        # Save to vector DB for searchability
        await self._save_to_vector_db(artifact_id, title, description, artifact_type)
        
        return Response(message=f"Created artifact '{title}' (ID: {artifact_id}, Type: {artifact_type})\nDescription: {description}", break_loop=False)

    async def _update_artifact(self) -> Response:
        artifact_id = self.args.get("id", "").strip()
        content = self.args.get("content", "").strip()
        title = self.args.get("title", "").strip()
        description = self.args.get("description", "").strip()
        
        if not artifact_id:
            return Response(message="Artifact ID is required for updates", break_loop=False)
        
        metadata = self._load_metadata()
        if artifact_id not in metadata:
            return Response(message=f"Artifact {artifact_id} not found", break_loop=False)
        
        # Update content if provided
        if content:
            content_file = self.base_dir / f"{artifact_id}.txt"
            content_file.write_text(content, encoding="utf-8")
            metadata[artifact_id]["size"] = len(content)
            metadata[artifact_id]["type"] = self._detect_type(content)
        
        # Update metadata
        if title:
            metadata[artifact_id]["title"] = title
        if description:
            metadata[artifact_id]["description"] = description
        
        metadata[artifact_id]["updated"] = datetime.now().isoformat()
        self._save_metadata(metadata)
        
        # Update vector DB entry
        await self._update_vector_db(artifact_id, metadata[artifact_id])
        
        return Response(message=f"Updated artifact '{metadata[artifact_id]['title']}' (ID: {artifact_id})", break_loop=False)

    async def _get_artifact(self) -> Response:
        artifact_id = self.args.get("id", "").strip()
        
        if not artifact_id:
            return Response(message="Artifact ID is required", break_loop=False)
        
        metadata = self._load_metadata()
        if artifact_id not in metadata:
            return Response(message=f"Artifact {artifact_id} not found", break_loop=False)
        
        artifact_info = metadata[artifact_id]
        
        # Return full content
        content_file = self.base_dir / f"{artifact_id}.txt"
        if not content_file.exists():
            return Response(message=f"Artifact content file missing for {artifact_id}", break_loop=False)
        
        content = content_file.read_text(encoding="utf-8")
        return Response(message=f"Artifact: {artifact_info['title']}\nType: {artifact_info['type']}\nDescription: {artifact_info['description']}\nContent:\n{content}", break_loop=False)

    async def _list_artifacts(self) -> Response:
        metadata = self._load_metadata()
        
        if not metadata:
            return Response(message="No artifacts found", break_loop=False)
        
        artifact_list = []
        for artifact_id, info in metadata.items():
            artifact_list.append(f"ID: {artifact_id} | {info['title']} ({info['type']}) - {info['size']} chars")
            if info.get('description'):
                artifact_list.append(f"  Description: {info['description']}")
            artifact_list.append("")
        
        return Response(message=f"Artifacts ({len(metadata)} total):\n" + "\n".join(artifact_list), break_loop=False)

    async def _delete_artifact(self) -> Response:
        artifact_id = self.args.get("id", "").strip()
        
        if not artifact_id:
            return Response(message="Artifact ID is required for deletion", break_loop=False)
        
        metadata = self._load_metadata()
        if artifact_id not in metadata:
            return Response(message=f"Artifact {artifact_id} not found", break_loop=False)
        
        title = metadata[artifact_id]["title"]
        
        # Delete content file
        content_file = self.base_dir / f"{artifact_id}.txt"
        if content_file.exists():
            content_file.unlink()
        
        # Remove from metadata
        del metadata[artifact_id]
        self._save_metadata(metadata)
        
        # Remove from vector DB
        await self._delete_from_vector_db(artifact_id)
        
        return Response(message=f"Deleted artifact '{title}' (ID: {artifact_id})", break_loop=False)

    async def _search_artifacts(self) -> Response:
        query = self.args.get("query", "").strip().lower()
        artifact_type = self.args.get("type", "").strip().lower()
        
        if not query and not artifact_type:
            return Response(message="Search query or type filter is required", break_loop=False)
        
        metadata = self._load_metadata()
        matches = []
        
        for artifact_id, info in metadata.items():
            match = False
            
            # Search by query in title, description
            if query:
                searchable = f"{info['title']} {info.get('description', '')}".lower()
                if query in searchable:
                    match = True
            
            # Filter by type
            if artifact_type and info['type'].lower() == artifact_type:
                match = True
            
            # If both query and type provided, both must match
            if query and artifact_type:
                searchable = f"{info['title']} {info.get('description', '')}".lower()
                match = query in searchable and info['type'].lower() == artifact_type
            
            if match:
                matches.append(f"ID: {artifact_id} | {info['title']} ({info['type']})\n  Description: {info.get('description', 'No description')}")
        
        if not matches:
            return Response(message="No artifacts found matching search criteria", break_loop=False)
        
        return Response(message=f"Found {len(matches)} matching artifacts:\n\n" + "\n\n".join(matches), break_loop=False)

    async def _save_to_vector_db(self, artifact_id: str, title: str, description: str, artifact_type: str):
        """Save artifact metadata to vector DB for searchability"""
        try:
            memory = await Memory.get(self.agent)
            
            # Create searchable content from title and description
            content = f"Artifact: {title}"
            if description:
                content += f"\nDescription: {description}"
            
            # Create document with metadata
            doc = Document(
                page_content=content,
                metadata={
                    "area": "artifacts",
                    "artifact_id": artifact_id,
                    "title": title,
                    "description": description,
                    "type": artifact_type,
                    "timestamp": Memory.get_timestamp()
                }
            )
            
            # Insert into vector DB
            await memory.insert_documents([doc])
            
        except Exception as e:
            # Don't fail artifact creation if vector DB fails, just log
            pass

    async def _update_vector_db(self, artifact_id: str, metadata: dict):
        """Update artifact in vector DB"""
        try:
            # Delete old entry
            await self._delete_from_vector_db(artifact_id)
            
            # Add updated entry
            await self._save_to_vector_db(
                artifact_id, 
                metadata["title"], 
                metadata["description"], 
                metadata["type"]
            )
            
        except Exception as e:
            # Don't fail artifact update if vector DB fails
            pass

    async def _delete_from_vector_db(self, artifact_id: str):
        """Remove artifact from vector DB"""
        try:
            memory = await Memory.get(self.agent)
            
            # Find and delete documents with matching artifact_id
            docs = await memory.search_by_metadata(f"artifact_id=='{artifact_id}'")
            if docs:
                doc_ids = [doc.metadata["id"] for doc in docs]
                await memory.delete_documents_by_ids(doc_ids)
                
        except Exception as e:
            # Don't fail artifact deletion if vector DB fails
            pass