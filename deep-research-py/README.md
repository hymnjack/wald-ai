# Deep Research Python

A Python implementation of the Deep Research system with Streamlit UI. This version builds upon the original TypeScript implementation, adding a user-friendly interface and additional features.

## Features

- Iterative deep research using LLMs and web search
- Real-time progress visualization
- Interactive parameter tuning
- Export options (PDF/HTML/Markdown)
- Caching and rate limiting
- Concurrent processing

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run Streamlit app:
```bash
streamlit run streamlit_app/app.py
```

## Project Structure

```
deep-research-py/
├── src/                   # Core Python implementation
│   ├── core/             # Core research logic
│   ├── integrations/     # External API clients
│   └── utils/            # Helper functions
├── streamlit_app/        # Streamlit interface
├── tests/                # Test cases
└── requirements.txt      # Python dependencies
```

## Development

1. Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest tests/
```

## License

Same as the original project.
