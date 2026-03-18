# CombatSimulator

A turn-based combat simulator written in Python.

## Project Structure

```
CombatSimulator/
├── main.py                 # Entry point
├── Combat/                 # Core combat logic
│   ├── Combat.py           # Combat simulation
│   ├── gol.py              # Global variable manager
│   ├── Data/               # Data loading and configuration
│   │   ├── DataConfig.py   # Data loader (reads CSV tables)
│   │   ├── ServantData.py  # Servant (unit) data model
│   │   ├── SkillData.py    # Skill data model
│   │   └── Tables/         # CSV data tables
│   │       ├── servant.csv # Servant configuration
│   │       └── skill.csv   # Skill configuration
│   └── Skills/             # Skill implementations
│       ├── ActiveSkill.py  # Active skills
│       ├── ChaseSkill.py   # Chase skills
│       ├── CommandSkill.py # Command skills
│       └── PassiveSkill.py # Passive skills
└── Editor/                 # Editor tools
    └── editor.py
```

## Getting Started

Install dependencies:

```bash
pip install pandas
```

Run the simulator:

```bash
python main.py
```

