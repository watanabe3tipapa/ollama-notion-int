[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/watanabe3tipapa/ollama-notion-int)

# Ollama Notion Int

Web UI to generate text with Ollama and save to Notion.

> This tool does not use MCP (Model Context Protocol).
> It simply makes direct calls to the HTTP API.


## Status

- Version: 0.2.0
- Primary language: Python
- Last updated: 2026-03-26 (repository metadata)
- Archived: no


## Main functionality

- Provide a web UI for generating text with Ollama
- Save generated text into Notion
- Communicates with the model via direct HTTP API calls (does not use MCP)


## Quick start

Run the commands shown below in a suitable environment (as provided in the project):

```bash
# Create venv
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Run
.venv/bin/python app.py
```

Open http://localhost:7860


## Documentation

See docs/USAGE.md for usage details.


## Repository contents (top-level)

- .gitignore
- README.md
- app.py
- docs/
- requirements.txt


## License

This project is released under the MIT License.
