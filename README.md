# Pygame Hide and Seek Game

A fun two-player hide and seek game built with Python and Pygame where Tom (you) competes against Spike (computer) to find Jerry first!

## Game Features

- **Two Game Modes**:
  - **Player vs Computer**: Tom (human) vs Spike (AI)
  - **Player vs Player**: Tom (Player 1) vs Spike (Player 2)
- **Dynamic Hiding**: Jerry hides in random locations each game
- **Move Target Button**: Each player can move Jerry once per game to a new location
- **Visual Feedback**: Hot/Cold system with visual indicators
- **Distance Display**: Shows steps to Jerry for both players
- **Sound Effects**: Background music and game sounds
- **A* Pathfinding**: Smart AI movement for Spike
- **Enhanced Computer AI**: Computer can use Move Target button and considers both players' positions
- **Beautiful Graphics**: Custom sprites and animations
- **Next Round Button**: Quick restart without returning to menu
- **Block Placement**: Each player can place one block per game to block the opponent's path. Blocks can be placed horizontally or vertically (press **'R'** to rotate).
- **Surprise Gift Box**: A surprise gift box appears on the board. Collecting it will **freeze your opponent for 2 turns**!

## Installation

### Prerequisites

- Python 3.12 (already installed on your system)

### Setup Instructions

1. **Install Dependencies**

   ```bash
   # Run the installation script
   .\install_pip.bat
   ```

2. **Run the Game**

   ```bash
   # Use the launcher script
   .\run_game.bat
   ```

   Or run directly:

   ```bash
   "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" hide_seek_game.py
   ```

## How to Play

1. **Start Screen**: Choose your game mode:

   - **Player vs Computer**: Tom (You) vs Spike (Computer)
   - **Player vs Player**: Tom (Player 1) vs Spike (Player 2)

2. **Gameplay**:

   - **Player vs Computer**: Use arrow keys to move Tom, find Jerry before Spike does
   - **Player vs Player**:
     - Player 1 (Tom): Use arrow keys
     - Player 2 (Spike): Use WASD keys
   - Find Jerry before your opponent does
   - **Block your opponent's movement**: Each player can place one block per game to block the opponent's path. Click the "Place Block" button, then click on the grid. Press **'R'** to rotate the block between horizontal and vertical.
   - Visual feedback shows how close you are to Jerry
   - **Move Target**: Each player can click the "Move Target" button once per game to move Jerry to a new location
   - **Surprise Gift Box**: Collect the gift box to **freeze your opponent for 2 turns**. The frozen player will skip their next two turns.
   - **Computer AI**: In Player vs Computer mode, the computer can strategically use the Move Target button, place blocks, and considers both players' positions when making decisions

3. **Distance Display**:

   - Shows "Tom→Jerry: X steps" and "Spike→Jerry: Y steps"
   - Both players can see how far each is from Jerry
   - Updates immediately when Jerry is moved to a new location

4. **Feedback System**:

   - 🔥 **Burning Hot**: Very close (≤2 steps)
   - 🔥 **Hot**: Close (≤4 steps)
   - 🌡️ **Warm**: Getting closer (≤6 steps)
   - ❄️ **Cool**: Some distance (≤10 steps)
   - ❄️ **Cold**: Far away (>10 steps)

5. **Next Round**: After a game ends, click the "Next Round" button to play again with the same mode

## Game Controls

### Player vs Computer Mode

- **Arrow Keys**: Move Tom
- **Mouse**: Click buttons in menus, "Move Target", and "Place Block"
- **Move Target Button**: Click to move Jerry once per game
- **Place Block Button**: Click to place a block once per game, then click on the grid to place it
- **R**: Rotate block orientation (horizontal/vertical) during block placement
- **ESC**: Quit game

### Player vs Player Mode

- **Player 1 (Tom)**: Arrow keys
- **Player 2 (Spike)**: WASD keys
- **Mouse**: Click buttons in menus, "Move Target", and "Place Block"
- **Move Target Button**: Click to move Jerry once per game (each player)
- **Place Block Button**: Click to place a block once per game (each player), then click on the grid to place it
- **R**: Rotate block orientation (horizontal/vertical) during block placement
- **ESC**: Quit game

## File Structure

```
pygame_hide_seek/
├── hide_seek_game.py      # Main game file
├── requirements.txt       # Python dependencies
├── run_game.bat          # Game launcher
├── README.md             # This file
├── assets/               # Game assets
├── tom/                  # Tom character sprites
├── spike/                # Spike character sprites
├── jerry/                # Jerry character sprites
├── feed_back/            # Feedback images
└── sound_track/          # Audio files
```

## Dependencies

- `pygame>=2.5.0` - Game development library

## Troubleshooting

If you encounter issues:

1. **Python not found**: Make sure Python 3.12 is installed
2. **Pygame not installed**: Run the installation script again
3. **Missing assets**: Ensure all image and sound files are in their respective folders
4. **Game not responding**: Try clicking the "Next Round" button or press any key to restart

## Development

The game is built with:

- **Python 3.12** - Programming language
- **Pygame 2.6.1** - Game development framework
- **A* Algorithm** - Pathfinding for AI
- **Custom Sprites** - Character and UI graphics

## Recent Updates

- ✅ Added Player vs Player mode
- ✅ Added distance display for both players
- ✅ Added "Next Round" button for quick restarts
- ✅ Added "Move Target" button for strategic gameplay
- ✅ Enhanced Computer AI with strategic Move Target usage
- ✅ Improved game mode selection interface
- ✅ Fixed movement controls and game flow
- ✅ Added computer thinking delay and indicator
- ✅ Added block placement and surprise gift box mechanics

Enjoy playing! 🎮
