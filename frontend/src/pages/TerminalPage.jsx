import React from 'react';
import { motion } from 'framer-motion';
import { Terminal } from 'lucide-react';

export default function TerminalPage() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex flex-col gap-8 pb-24 h-full"
        >
            <div className="flex items-center gap-4 border-b border-white/5 pb-6">
                <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-gray-300">
                    <Terminal size={32} />
                </div>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white drop-shadow-md">
                        Server Terminal
                    </h1>
                    <p className="text-sm text-gray-400 font-mono mt-1">
                        Direct console access to the backend management system.
                    </p>
                </div>
            </div>

            <div className="flex-1 min-h-[500px] glass-panel p-6 border-t-white/10 border-l-white/10 font-mono text-sm text-gray-300 relative overflow-hidden">
                <div className="absolute inset-x-0 top-0 h-8 bg-black/40 border-b border-white/5 flex items-center px-4 gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-cyber-danger"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-cyber-warning"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-cyber-success"></div>
                    <span className="ml-4 text-xs text-gray-500">root@a3sc-core:~</span>
                </div>
                <div className="pt-8 overflow-y-auto h-full pb-4">
                    <div className="text-cyber-primary mb-2">A³SC Interactive Shell v1.0.0</div>
                    <div className="opacity-70">Type 'help' to see available commands.</div>
                    <div className="mt-4 flex gap-2">
                        <span className="text-cyber-success">admin@system:$</span>
                        <span className="text-white">tail -f /var/log/a3sc/core.log</span>
                    </div>
                    <div className="mt-2 text-gray-400 space-y-1">
                        <p>[INFO] Model Qwen2.5 loaded successfully.</p>
                        <p>[INFO] FastAPI server listening on 0.0.0.0:8000</p>
                        <p>[DEBUG] Incoming connection from 127.0.0.1</p>
                        <p>[INFO] AST Analysis complete for TargetModule. Cost: 42ms</p>
                    </div>
                    <div className="mt-4 flex gap-2">
                        <span className="text-cyber-success animate-pulse">admin@system:</span>
                        <span className="w-2 h-4 bg-white/80 animate-pulse"></span>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
