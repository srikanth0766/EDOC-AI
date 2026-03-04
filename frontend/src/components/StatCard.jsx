import React from 'react';
import Tilt from 'react-parallax-tilt';

export default function StatCard({ title, value, icon, isString }) {
    return (
        <Tilt
            tiltMaxAngleX={10}
            tiltMaxAngleY={10}
            perspective={1000}
            scale={1.02}
            transitionSpeed={1000}
            className="h-full"
        >
            <div className="glass-panel h-full p-6 flex items-center gap-5 group border-t-white/10 border-l-white/10">
                <div className="glass-panel-content flex items-center gap-5 w-full">
                    <div className="p-4 rounded-xl bg-white/5 border border-white/10 group-hover:bg-white/10 transition-colors shadow-inner">
                        {icon}
                    </div>
                    <div>
                        <div className="text-sm font-mono text-gray-400 uppercase tracking-wider mb-1">{title}</div>
                        <div className={`text-3xl font-bold tracking-tight capitalize ${isString ? 'text-xl' : ''}`}>
                            <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                                {value}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </Tilt>
    );
}
