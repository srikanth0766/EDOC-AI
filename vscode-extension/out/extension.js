"use strict";
/**
 * VS Code Extension for AI-based Python Code Analysis
 *
 * This extension provides a chatbot interface to analyze Python code for errors,
 * logic issues, and optimizations using a backend AI model.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const axios_1 = __importDefault(require("axios"));
// Backend API configuration
const BACKEND_URL = 'http://localhost:8000';
const REVIEW_ENDPOINT = `${BACKEND_URL}/review`;
const CHAT_ENDPOINT = `${BACKEND_URL}/chat`;
// Global webview panel reference
let chatPanel;
// Context storage for chat
let currentCode = '';
let currentAnalysis;
let chatHistory = [];
/**
 * Activate the extension
 */
function activate(context) {
    console.log('AI Code Assistant extension is now active');
    // Register the "Analyze Python Code Error" command
    const disposable = vscode.commands.registerCommand('code-error-detector.analyze', async () => {
        await showChatbotAndAnalyze(context);
    });
    context.subscriptions.push(disposable);
}
/**
 * Show chatbot panel and analyze code
 */
async function showChatbotAndAnalyze(context) {
    // Get the active text editor
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No file is currently open');
        return;
    }
    // Check if the file language is supported
    const document = editor.document;
    const supportedLanguages = ['python', 'javascript', 'typescript', 'javascriptreact', 'typescriptreact'];
    if (!supportedLanguages.includes(document.languageId)) {
        vscode.window.showWarningMessage(`Language "${document.languageId}" is not yet supported. Supported languages: ${supportedLanguages.join(', ')}`);
        return;
    }
    // Get the code content
    const code = document.getText();
    if (!code || code.trim().length === 0) {
        vscode.window.showWarningMessage('The file is empty');
        return;
    }
    // Create or show the chatbot panel
    if (chatPanel) {
        chatPanel.reveal(vscode.ViewColumn.Beside);
    }
    else {
        chatPanel = vscode.window.createWebviewPanel('aiCodeAssistant', 'AI Code Assistant', vscode.ViewColumn.Beside, {
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: [
                vscode.Uri.file(path.join(context.extensionPath, 'src'))
            ]
        });
        // Load the HTML content
        chatPanel.webview.html = getWebviewContent(context, chatPanel.webview);
        // Handle panel disposal
        chatPanel.onDidDispose(() => {
            chatPanel = undefined;
        }, null, context.subscriptions);
        // Handle messages from the webview
        chatPanel.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'ready':
                    // Webview is ready, start analysis
                    analyzeCode(code, chatPanel);
                    break;
                case 'sendChatMessage':
                    // Handle chat message from user
                    await handleChatMessage(message.text, chatPanel);
                    break;
            }
        }, undefined, context.subscriptions);
    }
    // Store the code for when webview sends 'ready' message
    currentCode = code;
}
/**
 * Analyze code and send results to chatbot
 */
async function analyzeCode(code, panel) {
    // Clear previous analysis
    panel.webview.postMessage({ type: 'clearChat' });
    // Show loading indicator
    panel.webview.postMessage({ type: 'showLoading' });
    // Store code for chat context
    currentCode = code;
    chatHistory = []; // Reset chat history for new analysis
    try {
        // Send request to backend
        const response = await axios_1.default.post(REVIEW_ENDPOINT, {
            code,
            include_logic_analysis: true,
            include_optimizations: true,
            include_control_flow: true
        }, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 30000 // 30 second timeout
        });
        // Store analysis results for chat context
        currentAnalysis = response.data;
        // Send analysis results to webview
        panel.webview.postMessage({
            type: 'showAnalysis',
            data: response.data
        });
    }
    catch (error) {
        // Hide loading and show error
        panel.webview.postMessage({ type: 'hideLoading' });
        const errorMessage = getErrorMessage(error);
        panel.webview.postMessage({
            type: 'showError',
            text: errorMessage
        });
    }
}
/**
 * Handle chat message from user
 */
async function handleChatMessage(userMessage, panel) {
    // Show loading indicator
    panel.webview.postMessage({ type: 'showLoading' });
    try {
        // Add user message to history
        chatHistory.push({ role: 'user', content: userMessage });
        // Send request to backend chat endpoint
        const response = await axios_1.default.post(CHAT_ENDPOINT, {
            message: userMessage,
            code: currentCode,
            analysis_results: currentAnalysis || {},
            chat_history: chatHistory
        }, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 30000
        });
        const aiResponse = response.data.response;
        // Add AI response to history
        chatHistory.push({ role: 'assistant', content: aiResponse });
        // Hide loading and send response to webview
        panel.webview.postMessage({ type: 'hideLoading' });
        panel.webview.postMessage({
            type: 'addAssistantMessage',
            text: aiResponse
        });
    }
    catch (error) {
        // Hide loading and show error
        panel.webview.postMessage({ type: 'hideLoading' });
        const errorMessage = getErrorMessage(error);
        panel.webview.postMessage({
            type: 'addAssistantMessage',
            text: `❌ Error: ${errorMessage}`
        });
    }
}
/**
 * Get error message from axios error
 */
function getErrorMessage(error) {
    if (error.code === 'ECONNREFUSED') {
        return 'Backend server is not running. Please start the backend server on localhost:8000';
    }
    else if (error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
        return 'Request timed out. The backend server may be overloaded or not responding';
    }
    else if (error.response) {
        const status = error.response.status;
        const detail = error.response.data?.detail || 'Unknown error';
        return `Backend error (${status}): ${detail}`;
    }
    else {
        return `Error communicating with backend: ${error.message}`;
    }
}
/**
 * Get the HTML content for the webview
 */
function getWebviewContent(context, webview) {
    const htmlPath = path.join(context.extensionPath, 'src', 'chatbot.html');
    let html = fs.readFileSync(htmlPath, 'utf8');
    // Generate a nonce for CSP
    const nonce = getNonce();
    // Replace placeholders
    html = html.replace(/{{nonce}}/g, nonce);
    html = html.replace(/{{cspSource}}/g, webview.cspSource);
    return html;
}
/**
 * Generate a random nonce for CSP
 */
function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
/**
 * Deactivate the extension
 */
function deactivate() {
    console.log('AI Code Assistant extension is now deactivated');
}
//# sourceMappingURL=extension.js.map