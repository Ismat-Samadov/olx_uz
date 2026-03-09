'use client';

// ============================================================
// PauseMenu — semi-transparent overlay when game is paused
// ============================================================

import { motion, AnimatePresence } from 'framer-motion';

interface Props {
  visible: boolean;
  onResume: () => void;
  onMenu: () => void;
}

export default function PauseMenu({ visible, onResume, onMenu }: Props) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          key="pause"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 flex flex-col items-center justify-center bg-[#07071a]/80 z-20 select-none"
        >
          <motion.div
            initial={{ scale: 0.85, opacity: 0 }}
            animate={{ scale: 1,    opacity: 1 }}
            exit={{ scale: 0.85,    opacity: 0 }}
            className="bg-white/5 border border-white/10 rounded-2xl p-10 flex flex-col items-center gap-6 shadow-2xl"
          >
            <h2 className="text-3xl font-extrabold text-white tracking-widest uppercase">Paused</h2>

            <button
              onClick={onResume}
              className="w-44 py-3 rounded-xl border-2 border-cyan-500 text-cyan-400 font-bold tracking-widest uppercase hover:bg-cyan-500/20 transition-colors shadow-lg shadow-cyan-500/30"
            >
              Resume
            </button>
            <button
              onClick={onMenu}
              className="w-44 py-3 rounded-xl border-2 border-slate-600 text-slate-400 font-bold tracking-widest uppercase hover:bg-white/5 transition-colors"
            >
              Main Menu
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
