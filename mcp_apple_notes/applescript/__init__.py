from .base_operations import BaseAppleScriptOperations
from .list_notes import ListNotesOperations
from .create_note import CreateNoteOperations
from .list_folders import ListFoldersOperations
from .list_notes_by_folder import ListNotesByFolderOperations
from .create_folder import CreateFolderOperations
from .read_note import ReadNoteOperations
from .notes_utilities import AppleScriptNotesUtilities

# Legacy compatibility - keep the old class name
from .notes_operations import AppleScriptNotes

__all__ = [
    'BaseAppleScriptOperations',
    'ListNotesOperations', 
    'CreateNoteOperations',
    'ListFoldersOperations',
    'ListNotesByFolderOperations',
    'CreateFolderOperations',
    'ReadNoteOperations',
    'AppleScriptNotesUtilities',
    'AppleScriptNotes'  # Legacy compatibility
]
