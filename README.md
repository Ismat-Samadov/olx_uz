# 🫧 Bubble Shooter — Neon Edition

A full-featured, browser-based bubble-shooter game built with **Next.js 15**, **TypeScript**, and **Tailwind CSS**. Styled in a **neon cyberpunk** aesthetic with glowing bubbles, particle explosions, and procedural sound effects — no external assets required.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Three difficulty levels** | Easy (3 colours), Medium (4 colours), Hard (6 colours) |
| **Hex grid** | Classic staggered honeycomb layout |
| **Aim guide** | Dotted neon line with wall reflections |
| **Cluster matching** | BFS flood-fill — pop 3+ same-colour bubbles |
| **Floating bubble physics** | Disconnected bubbles fall off screen with animation |
| **Particle effects** | Per-bubble particle burst on pop |
| **Procedural sounds** | Web Audio API — no audio files needed |
| **High-score persistence** | Per-difficulty, saved in `localStorage` |
| **Pause / resume** | Button or keyboard shortcut |
| **Keyboard controls** | Full desktop keyboard support |
| **Touch controls** | Drag-to-aim + tap-to-shoot on mobile |
| **On-screen buttons** | Aim-left / Shoot / Aim-right for mobile |
| **Fully responsive** | Adapts bubble size to screen width |
| **Neon favicon** | Custom SVG favicon matching the theme |

---

## 🕹 Controls

### Desktop
| Action | Input |
|---|---|
| Aim | Move mouse over canvas |
| Shoot | Click anywhere on canvas or `Space` |
| Pause / Resume | `P` or `Escape` |
| Mute / Unmute | `M` |

### Mobile / Touch
| Action | Input |
|---|---|
| Aim | Drag finger across canvas |
| Shoot | Tap canvas or tap **🎯** button |
| Aim incrementally | Hold **◀** / **▶** buttons |

---

## 🗂 Project Structure

```
src/
├── app/
│   ├── globals.css        # Global reset + neon base styles
│   ├── layout.tsx         # Root layout with metadata & viewport
│   └── page.tsx           # Mounts the full-screen game
├── components/
│   ├── BubbleShooterGame.tsx  # Canvas game loop, rendering, input
│   ├── StartScreen.tsx        # Difficulty selection splash
│   ├── EndScreen.tsx          # Win / Game-over overlay
│   └── PauseMenu.tsx          # Pause overlay
├── hooks/
│   ├── useSound.ts            # Mute toggle + sound dispatchers
│   └── useHighScore.ts        # localStorage high-score per difficulty
├── lib/
│   ├── colors.ts              # Neon colour palette
│   ├── grid.ts                # Hex grid layout, snap-to-grid, adjacency
│   ├── matching.ts            # Cluster BFS, floating-bubble detection
│   ├── physics.ts             # Projectile movement, wall bounce, aim guide
│   └── sounds.ts              # Web Audio API procedural sounds
└── types/
    └── game.ts                # All TypeScript types & interfaces
```

---

## 🚀 Running Locally

**Prerequisites:** Node.js 18+ and npm.

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd bubble_shooter

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## ☁️ Deploy to Vercel

The project is **zero-config** for Vercel.

```bash
# Option A — Vercel CLI
npm i -g vercel
vercel

# Option B — GitHub integration
# Push to GitHub → Import project at https://vercel.com/new
# Vercel auto-detects Next.js and deploys with default settings.
```

No environment variables are required.

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| [Next.js 15](https://nextjs.org/) (App Router) | Framework & routing |
| [TypeScript](https://www.typescriptlang.org/) strict | Type safety |
| [Tailwind CSS v4](https://tailwindcss.com/) | UI styling |
| [Framer Motion](https://www.framer-motion.com/) | Screen transition animations |
| HTML5 Canvas 2D | Game rendering |
| Web Audio API | Procedural sound effects |
| `localStorage` | High-score persistence |

---

## 🎮 Gameplay

1. Select a difficulty on the start screen.
2. Aim the cannon (bottom centre) with your mouse or finger.
3. Click / tap to shoot a coloured bubble.
4. Match **3 or more** same-colour bubbles to pop them.
5. Bubbles disconnected from the ceiling **fall off** for bonus points.
6. Every N shots (difficulty-dependent) a new row is added at the top.
7. **Game over** when any bubble crosses the red danger line.
8. **Win** by clearing the entire grid.

---

## 📜 License

MIT — free to use and modify.
