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

    @staticmethod
    async def get_filtered_folders_structure() -> str:
        """Get filtered folder structure - remove root folders whose IDs appear in subfolders."""
        # First get the complete folder structure
        complete_structure = await FolderStructureOperations.get_folders_structure()
        
        # Parse the structure to extract IDs
        lines = complete_structure.split('\r')
        root_folder_ids = set()
        subfolder_ids = set()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Extract ID from the line
            if '(ID:' in line:
                # Extract the ID part
                start_idx = line.find('(ID:') + 4
                end_idx = line.find(')', start_idx)
                if start_idx > 3 and end_idx > start_idx:
                    folder_id = line[start_idx:end_idx].strip()
                    
                    # Determine if it's a root folder or subfolder based on indentation
                    if line.startswith('Root Folder:'):
                        root_folder_ids.add(folder_id)
                    elif '├──' in line:
                        subfolder_ids.add(folder_id)
        
        # Filter out root folders whose IDs appear in subfolders
        filtered_root_ids = root_folder_ids - subfolder_ids
        
        # Rebuild the structure with only filtered root folders
        filtered_lines = []
        current_root_id = None
        include_current_root = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if include_current_root:
                    filtered_lines.append('')
                current_root_id = None
                include_current_root = False
                continue
                
            # Check if this is a root folder line
            if line.startswith('Root Folder:'):
                # Extract the ID
                if '(ID:' in line:
                    start_idx = line.find('(ID:') + 4
                    end_idx = line.find(')', start_idx)
                    if start_idx > 3 and end_idx > start_idx:
                        current_root_id = line[start_idx:end_idx].strip()
                        include_current_root = current_root_id in filtered_root_ids
                
                if include_current_root:
                    # Remove "Root Folder:" prefix and ID from the line for display
                    clean_line = line.split(' (ID:')[0].replace('Root Folder:', '').strip()
                    filtered_lines.append(clean_line)
            elif include_current_root and line:
                # Include subfolder lines if we're including the current root
                # Remove ID from the line for display and format with tree symbols
                if '(ID:' in line:
                    clean_line = line.split(' (ID:')[0]
                    
                    # Determine the level and format accordingly
                    if '├── Subfolder:' in clean_line:
                        # Level 1: ├──
                        folder_name = clean_line.replace('├── Subfolder:', '').strip()
                        formatted_line = f"├── {folder_name}"
                    elif '├── Sub-subfolder:' in clean_line:
                        # Level 2: │   ├──
                        folder_name = clean_line.replace('├── Sub-subfolder:', '').strip()
                        formatted_line = f"│   ├── {folder_name}"
                    elif '├── Sub-sub-subfolder:' in clean_line:
                        # Level 3: │   │   ├──
                        folder_name = clean_line.replace('├── Sub-sub-subfolder:', '').strip()
                        formatted_line = f"│   │   ├── {folder_name}"
                    elif '├── Sub-sub-sub-subfolder:' in clean_line:
                        # Level 4: │   │   │   └──
                        folder_name = clean_line.replace('├── Sub-sub-sub-subfolder:', '').strip()
                        formatted_line = f"│   │   │   └── {folder_name}"
                    else:
                        formatted_line = clean_line
                    
                    filtered_lines.append(formatted_line)
                else:
                    filtered_lines.append(line)
        
        # Convert back to string
        return '\r'.join(filtered_lines)
