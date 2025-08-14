from typing import Dict, List
from .base_operations import BaseAppleScriptOperations

class FolderContentsOperations(BaseAppleScriptOperations):
    """Operations for listing both notes and direct child folders in Apple Notes."""
    
    @staticmethod
    async def list_folder_contents(folder_path: str = "Notes") -> Dict[str, any]:
        """List both notes and direct child folders in the specified folder path.
        
        This method provides a comprehensive view of folder contents by listing
        both notes (with names and IDs) and direct child folders (with names).
        
        Args:
            folder_path: Folder path to list contents from (default: "Notes")
            
        Returns:
            Dictionary containing notes list and folders list
            
        Raises:
            ValueError: If folder path is invalid
            RuntimeError: If folder path doesn't exist
        """
        # Validate inputs
        if not folder_path or not folder_path.strip():
            folder_path = "Notes"
        folder_path = folder_path.strip()
        
        # Check if folder path exists
        from .validation_utils import ValidationUtils
        if not await ValidationUtils.check_path_exists(folder_path):
            raise RuntimeError(f"Folder path '{folder_path}' does not exist")
        
        # Get notes using existing functionality
        from .list_notes import ListNotesOperations
        notes_result = await ListNotesOperations.list_notes(folder_path)
        
        # Get folders using existing functionality
        from .folder_structure import FolderStructureOperations
        folders_result = await FolderStructureOperations.get_filtered_folders_structure()
        
        # Extract direct child folders for the specified path
        direct_folders = FolderContentsOperations._extract_direct_children(folders_result, folder_path)
        
        return {
            'folder_path': folder_path,
            'notes_count': len(notes_result),
            'folders_count': len(direct_folders),
            'notes': notes_result,
            'folders': direct_folders,
            'status': 'success'
        }
    
    @staticmethod
    def _extract_direct_children(folder_structure: str, target_path: str) -> List[Dict[str, str]]:
        """Extract direct child folders for the specified path from folder structure."""
        try:
            # Parse the folder structure to find direct children
            lines = folder_structure.split('\r')
            direct_children = []
            
            if target_path == "Notes":
                # For root level, look for root folders (lines that don't start with ├── or │)
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('├──') and not line.startswith('│') and not line.startswith('└──'):
                        # This is a root folder
                        direct_children.append({
                            'name': line,
                            'type': 'folder'
                        })
            else:
                # For nested folders, find the target folder and its direct children
                target_components = target_path.split('/')
                target_folder = target_components[-1]  # Last component is the target folder
                
                # Find the target folder in the structure
                target_found = False
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if this is the target folder
                    if target_folder in line and not line.startswith('├──') and not line.startswith('│'):
                        target_found = True
                        continue
                    
                    # If we found the target, look for its direct children
                    if target_found:
                        if line.startswith('├──'):
                            # Direct child folder
                            folder_name = line.replace('├──', '').strip()
                            direct_children.append({
                                'name': folder_name,
                                'type': 'folder'
                            })
                        elif line.startswith('│   ├──'):
                            # This is a deeper level, not a direct child
                            break
                        elif not line.startswith('│') and not line.startswith('└──'):
                            # We've moved past the target folder's children
                            break
            
            return direct_children
        except Exception as e:
            # Fallback: return empty list if parsing fails
            return []
