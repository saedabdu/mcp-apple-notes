#!/usr/bin/env python3
"""
Auto setup script for Apple Notes MCP Server
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 10):
        print("❌ Python 3.10+ is required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("❌ This package requires macOS for AppleScript support")
        return False
    print("✅ macOS detected")
    
    # Check if Apple Notes is accessible
    try:
        result = run_command('osascript -e "tell application \\"Notes\\" to return name"')
        if result:
            print("✅ Apple Notes is accessible")
        else:
            print("⚠️  Apple Notes might not be accessible")
    except:
        print("⚠️  Could not verify Apple Notes accessibility")
    
    return True

def install_uv():
    """Install uv if not already installed."""
    print("\n📦 Checking uv installation...")
    
    uv_path = run_command("which uv")
    if uv_path:
        print(f"✅ uv is already installed at: {uv_path}")
        return True
    
    print("Installing uv...")
    install_script = "curl -LsSf https://astral.sh/uv/install.sh | sh"
    result = run_command(install_script)
    
    if result is not None:
        print("✅ uv installed successfully")
        return True
    else:
        print("❌ Failed to install uv")
        return False

def setup_project():
    """Set up the project dependencies."""
    print("\n🔧 Setting up project...")
    
    # Install dependencies
    result = run_command("uv sync")
    if result is not None:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install dependencies")
        return False

def create_mcp_config():
    """Create MCP configuration file."""
    print("\n⚙️  Creating MCP configuration...")
    
    config = {
        "mcpServers": {
            "apple-notes": {
                "command": "uvx",
                "args": ["mcp-apple-notes@latest"]
            }
        }
    }
    
    config_path = Path.home() / ".mcp" / "servers.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ MCP configuration created at: {config_path}")
    return True

def test_server():
    """Test if the server can start."""
    print("\n🧪 Testing server...")
    
    try:
        result = run_command("uv run python -m mcp_apple_notes.server --help", check=False)
        if result is not None:
            print("✅ Server test successful")
            return True
        else:
            print("❌ Server test failed")
            return False
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Apple Notes MCP Server Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup failed: Requirements not met")
        sys.exit(1)
    
    # Install uv
    if not install_uv():
        print("\n❌ Setup failed: Could not install uv")
        sys.exit(1)
    
    # Setup project
    if not setup_project():
        print("\n❌ Setup failed: Could not set up project")
        sys.exit(1)
    
    # Create MCP config
    if not create_mcp_config():
        print("\n❌ Setup failed: Could not create MCP config")
        sys.exit(1)
    
    # Test server
    if not test_server():
        print("\n⚠️  Setup completed but server test failed")
        print("You may need to check your Apple Notes permissions")
    else:
        print("\n✅ Setup completed successfully!")
    
    print("\n📋 Next Steps:")
    print("1. Configure your MCP client to use the Apple Notes server")
    print("2. Grant necessary permissions to your terminal/MCP client")
    print("3. Test the integration with your MCP client")
    print("\n📚 Documentation: https://github.com/henilcalagiya/mcp-apple-notes")

if __name__ == "__main__":
    main()
