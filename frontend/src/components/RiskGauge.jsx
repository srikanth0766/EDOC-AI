import React from 'react';
import Tilt from 'react-parallax-tilt';
import { ShieldAlert, TrendingUp, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function RiskGauge({ risk }) {
    const prob = risk?.risk_probability || 0;
    const pct = Math.round(prob * 100);

    // Decide color based on risk
    let color = '#22c55e'; // cyber-success
    let Icon = ShieldCheck;
    let shadow = 'shadow-neon-success';
    if (prob > 0.7) {
        color = '#ff003c'; // cyber-danger
        Icon = ShieldAlert;
        shadow = 'shadow-[0_0_15px_rgba(255,0,60,0.6)]';
    } else if (prob > 0.4) {
        color = '#ffb703'; // cyber-warning
        Icon = AlertTriangle;
        shadow = 'shadow-[0_0_15px_rgba(255,183,3,0.6)]';
    }

    // SVG Gauge Calculations
    const radius = 60;
    const circumference = 2 * Math.PI * radius;
    // We want a 270 degree arc (0.75 of circle)
    const arcLength = 0.75 * circumference;
    const strokeDashoffset = arcLength - (prob * arcLength);

    return (
        <Tilt
            tiltMaxAngleX={5}
            tiltMaxAngleY={5}
            perspective={800}
            scale={1.01}
            transitionSpeed={1500}
            className="h-full"
        >
            <div className="glass-panel h-full flex flex-col border-t-white/10 border-l-white/10">
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-bold text-white tracking-wide">Predictive Risk</h2>
                        <div className="text-xs text-gray-400 font-mono tracking-widest mt-1 uppercase">Next Sprint Forecast</div>
                    </div>
                    <div className={`p-2 rounded-lg bg-cyber-900/50 border border-white/10 ${shadow}`}>
                        <Icon size={20} color={color} />
                    </div>
                </div>

                <div className="p-6 flex-1 flex flex-col relative overflow-hidden">
                    {/* Background glow for the gauge */}
                    <div
                        className="absolute inset-x-0 top-10 h-32 blur-[60px] opacity-30 rounded-full"
                        style={{ backgroundColor: color }}
                    />

                    <div className="relative flex justify-center items-center py-4">
                        <svg className="w-48 h-48 transform -rotate-135" viewBox="0 0 160 160">
                            {/* Background Arc */}
                            <circle
                                cx="80" cy="80" r={radius}
                                fill="transparent"
                                stroke="rgba(255,255,255,0.05)"
                                strokeWidth="12"
                                strokeDasharray={`${arcLength} ${circumference}`}
                                strokeLinecap="round"
                            />
                            {/* Foreground Arc */}
                            <circle
                                cx="80" cy="80" r={radius}
                                fill="transparent"
                                stroke={color}
                                strokeWidth="12"
                                strokeDasharray={`${arcLength} ${circumference}`}
                                strokeDashoffset={strokeDashoffset}
                                strokeLinecap="round"
                                className="transition-all duration-1000 ease-out"
                                style={{ filter: `drop-shadow(0 0 8px ${color})` }}
                            />
                        </svg>
                        {/* Center Text */}
                        <div className="absolute flex flex-col items-center top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 mt-4">
                            <span className="text-4xl font-bold font-mono" style={{ color }}>{pct}%</span>
                            <span className="text-xs text-gray-400 uppercase tracking-widest mt-1">Probability</span>
                        </div>
                    </div>

                    <div className="mt-auto space-y-4 relative z-10 glass-panel p-4 rounded-xl border border-white/5 bg-black/20">
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Predicted Smells</span>
                            <span className="font-mono text-white">{Math.round(risk?.predicted_smell_count || 0)}</span>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Threshold Limit</span>
                            <span className="font-mono text-cyber-accent">{risk?.threshold || 10}</span>
                        </div>
                        <div className="pt-3 border-t border-white/5 text-xs text-gray-300 leading-relaxed font-mono">
                            {risk?.recommendation || "Syncing with stochastic model..."}
                        </div>
                    </div>
                </div>
            </div>
        </Tilt>
    );
}
