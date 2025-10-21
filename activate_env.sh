#!/bin/bash
#
# Environment activation helper for Poetry 2.0+
# Author: DmitrTRC
# Repository: https://github.com/DmitrTRC/schedule-dnd
#
# This script helps activate the Poetry virtual environment
# Usage: source activate_env.sh
#

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}Poetry is not installed${NC}"
    echo "Please install Poetry first: curl -sSL https://install.python-poetry.org | python3 -"
    return 1 2>/dev/null || exit 1
fi

# Get virtual environment path
VENV_PATH=$(poetry env info --path 2>/dev/null)

if [ -z "$VENV_PATH" ]; then
    echo -e "${YELLOW}Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    poetry install
    VENV_PATH=$(poetry env info --path)
fi

# Activate based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    ACTIVATE_SCRIPT="$VENV_PATH/Scripts/activate"
else
    # Linux/macOS
    ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"
fi

if [ -f "$ACTIVATE_SCRIPT" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "$ACTIVATE_SCRIPT"
    echo -e "${GREEN}✓ Environment activated${NC}"
    echo -e "${BLUE}Python: $(which python)${NC}"
    echo -e "${BLUE}Version: $(python --version)${NC}"
    echo ""
    echo -e "To deactivate, run: ${GREEN}deactivate${NC}"
else
    echo -e "${YELLOW}Could not find activation script at:${NC}"
    echo "$ACTIVATE_SCRIPT"
    echo ""
    echo "Try manually:"
    echo "  source $VENV_PATH/bin/activate  # Linux/macOS"
    return 1 2>/dev/null || exit 1
fi
