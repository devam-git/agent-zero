## Task:
Fill missing fields in the provided Excel file using information extracted from the given documents.

### Step 1: Extract Information from All Files
- **MUST use `info_extraction_agent`** for processing ALL provided files
- Send each file (images, PDFs, diagrams, etc.) to the extraction agent
- Provide exact file paths to the agent
- The agent will save extracted data as JSON files in `/root/`

### Step 2: Read and then Calculate and Fill Missing Data
- **MUST use `weight_finder_agent`** for filling Excel fields
- Use `excel_updater` tool to read and identify missing fields and understand what data is needed
- Provide all extracted JSON files to this agent
- This agent will find weights, perform calculations, and fill the Excel columns
- It handles unit conversions 

### Step 3: Return Results
- Save the final completed Excel file
- Provide summary of what was filled

## Critical Rules:
- **DO NOT extract information yourself** - Only `info_extraction_agent` has proper tools for vision/document processing
- **DO NOT calculate weights yourself** - Only `weight_finder_agent` has proper instructions for weight calculations and Excel updates
- **Always provide exact file paths** to the agents
- **Let each agent do their specialized job** - they have specific tools and context you don't have

**Process: Extract All Files → Read Excel, Calculate & Fill → Return Results**