# AI-Based Python Code Analyzer with Visual Error Explanation

A VS Code extension that combines AI-powered error detection with visual control flow graphs to help developers understand **WHY** errors occur, not just **WHAT** they are.

## 🎯 Project Overview

This system provides comprehensive Python code analysis:

- **AI-Based Analysis**: CodeBERT model for runtime error prediction, LLM-based logic analysis
- **Visual Explanation**: Control flow graphs showing program behavior (infinite loops, unreachable code)
- **Interactive Chat**: Ask follow-up questions about your code and analysis results
- **Backend**: FastAPI server orchestrating multiple analyzers
- **Frontend**: VS Code extension with rich chatbot interface

## 📁 Project Structure

```
compiler design project/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # FastAPI server with /predict endpoint
│   ├── model.py            # CodeBERT model wrapper
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Backend documentation
│
└── vscode-extension/       # VS Code extension
    ├── src/
    │   └── extension.ts    # Extension logic
    ├── package.json        # Extension manifest
    ├── tsconfig.json       # TypeScript config
    └── README.md           # Extension documentation
```

## 🚀 Quick Start

### 1. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the server (will download CodeBERT model on first run)
python main.py
```

The backend will be running on `http://localhost:8000`

### 2. Set Up VS Code Extension

```bash
# Navigate to extension directory
cd vscode-extension

# Install Node.js dependencies
npm install

# Compile TypeScript
npm run compile

# Open in VS Code
code .
```

### 3. Run the Extension

1. In VS Code, press `F5` to launch the Extension Development Host
2. In the new window, open a Python file
3. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
4. Type and select: **"Analyze Python Code Error"**
5. View the prediction in the notification

## 💡 Example Usage

Create a Python file with potential errors:

```python
# example.py
x = [1, 2, 3]
print(x[10])  # This will cause an IndexError

import nonexistent_module  # This will cause an ImportError
```

Run the "Analyze Python Code Error" command to see predictions like:

```
Predicted Error: IndexError (confidence: 72.34%)
```

## 🔧 System Requirements

### Backend
- Python 3.9 or higher
- ~2GB RAM (for CodeBERT model)
- ~500MB disk space (for model download)

### Extension
- Visual Studio Code 1.85.0 or higher
- Node.js 18.0 or higher

## 📚 Documentation

- [Backend README](backend/README.md) - API documentation, setup, and troubleshooting
- [Extension README](vscode-extension/README.md) - Installation, usage, and development guide

## 🎓 Technical Details

### Backend Architecture

- **Framework**: FastAPI for REST API
- **Model**: Microsoft CodeBERT (pretrained transformer)
- **Classifier**: Simple linear layer (randomly initialized for MVP)
- **Endpoint**: POST `/predict` accepts code, returns error type and confidence

### Extension Architecture

- **Language**: TypeScript
- **API**: VS Code Extension API
- **HTTP Client**: Axios
- **Interface**: Command-based (no UI panels)

### Analysis Features

**AI-Based Detection:**
- Compile-time errors (syntax, imports)
- Runtime error prediction (IndexError, RuntimeError, ImportError, etc.)
- Logic issues and edge cases (LLM-powered)
- Code optimization suggestions

**Visual Error Explanation (NEW):**
- Control flow graph generation using Mermaid.js
- Infinite loop detection (`while True` without break)
- Loop variable not updated warnings
- Unreachable code detection (after return/break)
- Interactive flowcharts showing WHY code fails

## ⚠️ Current Capabilities

This system provides:

- ✅ Full end-to-end AI-based code analysis
- ✅ Visual control flow graphs for error explanation
- ✅ Interactive chat interface for follow-up questions
- ✅ Multiple analysis layers (compile, runtime, logic, optimization, control flow)
- ✅ Offline LLM support (Ollama)
- ⚠️ CodeBERT classifier needs training for accurate runtime predictions
- ⚠️ Python-only support (multi-language planned)

For production use, the classifier would need to be trained on labeled data.

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Ensure dependencies installed: `pip install -r requirements.txt`
- Check if port 8000 is available

### Extension command not found
- Ensure backend is running first
- Reload VS Code window: `Cmd+R` / `Ctrl+R`
- Check Extension Host output: View → Output → Extension Host

### Connection refused error
- Verify backend is running: `curl http://localhost:8000`
- Check firewall settings
- Ensure backend URL is `http://localhost:8000`

## 📝 Success Criteria

- ✅ Backend runs with one command
- ✅ VS Code extension installs and runs
- ✅ Clicking the command shows an error prediction
- ✅ Entire system works locally without manual file copying
- ✅ Clear separation of backend and extension
- ✅ Fast startup time
- ✅ Minimal configuration

## 🔮 Future Enhancements

- Train the classifier on real error datasets
- Add error localization (highlight specific lines)
- Support multiple error types per file
- Add auto-fix suggestions
- Integrate with VS Code diagnostics
- Background monitoring mode
- Support for more programming languages

## 📄 License

This is an educational MVP project.
