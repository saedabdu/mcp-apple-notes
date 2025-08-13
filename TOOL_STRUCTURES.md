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
│   ├── Check folder name not empty/whitespace
│   ├── Validate name length (max 128 chars)
│   ├── Check for invalid characters
│   └── Validate folder path if provided
│
├── 3. Path Processing
│   ├── If path empty → root level creation
│   ├── If path provided → split into components
│   ├── Check each path component exists
│   └── Validate nesting depth (max 5 levels)
│
├── 4. Duplicate Check
│   ├── Check if folder exists at target location
│   └── Prevent creation if duplicate found
│
├── 5. AppleScript Execution
│   ├── Build AppleScript command
│   ├── Execute via subprocess
│   └── Create folder in Apple Notes
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
Input → Validate → Process Path → Check Duplicates → Execute → Process Response → Return Result
```

### **⚡ Key Decision Points:**
- **Path empty?** → Create at root
- **Path exists?** → Continue
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
│   ├── Step 4a: Root Level Check
│   │   ├── Check if folder_path is empty or same as current_name
│   │   ├── If true → handle root level rename
│   │   ├── Search through root folders
│   │   └── Rename if found, return error if not
│   │
│   ├── Step 4b: Nested Folder Processing
│   │   ├── Split folder_path into components
│   │   ├── Navigate through path hierarchy
│   │   ├── Check each path component exists
│   │   └── Build navigation to parent folder
│   │
│   ├── Step 4c: Target Folder Rename
│   │   ├── Find target folder in parent
│   │   ├── Rename the folder
│   │   └── Return success/error result
│   │
│   └── Step 4d: Result Parsing
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
Tool Call → Server → Tools → AppleScript → Path Navigation → Rename → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
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
│   │   ├── Check note name not empty/whitespace
│   │   ├── Validate name length (max 128 chars)
│   │   ├── Check for invalid characters (< > : " | ? *)
│   │   ├── Validate note body content
│   │   └── Validate folder path if provided
│   │
│   ├── Step 4b: Duplicate Detection
│   │   ├── Check for existing note with same name
│   │   ├── Use centralized validation utilities
│   │   └── Prevent creation if duplicate found
│   │
│   ├── Step 4c: HTML Content Processing
│   │   ├── Wrap title in <h1> tags automatically
│   │   ├── Concatenate: html_content = "<h1>{name}</h1>{body}"
│   │   ├── No additional processing or escaping
│   │   └── Pass complete HTML content to AppleScript
│   │
│   ├── Step 4d: Path Processing
│   │   ├── If folder_path is simple (no slashes) → simple folder creation
│   │   ├── If folder_path is nested → split into components
│   │   ├── Check each path component exists
│   │   └── Validate nesting depth (max 5 levels)
│   │
│   └── Step 4e: Note Creation
│       ├── Build AppleScript command with HTML content
│       ├── Execute via subprocess
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
Tool Call → Server → Tools → Validate → Check Duplicates → Process HTML → Process Path → Create Note → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
- **Name valid?** → Continue with validation
- **Duplicate exists?** → Return error
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
- **Duplicate Detection**: Prevents duplicate note names in same folder
- **HTML Processing**: Automatic title wrapping and content concatenation
- **Path Navigation**: Proper handling of nested folder structures
- **No Content Escaping**: Direct HTML pass-through for clean output
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
│   ├── Step 6a: Root Level Moves
│   │   ├── Handle root to root (no-op)
│   │   ├── Handle root to nested path
│   │   └── Handle nested path to root
│   │
│   ├── Step 6b: Nested Path Navigation
│   │   ├── Split path into components
│   │   ├── Navigate step-by-step through hierarchy
│   │   ├── Find source folder object
│   │   ├── Find target folder object
│   │   └── Use folder objects for move operation
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
Input → Validate → Check Paths → Validate Depth → Select Operation → Navigate → Move → Parse Result → Return Details
```

### **⚡ Key Decision Points:**
- **Target path empty?** → Move to root level
- **Source path empty?** → Move from root level
- **Paths exist?** → Continue with navigation
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

### **🔧 Technical Improvements:**
- **Inline Navigation**: Replaced custom AppleScript functions with inline path navigation
- **Object References**: Use folder objects instead of path strings for move operations
- **Step-by-step Logic**: Proper iterative path traversal for all nesting levels
- **Error Handling**: Comprehensive error detection and user-friendly messages
- **Depth Validation**: Proper enforcement of 5-level nesting limit

---

## 📋 Tool Status Overview

### **✅ Production Ready Tools:**
1. **create_folder** - Create folders with comprehensive validation
2. **list_folder_with_structure** - Display complete folder hierarchy
3. **list_notes_with_structure** - Display folders and notes hierarchy
4. **rename_folder** - Rename folders with path support and validation
5. **move_folder** - Move folders between locations with full nesting support
6. **create_note** - Create notes with rich content support and validation

### **🔄 In Development:**
- Additional tools will be documented here as they are completed

### **📊 Tool Categories:**
- **Folder Operations** - Create, list, rename, move folders
- **Note Operations** - Create, read, update, delete notes
- **Structure Tools** - Display hierarchies and relationships
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
