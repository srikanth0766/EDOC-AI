/**
 * VS Code Extension for AI-based Python Code Analysis
 * 
 * This extension provides a chatbot interface to analyze Python code for errors,
 * logic issues, and optimizations using a backend AI model.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import axios from 'axios';

// Backend API configuration
const BACKEND_URL = 'http://localhost:8000';
const REVIEW_ENDPOINT = `${BACKEND_URL}/review`;
const CHAT_ENDPOINT = `${BACKEND_URL}/chat`;

// Response interface matching backend API
interface ReviewResponse {
    compile_time: {
        status: string;
        errors?: Array<{ line: number; message: string }>;
    };
    runtime_risks: Array<{
        error_type: string;
        confidence: number;
    }>;
    logical_concerns: string[];
    optimizations: Array<{
        type: string;
        line: number;
        suggestion: string;
        impact: string;
        example?: string;
    }>;
    control_flow?: {
        has_issues: boolean;
        issues: Array<{
            type: string;
            line: number;
            description: string;
            severity: string;
        }>;
        mermaid_code: string;
    };
    summary: string;
}

// Global webview panel reference
let chatPanel: vscode.WebviewPanel | undefined;

// Context storage for chat
let currentCode: string = '';
let currentAnalysis: ReviewResponse | undefined;
let chatHistory: Array<{ role: string; content: string }> = [];

/**
 * Activate the extension
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('AI Code Assistant extension is now active');

    // Register the "Analyze Python Code Error" command
    const disposable = vscode.commands.registerCommand(
        'python-error-detector.analyze',
        async () => {
            await showChatbotAndAnalyze(context);
        }
    );

    context.subscriptions.push(disposable);
}

/**
 * Show chatbot panel and analyze code
 */
async function showChatbotAndAnalyze(context: vscode.ExtensionContext) {
    // Get the active text editor
    const editor = vscode.window.activeTextEditor;

    if (!editor) {
        vscode.window.showErrorMessage('No file is currently open');
        return;
    }

    // Check if the file is a Python file
    const document = editor.document;
    if (document.languageId !== 'python') {
        vscode.window.showWarningMessage('Please open a Python file to analyze');
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
    } else {
        chatPanel = vscode.window.createWebviewPanel(
            'aiCodeAssistant',
            'AI Code Assistant',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.file(path.join(context.extensionPath, 'src'))
                ]
            }
        );

        // Load the HTML content
        chatPanel.webview.html = getWebviewContent(context, chatPanel.webview);

        // Handle panel disposal
        chatPanel.onDidDispose(
            () => {
                chatPanel = undefined;
            },
            null,
            context.subscriptions
        );

        // Handle messages from the webview
        chatPanel.webview.onDidReceiveMessage(
            async message => {
                switch (message.type) {
                    case 'ready':
                        // Webview is ready, start analysis
                        analyzeCode(code, chatPanel!);
                        break;
                    case 'sendChatMessage':
                        // Handle chat message from user
                        await handleChatMessage(message.text, chatPanel!);
                        break;
                }
            },
            undefined,
            context.subscriptions
        );
    }

    // If panel already exists, just trigger analysis
    if (chatPanel) {
        analyzeCode(code, chatPanel);
    }
}

/**
 * Analyze code and send results to chatbot
 */
async function analyzeCode(code: string, panel: vscode.WebviewPanel) {
    // Show loading indicator
    panel.webview.postMessage({ type: 'showLoading' });

    // Store code for chat context
    currentCode = code;
    chatHistory = []; // Reset chat history for new analysis

    try {
        // Send request to backend
        const response = await axios.post<ReviewResponse>(
            REVIEW_ENDPOINT,
            {
                code,
                include_logic_analysis: true,
                include_optimizations: true
            },
            {
                headers: { 'Content-Type': 'application/json' },
                timeout: 30000 // 30 second timeout
            }
        );

        // Store analysis results for chat context
        currentAnalysis = response.data;

        // Send analysis results to webview
        panel.webview.postMessage({
            type: 'showAnalysis',
            data: response.data
        });

    } catch (error: any) {
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
async function handleChatMessage(userMessage: string, panel: vscode.WebviewPanel) {
    // Show loading indicator
    panel.webview.postMessage({ type: 'showLoading' });

    try {
        // Add user message to history
        chatHistory.push({ role: 'user', content: userMessage });

        // Send request to backend chat endpoint
        const response = await axios.post(
            CHAT_ENDPOINT,
            {
                message: userMessage,
                code: currentCode,
                analysis_results: currentAnalysis || {},
                chat_history: chatHistory
            },
            {
                headers: { 'Content-Type': 'application/json' },
                timeout: 30000
            }
        );

        const aiResponse = response.data.response;

        // Add AI response to history
        chatHistory.push({ role: 'assistant', content: aiResponse });

        // Hide loading and send response to webview
        panel.webview.postMessage({ type: 'hideLoading' });
        panel.webview.postMessage({
            type: 'addAssistantMessage',
            text: aiResponse
        });

    } catch (error: any) {
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
function getErrorMessage(error: any): string {
    if (error.code === 'ECONNREFUSED') {
        return 'Backend server is not running. Please start the backend server on localhost:8000';
    } else if (error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
        return 'Request timed out. The backend server may be overloaded or not responding';
    } else if (error.response) {
        const status = error.response.status;
        const detail = error.response.data?.detail || 'Unknown error';
        return `Backend error (${status}): ${detail}`;
    } else {
        return `Error communicating with backend: ${error.message}`;
    }
}

/**
 * Get the HTML content for the webview
 */
function getWebviewContent(context: vscode.ExtensionContext, webview: vscode.Webview): string {
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
function getNonce(): string {
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
export function deactivate() {
    console.log('AI Code Assistant extension is now deactivated');
}
