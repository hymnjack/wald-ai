# Sanitization LangChain Tools

This package provides LangChain tools for text sanitization, sensitivity checking, and image content analysis.

## Components

1. `SanitizeTool`: Comprehensive text sanitization that handles sensitive information and code
2. `SensitivityCheckTool`: Quick check for sensitive information in text
3. `ImageAnalysisTool`: Analysis of image-related content in text

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Individual Tools

```python
from sanitize_tools import SanitizeTool, SensitivityCheckTool, ImageAnalysisTool

# Initialize tools
sanitize_tool = SanitizeTool()
sensitivity_tool = SensitivityCheckTool()
image_tool = ImageAnalysisTool()

# Use tools
sanitize_result = sanitize_tool.run({
    "prompt": "Text to sanitize"
    })

sensitivity_result = sensitivity_tool.run({
    "prompt": "Text to check"
})

image_result = image_tool.run({
    "prompt": "Text to analyze for image content"
})
```

### With LangChain Agent

```python
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from sanitize_tools import SanitizeTool, SensitivityCheckTool, ImageAnalysisTool

# Initialize tools
tools = [
    SanitizeTool(),
    SensitivityCheckTool(),
    ImageAnalysisTool()
]

# Initialize LLM and agent
llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# Use agent
result = agent.run("Check if this text contains sensitive information: 'My password is 12345'")
```

## Testing

Run the test file to see the tools in action:

```bash
python test_sanitize_tools.py
```

## Prerequisites

1. The backend service should be running at `http://localhost:8080`
2. OpenAI API key should be set in your environment variables:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

## Note

Make sure the backend service (Flask app) is running before using these tools, as they depend on the API endpoints being available.
