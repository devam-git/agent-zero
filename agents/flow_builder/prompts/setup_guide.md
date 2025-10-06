## Setup & Guide
1. Read **Builder Instructions** section for reference and some example workflows built
2. Check **Component Summary** table for quick component selection
3. Use **document_query** tool on `/a0/flow_builder/component_registry.md` for detailed API specs of selected components
4. **STRICTLY FOLLOW**:
Import builder: `sys.path.append(/a0/flow_builder')`
then `from builder import LangflowBuilder`
**ALWAYS ENSURE THAT YOU USE ONLY THIS WHILE BUILDING FLOWS**


## Importing LangflowBuilder
- Append ```/a0/flow_builder``` to sys.path in your Python script:
```python
import sys
sys.path.append('/a0/flow_builder')
```
- Import the class directly from the correct file
`from builder import LangflowBuilder`.  
This is necessary because LangflowBuilder is defined in builder.py, not in the package's ```__init__.py```.
- Verify the module structure before importing to avoid ImportError.  
These steps ensure that the builder module is always accessible and workflows can be created and saved without path or import issues.
