from typing import List, Dict, Any
from .base_operations import BaseAppleScriptOperations

class ListNotesOperations(BaseAppleScriptOperations):
    """Operations for listing Apple Notes."""
    
    @staticmethod
    async def list_all_notes() -> List[Dict[str, str]]:
        """Get all notes with their folder names."""
        script = '''
        tell application "Notes"
            set noteList to {}
            repeat with theFolder in folders
                set folderName to name of theFolder
                repeat with theNote in notes of theFolder
                    set noteInfo to {name:(name of theNote), folder:folderName}
                    copy noteInfo to end of noteList
                end repeat
            end repeat
            return noteList
        end tell
        '''
        result = await ListNotesOperations.execute_applescript(script)
        
        # Parse AppleScript result - simplified since we only have name and folder
        notes = []
        
        # Split the result into individual note entries
        # Each note entry starts with 'name:' and contains 2 fields
        entries = result.split('name:')
        
        for entry in entries[1:]:  # Skip the first empty entry
            try:
                # Find the end of the name (before ', folder:')
                name_end = entry.find(', folder:')
                if name_end == -1:
                    continue
                    
                name = entry[:name_end].strip()
                
                # Find folder (go to end or next 'name:')
                folder_start = entry.find('folder:') + 7
                folder_end = entry.find(', name:', folder_start)
                if folder_end == -1:
                    folder_end = len(entry)
                    
                folder = entry[folder_start:folder_end].strip().rstrip(',')
                
                notes.append({
                    'name': name,
                    'folder': folder
                })
                
            except Exception as e:
                # Skip malformed entries
                continue
        
        return notes
