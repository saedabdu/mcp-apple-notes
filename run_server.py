#!/usr/bin/env python3
"""
Standalone script to run the MCP Apple Notes server
"""
import sys
import os
import subprocess
import shutil

def run_with_uv():
    """Run the server using uv if available."""
    uv_path = shutil.which("uv")
    if uv_path:
        try:
            # Use uv to run the server
            result = subprocess.run([
                uv_path, "run", "python", "-m", "mcp_apple_notes.server"
            ], check=True)
            return result.returncode
        except subprocess.CalledProcessError as e:
            print(f"Error running with uv: {e}", file=sys.stderr)
            return e.returncode
    return None

def run_direct():
    """Run the server directly (fallback)."""
    try:
        # Add the current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Try to import and run the server
        from mcp_apple_notes.server import mcp
        mcp.run()
        return 0
    except ImportError as e:
        print(f"Import error: {e}", file=sys.stderr)
        print("Make sure you're running this with uv: uv run python run_server.py", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    # Try uv first, then fallback to direct execution
    exit_code = run_with_uv()
    if exit_code is None:
        exit_code = run_direct()
    
    sys.exit(exit_code if exit_code is not None else 1)
