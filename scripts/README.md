# 📜 Scripts Directory

This directory contains utility scripts for project setup and maintenance.

**Author:** DmitrTRC  
**Repository:** https://github.com/DmitrTRC/schedule-dnd

---

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

Run the complete setup script:

```bash
# Make script executable
chmod +x scripts/setup.sh

# Run setup
./scripts/setup.sh
```

This will:
1. ✅ Check Python and Poetry installation
2. ✅ Create complete project structure
3. ✅ Copy .env.example to .env
4. ✅ Install all dependencies
5. ✅ Setup pre-commit hooks
6. ✅ Initialize git repository
7. ✅ Create initial commit

### Option 2: Manual Setup

If you prefer manual control:

```bash
# 1. Create project structure
python3 scripts/setup_project_structure.py

# 2. Create .env file
cp .env.example .env

# 3. Install dependencies
poetry install

# 4. Setup pre-commit hooks
poetry run pre-commit install
```

---

## 📝 Available Scripts

### `setup.sh`

**Purpose:** Complete automated project setup  
**Language:** Bash  
**Usage:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**What it does:**
- Verifies Python installation (3.11+)
- Installs Poetry if not present
- Creates project structure
- Sets up environment configuration
- Installs dependencies
- Configures pre-commit hooks
- Initializes git repository

**Requirements:**
- Python 3.11 or higher
- Bash shell
- Internet connection (for Poetry installation)

---

### `setup_project_structure.py`

**Purpose:** Create complete directory structure and placeholder files  
**Language:** Python  
**Usage:**
```bash
python3 scripts/setup_project_structure.py
```

**What it creates:**

#### 📁 Directory Structure
```
schedule-dnd/
├── .github/
│   ├── workflows/
│   └── ISSUE_TEMPLATE/
├── docs/
│   ├── api/
│   └── architecture/
├── src/schedule_dnd/
│   ├── domain/              # Business logic
│   ├── application/         # Use cases
│   ├── infrastructure/      # Technical details
│   └── presentation/        # UI layer
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── scripts/
├── data/
├── output/
└── logs/
```

#### 📄 Generated Files

**Source Code:**
- All `__init__.py` files with proper docstrings
- Placeholder modules for each layer
- Entry point (`__main__.py`)

**Tests:**
- Test structure for all layers
- `conftest.py` for pytest fixtures
- Sample test files

**Documentation:**
- Architecture documentation template
- API documentation template
- Contributing guide template

**Configuration:**
- `.env` file (empty)
- `.gitkeep` files for empty directories

**Features:**
- ✅ Idempotent (safe to run multiple times)
- ✅ Colored output for clarity
- ✅ Skips existing files/directories
- ✅ Creates all necessary __init__.py files
- ✅ Adds proper docstrings

---

### `lint.sh`

**Purpose:** Run code quality checks  
**Language:** Bash  
**Status:** 🚧 To be implemented

**Planned functionality:**
```bash
chmod +x scripts/lint.sh
./scripts/lint.sh
```

Will run:
- Black (code formatting check)
- isort (import sorting check)
- Pylint (linting)
- mypy (type checking)
- Bandit (security scan)

---

### `test.sh`

**Purpose:** Run test suite with coverage  
**Language:** Bash  
**Status:** 🚧 To be implemented

**Planned functionality:**
```bash
chmod +x scripts/test.sh
./scripts/test.sh
```

Will run:
- Unit tests
- Integration tests
- Coverage report
- Generate HTML coverage report

---

## 🔧 Usage Examples

### First Time Setup

```bash
# Clone repository
git clone https://github.com/DmitrTRC/schedule-dnd.git
cd schedule-dnd

# Run automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh

# Activate virtual environment
poetry shell

# Start coding!
```

### Rebuilding Structure

If you need to recreate the structure:

```bash
# Recreate structure (safe - won't overwrite existing files)
python3 scripts/setup_project_structure.py

# Check what would be created
python3 scripts/setup_project_structure.py --dry-run  # (feature to be added)
```

### Development Workflow

```bash
# Setup (once)
./scripts/setup.sh

# Daily workflow
poetry shell                    # Activate environment
make test                       # Run tests
make lint                       # Check code quality
make format                     # Format code
make run                        # Run application

# Before commit
make ci                         # Run full CI pipeline locally
git add .
git commit -m "Your message"
```

---

## 🎯 Script Features

### Safety Features
- ✅ **Idempotent**: Safe to run multiple times
- ✅ **Non-destructive**: Won't overwrite existing files
- ✅ **Error handling**: Graceful failure with clear messages
- ✅ **Validation**: Checks prerequisites before proceeding

### User Experience
- 🎨 **Colored output**: Easy to see status
- 📊 **Progress indicators**: Know what's happening
- ✅ **Success summaries**: Clear completion status
- 📝 **Next steps**: Guidance after completion

### Compatibility
- 🐧 **Linux**: Fully supported
- 🍎 **macOS**: Fully supported
- 🪟 **Windows**: Python script works, bash needs WSL/Git Bash

---

## 🐛 Troubleshooting

### Python not found
```bash
# Check Python version
python3 --version

# If not installed, install Python 3.11+
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.11

# On macOS:
brew install python@3.11
```

### Poetry not found
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH (check Poetry installation output)
export PATH="$HOME/.local/bin:$PATH"
```

### Permission denied
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Or run with bash
bash scripts/setup.sh
```

### Structure already exists
This is normal! The script will:
- Skip existing files/directories
- Show yellow indicators for existing items
- Only create missing items

---

## 📚 Additional Resources

### Makefile Commands
All common tasks are also available through Make:

```bash
make help           # Show all commands
make dev-install    # Install dev dependencies
make test           # Run tests
make lint           # Run linting
make format         # Format code
make ci             # Run full CI pipeline
```

### Documentation
- [Architecture Documentation](../docs/architecture.md)
- [Contributing Guide](../docs/contributing.md)
- [API Documentation](../docs/api.md)

### Tools Used
- **Poetry**: Dependency management
- **Pre-commit**: Git hooks for code quality
- **Black**: Code formatting
- **mypy**: Type checking
- **pytest**: Testing framework
- **Rich**: Terminal UI library

---

## 🤝 Contributing

To add new scripts:

1. Create script file in `scripts/` directory
2. Add shebang and header with author info
3. Make executable: `chmod +x scripts/your_script.sh`
4. Update this README with documentation
5. Test on multiple platforms if possible

**Script Template:**
```bash
#!/bin/bash
#
# Script description
# Author: DmitrTRC
# Repository: https://github.com/DmitrTRC/schedule-dnd
#

set -e  # Exit on error

# Your code here
```

---

## 📝 Notes

- All scripts are designed to be idempotent
- Scripts use colored output for better UX
- Python scripts work cross-platform
- Bash scripts need bash shell (WSL on Windows)
- Always test scripts before committing

---

**Last Updated:** October 2025  
**Maintained by:** DmitrTRC
