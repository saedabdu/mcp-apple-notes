from typing import Dict, Optional
from .base_operations import BaseAppleScriptOperations

class ReadNoteOperations(BaseAppleScriptOperations):
    """Operations for reading Apple Notes content."""
    
    @staticmethod
    async def read_note_by_name(note_name: str, folder_name: str = None) -> Dict[str, str]:
        """Read a note's content by name and optional folder."""
        if folder_name:
            script = f'''
            tell application "Notes"
                try
                    set targetFolder to folder "{folder_name}"
                    repeat with theNote in notes of targetFolder
                        if name of theNote is "{note_name}" then
                            return {{name:(name of theNote), folder:"{folder_name}", body:(body of theNote as string), creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
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
                    repeat with theFolder in folders
                        repeat with theNote in notes of theFolder
                            if name of theNote is "{note_name}" then
                                set noteFolder to name of theFolder
                                return {{name:(name of theNote), folder:noteFolder, body:(body of theNote as string), creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
                            end if
                        end repeat
                    end repeat
                    return "error:Note not found"
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        result = await ReadNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to read note: {result[6:]}")
        
        # Parse the result manually since body content may contain commas and special characters
        try:
            # Extract the note information from the result
            # Format: {name:noteName, folder:folderName, body:noteBody, creation_date:date, modification_date:date}
            
            # Find name
            name_start = result.find('name:') + 5
            name_end = result.find(', folder:', name_start)
            if name_end == -1:
                raise RuntimeError("Could not parse note name")
            name = result[name_start:name_end].strip()
            
            # Find folder
            folder_start = result.find('folder:') + 7
            folder_end = result.find(', body:', folder_start)
            if folder_end == -1:
                raise RuntimeError("Could not parse folder name")
            folder = result[folder_start:folder_end].strip()
            
            # Find body (this is tricky because body can contain commas and special characters)
            body_start = result.find(', body:') + 7
            body_end = result.find(', creation_date:', body_start)
            if body_end == -1:
                # If no creation_date, body goes to the end
                body_end = result.find(', modification_date:', body_start)
                if body_end == -1:
                    body_end = len(result)
            
            body = result[body_start:body_end].strip()
            
            # Find creation_date
            creation_start = result.find('creation_date:') + 14
            creation_end = result.find(', modification_date:', creation_start)
            if creation_end == -1:
                creation_end = len(result)
            creation_date = result[creation_start:creation_end].strip().rstrip(',')
            
            # Find modification_date
            modification_start = result.find('modification_date:') + 18
            modification_end = result.find('}', modification_start)
            if modification_end == -1:
                modification_end = len(result)
            modification_date = result[modification_start:modification_end].strip().rstrip(',')
            
            return {
                'name': name,
                'folder': folder,
                'body': body,
                'creation_date': creation_date,
                'modification_date': modification_date
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse note content: {str(e)}")
