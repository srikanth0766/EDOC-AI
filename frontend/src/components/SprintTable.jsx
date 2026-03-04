import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Archive, ServerCrash } from 'lucide-react';

export default function SprintTable({ sprints, onRefresh }) {
    return (
        <div className="glass-panel h-full flex flex-col border-t-white/10 border-l-white/10">
            <div className="p-6 border-b border-white/5 flex justify-between items-center">
                <div>
                    <h2 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
                        Sprint Manifest
                    </h2>
                    <div className="text-xs text-gray-400 font-mono tracking-widest mt-1 uppercase">Historical Debt Trajectory</div>
                </div>
                <button
                    onClick={onRefresh}
                    className="cyber-button text-xs py-2 px-4 flex items-center gap-2"
                >
                    <Activity size={14} /> Synchronize
                </button>
            </div>

            <div className="flex-1 p-0 overflow-hidden relative">
                <div className="absolute inset-0 overflow-auto">
                    <table className="w-full text-left border-collapse">
                        <thead className="sticky top-0 bg-cyber-900/90 backdrop-blur-md z-10 text-xs uppercase tracking-widest text-gray-400 font-mono border-b border-white/5">
                            <tr>
                                <th className="py-4 px-6 font-medium">Sprint ID</th>
                                <th className="py-4 px-6 font-medium">Detected</th>
                                <th className="py-4 px-6 font-medium">Refactored</th>
                                <th className="py-4 px-6 font-medium">Net Debt</th>
                                <th className="py-4 px-6 font-medium text-center">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 font-mono text-sm">
                            {sprints.length === 0 ? (
                                <tr><td colSpan="5" className="text-center py-12 text-gray-500">No sprint data found. Awaiting telemetry.</td></tr>
                            ) : (
                                sprints.map((s, i) => {
                                    const net = s.smell_count - s.refactor_count;
                                    const isDanger = net > 15;
                                    const isWarn = net > 8 && !isDanger;

                                    return (
                                        <motion.tr
                                            key={s.sprint_id}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: i * 0.05 }}
                                            className="group hover:bg-white/[0.02] transition-colors cursor-default"
                                        >
                                            <td className="py-4 px-6 text-white group-hover:text-cyber-primary transition-colors flex items-center gap-3">
                                                <Archive size={14} className="text-gray-500 group-hover:text-cyber-primary" />
                                                {s.sprint_id}
                                            </td>
                                            <td className="py-4 px-6 text-gray-300">{s.smell_count}</td>
                                            <td className="py-4 px-6 text-cyber-success">{s.refactor_count}</td>
                                            <td className={`py-4 px-6 ${isDanger ? 'text-cyber-danger' : isWarn ? 'text-cyber-warning' : 'text-gray-400'}`}>
                                                {net > 0 ? '+' : ''}{net}
                                            </td>
                                            <td className="py-4 px-6 flex justify-center">
                                                <div className={`w-2 h-2 rounded-full ${isDanger ? 'bg-cyber-danger shadow-neon-primary' : isWarn ? 'bg-cyber-warning' : 'bg-cyber-success'}`} />
                                            </td>
                                        </motion.tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
