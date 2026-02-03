"""
Chat handler for interactive code analysis conversations.
Manages context and generates responses to user questions about code analysis.
"""

import requests
from typing import List, Dict, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Represents a single chat message."""
    role: str  # 'user' or 'assistant'
    content: str


class ChatContext(BaseModel):
    """Context for a chat conversation."""
    code: str
    analysis_results: Dict
    chat_history: List[ChatMessage] = []


class ChatHandler:
    """Handles interactive chat conversations about code analysis."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        """
        Initialize chat handler.
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = 30
    
    def _build_context_prompt(self, context: ChatContext) -> str:
        """
        Build a context prompt from code and analysis results.
        
        Args:
            context: Chat context with code and analysis
            
        Returns:
            Formatted context string
        """
        analysis = context.analysis_results
        
        prompt_parts = [
            "# Code Being Analyzed:",
            "```python",
            context.code,
            "```",
            "",
            "# Analysis Results:",
        ]
        
        # Compile-time errors
        if analysis.get("compile_time", {}).get("errors"):
            prompt_parts.append("\n## Compile-Time Errors:")
            for error in analysis["compile_time"]["errors"]:
                prompt_parts.append(f"- Line {error['line']}: {error['message']}")
        elif analysis.get("compile_time", {}).get("status") == "valid":
            prompt_parts.append("\n## Compile-Time: No errors detected")
        
        # Runtime risks
        if analysis.get("runtime_risks"):
            prompt_parts.append("\n## Runtime Risk Predictions:")
            for risk in analysis["runtime_risks"]:
                confidence = risk.get("confidence", 0) * 100
                prompt_parts.append(f"- {risk['error_type']} ({confidence:.1f}% confidence)")
        
        # Logical concerns
        if analysis.get("logical_concerns"):
            prompt_parts.append("\n## Logical Concerns:")
            for concern in analysis["logical_concerns"]:
                prompt_parts.append(f"- {concern}")
        
        # Optimizations
        if analysis.get("optimizations"):
            prompt_parts.append("\n## Optimization Suggestions:")
            for opt in analysis["optimizations"]:
                line_info = f"Line {opt['line']}: " if opt.get('line', 0) > 0 else ""
                prompt_parts.append(f"- {line_info}{opt['suggestion']} ({opt['impact']})")
        
        return "\n".join(prompt_parts)
    
    def _generate_response(self, user_message: str, context_prompt: str, chat_history: List[ChatMessage]) -> str:
        """
        Generate a response using Ollama.
        
        Args:
            user_message: User's question
            context_prompt: Context about code and analysis
            chat_history: Previous messages in conversation
            
        Returns:
            AI-generated response
        """
        system_prompt = """You are an expert Python code analysis assistant. You help developers understand code issues, errors, and optimizations.

Your role:
- Answer questions about the analyzed code and its issues
- Explain errors, warnings, and optimization suggestions clearly
- Provide actionable advice on how to fix problems
- Reference specific line numbers when relevant
- Be concise but thorough

Guidelines:
- Use the code and analysis results provided as context
- If asked about a specific error or suggestion, explain it in detail
- Suggest concrete fixes with code examples when appropriate
- If the question is unclear, ask for clarification
- Stay focused on the code analysis context provided"""

        # Build the full prompt with context and history
        full_prompt_parts = [context_prompt, "\n\n# Conversation:"]
        
        # Add chat history
        for msg in chat_history[-6:]:  # Keep last 6 messages for context
            role_label = "User" if msg.role == "user" else "Assistant"
            full_prompt_parts.append(f"\n{role_label}: {msg.content}")
        
        # Add current user message
        full_prompt_parts.append(f"\nUser: {user_message}")
        full_prompt_parts.append("\nAssistant:")
        
        full_prompt = "\n".join(full_prompt_parts)
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get("response", "I'm sorry, I couldn't generate a response.")
            else:
                return "I'm having trouble connecting to the AI model. Please try again."
        
        except requests.exceptions.Timeout:
            return "The request timed out. Please try asking a simpler question."
        except Exception as e:
            print(f"Chat generation error: {e}")
            return "An error occurred while generating a response. Please try again."
    
    def chat(self, user_message: str, context: ChatContext) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: User's question or message
            context: Chat context with code, analysis, and history
            
        Returns:
            AI-generated response
        """
        # Build context prompt
        context_prompt = self._build_context_prompt(context)
        
        # Generate response
        response = self._generate_response(user_message, context_prompt, context.chat_history)
        
        return response
    
    def is_available(self) -> bool:
        """Check if Ollama is running and available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
