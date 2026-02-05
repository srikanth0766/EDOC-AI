# Debugging Guide: Mermaid Diagram Not Showing

## Problem
The Mermaid control flow diagrams are not appearing in the VS Code extension chat UI.

## Checklist to Debug

### 1. Verify Backend is Generating Mermaid Code

**Test the backend directly:**
```bash
cd "/Users/ramkey03/Desktop/compiler design project/backend"
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "while True:\n    print(\"loop\")",
    "include_control_flow": true,
    "include_logic_analysis": false,
    "include_optimizations": false
  }'
```

**Expected output should include:**
```json
{
  "control_flow": {
    "has_issues": true,
    "issues": [...],
    "mermaid_code": "flowchart TD\n    start[\"Start\"]..."
  }
}
```

**If `control_flow` is `null` or `mermaid_code` is empty**, the backend isn't generating diagrams.

---

### 2. Check Extension is Reloaded

After making changes to `chatbot.html`:
1. In VS Code, close the Extension Development Host window
2. Press **F5** again to reload the extension
3. The HTML file is loaded fresh each time the webview is created

**No compilation needed** - HTML files are loaded directly!

---

### 3. Verify Mermaid.js is Loading

Open the Extension Development Host and:
1. Press `Cmd+Option+I` (macOS) or `Ctrl+Shift+I` (Windows/Linux) to open DevTools
2. Go to the **Console** tab
3. Look for any errors related to Mermaid or CSP (Content Security Policy)

**Common issues:**
- CSP blocking Mermaid CDN
- Network error loading Mermaid library

---

### 4. Test with Known Problematic Code

Use these test files that SHOULD trigger diagrams:

**Infinite Loop (`test_infinite_loop.py`):**
```python
while True:
    print("This will run forever!")
    print("No way to exit this loop")
```

**Unreachable Code (`test_unreachable.py`):**
```python
def calculate():
    x = 10
    return x + 20
    print("This line will never execute")
```

---

### 5. Check Browser Console for Mermaid Rendering

In the Extension Development Host DevTools Console, type:
```javascript
mermaid
```

**Expected:** Should show the Mermaid object
**If undefined:** Mermaid.js didn't load

---

### 6. Manual Test in Browser

Create a test HTML file to verify Mermaid works:
```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>
    <pre class="mermaid">
flowchart TD
    start["Start"]
    condition{"while True"}:::problem
    body["Loop Body"]
    exit[["Exit (unreachable)"]]:::problem
    
    start --> condition
    condition -->|true| body
    body -->|repeat| condition
    condition -->|false (never taken)| exit
    
    classDef problem fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    </pre>
    <script>
        mermaid.initialize({ startOnLoad: true });
    </script>
</body>
</html>
```

Save as `test_mermaid.html` and open in browser. If this works, Mermaid syntax is correct.

---

## Quick Fix Commands

### Restart Everything:
```bash
# Terminal 1 - Ollama
ollama serve

# Terminal 2 - Backend  
cd "/Users/ramkey03/Desktop/compiler design project/backend"
python main.py

# Terminal 3 - Extension (in VS Code)
# Press F5 to launch Extension Development Host
```

### Force Reload Extension:
1. Close Extension Development Host window
2. In main VS Code window, press `Cmd+Shift+P`
3. Type "Developer: Reload Window"
4. Press **F5** again

---

## Expected Behavior

When you analyze `test_infinite_loop.py`:

1. **Chat panel opens** on the right side
2. **Analysis shows:**
   - ❌ Compile-Time: No errors
   - ⚠️ Runtime risks (if any)
   - 📊 **Control Flow Analysis** section
3. **Under Control Flow Analysis:**
   - Issue description: "Infinite loop: while True without break statement"
   - **Visual flowchart** showing the loop structure
   - Red/highlighted nodes showing the problem

---

## If Still Not Working

### Check the actual response data:

Add console logging to `chatbot.html` line 597:
```javascript
// Control Flow Graph (NEW)
console.log('Control flow data:', data.control_flow);  // ADD THIS
if (data.control_flow && data.control_flow.has_issues) {
```

Then check the DevTools console to see what data is actually being received.

---

## Contact Points

If diagrams still don't show:
1. Check backend logs for errors
2. Check Extension Host console for JavaScript errors  
3. Verify `include_control_flow: true` in the request (line 180 of `extension.ts`)
