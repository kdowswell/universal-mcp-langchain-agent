# Universal MCP Langchain Agent

A flexible agent architecture for creating and configuring AI agents with customizable personas and tool integrations. This project aims to simplify the process of setting up and modifying agent behaviors across different Model Control Protocol (MCP) servers.

## Features 

- [x] Easy configuration of agent personas
- [x] Flexible tool integration
- [x] Support for multiple MCP servers (expanding)
- [x] Quick setup and modification of agent behaviors
- [ ] Add more MCP servers
- [ ] Support multiple LLM providers

## Getting Started

1. Install uv (if you haven't already):
```sh
pip install uv
```

2. Create and activate a virtual environment:
```sh
uv venv
source .venv/bin/activate  # On Unix/MacOS
# or
.venv\Scripts\activate  # On Windows
```

3. Install the package using uv:
```sh
uv pip install -e .
```

4. Get a [Groq API key](https://groq.com/)

5. Create a `.env` file in the project root:
```sh
GROQ_API_KEY=your_api_key_here
```

6. Run the agent (make sure your virtual environment is activated):
```sh
# First, ensure your virtual environment is activated:
source .venv/bin/activate  # On Unix/MacOS
# or
.venv\Scripts\activate  # On Windows

# Then run the agent:
python src/main.py "Read and summarize the contents of README.md"
```

## Current Status

This project is in active development. While currently in proof-of-concept phase, we are working on expanding support for various MCP servers and adding more configuration options for agent personas and tool integrations.

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests to help improve the framework.