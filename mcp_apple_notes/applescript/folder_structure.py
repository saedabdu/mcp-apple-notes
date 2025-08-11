from .base_operations import BaseAppleScriptOperations

class FolderStructureOperations(BaseAppleScriptOperations):
    """Operations for getting complete Apple Notes folder structure."""
    
    @staticmethod
    async def get_folders_structure() -> str:
        """Get complete folder structure - return raw AppleScript data."""
        script = '''
tell application "Notes"
	try
		set folderList to {}
		
		-- Get all root folders and their subfolders
		repeat with rootFolder in folders
			set rootName to name of rootFolder
			set rootId to id of rootFolder as string
			set folderList to folderList & {"Root Folder: " & rootName & " (ID: " & rootId & ")"}
			
			-- Get level 2 subfolders
			repeat with subFolder in folders of rootFolder
				set subName to name of subFolder
				set subId to id of subFolder as string
				set folderList to folderList & {"  ├── Subfolder: " & subName & " (ID: " & subId & ")"}
				
				-- Get level 3 subfolders
				repeat with subSubFolder in folders of subFolder
					set subSubName to name of subSubFolder
					set subSubId to id of subSubFolder as string
					set folderList to folderList & {"    ├── Sub-subfolder: " & subSubName & " (ID: " & subSubId & ")"}
					
					-- Get level 4 subfolders
					repeat with subSubSubFolder in folders of subSubFolder
						set subSubSubName to name of subSubSubFolder
						set subSubSubId to id of subSubSubFolder as string
						set folderList to folderList & {"      ├── Sub-sub-subfolder: " & subSubSubName & " (ID: " & subSubSubId & ")"}
						
						-- Get level 5 subfolders
						repeat with subSubSubSubFolder in folders of subSubSubFolder
							set subSubSubName to name of subSubSubSubFolder
							set subSubSubSubId to id of subSubSubSubFolder as string
							set folderList to folderList & {"        ├── Sub-sub-sub-subfolder: " & subSubSubName & " (ID: " & subSubSubSubId & ")"}
						end repeat
					end repeat
				end repeat
			end repeat
			
			set folderList to folderList & {""}
		end repeat
		
		-- Convert to string
		set AppleScript's text item delimiters to return
		set folderStructure to folderList as string
		set AppleScript's text item delimiters to ""
		
		return folderStructure
		
	on error errMsg
		return "error:" & errMsg
	end try
end tell
        '''
        
        result = await FolderStructureOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get folders structure: {result[6:]}")
        
        return result
