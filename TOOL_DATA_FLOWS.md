# Apple Notes MCP - Tool Data Flows

## Overview
All tools follow a 3-layer architecture: **Server** → **Tools** → **Operations** → **AppleScript**

---

## 📝 Note Management Tools

### 1. `create_note`
**Input**: `name` + `body` + `folder_path`
**Output**: `note_id`, `name`, `status`
**Flow**: Server → Tools → CreateNoteOperations → AppleScript
**Steps**: Validate HTML → Combine content → Create note in folder → Return note data

### 2. `read_note`
**Input**: `note_id` + `note_name`
**Output**: `name`, `note_id`, `body`, `creation_date`, `modification_date`, `status`
**Flow**: Server → Tools → ReadNoteOperations → AppleScript
**Steps**: Validate inputs → Build Core Data ID → Verify name match → Read note → Parse content

### 3. `update_note`
**Input**: `note_id` + `note_name` + `new_name` + `new_body`
**Output**: `name`, `note_id`, `status`
**Flow**: Server → Tools → UpdateNoteOperations → AppleScript
**Steps**: Validate inputs → Combine content → Verify name match → Update note → Parse result

### 4. `delete_note`
**Input**: `note_id` + `note_name`
**Output**: `name`, `note_id`, `status`
**Flow**: Server → Tools → DeleteNoteOperations → AppleScript
**Steps**: Validate inputs → Build Core Data ID → Verify name match → Delete note → Parse result

### 5. `move_note`
**Input**: `note_id` + `note_name` + `target_folder_path`
**Output**: `name`, `note_id`, `source_folder`, `target_folder`, `status`, `message`
**Flow**: Server → Tools → MoveNoteOperations → AppleScript
**Steps**: Validate inputs → Build Core Data ID → Verify name match → Move note → Parse result

### 6. `list_notes`
**Input**: `folder_path` (optional)
**Output**: `notes_list` (name, note_id), `count`
**Flow**: Server → Tools → ListNotesOperations → AppleScript
**Steps**: Validate path → Get notes in folder → Parse note list → Format response

### 7. `list_all_notes`
**Input**: None
**Output**: `notes_list` (name, note_id, folder), `count`
**Flow**: Server → Tools → ListNotesOperations → AppleScript
**Steps**: Get all notes → Parse note list → Format response with folder info

---

## 📁 Folder Management Tools

### 8. `create_folder`
**Input**: `folder_name` + `folder_path`
**Output**: `name`, `id`, `status`
**Flow**: Server → Tools → CreateFolderOperations → AppleScript
**Steps**: Validate name → Check path exists → Create folder → Return folder data

### 9. `read_folder`
**Input**: `folder_id` + `folder_name`
**Output**: `name`, `folder_id`, `child_folders` (name, id), `notes` (name, note_id), `counts`
**Flow**: Server → Tools → ReadFolderOperations → AppleScript
**Steps**: Validate inputs → Build Core Data ID → Verify name match → Get child folders & notes → Parse result

### 10. `rename_folder`
**Input**: `folder_id` + `current_name` + `new_name`
**Output**: `folder_id`, `current_name`, `new_name`, `folder_path`, `status`
**Flow**: Server → Tools → RenameFolderOperations → AppleScript
**Steps**: Validate inputs → Build Core Data ID → Verify name match → Rename folder → Parse result

### 11. `delete_folder`
**Input**: `folder_id` + `folder_name`
**Output**: `name`, `folder_id`, `status`
**Flow**: Server → Tools → DeleteFolderOperations → AppleScript
**Steps**: Validate inputs → Build Core Data ID → Verify name match → Delete folder → Parse result

### 12. `move_folder`
**Input**: `folder_id` + `folder_name` + `target_path`
**Output**: `name`, `folder_id`, `source_path`, `target_path`, `status`
**Flow**: Server → Tools → MoveFolderOperations → AppleScript
**Steps**: Validate inputs → Build Core Data ID → Verify name match → Move folder → Parse result

### 13. `list_folder_contents`
**Input**: `folder_path` (optional)
**Output**: `notes` (name, note_id), `folders` (name, id), `counts`
**Flow**: Server → Tools → FolderContentsOperations → AppleScript
**Steps**: Validate path → Get folder contents → Parse notes & folders → Format response

### 14. `list_folder_with_structure`
**Input**: None
**Output**: `folder_tree` (hierarchical structure with IDs)
**Flow**: Server → Tools → FolderStructureOperations → AppleScript
**Steps**: Get all folders → Build hierarchy tree → Format tree structure

---

## 🔍 Search and Structure Tools

### 15. `search_notes`
**Input**: `keywords` (comma-separated)
**Output**: `matching_notes` (name, note_id, folder, keywords), `count`
**Flow**: Server → Tools → SearchNotesOperations → AppleScript
**Steps**: Parse keywords → Search all notes → Match keywords → Format results

### 16. `list_notes_with_structure`
**Input**: None
**Output**: `complete_tree` (folders + notes in hierarchical structure)
**Flow**: Server → Tools → NotesStructureOperations → AppleScript
**Steps**: Get all folders & notes → Build complete hierarchy → Format tree with notes

---

## 🔧 Common Processing Patterns

### Simplified Pattern (8 tools)
- **Input**: ID + name for verification
- **Security**: AppleScript verifies ID and name match
- **Tools**: `read_note`, `update_note`, `delete_note`, `move_note`, `read_folder`, `rename_folder`, `delete_folder`, `move_folder`

### Original Pattern (8 tools)
- **Input**: Path-based or no parameters
- **Security**: Path validation and existence checks
- **Tools**: `create_note`, `create_folder`, `list_notes`, `list_all_notes`, `list_folder_contents`, `list_folder_with_structure`, `list_notes_with_structure`, `search_notes`

---

## 🛡️ Security Features

### Input Validation
- Empty/whitespace checks
- HTML content validation
- Path format validation
- Name format validation

### AppleScript Verification
- ID and name matching
- Path existence checks
- Duplicate detection
- Error handling

### Error Handling
- Validation errors (ValueError)
- Runtime errors (RuntimeError)
- Unexpected errors (Exception)
- Clear error messages with context

---

## 📊 Data Flow Summary

| Category | Tools | Pattern | Primary Input | Security Method |
|----------|-------|---------|---------------|-----------------|
| Note Management | 7 | Mixed | ID+Name / Path | AppleScript / Path validation |
| Folder Management | 7 | Mixed | ID+Name / Path | AppleScript / Path validation |
| Search/Structure | 2 | Original | Keywords / None | Path validation |

**Total: 16 tools** - All following consistent 3-layer architecture with appropriate security measures.


// List of all tools:
// - read_note (tested)
// - update_note (tested)
// - delete_note (tested)
// - move_note (tested)
// - read_folder (tested)
// - rename_folder (tested)
// - delete_folder (tested)
// - move_folder (tested)
// - create_note (tested)
// - create_folder (tested)
// 🟡 list_notes   // remove
// 🔴 list_all_notes (tested)
// 🟡 list_folder_contents   // remove
// - list_folder_with_structure
// - list_notes_with_structure
// - search_notes (tested)