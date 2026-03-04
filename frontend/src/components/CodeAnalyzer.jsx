import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Code2, Play, GitMerge, AlertCircle, ShieldAlert } from 'lucide-react';
import clsx from 'clsx';

const BACKEND = 'http://localhost:8000';

export default function CodeAnalyzer() {
    const [code, setCode] = useState('');
    const [smells, setSmells] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [hasRun, setHasRun] = useState(false);

    const analyzeCode = async () => {
        if (!code.trim()) return;
        setLoading(true);
        setError('');
        setHasRun(true);
        try {
            const res = await fetch(`${BACKEND}/analyze-smells`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, language: 'python' })
            });
            if (!res.ok) throw new Error(`Analysis rejected: ${res.statusText}`);
            const data = await res.json();
            setSmells(data.smells || []);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass-panel w-full border-t-white/10 border-l-white/10 overflow-hidden relative">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-cyber-secondary/10 blur-[100px] rounded-full pointer-events-none -translate-y-1/2 translate-x-1/2" />

            <div className="p-6 border-b border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative z-10">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-lg bg-cyber-primary/10 border border-cyber-primary/20 text-cyber-primary shadow-neon-primary">
                        <Code2 size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-white tracking-wide">A³SC Neural Auditor</h2>
                        <div className="text-xs text-cyber-primary/60 font-mono tracking-widest mt-0.5 uppercase">Paste Source For Analysis</div>
                    </div>
                </div>
                <button
                    onClick={analyzeCode}
                    disabled={loading || !code.trim()}
                    className="cyber-button flex items-center justify-center gap-2 group disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <div className="w-5 h-5 border-2 border-cyber-primary border-t-transparent rounded-full animate-spin" />
                    ) : (
                        <>
                            <Play size={16} className="group-hover:text-white transition-colors" />
                            <span className="font-mono tracking-widest uppercase text-xs">Execute Scan</span>
                        </>
                    )}
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 min-h-[400px] relative z-10">

                {/* Editor Pane */}
                <div className="border-b lg:border-b-0 lg:border-r border-white/5 relative group">
                    <div className="absolute top-3 left-4 text-[10px] font-mono text-gray-500 uppercase tracking-widest pointer-events-none z-20 flex gap-4">
                        <span>input.py</span>
                        <span className="text-cyber-primary/40 group-focus-within:text-cyber-primary transition-colors">Editing</span>
                    </div>
                    {/* Minimal line numbers illusion */}
                    <div className="absolute left-0 top-0 bottom-0 w-12 bg-black/20 border-r border-white/5 flex flex-col items-end pt-12 pr-2 font-mono text-[10px] text-gray-600 space-y-1 select-none pointer-events-none">
                        {[...Array(15)].map((_, i) => <div key={i}>{i + 1}</div>)}
                    </div>
                    <textarea
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        className="w-full h-full min-h-[400px] bg-transparent text-gray-300 font-mono text-sm p-4 pt-12 pl-16 resize-none focus:outline-none focus:ring-1 focus:ring-inset focus:ring-cyber-primary/50"
                        spellCheck="false"
                        placeholder="def god_class_example():&#10;    # Write or paste Python code here&#10;    pass"
                    />
                </div>

                {/* Results Pane */}
                <div className="bg-black/40 p-6 flex flex-col relative overflow-hidden">
                    <div className="absolute inset-0 bg-glass-glow opacity-50 pointer-events-none" />

                    <h3 className="text-xs font-mono text-gray-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                        <GitMerge size={14} /> Telemetry Output
                    </h3>

                    {loading ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-cyber-primary/70 font-mono">
                            <div className="w-12 h-12 border-b-2 border-l-2 border-cyber-primary rounded-full animate-spin mb-4" />
                            Scanning AST nodes...
                        </div>
                    ) : error ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-cyber-danger font-mono text-center px-4">
                            <AlertCircle size={32} className="mb-3 opacity-80" />
                            <span className="text-sm">Scan Failed</span>
                            <span className="text-xs opacity-70 mt-1">{error}</span>
                        </div>
                    ) : hasRun ? (
                        smells.length === 0 ? (
                            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex-1 flex flex-col items-center justify-center text-cyber-success font-mono text-center">
                                <ShieldAlert size={48} className="mb-4 opacity-50" />
                                <span className="text-lg tracking-widest uppercase">Pure Code</span>
                                <span className="text-xs text-gray-400 mt-2">Zero architectural smells detected in selection.</span>
                            </motion.div>
                        ) : (
                            <div className="space-y-4">
                                {smells.map((s, i) => {
                                    const pct = Math.round(s.confidence * 100);
                                    const isHighRisk = pct > 75;
                                    return (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                                            className="glass-panel p-4 bg-white/[0.02] border border-white/10 hover:border-cyber-primary/50 transition-colors"
                                        >
                                            <div className="flex justify-between items-start mb-3">
                                                <div className="font-medium text-sm text-white">{s.display_name}</div>
                                                <div className="font-mono text-xs px-2 py-0.5 rounded bg-black/50 border border-white/10 text-gray-400">Line {s.start_line}</div>
                                            </div>

                                            <div className="w-full h-1.5 bg-black/50 rounded-full overflow-hidden relative">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${pct}%` }}
                                                    transition={{ duration: 1, ease: "easeOut" }}
                                                    className={clsx("absolute top-0 left-0 h-full", isHighRisk ? "bg-cyber-danger shadow-[0_0_10px_#ff003c]" : "bg-cyber-warning text-cyber-warning")}
                                                />
                                            </div>
                                            <div className="flex justify-between items-center mt-2 font-mono text-[10px] uppercase tracking-wider">
                                                <span className="text-gray-500">Confidence</span>
                                                <span className={clsx(isHighRisk ? "text-cyber-danger" : "text-cyber-warning")}>{pct}%</span>
                                            </div>
                                        </motion.div>
                                    )
                                })}
                            </div>
                        )
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-gray-600 font-mono text-center">
                            <Code2 size={48} className="mb-4 opacity-20" />
                            <span className="text-xs uppercase tracking-widest">Awaiting Input</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
