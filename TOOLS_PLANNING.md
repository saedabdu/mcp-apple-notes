# MCP Apple Notes - Tools Planning

## **Current Implementation Status**

### **Core Note Management**
- ✅ `list_notes` - Get all notes with filters/pagination
- ✅ `list_notes_by_folder` - Get notes from specific folder
- ✅ `create_note` - Create note with body, folder, account
- 🔄 `get_note` / `read_note` - Retrieve note by ID/name with content
- 🔄 `update_note` - Modify note body/name
- 🔄 `delete_note` - Remove notes

### **Folder Operations**
- ✅ `create_folder` - Make new folders in accounts
- 🔄 `get_folder` - Retrieve folder info and contents
- 🔄 `delete_folder` - Remove folders (with safety checks)
- ✅ `list_folders` - Get folder hierarchy
- 🔄 `move_note_to_folder` - Organize notes

### **Search & Query**
- 🔄 `search_notes` - Find notes by content/name/date
- 🔄 `filter_notes` - Advanced filtering with conditions
- 🔄 `get_notes_by_date_range` - Time-based queries

### **Attachment Handling**
- 🔄 `add_attachment` - Add files/images to notes
- 🔄 `get_attachments` - List note attachments
- 🔄 `delete_attachment` - Remove attachments

### **Account Management**
- 🔄 `list_accounts` - Get available accounts (iCloud/local)
- 🔄 `get_account_info` - Account details and folder structure

### **Batch Operations**
- 🔄 `bulk_move_notes` - Mass organization
- 🔄 `bulk_delete_notes` - Cleanup operations
- 🔄 `export_notes` - Backup/export functionality

### **Utility Tools**
- 🔄 `get_app_info` - Notes app version/status
- 🔄 `activate_notes` - Bring app to foreground

---

## **Tool Implementation Details**

### **Current Tools (Server Implementation)**

#### `list_notes`
```python
async def list_notes(ctx: Context) -> str:
    """List all Apple Notes with metadata."""
```
- **Status**: ✅ Implemented
- **Returns**: List of all notes with metadata
- **Error Handling**: Graceful error reporting via Context

#### `create_note`
```python
async def create_note(ctx: Context, name: str, body: str, folder_name: str = "Notes") -> str:
    """Create a new Apple Note with specified name, body, and folder."""
```
- **Status**: ✅ Implemented
- **Parameters**: `name` (required), `body` (required), `folder_name` (optional, default: "Notes")
- **Returns**: Created note metadata (name, folder, creation_date, modification_date)
- **Error Handling**: Graceful error reporting via Context
- **AppleScript**: Uses `make new note at targetFolder with properties`

#### `list_notes_by_folder`
```python
async def list_notes_by_folder(ctx: Context, folder_name: str) -> str:
    """List all notes from a specific folder."""
```
- **Status**: ✅ Implemented
- **Parameters**: `folder_name` (required) - Name of the folder to list notes from
- **Returns**: List of notes with metadata (name, folder, creation_date, modification_date)
- **Error Handling**: Graceful error reporting via Context
- **AppleScript**: Uses `set targetFolder to folder "{folder_name}"` and iterates through notes
- **No IDs Required**: Works with folder names only, no need for folder IDs

#### `create_folder`
```python
async def create_folder(ctx: Context, folder_name: str) -> str:
    """Create a new Apple Notes folder."""
```
- **Status**: ✅ Implemented
- **Parameters**: `folder_name` (required) - Name of the folder to create
- **Returns**: Created folder metadata (name, status)
- **Error Handling**: Graceful error reporting via Context, handles duplicate folder names
- **AppleScript**: Uses `make new folder with properties {name:"{folder_name}"}`
- **Integration**: Can be used with create_note to organize notes in new folders

---

## **Planned Tools (To Be Implemented)**

### **Folder Operations**



#### `get_folder`
- **Purpose**: Retrieve folder information and contents
- **Parameters**: `folder_id` or `folder_name`
- **Returns**: Folder metadata and contained notes
- **AppleScript**: `tell application "Notes" to get folder`

#### `delete_folder`
- **Purpose**: Remove folders with safety checks
- **Parameters**: `folder_id`, `force` (boolean, optional)
- **Returns**: Success/failure message
- **Safety**: Check if folder is empty or confirm deletion

#### `list_folders`
- **Purpose**: Get complete folder hierarchy
- **Parameters**: `account_name` (optional)
- **Returns**: Folder tree structure
- **AppleScript**: `tell application "Notes" to get folders`

#### `move_note_to_folder`
- **Purpose**: Organize notes into folders
- **Parameters**: `note_id`, `folder_id`
- **Returns**: Success confirmation
- **AppleScript**: `tell application "Notes" to move note to folder`

### **Advanced Search & Query**

#### `filter_notes`
- **Purpose**: Advanced filtering with multiple conditions
- **Parameters**: `filters` (dict with date_range, folder, account, etc.)
- **Returns**: Filtered notes list
- **Features**: Date ranges, folder filters, account filters

#### `get_notes_by_date_range`
- **Purpose**: Time-based note queries
- **Parameters**: `start_date`, `end_date`, `created` or `modified`
- **Returns**: Notes within date range
- **AppleScript**: Date comparison logic

### **Attachment Handling**

#### `add_attachment`
- **Purpose**: Add files/images to notes
- **Parameters**: `note_id`, `file_path`, `attachment_name` (optional)
- **Returns**: Attachment metadata
- **AppleScript**: `tell application "Notes" to make new attachment`

#### `get_attachments`
- **Purpose**: List note attachments
- **Parameters**: `note_id`
- **Returns**: List of attachments with metadata
- **AppleScript**: `tell application "Notes" to get attachments`

#### `delete_attachment`
- **Purpose**: Remove attachments from notes
- **Parameters**: `note_id`, `attachment_id`
- **Returns**: Success confirmation
- **AppleScript**: `tell application "Notes" to delete attachment`

### **Account Management**

#### `list_accounts`
- **Purpose**: Get available Apple Notes accounts
- **Parameters**: None
- **Returns**: List of accounts (iCloud, local, etc.)
- **AppleScript**: `tell application "Notes" to get accounts`

#### `get_account_info`
- **Purpose**: Account details and folder structure
- **Parameters**: `account_name`
- **Returns**: Account metadata and folder hierarchy
- **AppleScript**: `tell application "Notes" to get account`

### **Batch Operations**

#### `bulk_move_notes`
- **Purpose**: Mass organization of notes
- **Parameters**: `note_ids` (list), `folder_id`
- **Returns**: Operation summary
- **Features**: Progress reporting, error handling

#### `bulk_delete_notes`
- **Purpose**: Cleanup operations
- **Parameters**: `note_ids` (list), `confirm` (boolean)
- **Returns**: Deletion summary
- **Safety**: Confirmation required for large batches

#### `export_notes`
- **Purpose**: Backup/export functionality
- **Parameters**: `note_ids` (list), `format` (txt, html, etc.), `output_path`
- **Returns**: Export file path
- **Features**: Multiple export formats

### **Utility Tools**

#### `get_app_info`
- **Purpose**: Notes app version/status
- **Parameters**: None
- **Returns**: App version, status, capabilities
- **AppleScript**: `tell application "Notes" to get version`

#### `activate_notes`
- **Purpose**: Bring Notes app to foreground
- **Parameters**: None
- **Returns**: Success confirmation
- **AppleScript**: `tell application "Notes" to activate`

---

## **Implementation Priority**

### **Phase 1: Essential Folder Operations**
1. `list_folders` - Foundation for organization
2. `create_folder` - Basic folder creation
3. `move_note_to_folder` - Core organization feature

### **Phase 2: Advanced Search**
1. `filter_notes` - Enhanced search capabilities
2. `get_notes_by_date_range` - Time-based queries

### **Phase 3: Account & Attachment Management**
1. `list_accounts` - Account awareness
2. `add_attachment` - File handling
3. `get_attachments` - Attachment listing

### **Phase 4: Batch Operations**
1. `bulk_move_notes` - Mass organization
2. `export_notes` - Backup functionality

### **Phase 5: Advanced Features**
1. `bulk_delete_notes` - Cleanup tools
2. `delete_folder` - Folder management
3. `get_app_info` - System information

---

## **Error Handling Strategy**

### **Standard Error Patterns**
- **Context Logging**: Use `ctx.info()` and `ctx.error()` for all operations
- **Graceful Degradation**: Return meaningful error messages
- **AppleScript Errors**: Catch and translate AppleScript errors to user-friendly messages
- **Validation**: Validate parameters before AppleScript execution

### **Common Error Scenarios**
- **Note Not Found**: Return clear "Note not found" message
- **Permission Denied**: Handle AppleScript permission issues
- **Network Issues**: Handle iCloud connectivity problems
- **Invalid Parameters**: Validate input before processing

---

## **Testing Strategy**

### **Unit Tests**
- Test each tool function independently
- Mock AppleScript responses
- Test error conditions

### **Integration Tests**
- Test with actual Apple Notes app
- Verify AppleScript execution
- Test error handling scenarios

### **End-to-End Tests**
- Test complete workflows
- Verify MCP protocol compliance
- Test with real client applications

---

## **Documentation Requirements**

### **Tool Documentation**
- Clear parameter descriptions
- Return value specifications
- Example usage
- Error scenarios

### **AppleScript Reference**
- Document all AppleScript commands used
- Error code meanings
- Best practices for AppleScript execution

### **User Guide**
- Installation instructions
- Configuration guide
- Common use cases
- Troubleshooting guide
