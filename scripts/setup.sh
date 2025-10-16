#!/bin/bash
#
# Quick setup script for Schedule DND project
# Author: DmitrTRC
# Repository: https://github.com/DmitrTRC/schedule-dnd
#
# This script automates the initial project setup
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Print header
echo -e "\n${BLUE}${BOLD}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}${BOLD}Schedule DND - Quick Setup${NC}"
echo -e "${BLUE}${BOLD}Author: DmitrTRC${NC}"
echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════════════${NC}\n"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo -e "Please install Python 3.11 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} detected${NC}"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}Poetry is not installed${NC}"
    echo -e "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    echo -e "${GREEN}✓ Poetry installed${NC}"
else
    POETRY_VERSION=$(poetry --version | awk '{print $3}')
    echo -e "${GREEN}✓ Poetry ${POETRY_VERSION} detected${NC}"
fi

# Run the Python structure setup script
echo -e "\n${BOLD}Step 1: Creating project structure...${NC}"
python3 scripts/setup_project_structure.py

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create project structure${NC}"
    exit 1
fi

# Copy .env.example to .env if it doesn't exist
echo -e "\n${BOLD}Step 2: Setting up environment...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from .env.example${NC}"
    else
        echo -e "${YELLOW}⊙ .env.example not found, skipping${NC}"
    fi
else
    echo -e "${YELLOW}⊙ .env already exists${NC}"
fi

# Install dependencies with Poetry
echo -e "\n${BOLD}Step 3: Installing dependencies...${NC}"
poetry install

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Install pre-commit hooks
echo -e "\n${BOLD}Step 4: Setting up pre-commit hooks...${NC}"
poetry run pre-commit install

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⊙ Failed to install pre-commit hooks${NC}"
else
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
fi

# Create initial git commit if this is a new repo
if [ -d .git ]; then
    echo -e "\n${BOLD}Step 5: Git repository detected${NC}"

    # Check if there are any commits
    if ! git rev-parse HEAD &> /dev/null; then
        echo -e "${YELLOW}No commits found. Creating initial commit...${NC}"
        git add .
        git commit -m "Initial commit: Project structure setup

- Created project structure with clean architecture
- Configured Poetry for dependency management
- Set up CI/CD with GitHub Actions
- Added pre-commit hooks for code quality
- Configured development tools (black, mypy, pytest, etc.)

Author: DmitrTRC
Repository: https://github.com/DmitrTRC/schedule-dnd"
        echo -e "${GREEN}✓ Initial commit created${NC}"
    else
        echo -e "${YELLOW}⊙ Repository already has commits${NC}"
    fi
else
    echo -e "\n${BOLD}Step 5: Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"

    # Create initial commit
    git add .
    git commit -m "Initial commit: Project structure setup

- Created project structure with clean architecture
- Configured Poetry for dependency management
- Set up CI/CD with GitHub Actions
- Added pre-commit hooks for code quality
- Configured development tools (black, mypy, pytest, etc.)

Author: DmitrTRC
Repository: https://github.com/DmitrTRC/schedule-dnd"
    echo -e "${GREEN}✓ Initial commit created${NC}"
fi

# Final summary
echo -e "\n${BLUE}${BOLD}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}✓ Setup completed successfully!${NC}"
echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BOLD}Quick start commands:${NC}"
echo -e "  ${GREEN}make help${NC}           - Show all available commands"
echo -e "  ${GREEN}make run${NC}            - Run the application"
echo -e "  ${GREEN}make test${NC}           - Run tests"
echo -e "  ${GREEN}make lint${NC}           - Run linting checks"
echo -e "  ${GREEN}make format${NC}         - Format code"
echo -e "  ${GREEN}poetry shell${NC}        - Activate virtual environment\n"

echo -e "${BOLD}Next steps:${NC}"
echo -e "  1. Review .env file and adjust settings if needed"
echo -e "  2. Start implementing domain models"
echo -e "  3. Write tests as you develop"
echo -e "  4. Run ${GREEN}make ci${NC} before committing\n"

echo -e "${YELLOW}Happy coding! 🚀${NC}\n"
