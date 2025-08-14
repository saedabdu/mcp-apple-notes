# MCP Apple Notes Tools - Flow Structures

This document provides detailed flow structures for all MCP Apple Notes tools, showing the step-by-step process of how each tool works internally.

## 📁 create_folder Tool Flow Structure

```
🔄 create_folder Tool Flow
├── 1. Tool Call
│   ├── User provides folder_name
│   └── User provides folder_path (optional)
│
├── 2. Input Validation
│   ├── Validate and clean folder name
│   ├── Validate and clean folder path
│   ├── Check for invalid characters
│   └── Validate nesting depth (max 5 levels)
│
├── 3. Path Processing
│   ├── If path empty → root level creation
│   ├── If path provided → validate path exists
│   ├── Check parent path exists before creation
│   └── Validate nesting depth (max 5 levels)
│
├── 4. Duplicate Check
│   ├── Check if folder exists at target location
│   └── Prevent creation if duplicate found
│
├── 5. AppleScript Execution
│   ├── Step 5a: Root Level Creation
│   │   ├── Use direct folder creation for root level
│   │   ├── Escape folder name for AppleScript
│   │   └── Return creation details
│   │
│   └── Step 5b: Nested Path Creation
│       ├── Parse path components
│       ├── Navigate through folder hierarchy
│       ├── Create folder in parent location
│       └── Return creation details with path info
│
├── 6. Response Processing
│   ├── Capture AppleScript output
│   ├── Check success/error status
│   └── Format response with details
│
├── 7. Error Handling
│   ├── If any step fails → return error message
│   ├── Provide helpful suggestions
│   └── Handle AppleScript errors
│
└── 8. Success Response
    ├── Return folder creation details
    ├── Show created path and components
    └── Confirm successful creation
```

### **🔄 Flow Summary:**
```
Input → Validate → Process Path → Check Duplicates → Execute (Root/Nested) → Process Response → Return Result
```

### **⚡ Key Decision Points:**
- **Path empty?** → Create at root level
- **Path exists?** → Continue with nested creation
- **Parent path exists?** → Continue with creation
- **Duplicate found?** → Return error
- **Depth > 5?** → Return error
- **AppleScript success?** → Return success details

### **🎯 Tool Capabilities:**
- ✅ Creates folders at root level and nested paths
- ✅ Handles complex hierarchies up to 5 levels deep
- ✅ Supports Unicode and special characters
- ✅ Validates paths and ensures parent folders exist
- ✅ Prevents duplicate folder names
- ✅ Enforces character and length limits
- ✅ Provides helpful error messages

---

## 📝 list_folder_with_structure Tool Flow Structure

```
🔄 list_folder_with_structure Tool Flow
├── 1. Tool Call
│   └── User calls with dummy parameter
│
├── 2. Server Layer Processing
│   ├── Create context object for error handling
│   ├── Call tools layer method
│   └── Wrap result in error handling try-catch
│
├── 3. Tools Layer Processing
│   └── Call AppleScript operations layer
│
├── 4. AppleScript Operations Layer
│   ├── Step 4a: Raw Data Collection
│   │   ├── Execute AppleScript via subprocess
│   │   ├── Traverse 5 levels deep
│   │   ├── Collect folder names and IDs
│   │   └── Return raw data with structure
│   │
│   └── Step 4b: Data Filtering & Formatting
│       ├── Parse raw AppleScript output
│       ├── Extract folder IDs from each line
│       ├── Identify root folders vs subfolders
│       ├── Filter out duplicate root folders
│       ├── Rebuild clean tree structure
│       ├── Remove ID information and prefixes
│       └── Format with proper tree symbols
│
├── 5. Base Operations Layer
│   ├── Create subprocess to run osascript
│   ├── Capture stdout and stderr
│   ├── Handle process return codes
│   └── Return decoded output or raise error
│
├── 6. AppleScript Content
│   ├── Complex nested loop structure
│   ├── Iterate through all root folders
│   ├── Get subfolders (5 levels deep)
│   ├── Build hierarchical list
│   └── Include folder IDs for processing
│
├── 7. Final Output Processing
│   ├── Add "📁 Apple Notes Folder Structure:" header
│   ├── Handle empty results
│   └── Provide error context if needed
│
└── 8. Key Technical Details
    ├── Async/Await pattern for non-blocking execution
    ├── Multiple layers of try-catch blocks
    ├── Data transformation: Raw → Filtered → Formatted
    ├── Tree visualization with hierarchical structure
    └── Automatic duplicate handling
```

### **🔄 Flow Summary:**
```
Tool Call → Server → Tools → AppleScript → Data Processing → Formatting → Return Tree Structure
```

### **⚡ Key Features:**
- ✅ Real-time folder hierarchy snapshot
- ✅ Professional tree formatting
- ✅ Duplicate folder filtering
- ✅ 5-level depth support
- ✅ Clean, readable output

---

## ✏️ rename_folder Tool Flow Structure

```
🔄 rename_folder Tool Flow
├── 1. Tool Call
│   ├── User provides folder_path
│   ├── User provides current_name
│   └── User provides new_name
│
├── 2. Server Layer Processing
│   ├── Create context object for error handling
│   ├── Call tools layer method
│   ├── Wrap result in error handling try-catch
│   └── Format response with emojis and structure
│
├── 3. Tools Layer Processing
│   └── Call AppleScript operations layer
│
├── 4. AppleScript Operations Layer
│   ├── Step 4a: Input Validation
│   │   ├── Validate folder names using same validation as create_folder
│   │   ├── Check for invalid characters
│   │   └── Ensure new name is different from current name
│   │
│   ├── Step 4b: Duplicate Check
│   │   ├── Check if new name would create duplicate
│   │   ├── Handle root level vs nested path logic
│   │   ├── Get all folder names in target location
│   │   └── Prevent rename if duplicate found
│   │
│   ├── Step 4c: Root Level Rename
│   │   ├── Search through root folders
│   │   ├── Find folder with current name
│   │   ├── Rename folder if found
│   │   └── Return error if not found
│   │
│   ├── Step 4d: Nested Folder Rename
│   │   ├── Navigate through path hierarchy
│   │   ├── Find target folder in parent
│   │   ├── Rename the folder
│   │   └── Return success/error result
│   │
│   └── Step 4e: Result Parsing
│       ├── Parse AppleScript return value
│       ├── Extract success/error status
│       ├── Format structured response
│       └── Handle parsing errors
│
├── 5. Base Operations Layer
│   ├── Create subprocess to run osascript
│   ├── Capture stdout and stderr
│   ├── Handle process return codes
│   └── Return decoded output or raise error
│
├── 6. AppleScript Content
│   ├── Complex path navigation logic
│   ├── Root vs nested folder handling
│   ├── String splitting for path components
│   ├── Iterative folder traversal
│   └── Error handling with descriptive messages
│
├── 7. Error Handling
│   ├── Path not found errors
│   ├── Target folder not found errors
│   ├── AppleScript execution errors
│   ├── Result parsing errors
│   └── Provide helpful error messages
│
└── 8. Success Response
    ├── Return structured rename details
    ├── Show old and new names
    ├── Display folder path information
    └── Confirm successful operation
```

### **🔄 Flow Summary:**
```
Tool Call → Server → Tools → Validate → Check Duplicates → Rename (Root/Nested) → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
- **Names valid?** → Continue with validation
- **New name different?** → Continue with duplicate check
- **Duplicate exists?** → Return error
- **Path empty?** → Handle as root level rename
- **Path exists?** → Navigate through hierarchy
- **Target found?** → Perform rename operation
- **AppleScript success?** → Parse and return result
- **Error occurred?** → Return descriptive error message

### **🎯 Tool Capabilities:**
- ✅ Renames folders at root level and nested paths
- ✅ Handles complex path navigation up to 5 levels deep
- ✅ Supports special characters and Unicode in names
- ✅ Validates path existence before attempting rename
- ✅ Provides detailed success/error messages
- ✅ Maintains folder structure integrity
- ✅ Handles edge cases gracefully

---

## 📝 create_note Tool Flow Structure

```
🔄 create_note Tool Flow
├── 1. Tool Call
│   ├── User provides name
│   ├── User provides body (HTML-formatted content)
│   └── User provides folder_path (optional, defaults to "Notes")
│
├── 2. Server Layer Processing
│   ├── Create context object for error handling
│   ├── Call tools layer method
│   ├── Wrap result in error handling try-catch
│   └── Format response with structured output
│
├── 3. Tools Layer Processing
│   └── Call AppleScript operations layer
│
├── 4. AppleScript Operations Layer
│   ├── Step 4a: Input Validation
│   │   ├── Validate and clean note name
│   │   ├── Validate note body content
│   │   ├── Clean folder path
│   │   └── Handle name truncation if needed
│   │
│   ├── Step 4b: HTML Content Processing
│   │   ├── Use body content directly (contains combined title + body HTML)
│   │   ├── No additional processing or escaping
│   │   └── Pass complete HTML content to AppleScript
│   │
│   ├── Step 4c: Path Processing
│   │   ├── If folder_path is simple (no slashes) → simple folder creation
│   │   ├── If folder_path is nested → validate path exists
│   │   ├── Check folder path exists before creation
│   │   └── Parse path components for navigation
│   │
│   ├── Step 4d: Simple Folder Creation
│   │   ├── Use direct folder access
│   │   ├── Escape HTML content for AppleScript
│   │   ├── Create note in target folder
│   │   └── Return creation details
│   │
│   └── Step 4e: Nested Path Creation
│       ├── Navigate through folder hierarchy
│       ├── Find target folder
│       ├── Create note in target folder
│       └── Return creation details
│
├── 5. Base Operations Layer
│   ├── Create subprocess to run osascript
│   ├── Capture stdout and stderr
│   ├── Handle process return codes
│   └── Return decoded output or raise error
│
├── 6. AppleScript Content
│   ├── Simple folder vs nested path logic
│   ├── Path navigation for nested folders
│   ├── Note creation with HTML content
│   ├── Error handling with descriptive messages
│   └── Return structured creation details
│
├── 7. Response Processing
│   ├── Parse AppleScript return value
│   ├── Extract note creation details
│   ├── Format structured response
│   └── Handle parsing errors
│
├── 8. Error Handling
│   ├── Invalid input errors (empty name, special chars)
│   ├── Duplicate name errors
│   ├── Path not found errors
│   ├── Folder not found errors
│   ├── AppleScript execution errors
│   ├── HTML content processing errors
│   └── Provide helpful error messages
│
└── 9. Success Response
    ├── Return structured note details
    ├── Show note name and folder location
    ├── Display creation and modification dates
    └── Confirm successful creation
```

### **🔄 Flow Summary:**
```
Tool Call → Server → Tools → Validate → Process HTML → Process Path → Create Note (Simple/Nested) → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
- **Name valid?** → Continue with validation
- **Body valid?** → Process HTML content
- **Path is simple?** → Use simple folder logic
- **Path is nested?** → Use nested path logic
- **Path exists?** → Continue with creation
- **HTML content ready?** → Create note
- **AppleScript success?** → Return success details
- **Error occurred?** → Return descriptive error message

### **🎯 Tool Capabilities:**
- ✅ Creates notes in root folders and nested paths (up to 5 levels)
- ✅ **HTML-First Approach**: User provides HTML-formatted content
- ✅ **Automatic Title Formatting**: Title wrapped in `<h1>` tags
- ✅ **No Content Processing**: Direct HTML pass-through to AppleScript
- ✅ Supports rich formatting: headers, bold, italic, lists, links
- ✅ Handles Unicode characters and emojis
- ✅ Validates input and prevents invalid characters
- ✅ **Prevents duplicate note names** in same folder
- ✅ Provides detailed creation metadata
- ✅ Maintains HTML formatting and structure

### **📋 Content Support:**
- **HTML-First**: User provides complete HTML-formatted content
- **Automatic Title**: Title automatically wrapped in `<h1>` tags
- **Rich Formatting**: `<h1>`, `<h2>`, `<h3>`, `<strong>`, `<em>`, `<ul><li>`, `<ol><li>`, `<p>`, `<br>`
- **Lists**: Ordered and unordered lists with nested items
- **Emojis & Symbols**: Full Unicode support (🚀, ±, ©, etc.)
- **Special Characters**: HTML entities and special characters
- **No Processing**: Direct HTML pass-through for maximum flexibility

### **🔧 Technical Features:**
- **Input Validation**: Comprehensive validation at multiple levels
- **HTML Processing**: Direct body content usage (no title wrapping)
- **Path Navigation**: Proper handling of nested folder structures
- **Name Truncation**: Automatic handling of long note names
- **Error Handling**: User-friendly error messages and suggestions
- **Metadata Tracking**: Creation and modification date capture
- **Async Operations**: Non-blocking execution for better performance

---

## 📦 move_folder Tool Flow Structure

```
🔄 move_folder Tool Flow
├── 1. Tool Call
│   ├── User provides source_path
│   ├── User provides folder_name
│   └── User provides target_path (optional)
│
├── 2. Input Validation
│   ├── Validate folder name (length, characters)
│   ├── Validate source_path and target_path
│   ├── Check for invalid characters
│   └── Validate nesting depth limits
│
├── 3. Path Validation
│   ├── Check if source_path exists
│   ├── Check if target_path exists (if provided)
│   ├── Verify folder exists in source location
│   └── Check for duplicate names at target
│
├── 4. Nesting Depth Validation
│   ├── Calculate current nesting depth
│   ├── Calculate target nesting depth
│   ├── Validate move won't exceed 5 levels
│   └── Prevent invalid depth operations
│
├── 5. Move Operation Selection
│   ├── If target_path empty → move to root
│   ├── If source_path empty → move from root
│   └── If both provided → move between paths
│
├── 6. AppleScript Execution
│   ├── Step 6a: Move to Root Level
│   │   ├── Handle root to root (no-op)
│   │   ├── Handle nested path to root
│   │   ├── Navigate to source folder
│   │   └── Move folder to beginning of folders
│   │
│   ├── Step 6b: Move to Target Path
│   │   ├── Navigate to source folder
│   │   ├── Navigate to target folder
│   │   ├── Use folder objects for move operation
│   │   └── Execute move command
│   │
│   └── Step 6c: Move Operation
│       ├── Execute move command with folder objects
│       ├── Handle AppleScript errors
│       └── Return success/error result
│
├── 7. Path Navigation Logic
│   ├── Inline path component parsing
│   ├── Iterative folder traversal
│   ├── Root folder vs subfolder handling
│   ├── Missing folder detection
│   └── Error handling for navigation failures
│
├── 8. Response Processing
│   ├── Parse AppleScript return value
│   ├── Extract success/error status
│   ├── Format structured response
│   └── Handle parsing errors
│
├── 9. Error Handling
│   ├── Path not found errors
│   ├── Folder not found errors
│   ├── Duplicate name errors
│   ├── Depth limit errors
│   ├── AppleScript execution errors
│   └── Navigation failure errors
│
└── 10. Success Response
    ├── Return structured move details
    ├── Show source and target paths
    ├── Display folder name information
    └── Confirm successful operation
```

### **🔄 Flow Summary:**
```
Input → Validate → Check Paths → Validate Depth → Select Operation → Navigate → Move (Root/Path) → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
- **Target path empty?** → Move to root level
- **Source path empty?** → Move from root level
- **Paths exist?** → Continue with navigation
- **Folder exists in source?** → Continue with move
- **Duplicate at target?** → Return error
- **Depth > 5?** → Return error
- **Navigation successful?** → Execute move
- **AppleScript success?** → Return success details

### **🎯 Tool Capabilities:**
- ✅ Moves folders between root and nested locations
- ✅ Supports all 5 levels of nesting depth
- ✅ Handles complex path navigation step-by-step
- ✅ Validates paths and prevents invalid moves
- ✅ Prevents duplicate names at destination
- ✅ Enforces 5-level nesting depth limit
- ✅ Provides detailed success/error messages
- ✅ Maintains folder structure integrity
- ✅ Handles special characters and Unicode
- ✅ Uses folder object references for reliable moves

### **🔧 Technical Features:**
- **Inline Navigation**: Uses inline path navigation for folder traversal
- **Object References**: Use folder objects instead of path strings for move operations
- **Step-by-step Logic**: Proper iterative path traversal for all nesting levels
- **Error Handling**: Comprehensive error detection and user-friendly messages
- **Depth Validation**: Proper enforcement of 5-level nesting limit

---

## 📦 move_note Tool Flow Structure

```
🔄 move_note Tool Flow
├── 1. Tool Call
│   ├── User provides note_id
│   ├── User provides source_folder_path
│   └── User provides target_folder_path
│
├── 2. Server Layer Processing
│   ├── Create context object for error handling
│   ├── Call tools layer method
│   ├── Wrap result in error handling try-catch
│   └── Format response with structured output
│
├── 3. Tools Layer Processing
│   └── Call AppleScript operations layer
│
├── 4. AppleScript Operations Layer
│   ├── Step 4a: Input Validation
│   │   ├── Validate note ID is not empty
│   │   ├── Check source and target paths are different
│   │   ├── Clean and validate folder paths
│   │   └── Ensure paths follow validation rules
│   │
│   ├── Step 4b: Note Verification
│   │   ├── Verify note exists in source folder
│   │   ├── Handle root level vs nested path logic
│   │   ├── Navigate through folder hierarchy
│   │   └── Check note ID matches in source location
│   │
│   ├── Step 4c: Target Path Verification
│   │   ├── Verify target folder path exists
│   │   ├── Use centralized path validation
│   │   └── Ensure target is accessible
│   │
│   └── Step 4d: Move Operation
│       ├── Find note in source folder
│       ├── Find target folder
│       ├── Execute AppleScript move command
│       └── Return move result details
│
├── 5. Base Operations Layer
│   ├── Create subprocess to run osascript
│   ├── Capture stdout and stderr
│   ├── Handle process return codes
│   └── Return decoded output or raise error
│
├── 6. AppleScript Content
│   ├── Complex path navigation logic
│   ├── Root vs nested folder handling
│   ├── Note location verification
│   ├── Folder object references for move
│   └── Error handling with descriptive messages
│
├── 7. Response Processing
│   ├── Parse AppleScript return value
│   ├── Extract move operation details
│   ├── Format structured response
│   └── Handle parsing errors
│
├── 8. Error Handling
│   ├── Invalid input errors (empty note ID, same paths)
│   ├── Note not found errors
│   ├── Path not found errors
│   ├── AppleScript execution errors
│   ├── Move operation failures
│   └── Provide helpful error messages
│
└── 9. Success Response
    ├── Return structured move details
    ├── Show note name and ID
    ├── Display source and target folders
    └── Confirm successful move operation
```

### **🔄 Flow Summary:**
```
Tool Call → Server → Tools → Validate → Verify Note → Verify Target → Move → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
- **Note ID valid?** → Continue with validation
- **Paths different?** → Continue with verification
- **Note exists in source?** → Continue with target verification
- **Target path exists?** → Execute move operation
- **AppleScript success?** → Return success details
- **Error occurred?** → Return descriptive error message

### **🎯 Tool Capabilities:**
- ✅ Moves notes between root folders and nested paths (up to 5 levels deep)
- ✅ Comprehensive validation sequence (5-step process)
- ✅ Supports all folder path types (root, simple, nested)
- ✅ Maintains note content and metadata during move
- ✅ Verifies note existence before moving
- ✅ Validates target folder existence
- ✅ Prevents invalid move operations
- ✅ Provides detailed success/error messages
- ✅ Handles special characters and Unicode
- ✅ Uses folder object references for reliable moves

### **🔧 Technical Features:**
- **Input Validation**: Comprehensive validation at multiple levels
- **Note Verification**: Ensures note exists in source location
- **Path Validation**: Verifies both source and target paths
- **Move Operation**: Uses AppleScript move command for reliability
- **Error Handling**: User-friendly error messages and suggestions
- **Metadata Preservation**: Maintains note properties during move
- **Async Operations**: Non-blocking execution for better performance

---

## 📖 read_note Tool Flow Structure

```
🔄 read_note Tool Flow
├── 1. Tool Call
│   ├── User provides note_id
│   └── User provides folder_path (optional, defaults to "Notes")
│
├── 2. Server Layer Processing
│   ├── Create context object for error handling
│   ├── Call tools layer method
│   ├── Wrap result in error handling try-catch
│   └── Format response with structured output
│
├── 3. Tools Layer Processing
│   └── Call AppleScript operations layer
│
├── 4. AppleScript Operations Layer
│   ├── Step 4a: Input Validation
│   │   ├── Validate note ID is not empty/whitespace
│   │   ├── Clean and validate note ID
│   │   ├── Validate folder path (default to "Notes")
│   │   └── Ensure inputs follow validation rules
│   │
│   ├── Step 4b: Path Verification
│   │   ├── Check if folder path exists
│   │   ├── Use centralized path validation
│   │   └── Ensure path is accessible
│   │
│   ├── Step 4c: Note Verification
│   │   ├── Get all notes in specified folder
│   │   ├── Search for note with matching primary key ID
│   │   ├── Verify note exists in specified location
│   │   └── Return error if note not found
│   │
│   ├── Step 4d: Store UUID Extraction
│   │   ├── Get sample note to extract store UUID
│   │   ├── Parse Core Data store identifier
│   │   └── Build full note ID for AppleScript
│   │
│   └── Step 4e: Note Reading
│       ├── Execute AppleScript with full note ID
│       ├── Extract note content and metadata
│       └── Return structured note data
│
├── 5. Base Operations Layer
│   ├── Create subprocess to run osascript
│   ├── Capture stdout and stderr
│   ├── Handle process return codes
│   └── Return decoded output or raise error
│
├── 6. AppleScript Content
│   ├── Core Data ID construction logic
│   ├── Note retrieval by ID
│   ├── Metadata extraction (name, body, dates)
│   ├── Error handling with descriptive messages
│   └── Structured data return format
│
├── 7. Response Processing
│   ├── Parse AppleScript return value
│   ├── Extract note content and metadata
│   ├── Format structured response
│   └── Handle parsing errors
│
├── 8. Error Handling
│   ├── Invalid input errors (empty note ID)
│   ├── Path not found errors
│   ├── Note not found errors
│   ├── AppleScript execution errors
│   ├── Store UUID extraction errors
│   └── Provide helpful error messages
│
└── 9. Success Response
    ├── Return structured note details
    ├── Show note name, ID, and folder
    ├── Display creation and modification dates
    ├── Include full note content
    └── Confirm successful read operation
```

### **🔄 Flow Summary:**
```
Tool Call → Server → Tools → Validate → Verify Path → Verify Note → Extract UUID → Read Note → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
- **Note ID valid?** → Continue with validation
- **Path exists?** → Continue with note verification
- **Note found in folder?** → Continue with UUID extraction
- **Store UUID extracted?** → Continue with note reading
- **AppleScript success?** → Return success details
- **Error occurred?** → Return descriptive error message

### **🎯 Tool Capabilities:**
- ✅ Reads notes by primary key ID with folder verification
- ✅ Supports all folder path types (root, simple, nested)
- ✅ Verifies note exists in specified folder before reading
- ✅ Extracts full note content and metadata
- ✅ Handles Core Data ID construction automatically
- ✅ Provides detailed success/error messages
- ✅ Maintains note content integrity
- ✅ Supports special characters and Unicode
- ✅ Uses secure folder path verification

### **🔧 Technical Features:**
- **Input Validation**: Comprehensive validation at multiple levels
- **Path Verification**: Ensures folder path exists before proceeding
- **Note Verification**: Confirms note exists in specified location
- **Core Data Integration**: Automatic store UUID extraction and ID construction
- **Error Handling**: User-friendly error messages and suggestions
- **Metadata Extraction**: Retrieves creation and modification dates
- **Async Operations**: Non-blocking execution for better performance

---

## ✏️ update_note Tool Flow Structure

```
🔄 update_note Tool Flow
├── 1. Tool Call
│   ├── User provides note_id
│   ├── User provides new_name (HTML title)
│   └── User provides new_body (HTML content)
│
├── 2. Server Layer Processing
│   ├── Create context object for error handling
│   ├── Call tools layer method
│   ├── Wrap result in error handling try-catch
│   └── Format response with structured output
│
├── 3. Tools Layer Processing
│   └── Call AppleScript operations layer
│
├── 4. AppleScript Operations Layer
│   ├── Step 4a: Input Validation
│   │   ├── Validate note ID is not empty
│   │   ├── Clean and validate note ID
│   │   ├── Validate combined content is not None
│   │   └── Validate HTML content format
│   │
│   ├── Step 4b: Content Processing
│   │   ├── Validate note body content
│   │   ├── Process HTML content for AppleScript
│   │   ├── Escape HTML content for AppleScript
│   │   └── Prepare content for update operation
│   │
│   ├── Step 4c: Store UUID Extraction
│   │   ├── Get sample note to extract store UUID
│   │   ├── Parse Core Data store identifier
│   │   └── Build full note ID for AppleScript
│   │
│   └── Step 4d: Note Update
│       ├── Execute AppleScript with full note ID
│       ├── Update note body with new content
│       └── Return updated note metadata
│
├── 5. Base Operations Layer
│   ├── Create subprocess to run osascript
│   ├── Capture stdout and stderr
│   ├── Handle process return codes
│   └── Return decoded output or raise error
│
├── 6. AppleScript Content
│   ├── Core Data ID construction logic
│   ├── Note retrieval by ID
│   ├── Body content update
│   ├── Metadata extraction (name, dates)
│   ├── Error handling with descriptive messages
│   └── Structured data return format
│
├── 7. Response Processing
│   ├── Parse AppleScript return value
│   ├── Extract updated note metadata
│   ├── Format structured response
│   └── Handle parsing errors
│
├── 8. Error Handling
│   ├── Invalid input errors (empty note ID, invalid content)
│   ├── Note not found errors
│   ├── AppleScript execution errors
│   ├── Store UUID extraction errors
│   ├── Content processing errors
│   └── Provide helpful error messages
│
└── 9. Success Response
    ├── Return structured update details
    ├── Show updated note name and ID
    ├── Display creation and modification dates
    └── Confirm successful update operation
```

### **🔄 Flow Summary:**
```
Tool Call → Server → Tools → Validate → Process Content → Extract UUID → Update Note → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
- **Note ID valid?** → Continue with validation
- **Content valid?** → Continue with content processing
- **Store UUID extracted?** → Continue with note update
- **AppleScript success?** → Return success details
- **Error occurred?** → Return descriptive error message

### **🎯 Tool Capabilities:**
- ✅ Updates notes by primary key ID
- ✅ Supports HTML content updates
- ✅ Handles Core Data ID construction automatically
- ✅ Validates and processes HTML content
- ✅ Maintains note metadata during updates
- ✅ Provides detailed success/error messages
- ✅ Supports special characters and Unicode
- ✅ Uses secure note ID verification

### **🔧 Technical Features:**
- **Input Validation**: Comprehensive validation at multiple levels
- **Content Processing**: HTML validation and AppleScript escaping
- **Core Data Integration**: Automatic store UUID extraction and ID construction
- **Update Operation**: Direct note body modification
- **Error Handling**: User-friendly error messages and suggestions
- **Metadata Preservation**: Maintains note properties during update
- **Async Operations**: Non-blocking execution for better performance

---

## 🗑️ delete_note Tool Flow Structure

```
🔄 delete_note Tool Flow
├── 1. Tool Call
│   ├── User provides note_id
│   └── User provides folder_path (optional, defaults to "Notes")
│
├── 2. Server Layer Processing
│   ├── Create context object for error handling
│   ├── Call tools layer method
│   ├── Wrap result in error handling try-catch
│   └── Format response with structured output
│
├── 3. Tools Layer Processing
│   └── Call AppleScript operations layer
│
├── 4. AppleScript Operations Layer
│   ├── Step 4a: Input Validation
│   │   ├── Validate note ID is not empty/whitespace
│   │   ├── Clean and validate note ID
│   │   ├── Validate folder path (default to "Notes")
│   │   └── Ensure inputs follow validation rules
│   │
│   ├── Step 4b: Path Verification
│   │   ├── Check if folder path exists
│   │   ├── Use centralized path validation
│   │   └── Ensure path is accessible
│   │
│   ├── Step 4c: Note Verification
│   │   ├── Get all notes in specified folder
│   │   ├── Search for note with matching primary key ID
│   │   ├── Verify note exists in specified location
│   │   └── Return error if note not found
│   │
│   ├── Step 4d: Store UUID Extraction
│   │   ├── Get sample note to extract store UUID
│   │   ├── Parse Core Data store identifier
│   │   └── Build full note ID for AppleScript
│   │
│   └── Step 4e: Note Deletion
│       ├── Execute AppleScript with full note ID
│       ├── Extract note metadata before deletion
│       ├── Perform deletion operation
│       └── Return deletion confirmation
│
├── 5. Base Operations Layer
│   ├── Create subprocess to run osascript
│   ├── Capture stdout and stderr
│   ├── Handle process return codes
│   └── Return decoded output or raise error
│
├── 6. AppleScript Content
│   ├── Core Data ID construction logic
│   ├── Note retrieval by ID
│   ├── Metadata extraction before deletion
│   ├── Note deletion operation
│   ├── Error handling with descriptive messages
│   └── Structured data return format
│
├── 7. Response Processing
│   ├── Parse AppleScript return value
│   ├── Extract deletion confirmation details
│   ├── Format structured response
│   └── Handle parsing errors
│
├── 8. Error Handling
│   ├── Invalid input errors (empty note ID)
│   ├── Path not found errors
│   ├── Note not found errors
│   ├── AppleScript execution errors
│   ├── Store UUID extraction errors
│   └── Provide helpful error messages
│
└── 9. Success Response
    ├── Return structured deletion details
    ├── Show deleted note name and ID
    ├── Display creation and modification dates
    └── Confirm successful deletion operation
```

### **🔄 Flow Summary:**
```
Tool Call → Server → Tools → Validate → Verify Path → Verify Note → Extract UUID → Delete Note → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
- **Note ID valid?** → Continue with validation
- **Path exists?** → Continue with note verification
- **Note found in folder?** → Continue with UUID extraction
- **Store UUID extracted?** → Continue with note deletion
- **AppleScript success?** → Return success details
- **Error occurred?** → Return descriptive error message

### **🎯 Tool Capabilities:**
- ✅ Deletes notes by primary key ID with folder verification
- ✅ Supports all folder path types (root, simple, nested)
- ✅ Verifies note exists in specified folder before deletion
- ✅ Extracts note metadata before deletion
- ✅ Handles Core Data ID construction automatically
- ✅ Provides detailed success/error messages
- ✅ Maintains deletion confirmation data
- ✅ Supports special characters and Unicode
- ✅ Uses secure folder path verification

### **🔧 Technical Features:**
- **Input Validation**: Comprehensive validation at multiple levels
- **Path Verification**: Ensures folder path exists before proceeding
- **Note Verification**: Confirms note exists in specified location
- **Core Data Integration**: Automatic store UUID extraction and ID construction
- **Metadata Preservation**: Captures note details before deletion
- **Error Handling**: User-friendly error messages and suggestions
- **Async Operations**: Non-blocking execution for better performance

---

## 📝 list_notes Tool Flow Structure

```
🔄 list_notes Tool Flow
├── 1. Tool Call
│   ├── User provides folder_path (optional, defaults to "Notes")
│   └── User calls tool to list notes in specific folder
│
├── 2. Server Layer Processing
│   ├── Create context object for error handling
│   ├── Call tools layer method
│   ├── Wrap result in error handling try-catch
│   └── Format response with structured output
│
├── 3. Tools Layer Processing
│   └── Call AppleScript operations layer
│
├── 4. AppleScript Operations Layer
│   ├── Step 4a: Input Validation
│   │   ├── Validate and clean folder path
│   │   ├── Default to "Notes" if empty
│   │   └── Ensure path follows validation rules
│   │
│   ├── Step 4b: Path Verification
│   │   ├── Check if folder path exists
│   │   ├── Use centralized path validation
│   │   └── Ensure path is accessible
│   │
│   ├── Step 4c: Simple Folder Logic
│   │   ├── If folder_path is simple (no slashes)
│   │   ├── Use direct folder access
│   │   ├── Get all notes in folder
│   │   └── Return notes with IDs and names
│   │
│   └── Step 4d: Nested Path Logic
│       ├── If folder_path is nested (contains slashes)
│       ├── Split path into components
│       ├── Navigate through folder hierarchy
│       ├── Get notes in target folder
│       └── Return notes with IDs and names
│
├── 5. Base Operations Layer
│   ├── Create subprocess to run osascript
│   ├── Capture stdout and stderr
│   ├── Handle process return codes
│   └── Return decoded output or raise error
│
├── 6. AppleScript Content
│   ├── Simple folder vs nested path logic
│   ├── Path navigation for nested folders
│   ├── Note enumeration and ID extraction
│   ├── Error handling with descriptive messages
│   └── Structured data return format
│
├── 7. Response Processing
│   ├── Parse AppleScript return value
│   ├── Extract note IDs and names
│   ├── Format structured response
│   └── Handle parsing errors
│
├── 8. Error Handling
│   ├── Invalid folder path errors
│   ├── Path not found errors
│   ├── AppleScript execution errors
│   ├── Note enumeration errors
│   └── Provide helpful error messages
│
└── 9. Success Response
    ├── Return structured notes list
    ├── Show note names and IDs
    ├── Display folder information
    └── Confirm successful listing operation
```

### **🔄 Flow Summary:**
```
Tool Call → Server → Tools → Validate → Verify Path → List Notes → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
- **Path valid?** → Continue with validation
- **Path exists?** → Continue with note listing
- **Path is simple?** → Use simple folder logic
- **Path is nested?** → Use nested path logic
- **AppleScript success?** → Return success details
- **Error occurred?** → Return descriptive error message

### **🎯 Tool Capabilities:**
- ✅ Lists notes in specific folder paths
- ✅ Supports both simple and nested folder paths
- ✅ Returns note names and primary key IDs
- ✅ Handles empty folders gracefully
- ✅ Provides detailed success/error messages
- ✅ Supports special characters and Unicode
- ✅ Uses secure folder path verification

### **🔧 Technical Features:**
- **Input Validation**: Comprehensive validation at multiple levels
- **Path Verification**: Ensures folder path exists before proceeding
- **Dual Logic**: Handles both simple and nested folder structures
- **Note Enumeration**: Extracts note IDs and names efficiently
- **Error Handling**: User-friendly error messages and suggestions
- **Async Operations**: Non-blocking execution for better performance

---

## 📝 list_all_notes Tool Flow Structure

```
🔄 list_all_notes Tool Flow
├── 1. Tool Call
│   └── User calls tool to list all notes across all folders
│
├── 2. Server Layer Processing
│   ├── Create context object for error handling
│   ├── Call tools layer method
│   ├── Wrap result in error handling try-catch
│   └── Format response with structured output
│
├── 3. Tools Layer Processing
│   └── Call AppleScript operations layer
│
├── 4. AppleScript Operations Layer
│   ├── Step 4a: System-wide Note Collection
│   │   ├── Iterate through all folders in Apple Notes
│   │   ├── Collect notes from each folder
│   │   ├── Include Recently Deleted folder
│   │   └── Build comprehensive notes list
│   │
│   ├── Step 4b: Data Processing
│   │   ├── Extract note IDs and names
│   │   ├── Identify folder locations
│   │   ├── Filter out empty entries
│   │   └── Prepare structured data
│   │
│   └── Step 4c: Result Formatting
│       ├── Parse AppleScript return value
│       ├── Extract note information
│       ├── Format structured response
│       └── Handle parsing errors
│
├── 5. Base Operations Layer
│   ├── Create subprocess to run osascript
│   ├── Capture stdout and stderr
│   ├── Handle process return codes
│   └── Return decoded output or raise error
│
├── 6. AppleScript Content
│   ├── System-wide folder traversal
│   ├── Note enumeration across all folders
│   ├── ID and name extraction
│   ├── Error handling with descriptive messages
│   └── Structured data return format
│
├── 7. Response Processing
│   ├── Parse AppleScript return value
│   ├── Extract note IDs, names, and folders
│   ├── Format structured response
│   └── Handle parsing errors
│
├── 8. Error Handling
│   ├── AppleScript execution errors
│   ├── Note enumeration errors
│   ├── Data processing errors
│   └── Provide helpful error messages
│
└── 9. Success Response
    ├── Return comprehensive notes list
    ├── Show note names, IDs, and folder locations
    ├── Display total count
    └── Confirm successful listing operation
```

### **🔄 Flow Summary:**
```
Tool Call → Server → Tools → Collect Notes → Process Data → Format Result → Return Details
```

### **⚡ Key Decision Points:**
- **System accessible?** → Continue with note collection
- **Notes found?** → Continue with data processing
- **Data valid?** → Continue with formatting
- **AppleScript success?** → Return success details
- **Error occurred?** → Return descriptive error message

### **🎯 Tool Capabilities:**
- ✅ Lists ALL notes across ALL folders in Apple Notes
- ✅ Includes notes from Recently Deleted folder
- ✅ Returns note names, IDs, and folder locations
- ✅ Provides comprehensive system overview
- ✅ Handles empty systems gracefully
- ✅ Provides detailed success/error messages
- ✅ Supports special characters and Unicode

### **🔧 Technical Features:**
- **System-wide Traversal**: Iterates through all folders
- **Comprehensive Collection**: Includes all notes including deleted ones
- **Data Processing**: Extracts IDs, names, and folder locations
- **Error Handling**: User-friendly error messages and suggestions
- **Async Operations**: Non-blocking execution for better performance

---

## 📁 list_folder_contents Tool Flow Structure

```
🔄 list_folder_contents Tool Flow
├── 1. Tool Call
│   ├── User provides folder_path (optional, defaults to "Notes")
│   └── User calls tool to list both notes and folders
│
├── 2. Server Layer Processing
│   ├── Create context object for error handling
│   ├── Call tools layer method
│   ├── Wrap result in error handling try-catch
│   └── Format response with structured output
│
├── 3. Tools Layer Processing
│   └── Call AppleScript operations layer
│
├── 4. AppleScript Operations Layer
│   ├── Step 4a: Input Validation
│   │   ├── Validate and clean folder path
│   │   ├── Default to "Notes" if empty
│   │   └── Ensure path follows validation rules
│   │
│   ├── Step 4b: Path Verification
│   │   ├── Check if folder path exists
│   │   ├── Use centralized path validation
│   │   └── Ensure path is accessible
│   │
│   ├── Step 4c: Notes Collection
│   │   ├── Use existing list_notes functionality
│   │   ├── Get all notes in specified folder
│   │   ├── Extract note names and IDs
│   │   └── Prepare notes data
│   │
│   ├── Step 4d: Folders Collection
│   │   ├── Use existing folder_structure functionality
│   │   ├── Get complete folder hierarchy
│   │   ├── Extract direct child folders
│   │   └── Prepare folders data
│   │
│   └── Step 4e: Data Integration
│       ├── Combine notes and folders data
│       ├── Calculate counts and statistics
│       ├── Format structured response
│       └── Handle integration errors
│
├── 5. Base Operations Layer
│   ├── Create subprocess to run osascript
│   ├── Capture stdout and stderr
│   ├── Handle process return codes
│   └── Return decoded output or raise error
│
├── 6. AppleScript Content
│   ├── Dual operation: notes + folders
│   ├── Path navigation for nested folders
│   ├── Note enumeration and ID extraction
│   ├── Folder hierarchy parsing
│   ├── Error handling with descriptive messages
│   └── Structured data return format
│
├── 7. Response Processing
│   ├── Parse AppleScript return values
│   ├── Extract notes and folders data
│   ├── Calculate summary statistics
│   ├── Format structured response
│   └── Handle parsing errors
│
├── 8. Error Handling
│   ├── Invalid folder path errors
│   ├── Path not found errors
│   ├── AppleScript execution errors
│   ├── Data integration errors
│   └── Provide helpful error messages
│
└── 9. Success Response
    ├── Return comprehensive folder contents
    ├── Show notes with names and IDs
    ├── Show direct child folders
    ├── Display summary counts
    └── Confirm successful listing operation
```

### **🔄 Flow Summary:**
```
Tool Call → Server → Tools → Validate → Verify Path → Collect Notes → Collect Folders → Integrate Data → Return Details
```

### **⚡ Key Decision Points:**
- **Path valid?** → Continue with validation
- **Path exists?** → Continue with data collection
- **Notes found?** → Continue with folders collection
- **Folders found?** → Continue with data integration
- **AppleScript success?** → Return success details
- **Error occurred?** → Return descriptive error message

### **🎯 Tool Capabilities:**
- ✅ Lists both notes and direct child folders in specified path
- ✅ Provides comprehensive folder contents view
- ✅ Returns note names and IDs
- ✅ Returns direct child folder names
- ✅ Calculates summary counts and statistics
- ✅ Handles empty folders gracefully
- ✅ Provides detailed success/error messages
- ✅ Supports special characters and Unicode
- ✅ Uses secure folder path verification

### **🔧 Technical Features:**
- **Input Validation**: Comprehensive validation at multiple levels
- **Path Verification**: Ensures folder path exists before proceeding
- **Dual Collection**: Gathers both notes and folders data
- **Data Integration**: Combines and formats comprehensive results
- **Summary Statistics**: Provides counts and overview information
- **Error Handling**: User-friendly error messages and suggestions
- **Async Operations**: Non-blocking execution for better performance

---

## 📋 Tool Status Overview

### **✅ Production Ready Tools:**
1. **create_folder** - Create folders with comprehensive validation
2. **list_folder_with_structure** - Display complete folder hierarchy
3. **list_notes_with_structure** - Display folders and notes hierarchy
4. **rename_folder** - Rename folders with path support and validation
5. **move_folder** - Move folders between locations with full nesting support
6. **create_note** - Create notes with rich content support and validation
7. **read_note** - Read notes by ID with folder verification
8. **update_note** - Update notes by ID with HTML content support
9. **delete_note** - Delete notes by ID with folder verification
10. **move_note** - Move notes between folders with comprehensive validation
11. **list_notes** - List notes in specific folder with IDs
12. **list_all_notes** - List all notes across all folders
13. **list_folder_contents** - List both notes and folders in a folder

### **🔄 In Development:**
- Additional tools will be documented here as they are completed

### **📊 Tool Categories:**
- **Folder Operations** - Create, list, rename, move folders
- **Note Operations** - Create, read, update, delete, move notes
- **Structure Tools** - Display hierarchies and relationships
- **Listing Tools** - List notes and folders with various scopes
- **Utility Tools** - Validation, error handling, helpers

---

## 🔧 Technical Architecture

### **Layer Structure:**
```
MCP Server Layer
├── Error handling and context management
├── Tool routing and parameter validation
└── Response formatting

Tools Layer
├── Business logic coordination
├── Parameter processing
└── Operation delegation

AppleScript Operations Layer
├── Raw AppleScript execution
├── Data collection and processing
└── Response formatting

Base Operations Layer
├── Subprocess management
├── AppleScript execution
└── Error handling
```

### **Key Design Principles:**
- **Separation of Concerns** - Each layer has specific responsibilities
- **Error Handling** - Comprehensive error catching and user-friendly messages
- **Validation** - Input validation at multiple levels
- **Async Operations** - Non-blocking execution for better performance
- **User Experience** - Clear feedback and helpful error messages

---

*This document will be updated as new tools are developed and existing tools are enhanced.*
