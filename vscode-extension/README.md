# Python Error Detector - VS Code Extension

AI-based Python code error detection extension for Visual Studio Code.

## Features

- Analyze Python code for potential runtime errors
- AI-powered predictions using CodeBERT
- Simple command-based interface
- Real-time error type and confidence reporting

## Prerequisites

- Visual Studio Code 1.85.0 or higher
- Node.js 18.0 or higher
- Backend server running (see backend README)

## Installation & Development

### 1. Install Dependencies

Navigate to the extension directory and install dependencies:

```bash
cd vscode-extension
npm install
```

### 2. Compile TypeScript

Compile the TypeScript source code:

```bash
npm run compile
```

Or watch for changes during development:

```bash
npm run watch
```

### 3. Run in Development Mode

1. Open the `vscode-extension` folder in VS Code
2. Press `F5` to launch the Extension Development Host
3. A new VS Code window will open with the extension loaded

## Usage

### Starting the Backend

Before using the extension, ensure the backend server is running:

```bash
cd ../backend
python main.py
```

The backend should be running on `http://localhost:8000`

### Analyzing Python Code

1. Open a Python file (`.py`) in VS Code
2. Open the Command Palette:
   - **macOS**: `Cmd+Shift+P`
   - **Windows/Linux**: `Ctrl+Shift+P`
3. Type and select: **"Analyze Python Code Error"**
4. Wait for the analysis to complete
5. A notification will appear with the predicted error type and confidence

### Example

For a Python file with this code:

```python
x = [1, 2, 3]
print(x[10])  # IndexError
```

The extension will display:

```
Predicted Error: IndexError (confidence: 72.34%)
```

## Error Messages

### "Backend server is not running"

**Cause**: The backend server is not accessible on `localhost:8000`

**Solution**: Start the backend server:
```bash
cd ../backend
python main.py
```

### "No file is currently open"

**Cause**: No editor tab is active

**Solution**: Open a Python file first

### "Please open a Python file to analyze"

**Cause**: The current file is not a Python file

**Solution**: Open a `.py` file or change the language mode to Python

### "The file is empty"

**Cause**: The current file has no content

**Solution**: Add some Python code to analyze

## Development

### Project Structure

```
vscode-extension/
├── src/
│   └── extension.ts      # Main extension code
├── out/                   # Compiled JavaScript (generated)
├── package.json           # Extension manifest
├── tsconfig.json          # TypeScript configuration
└── README.md             # This file
```

### Key Files

- **src/extension.ts**: Main extension logic
  - Command registration
  - Code extraction from editor
  - HTTP communication with backend
  - Error handling and user notifications

- **package.json**: Extension manifest
  - Metadata (name, version, description)
  - Command contributions
  - Activation events
  - Dependencies

### Making Changes

1. Edit `src/extension.ts`
2. Compile: `npm run compile`
3. Reload the Extension Development Host:
   - Press `Cmd+R` (macOS) or `Ctrl+R` (Windows/Linux)
   - Or close and press `F5` again

## Packaging (Optional)

To create a `.vsix` package for distribution:

1. Install vsce:
```bash
npm install -g @vscode/vsce
```

2. Package the extension:
```bash
vsce package
```

3. Install the `.vsix` file:
   - Open VS Code
   - Go to Extensions view
   - Click "..." menu → "Install from VSIX..."
   - Select the generated `.vsix` file

## Troubleshooting

### Extension doesn't activate

- Check that you're opening the extension folder in VS Code
- Ensure all dependencies are installed: `npm install`
- Compile the code: `npm run compile`

### Command not found

- Reload the window: `Cmd+R` / `Ctrl+R`
- Check the Output panel (View → Output) and select "Extension Host"

### Backend connection issues

- Verify backend is running: `curl http://localhost:8000`
- Check firewall settings
- Ensure no other service is using port 8000

## MVP Notes

- This is a minimal viable product for demonstration
- The AI model uses a randomly initialized classifier
- Predictions demonstrate the system flow but are not trained/accurate
- For production use, the backend classifier would need training on labeled data

## Support

For issues or questions, check:
1. Backend server logs
2. VS Code Extension Host output (View → Output → Extension Host)
3. Browser DevTools console (Help → Toggle Developer Tools)
