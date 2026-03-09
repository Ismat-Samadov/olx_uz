'use client';

// ============================================================
// EndScreen — win / game-over overlay with score summary
// ============================================================

import { motion } from 'framer-motion';
import { Difficulty, GamePhase } from '@/types/game';
import { DIFFICULTY_SETTINGS } from '@/lib/grid';

interface Props {
  phase: GamePhase;
  score: number;
  highScore: number;
  difficulty: Difficulty;
  onRestart: () => void;
  onMenu: () => void;
}

export default function EndScreen({ phase, score, highScore, difficulty, onRestart, onMenu }: Props) {
  const won       = phase === 'won';
  const isNewBest = score > 0 && score >= highScore;

  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#07071a]/92 z-20 select-none">
      {/* Banner */}
      <motion.div
        initial={{ scale: 0.4, opacity: 0 }}
        animate={{ scale: 1,   opacity: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 18 }}
        className="mb-6 text-center"
      >
        {won ? (
          <>
            <div className="text-6xl mb-2">🏆</div>
            <h2 className="text-4xl sm:text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-yellow-300 to-orange-400">
              YOU WIN!
            </h2>
          </>
        ) : (
          <>
            <div className="text-6xl mb-2">💥</div>
            <h2 className="text-4xl sm:text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-red-400 to-pink-500">
              GAME OVER
            </h2>
          </>
        )}
      </motion.div>

      {/* Score card */}
      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0,  opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-white/5 border border-white/10 rounded-2xl px-10 py-6 mb-8 text-center space-y-2 shadow-xl"
      >
        <p className="text-slate-400 text-sm uppercase tracking-widest">
          {DIFFICULTY_SETTINGS[difficulty].label} mode
        </p>
        <p className="text-4xl font-bold text-white">{score.toLocaleString()}</p>
        {isNewBest && (
          <p className="text-yellow-400 text-sm font-semibold animate-pulse">⭐ New High Score!</p>
        )}
        {!isNewBest && (
          <p className="text-slate-500 text-sm">Best: {highScore.toLocaleString()}</p>
        )}
      </motion.div>

      {/* Action buttons */}
      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0,  opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="flex flex-col gap-3 w-48"
      >
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.97 }}
          onClick={onRestart}
          className="py-3 rounded-xl border-2 border-cyan-500 text-cyan-400 font-bold tracking-widest uppercase shadow-lg shadow-cyan-500/30 hover:bg-cyan-500/20 transition-colors"
        >
          Play Again
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.97 }}
          onClick={onMenu}
          className="py-3 rounded-xl border-2 border-slate-600 text-slate-400 font-bold tracking-widest uppercase hover:bg-white/5 transition-colors"
        >
          Main Menu
        </motion.button>
      </motion.div>
    </div>
  );
}
