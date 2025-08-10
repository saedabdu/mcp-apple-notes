# MCP Configuration Files

This directory contains configuration files for integrating the Apple Notes MCP server with various MCP clients.

## Configuration Files

### 1. `mcp-config.json` - Basic Configuration (Recommended)
Simple configuration for most MCP clients using uv:
```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_apple_notes.server"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

### 2. `mcp-config-standalone.json` - Standalone Configuration
Alternative configuration using direct Python script:
```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "python",
      "args": ["run_server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

### 3. `mcp-config-advanced.json` - Advanced Configuration
Extended configuration with additional settings:
```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_apple_notes.server"],
      "env": {
        "PYTHONPATH": ".",
        "MCP_APPLE_NOTES_DEBUG": "false",
        "MCP_APPLE_NOTES_TIMEOUT": "30"
      },
      "description": "MCP server for Apple Notes integration",
      "capabilities": {
        "tools": true,
        "resources": false,
        "prompts": false,
        "logging": true
      }
    }
  },
  "settings": {
    "logLevel": "info",
    "timeout": 30000,
    "maxRetries": 3
  }
}
```

### 4. `claude-desktop-config.json` - Claude Desktop Configuration
Optimized for Claude Desktop:
```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_apple_notes.server"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## Usage Instructions

### For Claude Desktop
1. Open Claude Desktop
2. Go to Settings → MCP Servers
3. Click "Add Server"
4. Select "Import from file"
5. Choose `claude-desktop-config.json`
6. The Apple Notes server will be available in your conversations

### For Other MCP Clients
1. Copy the appropriate config file to your MCP client's configuration directory
2. Restart your MCP client
3. The Apple Notes server should be available

## Troubleshooting

### Common Issues

#### 1. "No module named 'mcp'" Error
**Problem**: The MCP client can't find the `mcp` module.

**Solutions**:
- **Use uv command** (Recommended): Use `mcp-config.json` with `uv run`
- **Use standalone script**: Use `mcp-config-standalone.json` with `run_server.py`
- **Install dependencies**: Ensure MCP dependencies are installed in your Python environment

#### 2. Server Process Terminated Unexpectedly
**Problem**: Server fails to start or crashes immediately.

**Solutions**:
- **Check uv installation**: Ensure `uv` is installed and in PATH
- **Use standalone approach**: Try `mcp-config-standalone.json`
- **Check Python version**: Ensure Python 3.13+ is available
- **Verify dependencies**: Run `uv sync` to install dependencies

#### 3. Import Errors
**Problem**: Module import failures.

**Solutions**:
- **Set PYTHONPATH**: Ensure `PYTHONPATH` includes the project directory
- **Use absolute paths**: Use full path to the project directory
- **Check virtual environment**: Ensure you're using the correct Python environment

### Environment Variables
- `PYTHONPATH`: Set to current directory for proper module imports
- `MCP_APPLE_NOTES_DEBUG`: Enable debug logging (true/false)
- `MCP_APPLE_NOTES_TIMEOUT`: AppleScript timeout in seconds

### Capabilities
- **tools**: ✅ Available - All Apple Notes operations
- **resources**: ❌ Not implemented - Future enhancement
- **prompts**: ❌ Not implemented - Future enhancement
- **logging**: ✅ Available - Progress and error reporting

### Debug Mode
To enable debug logging, set the environment variable:
```bash
export MCP_APPLE_NOTES_DEBUG=true
```

### Custom Configuration
You can modify the configuration files to:
- Change the server name
- Add custom environment variables
- Modify timeout settings
- Enable/disable specific capabilities
