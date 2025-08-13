from typing import List, Dict, Optional
from .base_operations import BaseAppleScriptOperations

class AppleScriptNotesUtilities(BaseAppleScriptOperations):
    """Utility functions for Apple Notes operations."""
    
    @staticmethod
    async def get_note_id_by_name(note_name: str, folder_name: str = None) -> str:
        """Get note ID by name and optional folder."""
        if folder_name:
            script = f'''
            tell application "Notes"
                try
                    set targetFolder to folder "{folder_name}"
                    repeat with theNote in notes of targetFolder
                        if name of theNote is "{note_name}" then
                            return id of theNote
                        end if
                    end repeat
                    return "error:Note not found"
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        else:
            script = f'''
            tell application "Notes"
                try
                    repeat with theNote in notes
                        if name of theNote is "{note_name}" then
                            return id of theNote
                        end if
                    end repeat
                    return "error:Note not found"
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        result = await AppleScriptNotesUtilities.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get note ID: {result[6:]}")
        
        return result

    @staticmethod
    async def get_note_ids_by_names(note_names: List[str], folder_name: str = None) -> Dict[str, str]:
        """Get multiple note IDs by names and optional folder."""
        if folder_name:
            script = f'''
            tell application "Notes"
                try
                    set targetFolder to folder "{folder_name}"
                    set resultDict to {{}}
                    repeat with theNote in notes of targetFolder
                        set noteName to name of theNote
                        if noteName is in {{{", ".join([f'"{name}"' for name in note_names])}}} then
                            set resultDict to resultDict & {{noteName:(id of theNote)}}
                        end if
                    end repeat
                    return resultDict
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        else:
            script = f'''
            tell application "Notes"
                try
                    set resultDict to {{}}
                    repeat with theNote in notes
                        set noteName to name of theNote
                        if noteName is in {{{", ".join([f'"{name}"' for name in note_names])}}} then
                            set resultDict to resultDict & {{noteName:(id of theNote)}}
                        end if
                    end repeat
                    return resultDict
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        result = await AppleScriptNotesUtilities.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get note IDs: {result[6:]}")
        
        # Parse the AppleScript dictionary result
        # Format: {name1:id1, name2:id2, ...}
        note_ids = {}
        if result and result != "{}":
            # Remove outer braces and split by comma
            content = result.strip('{}')
            pairs = content.split(',')
            
            for pair in pairs:
                if ':' in pair:
                    name_part, id_part = pair.split(':', 1)
                    name = name_part.strip()
                    note_id = id_part.strip()
                    note_ids[name] = note_id
        
        return note_ids

    @staticmethod
    async def get_app_version() -> str:
        """Get Apple Notes app version."""
        script = '''
        tell application "Notes"
            return version
        end tell
        '''
        return await AppleScriptNotesUtilities.execute_applescript(script)

    @staticmethod
    async def activate_notes_app() -> str:
        """Bring Apple Notes app to foreground."""
        script = '''
        tell application "Notes"
            activate
            return "Notes app activated"
        end tell
        '''
        return await AppleScriptNotesUtilities.execute_applescript(script)

    @staticmethod
    async def check_folder_exists(folder_name: str) -> bool:
        """Check if a folder exists in Apple Notes."""
        script = f'''
        tell application "Notes"
            try
                set targetFolder to folder "{folder_name}"
                return "true"
            on error
                return "false"
            end try
        end tell
        '''
        result = await AppleScriptNotesUtilities.execute_applescript(script)
        return result.lower() == "true"

    @staticmethod
    async def get_note_count(folder_name: str = None) -> int:
        """Get the number of notes in a folder or total notes."""
        if folder_name:
            script = f'''
            tell application "Notes"
                try
                    set targetFolder to folder "{folder_name}"
                    return count of notes of targetFolder
                on error
                    return 0
                end try
            end tell
            '''
        else:
            script = '''
            tell application "Notes"
                return count of notes
            end tell
            '''
        
        result = await AppleScriptNotesUtilities.execute_applescript(script)
        try:
            return int(result)
        except ValueError:
            return 0


