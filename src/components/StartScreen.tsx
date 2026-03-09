'use client';

// ============================================================
// StartScreen — difficulty selection splash
// ============================================================

import { motion } from 'framer-motion';
import { Difficulty } from '@/types/game';
import { DIFFICULTY_SETTINGS } from '@/lib/grid';

interface Props {
  onStart: (difficulty: Difficulty) => void;
}

const DIFFICULTIES: Difficulty[] = ['easy', 'medium', 'hard'];

const DIFF_STYLES: Record<Difficulty, string> = {
  easy:   'border-green-500 text-green-400 hover:bg-green-500/20 shadow-green-500/30',
  medium: 'border-yellow-500 text-yellow-400 hover:bg-yellow-500/20 shadow-yellow-500/30',
  hard:   'border-red-500 text-red-400 hover:bg-red-500/20 shadow-red-500/30',
};

export default function StartScreen({ onStart }: Props) {
  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#07071a]/90 z-20 select-none">
      {/* Title */}
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, type: 'spring' }}
        className="mb-2 text-center"
      >
        <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 drop-shadow-lg">
          BUBBLE
        </h1>
        <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-pink-400 via-purple-400 to-cyan-400 drop-shadow-lg">
          SHOOTER
        </h1>
      </motion.div>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="text-slate-400 text-sm sm:text-base mb-10 tracking-widest uppercase"
      >
        Neon Edition
      </motion.p>

      {/* Difficulty buttons */}
      <motion.div
        initial={{ y: 40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.5 }}
        className="flex flex-col gap-4 w-56 sm:w-64"
      >
        {DIFFICULTIES.map(diff => {
          const s = DIFFICULTY_SETTINGS[diff];
          return (
            <motion.button
              key={diff}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onStart(diff)}
              className={`py-3 rounded-xl border-2 font-bold tracking-widest uppercase text-base shadow-lg transition-colors duration-150 ${DIFF_STYLES[diff]}`}
            >
              {s.label}
              <span className="block text-xs font-normal mt-0.5 opacity-70">
                {s.colors.length} colours · {s.shotsPerDescend} shots / row
              </span>
            </motion.button>
          );
        })}
      </motion.div>

      {/* Controls hint */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9 }}
        className="mt-10 text-center text-slate-500 text-xs sm:text-sm space-y-1"
      >
        <p>🖱 Move mouse to aim · Click to shoot</p>
        <p>📱 Drag to aim · Tap to shoot</p>
        <p>⌨ P to pause · M to mute</p>
      </motion.div>
    </div>
  );
}
