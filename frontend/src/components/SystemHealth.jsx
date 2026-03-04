import React from 'react';
import { motion } from 'framer-motion';
import { Activity, ServerCrash, Zap, Database, Cpu } from 'lucide-react';
import Tilt from 'react-parallax-tilt';

export default function SystemHealth() {
    const metrics = [
        { id: 1, label: 'CPU Load', value: '14%', status: 'optimal', icon: Cpu },
        { id: 2, label: 'Memory', value: '2.1 GB', status: 'optimal', icon: Database },
        { id: 3, label: 'API Uptime', value: '99.9%', status: 'optimal', icon: Zap },
        { id: 4, label: 'Error Rate', value: '0.01%', status: 'warning', icon: ServerCrash },
    ];

    return (
        <Tilt
            tiltMaxAngleX={5}
            tiltMaxAngleY={5}
            perspective={1000}
            scale={1.01}
            transitionSpeed={1500}
            className="h-full"
        >
            <div className="glass-panel h-full flex flex-col border-t-white/10 border-l-white/10">
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
                            System Telemetry
                        </h2>
                        <div className="text-xs text-gray-400 font-mono tracking-widest mt-1 uppercase">Live Instance Health</div>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-cyber-success animate-pulse shadow-neon-success" />
                        <span className="text-xs font-mono text-cyber-success uppercase tracking-widest">Active</span>
                    </div>
                </div>

                <div className="p-6 grid grid-cols-2 gap-4 flex-1">
                    {metrics.map((m, i) => (
                        <motion.div
                            key={m.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: i * 0.1 }}
                            className="bg-black/20 border border-white/5 rounded-xl p-4 flex flex-col justify-between group hover:bg-white/5 transition-colors"
                        >
                            <div className="flex justify-between items-start mb-2">
                                <m.icon size={16} className="text-gray-500 group-hover:text-cyber-primary transition-colors" />
                                <div className={`w-1.5 h-1.5 rounded-full ${m.status === 'optimal' ? 'bg-cyber-success shadow-neon-success' : 'bg-cyber-warning shadow-neon-secondary'}`} />
                            </div>
                            <div>
                                <div className="text-2xl font-mono font-bold text-white">{m.value}</div>
                                <div className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">{m.label}</div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </Tilt>
    );
}
