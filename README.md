# Apple Notes MCP Server

> Powerful tools for automating Apple Notes using Model Context Protocol (MCP)

[![PyPI version](https://badge.fury.io/py/mcp-apple-notes.svg)](https://pypi.org/project/mcp-apple-notes/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Overview

Apple Notes MCP Server provides seamless integration of Apple Notes with any MCP-compatible client. It enables full note automation — including creating, reading, updating, and deleting notes — through a simple and secure AppleScript API layer.

## Features

* **Full CRUD support** for Apple Notes (Create, Read, Update, Delete)
* **Works with Continue.dev, Claude Desktop, Perplexity, and other MCP clients**
* **Native AppleScript integration** for reliable macOS automation
* **Comprehensive tools** for Apple Notes automation
* **Automatic installation** via `uvx` or manual setup
* **FastMCP implementation** with modern decorator-based API

## Requirements

* **macOS** - Required for AppleScript support
* **Python 3.10+** - Required for MCP SDK compatibility
* **Apple Notes application** - Must be installed and accessible
* **MCP-compatible client** (e.g., Continue.dev, Claude Desktop)

## Quick Start

### 1. Install the Package

**Option A: Using uvx (Recommended)**
```bash
# Install directly with uvx
uvx mcp-apple-notes@latest
```

**Option B: Manual Installation**
```bash
# Clone the repository
git clone https://github.com/henilcalagiya/mcp-apple-notes.git
cd mcp-apple-notes

# Install dependencies
uv sync
```

### 2. Configure MCP Client

Add this configuration to your MCP client:

```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "uvx",
      "args": ["mcp-apple-notes@latest"]
    }
  }
}
```

**Alternative Configuration (Manual Setup):**
```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_apple_notes.server"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-apple-notes"
      }
    }
  }
}
```

### 3. Grant Permissions

Ensure your MCP client has permission to:
- Access Apple Notes application
- Execute AppleScript commands
- Read/write to your notes

**🎉 You're all set!** Your MCP client will automatically install and run the package when needed.

## Available Tools

### **🆕 Unified Note Creation**
The `create_note` tool now handles both simple folders and nested paths automatically:

```python
# Simple folder
await create_note("Meeting Notes", "Content", "Work")

# Nested path (must exist)
await create_note("Sprint Planning", "Content", "Work/Projects/2024/Q1")

# Special characters (automatically escaped)
await create_note("Code Note", 'Path: "C:\\Users\\Name\\file.txt"', "Work")

# Read note by name and path
await read_note("Meeting Notes", "Work")
await read_note("Sprint Planning", "Work/Projects/2024/Q1")
```

**Features:**
- ✅ **Smart Path Detection**: Automatically detects simple vs nested paths
- ✅ **Path Validation**: Ensures folder path exists before creating note
- ✅ **Character Escaping**: Automatically handles quotes and backslashes
- ✅ **Backward Compatible**: Works with existing simple folder usage
- ✅ **Error Handling**: Comprehensive validation and error messages
- ✅ **Rich Content Support**: Plain text, HTML, Unicode, URLs, checklists, code blocks

### **📝 Supported Content Types**

The `create_note` tool supports various content types in the note body:

#### **Plain Text & Unicode**
```python
await create_note("Status", "🚀 Project: ✅ Complete\n📱 Mobile: 🔄 In Progress")
```

#### **HTML Formatting**
```python
await create_note("Formatted", "<h1>Title</h1><p><strong>Bold</strong> and <em>italic</em></p>")
```

#### **Checklists**
```python
await create_note("Tasks", "☐ Review code<br>☐ Write tests<br>☑ Deploy")
```

#### **URLs & Links**
```python
await create_note("Links", "Visit: https://github.com/project\nContact: mailto:team@project.com")
```

#### **Code Blocks**
```python
await create_note("Code", "function hello() {<br>    console.log('Hello, World!');<br>}")
```

### **📝 Updating Notes with Rich Content**

The `update_note` tool supports the same content types as `create_note`:

#### **Update with Unicode & Emojis**
```python
await update_note("Status", "Work", new_body="🚀 Project: ✅ Complete\n📱 Mobile: 🔄 In Progress")
```

#### **Update with HTML Formatting**
```python
await update_note("Documentation", "Work", new_body="<h1>Updated Title</h1><p><strong>New content</strong> with <em>formatting</em></p>")
```

#### **Update with Checklists**
```python
await update_note("Tasks", "Work", new_body="☐ New task 1<br>☐ New task 2<br>☑ Completed task")
```

#### **Update with Code & URLs**
```python
await update_note("API Docs", "Work", new_body="Updated API:<br>function newAPI() {<br>    return 'updated';<br>}<br><br>Visit: https://docs.updated.com")
```

### **⚠️ Important: Line Breaks and Formatting**

**Apple Notes does NOT preserve plain text `\n` characters.** For proper formatting:

- **Use `<br>` for line breaks** instead of `\n`
- **Use `<ul><li>item</li></ul>` for bullet lists**
- **Use `<div>` tags for paragraph separation**

```python
# ❌ Wrong - \n characters are ignored
await create_note("Test", "Line 1\nLine 2\nLine 3")

# ✅ Correct - Use HTML line breaks
await create_note("Test", "Line 1<br>Line 2<br>Line 3")
```

### **Tool Reference**

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_notes_with_structure` | List complete folder structure with notes included | None |
| `list_folder_with_structure` | List complete folder structure | None |
| `create_note` | Create a new note (unified - handles simple and nested paths) | `name` (string), `body` (string, supports HTML/Unicode/URLs), `folder_path` (string, optional, default: "Notes") |
| `read_note` | Read notes by name and path (unified - handles simple and nested paths) | `note_name` (string), `folder_path` (string, optional, default: "Notes") |
| `update_note` | Update note content and metadata with duplicate validation | `note_name` (string), `folder_path` (string, optional, default: "Notes"), `new_name` (string, optional), `new_body` (string, supports HTML/Unicode/URLs, optional), `note_index` (integer, optional) |
| `delete_note` | Delete notes with duplicate handling | `note_name` (string), `folder_path` (string, optional, default: "Notes") |
| `create_folder` | Create folder with optional path | `folder_name` (string), `folder_path` (string, optional) |
| `get_folder_details` | Get comprehensive folder details | `folder_name` (string) |
| `rename_folder` | Rename folder with path support | `folder_path` (string), `current_name` (string), `new_name` (string) |
| `move_folder` | Move folder between locations | `source_path` (string), `folder_name` (string), `target_path` (string, optional) |

## Available Resources

| Resource | Description | MIME Type |
|----------|-------------|-----------|
| `notes://all` | All Apple Notes data | `application/json` |
| `notes://metadata` | Notes metadata and structure | `application/json` |

## Available Prompts

| Prompt | Description | Arguments |
|--------|-------------|-----------|
| `create_note_template` | Template for creating a new note | `title`, `content` |
| `search_notes_template` | Template for searching notes | `query` |

## Architecture

The server follows the MCP protocol specification and is built with a modular architecture using FastMCP:

- **AppleScript Layer** - Handles direct interaction with Apple Notes
- **Tools Layer** - Wraps AppleScript operations for MCP tools
- **FastMCP Server Layer** - Implements MCP protocol using decorators for clean tool definitions

## Development

### Running the Server

```bash
# Run the FastMCP server directly
uv run python -m mcp_apple_notes.server

# Or use the installed script
uv run mcp-apple-notes
```

### Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=mcp_apple_notes
```

### Code Quality

```bash
# Format code
uv run black .
uv run isort .

# Lint code
uv run ruff check .
uv run mypy .
```

## Troubleshooting

### Common Issues

1. **"No module named 'mcp'" Error**
   - Use `uvx` for automatic installation
   - Ensure `uv` is installed and in PATH

2. **AppleScript Permission Denied**
   - Grant permission to your terminal/MCP client in System Preferences → Security & Privacy → Privacy → Accessibility

3. **Notes Not Found**
   - Ensure Apple Notes app is installed and accessible
   - Check that notes exist in the default location

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Henil C Alagiya**

* **GitHub**: [@henilcalagiya](https://github.com/henilcalagiya)
* **LinkedIn**: [Henil C Alagiya](https://linkedin.com/in/henilcalagiya)

**Support & Contributions:**

* 🐛 **Report Issues**: [GitHub Issues](https://github.com/henilcalagiya/mcp-apple-notes/issues)
* 💬 **Questions**: Reach out on [LinkedIn](https://linkedin.com/in/henilcalagiya)
* 🤝 **Contributions**: Pull requests welcome!

## Related Projects

* [Google Sheets MCP](https://github.com/henilcalagiya/google-sheets-mcp) - MCP server for Google Sheets automation
* [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official Python SDK for MCP
