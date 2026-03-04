import React from 'react';
import { motion } from 'framer-motion';
import CodeAnalyzer from '../components/CodeAnalyzer';
import { Bug } from 'lucide-react';

export default function AuditorPage() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex flex-col gap-8 pb-24"
        >
            <div className="flex items-center gap-4 border-b border-white/5 pb-6">
                <div className="p-3 rounded-xl bg-cyber-primary/10 border border-cyber-primary/20 text-cyber-primary shadow-neon-primary">
                    <Bug size={32} />
                </div>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white drop-shadow-md">
                        Neural Auditor
                    </h1>
                    <p className="text-sm text-gray-400 font-mono mt-1">
                        Deep AST code inspection and architectural smell detection.
                    </p>
                </div>
            </div>

            <div className="h-[600px]">
                <CodeAnalyzer />
            </div>
        </motion.div>
    );
}
