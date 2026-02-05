# Complete Setup Commands for VS Code Extension

## Step 1: Start Ollama (in Terminal 1)
```bash
cd "/Users/ramkey03/Desktop/compiler design project"
ollama serve
```
**Keep this terminal running!**

---

## Step 2: Start Backend Server (in Terminal 2)
```bash
cd "/Users/ramkey03/Desktop/compiler design project/backend"

# If you haven't installed dependencies yet:
pip install -r requirements.txt

# Start the backend server
python main.py
```
**Keep this terminal running!**

---

## Step 3: Setup VS Code Extension (in Terminal 3)
```bash
cd "/Users/ramkey03/Desktop/compiler design project/vscode-extension"

# Install Node.js dependencies (only needed once)
npm install

# Compile TypeScript to JavaScript
npm run compile
```

---

## Step 4: Run the Extension in VS Code

### Option A: Using F5 (Recommended)
1. Open the `vscode-extension` folder in VS Code:
   ```bash
   cd "/Users/ramkey03/Desktop/compiler design project/vscode-extension"
   code .
   ```
2. Press **F5** to launch Extension Development Host
3. A new VS Code window will open with your extension loaded

### Option B: Manual Installation
1. Package the extension:
   ```bash
   cd "/Users/ramkey03/Desktop/compiler design project/vscode-extension"
   npm install -g @vscode/vsce
   vsce package
   ```
2. Install the generated `.vsix` file in VS Code

---

## Step 5: Test the Extension

In the Extension Development Host window:

1. Open any Python file (or create a new one)
2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
3. Type: **"Analyze Python Code Error"**
4. Select the command
5. The chat panel will open on the right side showing the analysis

---

## Quick Test Code

Create a test file with this code to see all features:

```python
# test_example.py
def process_data(items):
    # This will trigger runtime risk detection
    result = items[10]  # Potential IndexError
    
    # This will trigger infinite loop detection
    while True:
        print("Running...")
        # Missing break statement
    
    # This is unreachable code
    return result
```

---

## Troubleshooting

### If extension doesn't compile:
```bash
cd "/Users/ramkey03/Desktop/compiler design project/vscode-extension"
rm -rf node_modules out
npm install
npm run compile
```

### If backend fails to start:
```bash
cd "/Users/ramkey03/Desktop/compiler design project/backend"
pip install --upgrade -r requirements.txt
python main.py
```

### Check if services are running:
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check Backend
curl http://localhost:8000
```

---

## Summary of What Should Be Running

You need **3 terminals** running simultaneously:
1. **Terminal 1**: `ollama serve` (for LLM)
2. **Terminal 2**: `python main.py` (backend API)
3. **Terminal 3**: VS Code Extension Development Host (launched with F5)

That's it! The extension is now ready to use.
