import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import SprintTable from '../components/SprintTable';
import { History } from 'lucide-react';

const BACKEND = 'http://localhost:8000';

export default function HistoryPage() {
    const [sprints, setSprints] = useState([]);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const res = await fetch(`${BACKEND}/sprint-analytics`);
            if (res.ok) {
                const data = await res.json();
                setSprints(data.sprints);
            }
        } catch (e) {
            setSprints([
                { sprint_id: 'Sprint-1', smell_count: 5, refactor_count: 2, module: 'demo' },
                { sprint_id: 'Sprint-2', smell_count: 12, refactor_count: 6, module: 'demo' },
                { sprint_id: 'Sprint-3', smell_count: 15, refactor_count: 10, module: 'demo' },
            ]);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex flex-col gap-8 pb-24 h-full"
        >
            <div className="flex items-center gap-4 border-b border-white/5 pb-6">
                <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-gray-300">
                    <History size={32} />
                </div>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white drop-shadow-md">
                        Sprint History
                    </h1>
                    <p className="text-sm text-gray-400 font-mono mt-1">
                        Historical logging of codebase evolution and technical debt trajectory.
                    </p>
                </div>
            </div>

            <div className="flex-1 min-h-[500px]">
                <SprintTable sprints={sprints} onRefresh={fetchData} />
            </div>
        </motion.div>
    );
}
