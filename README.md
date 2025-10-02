# 🏰 AIge-Of-EmpAIres

**A Python-based Real-Time Strategy (RTS) Game with Intelligent AI Bots**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/pygame-2.6+-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎮 Overview

AIge-Of-EmpAIres is a sophisticated real-time strategy game inspired by Age of Empires, featuring intelligent AI bots that use decision trees to manage resources, build structures, train units, and engage in strategic warfare. The game combines classic RTS mechanics with advanced AI systems for an engaging single-player or bot-vs-bot experience.

## ✨ Features

### 🎯 Core Gameplay
- **Real-time Strategy Mechanics**: Classic RTS gameplay with resource management, base building, and unit combat
- **Multiple Unit Types**: Villagers, Archers, Swordsmen, and Horsemen with unique abilities
- **Building System**: Town Centers, Farms, Barracks, Archery Ranges, Stables, and defensive structures
- **Resource Management**: Wood, Food, and Gold collection and allocation
- **Combat System**: Strategic unit battles with different strengths and weaknesses

### 🤖 Advanced AI System
- **Decision Tree AI**: Sophisticated AI bots that make strategic decisions using decision trees
- **Multiple Bot Personalities**: 
  - **Economic**: Focuses on resource gathering and expansion
  - **Defensive**: Prioritizes defense and fortification
  - **Offensive**: Emphasizes military production and aggression
- **Dynamic Difficulty**: Configurable AI difficulty levels (lean, mean, marines, DEBUG)
- **Intelligent Pathfinding**: A* algorithm for efficient unit movement
- **Adaptive Strategy**: Bots adjust their tactics based on enemy composition

### 🎨 Display Options
- **Dual Display Modes**: GUI-only, Terminal-only, or Both simultaneously
- **Real-time Graphics**: Pygame-based graphical interface with sprites and animations
- **Terminal Interface**: Text-based display for headless or debugging scenarios
- **Minimap**: Strategic overview of the battlefield

## 🚀 Installation

### Prerequisites
- Python 3.13 or higher
- pip (Python package installer)

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/XpertLambda/AIge-Of-EmpAIres.git
   cd AIge-Of-EmpAIres
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install pygame
   ```

4. **Run the game**:
   ```bash
   python main.py
   ```

## 🎮 How to Play

### Game Modes
When starting the game, choose your display mode:
- **[1] GUI only**: Full graphical interface
- **[2] Terminal only**: Text-based interface
- **[3] Both**: Simultaneous GUI and terminal display

### Controls
- **Mouse**: Select units, buildings, and interact with the game world
- **Camera**: WASD or arrow keys to move the camera
- **ESC**: Pause menu
- **Mouse Wheel**: Zoom in/out

### Game Objectives
- Build and manage your base
- Gather resources (Wood, Food, Gold)
- Train military units
- Defeat enemy teams by destroying their structures and units

## 🏗️ Project Structure

```
AIge-Of-EmpAIres/
├── 📁 Controller/           # Game logic and AI controllers
│   ├── Bot.py              # Main AI bot implementation
│   ├── Decisonnode.py      # Decision tree system
│   ├── game_loop.py        # Main game loop
│   ├── event_handler.py    # Input handling
│   ├── drawing.py          # Rendering system
│   └── ...
├── 📁 Entity/              # Game entities
│   ├── 📁 Building/        # Building classes
│   ├── 📁 Unit/           # Unit classes
│   ├── 📁 Resource/       # Resource entities
│   └── Entity.py          # Base entity class
├── 📁 Models/              # Game models and data structures
│   ├── Map.py             # Game map implementation
│   ├── Team.py            # Team/player management
│   ├── Resources.py       # Resource management
│   └── Zone.py            # Zone control system
├── 📁 Settings/            # Configuration and setup
│   ├── setup.py           # Game constants and settings
│   ├── entity_mapping.py  # Entity type mappings
│   └── sync.py            # Synchronization settings
├── 📁 AiUtils/             # AI utilities
│   └── aStar.py           # A* pathfinding algorithm
├── 📁 Projectile/          # Projectile system
├── 📁 assets/              # Game assets (sprites, sounds)
├── 📁 saves/               # Save game files
├── main.py                # Main entry point
└── test_bot_logic.py      # Bot testing utilities
```

## 🤖 AI System

### Decision Trees
The AI system uses hierarchical decision trees that evaluate conditions and execute actions:

```python
# Example decision tree structure
Economic Bot:
├── Under Attack? → Defend
├── Resource Shortage? → Manage Resources
├── Buildings Needed? → Build Structures
└── Default → Balance Army
```

### Bot Personalities
- **Economic Bot**: Prioritizes villager production, resource gathering, and expansion
- **Defensive Bot**: Focuses on fortifications, defensive structures, and unit positioning
- **Offensive Bot**: Emphasizes military unit production and aggressive tactics

### AI Features
- **Resource Management**: Intelligent allocation of villagers to different resource types
- **Build Queues**: Automated construction of necessary buildings
- **Unit Production**: Strategic training of military units based on enemy composition
- **Combat Tactics**: Coordinated attacks and defensive positioning

## ⚙️ Configuration

### Game Settings (`Settings/setup.py`)
```python
GAME_SPEED = 5              # Game simulation speed
DPS = 1                     # Decisions per second for AI
RESOURCE_THRESHOLDS = Resources(food=150, gold=150, wood=100)
```

### Difficulty Levels
- **lean**: Basic AI with limited resources
- **mean**: Standard AI with balanced resources
- **marines**: Advanced AI with superior resources
- **DEBUG**: Development mode with enhanced debugging

## 🧪 Testing

### Bot Logic Testing
Run the isolated bot test to verify AI functionality:
```bash
python test_bot_logic.py
```

### Features Tested
- ✅ Decision tree evaluation
- ✅ Resource shortage detection
- ✅ Action cooldown systems
- ✅ Multi-bot coordination
- ✅ No infinite loops

## 🛠️ Development

### Adding New Units
1. Create unit class in `Entity/Unit/`
2. Add sprite assets to `assets/units/`
3. Update entity mappings in `Settings/entity_mapping.py`
4. Configure unit properties in `Settings/setup.py`

### Extending AI Behavior
1. Add new conditions in `Controller/Decisonnode.py`
2. Implement actions in `Controller/Bot.py`
3. Create decision tree structures for new strategies

### Debug Mode
Enable debug output by setting the difficulty to "DEBUG":
```python
# In main.py or configuration
bot = Bot(team, game_map, players, mode='economic', difficulty='DEBUG')
```

## 🎯 Roadmap

### Planned Features
- [ ] **Multiplayer Support**: Network-based multiplayer gameplay
- [ ] **Campaign Mode**: Single-player story campaigns
- [ ] **Map Editor**: Custom map creation tools
- [ ] **Advanced AI**: Machine learning-based AI improvements
- [ ] **Sound System**: Audio effects and background music
- [ ] **Unit Formations**: Military unit formation systems
- [ ] **Diplomacy**: Alliance and trade systems between AI players

### Performance Improvements
- [ ] **Optimized Rendering**: Improved graphics performance
- [ ] **Parallel AI Processing**: Multi-threaded AI decision making
- [ ] **Memory Management**: Reduced memory footprint

## 🤝 Contributing

We welcome contributions! Please read our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Setup
1. Install development dependencies
2. Run tests: `python test_bot_logic.py`
3. Follow PEP 8 style guidelines
4. Add docstrings to new functions

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the classic Age of Empires series
- Built with Python and Pygame
- AI decision tree concepts from game AI research
- Community contributions and feedback

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/XpertLambda/AIge-Of-EmpAIres/issues)
- **Discussions**: [GitHub Discussions](https://github.com/XpertLambda/AIge-Of-EmpAIres/discussions)
- **Wiki**: [Project Wiki](https://github.com/XpertLambda/AIge-Of-EmpAIres/wiki)

---

**Made with ❤️ by the AIge-Of-EmpAIres development team**

*Build your empire, command your armies, and let the AI challenge your strategic thinking!*
