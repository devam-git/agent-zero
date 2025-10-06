import os
import mimetypes
import base64
from typing import Union, Dict, Any 

class FileUtils:
    """Utility class for file operations used by coder tools."""
    
    @staticmethod
    def read_file(file_path: str, return_metadata: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Read a file from disk, returning content or metadata.

        **When to use 'read_file':**
        1. You want to load a file's contents into memory (string or base64 for images).
        2. You may optionally need metadata (MIME type, is_image).

        **Parameters**:
        - file_path: str  
          Absolute or relative path to the file to read.
        - return_metadata: bool (default=False)  
          If True, returns a dictionary with 'content', 'mime_type', 'is_image'.  
          Otherwise returns only the file's content as a string.

        **Error Handling**:
        - If the file cannot be read, tries reading as binary -> base64.  
        - If no parent directory is valid, prints a warning.

        Returns:
        - If return_metadata=False, a string of file contents.
        - If return_metadata=True, a dictionary with keys: content, mime_type, is_image.
        """
        valid_path = FileUtils.validate_path(file_path)
        mime_type, _ = mimetypes.guess_type(valid_path)
        is_img = FileUtils.is_image_file(mime_type if mime_type else "")
        if is_img:
            with open(valid_path, "rb") as f:
                content_bytes = f.read()
            content = base64.b64encode(content_bytes).decode("utf-8")
            result = {"content": content, "mime_type": mime_type, "is_image": True}
        else:
            try:
                with open(valid_path, "r", encoding="utf-8") as f:
                    content = f.read()
                result = {"content": content, "mime_type": mime_type or "text/plain", "is_image": False}
            except Exception:
                # fallback to binary -> base64 if text read fails
                with open(valid_path, "rb") as f:
                    content_bytes = f.read()
                content = "Binary file content (base64 encoded):\n" + base64.b64encode(content_bytes).decode("utf-8")
                result = {"content": content, "mime_type": "text/plain", "is_image": False}
        return result if return_metadata else result["content"]

    @staticmethod
    def write_file(file_path: str, content: str) -> None:
        """
        Overwrite a file with new content.

        **When to use 'write_file':**
        1. You're replacing an entire file's contents with new text.

        **Parameters**:
        - file_path: str  
          Path to the file to write.
        - content: str  
          The new text content to store in the file.

        **Error Handling**:
        - Creates parent directories if they don't exist.
        - Overwrites existing file content.
        """
        valid_path = FileUtils.validate_path(file_path)
        os.makedirs(os.path.dirname(valid_path), exist_ok=True)
        with open(valid_path, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def resolve_path(file_path: str) -> str:
        """Expand user shortcuts and return an absolute path."""
        expanded = os.path.expanduser(file_path)
        return os.path.abspath(expanded)

    @staticmethod
    def validate_parent_directories(directory_path: str) -> bool:
        """Recursively check if at least one parent directory exists."""
        parent_dir = os.path.dirname(directory_path)
        if parent_dir == directory_path or parent_dir == os.path.dirname(parent_dir):
            return False
        return os.path.exists(parent_dir) or FileUtils.validate_parent_directories(parent_dir)

    @staticmethod
    def validate_path(requested_path: str) -> str:
        """
        Resolve and validate a path.
        If the path exists, return its real (absolute) path.
        Otherwise, ensure that at least one parent directory exists.
        """
        full_path = FileUtils.resolve_path(requested_path)
        if os.path.exists(full_path):
            return os.path.realpath(full_path)
        if FileUtils.validate_parent_directories(full_path):
            return full_path
        print(f"Warning: No existing parent directory found for: {os.path.dirname(full_path)}")
        return full_path

    @staticmethod
    def is_image_file(mime_type: str) -> bool:
        """Return True if the MIME type indicates an image."""
        return mime_type.startswith("image/") if mime_type else False

# Create instance for backward compatibility
file_utils = FileUtils()

# Export functions for backward compatibility
read_file = FileUtils.read_file
write_file = FileUtils.write_file
resolve_path = FileUtils.resolve_path
validate_parent_directories = FileUtils.validate_parent_directories
validate_path = FileUtils.validate_path
is_image_file = FileUtils.is_image_file
