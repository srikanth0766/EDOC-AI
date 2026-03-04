import React from 'react';
import { motion } from 'framer-motion';
import { History, CheckCircle2, AlertCircle, FileCode2 } from 'lucide-react';

export default function ActivityFeed() {
    const activities = [
        { id: 1, type: 'scan', desc: 'Analyzed auth_service.py', time: '2m ago', risk: 'low', icon: FileCode2 },
        { id: 2, type: 'alert', desc: 'God Class detected in router.js', time: '14m ago', risk: 'high', icon: AlertCircle },
        { id: 3, type: 'refactor', desc: 'Auto-refactored utils.py', time: '1h ago', risk: 'success', icon: CheckCircle2 },
        { id: 4, type: 'scan', desc: 'Analyzed main.py (0 smells)', time: '3h ago', risk: 'low', icon: FileCode2 },
    ];

    return (
        <div className="glass-panel h-full flex flex-col border-t-white/10 border-l-white/10">
            <div className="p-6 border-b border-white/5">
                <h2 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
                    Action Log
                </h2>
                <div className="text-xs text-gray-400 font-mono tracking-widest mt-1 uppercase">Recent System Events</div>
            </div>

            <div className="flex-1 p-6 overflow-y-auto">
                <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-white/10 before:to-transparent">
                    {activities.map((item, i) => {
                        let colorClass = 'text-cyber-primary border-cyber-primary bg-cyber-primary/10';
                        if (item.risk === 'high') colorClass = 'text-cyber-danger border-cyber-danger bg-cyber-danger/10';
                        if (item.risk === 'success') colorClass = 'text-cyber-success border-cyber-success bg-cyber-success/10';

                        return (
                            <motion.div
                                key={item.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.15 }}
                                className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active"
                            >
                                {/* Icon */}
                                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 bg-cyber-900 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm z-10 ${colorClass}`}>
                                    <item.icon size={16} />
                                </div>

                                {/* Content */}
                                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-white/5 bg-black/20 group-hover:bg-white/[0.02] transition-colors">
                                    <div className="flex items-center justify-between mb-1">
                                        <div className="font-bold text-white text-sm">{item.desc}</div>
                                    </div>
                                    <div className="text-xs font-mono text-gray-500 uppercase">{item.time}</div>
                                </div>
                            </motion.div>
                        )
                    })}
                </div>
            </div>
        </div>
    );
}
