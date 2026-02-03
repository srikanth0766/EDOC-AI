# Agentic AI Code Review System

An intelligent Python code reviewer that orchestrates multiple analysis tools to provide comprehensive feedback on code quality, errors, and optimization opportunities.

## 🎯 Overview

This system goes beyond simple error detection by using an **Agentic AI** approach that coordinates multiple specialized tools:

1. **Compile-Time Analysis** (AST-based) - Syntax and import errors
2. **Runtime Error Prediction** (CodeBERT ML model) - IndexError, TypeError, etc.
3. **Logical Error Detection** (LLM reasoning) - Edge cases and incorrect assumptions
4. **Code Optimization** (Heuristics + LLM) - Performance and quality improvements

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         CodeReviewAgent (Orchestrator)          │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  Compile     │  │   Runtime    │            │
│  │  Checker     │  │   Predictor  │            │
│  │  (AST)       │  │  (CodeBERT)  │            │
│  └──────────────┘  └──────────────┘            │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │   Logic      │  │ Optimization │            │
│  │  Analyzer    │  │   Analyzer   │            │
│  │  (LLM)       │  │ (Heuristics  │            │
│  └──────────────┘  │   + LLM)     │            │
│                    └──────────────┘            │
└─────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- (Optional) Ollama for local LLM analysis

### Installation

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure LLM provider** (optional):
```bash
cp .env.example .env
# Edit .env to configure your LLM provider
```

3. **Install Ollama** (for local LLM - recommended):
```bash
# macOS
brew install ollama

# Start Ollama
ollama serve

# Pull a lightweight model
ollama pull llama3.2:3b
```

### Running the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## 📡 API Endpoints

### 1. Health Check

**GET** `/`

```bash
curl http://localhost:8000/
```

### 2. Simple Prediction (Legacy)

**POST** `/predict`

For backward compatibility. Returns only runtime error prediction.

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"code": "x = [1, 2, 3]\nprint(x[10])"}'
```

**Response**:
```json
{
  "error_type": "IndexError",
  "confidence": 0.7234
}
```

### 3. Comprehensive Review (New!)

**POST** `/review`

Full agentic AI code review with all analysis layers.

```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def process(items):\n    for i in range(len(items)):\n        print(items[i])\n    return items[10]",
    "include_logic_analysis": true,
    "include_optimizations": true
  }'
```

**Response**:
```json
{
  "compile_time": {
    "status": "ok",
    "errors": []
  },
  "runtime_risks": [
    {
      "type": "IndexError",
      "line": 4,
      "confidence": 0.89,
      "explanation": "Possible array/list index out of bounds"
    }
  ],
  "logical_concerns": [
    "Line 4: Hardcoded index 10 may exceed list bounds",
    "Line 2: No validation for empty list"
  ],
  "optimizations": [
    {
      "type": "readability",
      "line": 2,
      "suggestion": "Use enumerate() instead of range(len())",
      "impact": "More Pythonic and readable",
      "example": "for i, item in enumerate(items):"
    }
  ],
  "summary": "✓ No compile-time errors | 1 runtime risk(s) | 2 logical concern(s) | 1 optimization(s) available"
}
```

## 🧪 Testing

Run the test script:

```bash
python test_agent.py
```

## 🔧 Configuration

Edit `.env` file to configure:

```env
# LLM Provider (ollama, openai, claude, gemini)
LLM_PROVIDER=ollama

# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Enable/disable features
ENABLE_LOGIC_ANALYSIS=true
ENABLE_OPTIMIZATIONS=true
```

## 📊 Analysis Types Explained

### 🟡 Compile-Time Errors

**Tool**: Python AST + built-in compiler  
**Speed**: < 50ms  
**Purpose**: Catch syntax errors, import issues

**Example**:
```python
# Input
def hello()
    print("missing colon")

# Output
{
  "type": "SyntaxError",
  "line": 1,
  "message": "expected ':'",
  "suggestion": "Add colon ':' after function definition"
}
```

### 🔴 Runtime Errors

**Tool**: CodeBERT ML model  
**Speed**: ~500ms  
**Purpose**: Predict likely runtime errors

**Detects**:
- IndexError (array bounds)
- TypeError (type mismatches)
- ImportError (missing modules)
- RuntimeError (general errors)

### 🔵 Logical Errors

**Tool**: LLM reasoning (Ollama/GPT/Claude)  
**Speed**: ~3s  
**Purpose**: Find edge cases and logic bugs

**Detects**:
- Unhandled edge cases (empty lists, None values)
- Off-by-one errors
- Incorrect conditional logic
- Potential infinite loops

### 🟢 Optimizations

**Tool**: Heuristics + LLM  
**Speed**: ~3s  
**Purpose**: Suggest better code patterns

**Suggests**:
- Better algorithms/data structures
- More Pythonic patterns
- Performance improvements
- Safety enhancements

## 🎓 Example Use Cases

### Case 1: Syntax Error

```python
# Code
def greet(name)
    return f"Hello {name}"

# Review Result
✗ Compile-time: SyntaxError at line 1
  Suggestion: Add colon ':' after function definition
```

### Case 2: Runtime Risk

```python
# Code
numbers = [1, 2, 3]
print(numbers[5])

# Review Result
✓ Compile-time: OK
⚠ Runtime: IndexError (confidence: 0.92)
  Line 2: Possible array/list index out of bounds
```

### Case 3: Logic Issue

```python
# Code
def find_max(numbers):
    max_val = 0
    for n in numbers:
        if n > max_val:
            max_val = n
    return max_val

# Review Result
✓ Compile-time: OK
⚠ Logic: Line 2: Initializing max to 0 fails for all-negative lists
💡 Optimization: Use built-in max() function
```

### Case 4: Optimization Opportunity

```python
# Code
for i in range(len(items)):
    process(items[i])

# Review Result
✓ Compile-time: OK
💡 Optimization: Use enumerate() or direct iteration
  Impact: More readable and Pythonic
  Example: for i, item in enumerate(items):
```

## 🔌 VS Code Extension Integration

The backend is designed to work with the VS Code extension. The extension calls the `/review` endpoint and displays results inline.

## 🛠️ Development

### Project Structure

```
backend/
├── main.py                    # FastAPI app
├── model.py                   # CodeBERT runtime predictor
├── agent_orchestrator.py      # Main agent coordinator
├── config.py                  # Configuration management
├── analyzers/
│   ├── compile_checker.py     # AST-based syntax checker
│   ├── logic_analyzer.py      # LLM logic analysis
│   └── optimization_analyzer.py # Code optimization
├── llm_providers/
│   ├── base.py               # LLM provider interface
│   ├── ollama_provider.py    # Ollama implementation
│   └── factory.py            # Provider factory
└── tests/
    └── test_agent.py         # Basic tests
```

### Adding New LLM Providers

1. Create provider class in `llm_providers/`
2. Implement `LLMProvider` interface
3. Add to factory in `factory.py`
4. Update `.env.example` with config

## 📝 Notes

- **LLM is optional**: The system works without LLM (compile-time + runtime only)
- **Ollama recommended**: Free, local, no API keys needed
- **Backward compatible**: `/predict` endpoint unchanged
- **Performance**: Full review takes ~7s with LLM, ~500ms without

## 🚧 Future Enhancements

- [ ] Train runtime predictor on real bug dataset
- [ ] Add more LLM providers (OpenAI, Claude, Gemini)
- [ ] Cache LLM results for identical code
- [ ] Add security vulnerability detection
- [ ] Support for other languages (JavaScript, Java, etc.)

## 📄 License

MIT License - See LICENSE file for details
