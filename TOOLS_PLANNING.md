# MCP Apple Notes - Tools Planning

## **📋 Complete Tools Summary**

### **✅ Currently Available Tools (11 total)**

#### **Core Note Management (5 tools)**
1. ✅ `list_notes` - List all notes with metadata
   - **Description**: Retrieves all Apple Notes with their names, folders, creation dates, and modification dates
2. ✅ `create_note` - Create note in folder (backward compatibility)
   - **Description**: Creates a new note with specified name and content in a single folder
3. ✅ `create_note_in_path` - Create note in nested folder path
   - **Description**: Creates a new note in a nested folder structure, automatically creating parent folders if needed
4. ✅ `read_note_by_name` - Read notes by name in folder
   - **Description**: Retrieves all notes with a specific name from a single folder, including full content
5. ✅ `read_note_by_name_in_path` - Read notes by name in nested folder path
   - **Description**: Retrieves all notes with a specific name from a nested folder path, including full content

#### **Folder Operations (6 tools)**
6. ✅ `list_folder_structure` - List complete folder structure with hierarchy
   - **Description**: Returns the complete folder structure in hierarchical tree format
7. ✅ `create_folder` - Create folder with optional path
   - **Description**: Creates a folder with specified name, optionally within a nested path. If no path given, creates at root level.
8. ✅ `list_notes_by_folder` - List notes from folder (backward compatibility)
   - **Description**: Lists all notes within a single folder with their metadata
9. ✅ `list_notes_by_folder_path` - List notes from nested folder path
   - **Description**: Lists all notes within a nested folder path with their metadata
10. ✅ `get_folder_details` - Get comprehensive folder details with hierarchy
    - **Description**: Retrieves complete details about a folder including all subfolders and notes in hierarchical structure
11. ✅ `get_folder_hierarchy_details` - Get folder details with robust hierarchy
    - **Description**: Provides folder details with a more robust hierarchical structure and metadata

### **🔄 Planned Tools (14 total)**

#### **Core Note Management (2 tools)**
- 🔄 `update_note` - Modify note content and metadata
  - **Description**: Updates existing note content, name, or both while preserving creation date
- 🔄 `delete_note` - Remove notes with confirmation
  - **Description**: Permanently removes notes from folders with optional confirmation prompts

#### **Folder Operations (1 tool)**
- 🔄 `delete_folder` - Remove folders with safety checks
  - **Description**: Deletes folders and their contents with safety checks for empty folders

#### **Note Organization (1 tool)**
- 🔄 `move_note_to_folder` - Organize notes between folders
  - **Description**: Moves notes from one folder to another, supporting both flat and nested paths

#### **Search & Query (3 tools)**
- 🔄 `search_notes` - Find notes by content/name/date
  - **Description**: Searches across all notes for specific text content, names, or date ranges
- 🔄 `filter_notes` - Advanced filtering with conditions
  - **Description**: Applies complex filters to notes based on multiple criteria (date, folder, content, etc.)
- 🔄 `get_notes_by_date_range` - Time-based queries
  - **Description**: Retrieves notes created or modified within a specific date range

#### **Account & Attachment Management (5 tools)**
- 🔄 `list_accounts` - Get available accounts (iCloud/local)
  - **Description**: Lists all available Apple Notes accounts (iCloud, local, etc.)
- 🔄 `get_account_info` - Account details and folder structure
  - **Description**: Retrieves detailed information about a specific account and its folder hierarchy
- 🔄 `add_attachment` - Add files/images to notes
  - **Description**: Attaches files, images, or other media to existing notes
- 🔄 `get_attachments` - List note attachments
  - **Description**: Lists all attachments within a specific note with metadata
- 🔄 `delete_attachment` - Remove attachments
  - **Description**: Removes specific attachments from notes while preserving the note content

### **📊 Implementation Progress**
- **✅ Completed**: 11 tools (44%)
- **🔄 Planned**: 14 tools (56%)
- **📈 Total**: 25 tools

---

## **Current Implementation Status**

### **Core Note Management**
- ✅ `list_notes` - Get all notes with metadata
- ✅ `create_note` - Create note with body and folder
- ✅ `create_note_in_path` - Create note in nested folder path
- ✅ `read_note_by_name` - Read notes by name in folder
- ✅ `read_note_by_name_in_path` - Read notes by name in nested folder path
- 🔄 `update_note` - Modify note body/name
- 🔄 `delete_note` - Remove notes

### **Folder Operations**
- ✅ `list_folder_structure` - Get complete folder structure with hierarchy
- ✅ `create_folder` - Create folder with optional path
- ✅ `list_notes_by_folder` - List notes from specific folder
- ✅ `list_notes_by_folder_path` - List notes from nested folder path
- ✅ `get_folder_details` - Get comprehensive folder details with hierarchy
- ✅ `get_folder_hierarchy_details` - Get folder details with robust hierarchy
- 🔄 `delete_folder` - Remove folders (with safety checks)
- 🔄 `move_note_to_folder` - Organize notes between folders

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

#### **Core Note Management**

##### `list_notes`
```python
async def list_notes(ctx: Context) -> str:
    """List all Apple Notes with metadata."""
```
- **Status**: ✅ Implemented
- **Returns**: List of all notes with metadata
- **Error Handling**: Graceful error reporting via Context

##### `create_note`
```python
async def create_note(ctx: Context, name: str, body: str, folder_name: str = "Notes") -> str:
    """Create a new Apple Note with specified name, body, and folder."""
```
- **Status**: ✅ Implemented
- **Parameters**: `name` (required), `body` (required), `folder_name` (optional, default: "Notes")
- **Returns**: Created note metadata (name, folder, creation_date, modification_date)
- **Error Handling**: Graceful error reporting via Context
- **AppleScript**: Uses `make new note at targetFolder with properties`

##### `create_note_in_path`
```python
async def create_note_in_path(ctx: Context, name: str, body: str, folder_path: str) -> str:
    """Create a new note in a nested folder path."""
```
- **Status**: ✅ Implemented
- **Parameters**: `name` (required), `body` (required), `folder_path` (required)
- **Returns**: Created note metadata
- **Features**: Creates nested folder structure if needed
- **Example**: `"Work/Projects/2024/Q1"`

##### `read_note_by_name`
```python
async def read_note_by_name(ctx: Context, note_name: str, folder_name: str) -> str:
    """Read all notes with the given name in the specified folder."""
```
- **Status**: ✅ Implemented
- **Parameters**: `note_name` (required), `folder_name` (required)
- **Returns**: All matching notes with full content
- **Features**: Returns multiple matches if same name exists
- **Error Handling**: Clear messaging for no matches

##### `read_note_by_name_in_path`
```python
async def read_note_by_name_in_path(ctx: Context, note_name: str, folder_path: str) -> str:
    """Read all notes with the given name in the specified folder path."""
```
- **Status**: ✅ Implemented
- **Parameters**: `note_name` (required), `folder_path` (required)
- **Returns**: All matching notes with full content
- **Features**: Works with nested folder paths

#### **Folder Operations**

##### `list_folder_structure`
```python
async def list_folder_structure(ctx: Context) -> str:
    """List the complete folder structure with hierarchical tree format."""
```
- **Status**: ✅ Implemented
- **Returns**: Complete folder structure in hierarchical tree format
- **Features**: Shows parent-child relationships in tree structure

##### `create_folder`
```python
async def create_folder(ctx: Context, folder_name: str, folder_path: str = "") -> str:
    """Create a folder in Apple Notes."""
```
- **Status**: ✅ Implemented
- **Parameters**: 
  - `folder_name` (required) - Name of the folder to create
  - `folder_path` (optional) - Path where to create the folder. If empty, creates at root level.
- **Returns**: Created folder metadata
- **Features**: Creates folder at root level or within specified path
- **Error Handling**: Validates paths and provides helpful error messages for invalid inputs
- **Examples**: 
  - `create_folder("Work")` - Creates "Work" at root level
  - `create_folder("Q1", "Work/Projects/2024")` - Creates "Q1" inside "Work/Projects/2024"

##### `list_notes_by_folder`
```python
async def list_notes_by_folder(ctx: Context, folder_name: str) -> str:
    """List all notes from a specific folder."""
```
- **Status**: ✅ Implemented
- **Parameters**: `folder_name` (required)
- **Returns**: List of notes with metadata
- **Backward Compatibility**: Maintains original behavior

##### `list_notes_by_folder_path`
```python
async def list_notes_by_folder_path(ctx: Context, folder_path: str) -> str:
    """List all notes from a specific folder path."""
```
- **Status**: ✅ Implemented
- **Parameters**: `folder_path` (required)
- **Returns**: List of notes with metadata
- **Features**: Works with nested folder paths



##### `get_folder_details`
```python
async def get_folder_details(ctx: Context, folder_name: str) -> str:
    """Get comprehensive details about a folder including all subfolders and notes in hierarchy."""
```
- **Status**: ✅ Implemented
- **Parameters**: `folder_name` (required)
- **Returns**: Complete folder details with hierarchical structure
- **Features**: Shows all notes and subfolders in hierarchy, includes metadata

##### `get_folder_hierarchy_details`
```python
async def get_folder_hierarchy_details(ctx: Context, folder_name: str) -> str:
    """Get folder details with a more robust hierarchical structure."""
```
- **Status**: ✅ Implemented
- **Parameters**: `folder_name` (required)
- **Returns**: Folder details with robust hierarchical structure
- **Features**: Enhanced hierarchy with better metadata and structure

---

## **Planned Tools (To Be Implemented)**

### **Core Note Management**

#### `update_note`
- **Purpose**: Modify existing note content and metadata
- **Parameters**: `note_name`, `folder_path`, `new_name` (optional), `new_body` (optional)
- **Returns**: Updated note metadata
- **AppleScript**: `tell application "Notes" to set properties of note`

#### `delete_note`
- **Purpose**: Remove notes from folders
- **Parameters**: `note_name`, `folder_path`, `confirm` (boolean, optional)
- **Returns**: Success/failure message
- **Safety**: Confirmation required for deletion

### **Folder Operations**

#### `delete_folder`
- **Purpose**: Remove folders with safety checks
- **Parameters**: `folder_path`, `force` (boolean, optional)
- **Returns**: Success/failure message
- **Safety**: Check if folder is empty or confirm deletion
- **AppleScript**: `tell application "Notes" to delete folder`

#### `move_note_to_folder`
- **Purpose**: Organize notes between folders
- **Parameters**: `note_name`, `source_folder_path`, `target_folder_path`
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

### **Phase 1: Complete CRUD Operations** ✅ **COMPLETED**
1. ✅ `list_notes` - List all notes
2. ✅ `create_note` - Create notes in folders
3. ✅ `create_note_in_path` - Create notes in nested folders
4. ✅ `read_note_by_name` - Read notes by name
5. ✅ `read_note_by_name_in_path` - Read notes from nested paths
6. ✅ `list_folder_structure` - List complete folder structure
7. ✅ `create_folder` - Create folder with optional path
8. ✅ `list_notes_by_folder` - List notes from folders
9. ✅ `list_notes_by_folder_path` - List notes from nested folders
10. ✅ `get_folder_details` - Get comprehensive folder details

### **Phase 2: Update & Delete Operations** 🔄 **IN PROGRESS**
1. `update_note` - Modify note content and metadata
2. `delete_note` - Remove notes with confirmation
3. `delete_folder` - Remove folders with safety checks
4. `move_note_to_folder` - Organize notes between folders

### **Phase 3: Advanced Search & Query**
1. `search_notes` - Find notes by content/name/date
2. `filter_notes` - Advanced filtering with conditions
3. `get_notes_by_date_range` - Time-based queries

### **Phase 4: Account & Attachment Management**
1. `list_accounts` - Get available accounts (iCloud/local)
2. `get_account_info` - Account details and folder structure
3. `add_attachment` - Add files/images to notes
4. `get_attachments` - List note attachments
5. `delete_attachment` - Remove attachments

### **Phase 5: Batch Operations**
1. `bulk_move_notes` - Mass organization
2. `bulk_delete_notes` - Cleanup operations
3. `export_notes` - Backup/export functionality

### **Phase 6: Utility Tools**
1. `get_app_info` - Notes app version/status
2. `activate_notes` - Bring app to foreground

---

## **🚀 Usage Examples**

### **Basic Note Operations**
```python
# List all notes
await list_notes()

# Create note in default folder
await create_note("Meeting Notes", "Team meeting content")

# Create note in specific folder
await create_note("Project Ideas", "New project concepts", "Work")

# Read note by name
await read_note_by_name("Meeting Notes", "Work")
```

### **Nested Folder Operations**
```python
# Create folder structure step by step
await create_folder("Work")
await create_folder("Projects", "Work")
await create_folder("2024", "Work/Projects")
await create_folder("Q1", "Work/Projects/2024")

# Create note in nested folder
await create_note_in_path("Sprint Planning", "Sprint planning content", "Work/Projects/2024/Q1")

# List notes from nested folder
await list_notes_by_folder_path("Work/Projects/2024/Q1")

# Read note from nested folder
await read_note_by_name_in_path("Sprint Planning", "Work/Projects/2024/Q1")
```

### **Folder Management**
```python
# List complete folder structure with hierarchy
await list_folder_structure()

# Create folder at root level
await create_folder("Work")

# Create folder within existing path
await create_folder("Q1", "Work/Projects/2024")

# List notes from specific folder
await list_notes_by_folder("Work")

# List notes from nested folder path
await list_notes_by_folder_path("Work/Projects/2024/Q1")



# Get comprehensive folder details with hierarchy
await get_folder_details("Work")

# Get folder details with robust hierarchy
await get_folder_hierarchy_details("Work")
```

### **Path Notation**
- **Separator**: `/` (forward slash)
- **Examples**:
  - `"Work"` - Root folder
  - `"Work/Projects"` - Nested folder
  - `"Work/Projects/2024/Q1"` - Deeply nested folder
- **Folder Creation**: Use `create_folder(folder_name, folder_path)` where:
  - `folder_name` is the name of the folder to create
  - `folder_path` is the optional path where to create it (empty for root level)

### **Error Handling for Invalid Paths**
When users provide incorrect folder paths, the system provides helpful error messages:

#### **Common Path Errors:**
1. **Non-existent Path**: `create_folder("Q1", "Work/Projects/2024")` when "Work/Projects/2024" doesn't exist
   - **Error**: "Invalid folder path 'Work/Projects/2024'. The specified path does not exist."
   - **Solution**: Create parent folders first or use existing path

2. **Invalid Characters**: `create_folder("Test", "Work/Projects<2024")`
   - **Error**: "Folder path contains invalid character '<'"
   - **Solution**: Remove invalid characters

3. **Invalid Format**: `create_folder("Test", "Work//Projects")`
   - **Error**: "Folder path contains invalid double slashes"
   - **Solution**: Use single slashes between folder names

4. **Empty Folder Name**: `create_folder("", "Work")`
   - **Error**: "Folder name cannot be empty"
   - **Solution**: Provide a valid folder name

#### **Helpful Error Messages Include:**
- Clear description of the problem
- Suggestions for correction
- Examples of valid usage
- Guidance on creating parent folders

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
- **Invalid Folder Paths**: Provide helpful error messages with suggestions for correction

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
