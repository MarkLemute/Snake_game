# Snake Game

**Version 1.0** · A beginner-friendly Pygame project and visual design roadmap

This repository contains a simple Snake game written in Python with Pygame. It is intentionally small so you can understand the code, experiment with the graphics, and improve the game step by step.

The rest of this README is both a project guide and a design roadmap. It explains the current codebase, suggests visual improvements, and provides learning material for each stage.

## Quick start

### Requirements

- Python 3.10 or newer
- Pygame 2.6.1

### Install and run

```bash
git clone https://github.com/MarkLemute/snake-game.git
cd snake-game
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install the dependency and start the game:

```bash
python -m pip install -r requirements.txt
python snake_game.py
```

### Controls

- Arrow keys: change direction
- Space: restart after game over
- Close the game window: quit

## Project structure

| File | Purpose |
| --- | --- |
| `snake_game.py` | Game window, input handling, game rules, drawing, and main loop |
| `requirements.txt` | Pinned Python dependency |
| `README.md` | Setup instructions, learning path, and design roadmap |

### How the code works

1. `pygame.init()` starts Pygame.
2. `SnakeGame.__init__()` creates the window, clock, font, and initial state.
3. `reset_game()` creates the snake, direction, food, score, and game-over state.
4. `handle_events()` reads keyboard and window events.
5. `update()` moves the snake, checks food, and detects collisions.
6. `draw()` renders the snake, food, score, and game-over message.
7. `run()` repeats the event, update, draw, and clock steps.

When you begin redesigning the graphics, keep the game rules in `update()` and make most visual changes inside `draw()`. This separation makes experimentation safer.

---

## Learning materials

Use these in order. Start with the official documentation, then use the design references when you are ready to change the look and feel.

### Python foundations

- [Python official tutorial](https://docs.python.org/3/tutorial/) — variables, functions, classes, loops, and modules
- [Python standard library: `collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque) — the data structure used for the snake body
- [Python `Enum` documentation](https://docs.python.org/3/library/enum.html) — how the direction values work

### Pygame and game programming

- [Pygame official documentation](https://www.pygame.org/docs/) — the complete API reference
- [Pygame getting started](https://www.pygame.org/wiki/GettingStarted) — installation and first-project guidance
- [Pygame examples](https://github.com/pygame/pygame/tree/main/examples) — small examples for drawing, input, fonts, and animation
- [Real Python: Pygame tutorials](https://realpython.com/tutorials/pygame/) — beginner-friendly explanations and projects

### Graphics and visual design

- [Pygame drawing reference](https://www.pygame.org/docs/ref/draw.html) — rectangles, circles, lines, and rounded shapes
- [Pygame Surface reference](https://www.pygame.org/docs/ref/surface.html) — surfaces, transparency, and compositing
- [Lospec Pixel Art tutorials](https://lospec.com/pixel-art-tutorials) — palettes, pixel-art shapes, and shading
- [OpenGameArt](https://opengameart.org/) — reusable art references and assets; check each asset's license before using it
- [Kenney assets](https://kenney.nl/assets) — free game assets with clear licensing information

### Game feel and design

- [The 12 principles of animation](https://www.youtube.com/watch?v=uDqjIdI4bF4) — timing, anticipation, squash, stretch, and follow-through
- [Game accessibility guidelines](https://gameaccessibilityguidelines.com/) — readable contrast, controls, and player-friendly design
- Steve Swink, *Game Feel* — a useful book about responsiveness, motion, and feedback
- Jesse Schell, *The Art of Game Design* — a broad introduction to designing engaging games

Do not download random “free PDF” copies of books. Use official publishers, libraries, or legitimate ebook stores. Web documentation is usually more useful than a PDF because it stays updated.

---

## How to export this guide to PDF

If you want a PDF version for personal reference:

1. Open [README.md](C:/Users/chuko/my%20projects/snake%20game/README.md) in VS Code
2. Use the print option or export as PDF
3. Or copy the content into Microsoft Word and save as PDF

This keeps the project readable and portable while still being versioned in GitHub.

---

## 1. Design direction

Think of your game as a small arcade experience with a clean and modern identity.

### Recommended visual style
- Minimal but stylish
- Strong contrast between background, snake, and food
- Clean grid layout with a bit of personality
- Bright accent colors that stand out on dark backgrounds

A strong look usually comes from a few key choices:
- dark background
- neon or saturated snake colors
- soft shadows and highlights
- simple but readable UI text

---

## 2. Make the snake look better

Right now, the snake is a basic green block. That works, but it can feel much more alive with a few visual upgrades.

### A. Give the snake a head and body identity
Use different visuals for:
- head
- neck/body segment
- tail tip
- turning segments

A simple improvement is to make the head slightly brighter and more rounded, while the body is a bit darker and more uniform.

### B. Use rounded rectangles instead of sharp blocks
Instead of simple square tiles, try:
- rounded corners
- slightly larger rectangles
- body segments with a little spacing between them

This makes the snake feel more organic and less like a rigid blocky line.

### C. Add a sense of motion
Even if the snake still moves grid-by-grid, you can fake smooth motion with:
- a slightly different shade on the head
- a small eyes/face on the head
- subtle shadow behind the head
- body segments that appear a bit offset to create a flowing shape

### D. Give the snake personality
Good arcade snakes often look like they have a direction and attitude. You can make this happen by:
- giving the head a face
- making the head glow slightly
- changing color based on theme or score

A snake that feels alive becomes much more memorable.

---

## 3. Improve how the snake moves

Movement is where the feel of the game is really decided.

### A. Use smoother movement, not just instant tile switches
The game currently updates in discrete steps. That is okay for a classic snake game, but you can make it feel better by using interpolation.

Instead of moving only from one grid cell to the next, you can:
- move the snake in small sub-steps between cells
- animate the head turning before the body fully follows
- let the body update in a more flowing way

This is one of the best ways to make the game feel more premium.

### B. Add turn animation
If the player changes direction while the snake is moving, it should not feel like a sudden snap.

Good effect:
- head rotates slightly toward next direction
- body segments curve instead of staying rigid
- tail slides behind the movement

### C. Keep the motion consistent
Avoid making the snake feel jittery. Small things matter:
- same speed throughout the game
- no weird jumps when turning
- body should follow head smoothly

A stable movement rhythm makes the game feel intentionally designed.

---

## 4. Better level and background design

The background is important because it supports the snake without stealing attention.

### Great background ideas
- dark gradient background
- subtle tile pattern
- soft grid lines
- light glow around food
- faint visual echo of movement

### Avoid clutter
Do not overdo the background. The snake should remain the hero of the screen.

A simple environment with a strong foreground object is usually more effective than a busy one.

---

## 5. Food should feel rewarding

Food should not just be a red square. It should feel like a pickup.

### Good food ideas
- circular food with highlight
- glow effect
- slight pulse animation
- tiny particles when eaten
- different food colors for variety

### Visual principle
The food should always be easy to see and easy to understand. It must feel like a target and reward.

---

## 6. Add small moments of polish

These are the things that make a game feel “finished”.

### Examples
- screen shake when the snake eats
- brief flash when you crash
- subtle score pop-up
- a little trail behind the head
- animated game-over card
- pause menu or start screen

Even tiny effects can add a lot of character.

---

## 7. Sound can make a huge difference

Sound design is often overlooked, but a snake game benefits a lot from it.

### Good sound ideas
- short chomp sound for food pickup
- soft movement sound for snake motion
- slight fail sound for collision
- clean UI click sounds for menu actions

Keep the sound simple and pleasant. The goal is not loudness, but clarity and punch.

---

## 8. Smart UI design

The score should feel integrated into the game, not bolted on.

### Good UI choices
- score on the top-left or top-center
- compact and readable font
- mild shadows for text readability
- game-over overlay with a clean message
- restart prompt that is easy to understand

A good UI is easy to read at a glance.

---

## 9. Use a visual hierarchy

Your game should tell the player what matters first.

### Priority order
1. Snake
2. Food
3. Score/UI
4. Background

If the background is too strong, the snake loses focus. If the snake is too loud, the gameplay becomes confusing. Balance is everything.

---

## 10. A simple upgrade path for your game

If you want to improve the game step by step, follow this order:

### Phase 1 – Visual clarity
- rounded snake segments
- distinct head and body colors
- better food design
- cleaner background

### Phase 2 – Movement feel
- smoother transitions between tiles
- head direction animation
- body trailing motion

### Phase 3 – Polish
- score effects
- game-over overlay
- sound effects
- start screen

### Phase 4 – Features
- difficulty levels
- obstacles
- power-ups
- high score save
- modern menu system

---

## 11. Keep the game readable

Even if the graphics improve, gameplay must always stay easy to understand.

Good arcade design means:
- snake is always visible
- food stands out clearly
- screen never feels crowded
- actions are obvious

Players should instantly understand the game without confusion.

---

## 12. Final design advice

The best versions of this game almost always come from small and consistent upgrades.

Focus on:
- a clearer snake silhouette
- smoother body motion
- better food feedback
- stronger contrast and polish

Do not try to add too much at once. Build the game around a clean visual identity and improve it gradually.

A snake game becomes exciting when the snake feels alive, the food feels rewarding, and the screen feels polished without becoming chaotic.

## Publishing this project on GitHub

The intended public repository is:

`https://github.com/MarkLemute/snake-game`

Create that repository as **Public**, without adding a second README or `.gitignore`, then run:

```bash
git remote -v
git push -u origin main
```

GitHub will ask you to authenticate. Use GitHub's browser sign-in, Git Credential Manager, or a fine-grained personal access token created in your own GitHub account. Never paste a password or token into chat or commit one to this project.

## Version history

### Version 1.0

- Added the playable Pygame Snake game
- Added dependency setup through `requirements.txt`
- Added beginner-friendly codebase documentation
- Added a visual design and improvement roadmap
- Added learning resources for Python, Pygame, graphics, and game feel

---

## 13. Quick checklist before you call it “finished”

- Does the snake look distinct from the background?
- Does the head look readable and intentional?
- Does movement feel smooth and consistent?
- Does the food stand out clearly?
- Is the score easy to read?
- Does the game-over state feel polished?
- Does the game feel fun without being too busy?

If you can answer “yes” to most of these, your game is already much stronger.

---

## 14. Recommended next move

Your next improvement should be the snake itself.

Start by changing:
- head look
- body segmentation
- movement flow
- food appearance

Then move to sound and polish.

That is the best order because the core visual identity of the game matters most.
