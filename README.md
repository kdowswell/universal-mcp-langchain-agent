# Universal MCP Langchain Agent

A flexible agent architecture for creating and configuring AI agents with customizable personas and tool integrations. This project aims to simplify the process of setting up and modifying agent behaviors across different Model Control Protocol (MCP) servers.

## Features 

- [x] Easy configuration of agent personas
- [x] Flexible tool integration
- [x] Support for multiple MCP servers (expanding)
- [x] Quick setup and modification of agent behaviors
- [x] Add more MCP servers
- [x] Support multiple LLM providers (Anthropic, Groq)
- [ ] OpenAI support (GPT-4, etc.)

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

4. Get API keys for your preferred model provider:
   - [Groq API key](https://groq.com/) for using Groq models
   - [Anthropic API key](https://www.anthropic.com/) for using Claude models
   - [Ollama](https://ollama.com/) for using local models (no API key required)

5. Create a `.env` file in the project root with your chosen provider's API key:
```sh
# For Groq:
GROQ_API_KEY=your_groq_api_key_here

# For Anthropic:
ANTHROPIC_API_KEY=your_anthropic_api_key_here
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

## Configuring the Agent

The agent's behavior can be customized through the `config.json` file in the project root:

```json
{
  "agent": {
    "name": "Universal Agent",
    "systemPrompt": "Your custom system prompt here"
  },
  "mcpServers": ["filesystem", "memory", "brave-search", "sequential-thinking", "github"],
}
```

### Configuration Options

1. **Model Configuration**:
   The `model` section in `config.json` allows you to specify which LLM provider and model to use:

   ```json
   {
     "model": {
       "provider": "anthropic",
       "name": "claude-3-5-sonnet-latest",
       "options": {
         "stop_sequences": null
       }
     }
   }
   ```

   Supported providers and models:
   - Ollama:
     ```json
     {
       "provider": "ollama",
       "name": "llama3.2:latest",
       "options": {
         "stop_sequences": null
       }
     }
     ```
   - Anthropic:
     ```json
     {
       "provider": "anthropic",
       "name": "claude-3-5-sonnet-latest",
       "options": {
         "stop_sequences": null
       }
     }
     ```
   - Groq:
     ```json
     {
       "provider": "groq",
       "name": "llama-3.1-8b-instant",
       "options": {
         "stop_sequences": null
       }
     }
     ```

2. **Agent Configuration**:
   - `name`: Set a custom name for your agent
   - `systemPrompt`: Define the agent's personality and behavior through a custom system prompt

2. **Tool Integration**:
   - `mcpServers`: List of enabled MCP servers that provide tools to the agent
   - Available servers:
     - `filesystem`: File operations
     - `memory`: Memory management
     - `brave-search`: Web search capabilities (requires `BRAVE_API_KEY`)
     - `sequential-thinking`: Advanced reasoning
     - `github`: GitHub integration (requires `GITHUB_PERSONAL_ACCESS_TOKEN`)


## Current Status

This project is in active development. While currently in proof-of-concept phase, we are working on expanding support for various MCP servers and adding more configuration options for agent personas and tool integrations.

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests to help improve the framework.