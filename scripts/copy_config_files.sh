#!/bin/bash
#
# Copy configuration files helper script
# Author: DmitrTRC
# Repository: https://github.com/DmitrTRC/schedule-dnd
#
# This script helps you identify which configuration files
# need to be copied from Claude artifacts to your project
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "\n${BLUE}${BOLD}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}${BOLD}Configuration Files Checker${NC}"
echo -e "${BLUE}${BOLD}Author: DmitrTRC${NC}"
echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════════════${NC}\n"

# List of required configuration files with their locations
declare -A CONFIG_FILES=(
    ["pyproject.toml"]="Project root"
    [".gitignore"]="Project root"
    [".env.example"]="Project root"
    ["Makefile"]="Project root"
    [".pre-commit-config.yaml"]="Project root"
    [".github/workflows/ci.yml"]="GitHub workflows directory"
)

echo -e "${BOLD}Checking configuration files...${NC}\n"

missing_files=0
existing_files=0

for file in "${!CONFIG_FILES[@]}"; do
    location="${CONFIG_FILES[$file]}"

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC} (exists in $location)"
        ((existing_files++))
    else
        echo -e "${RED}✗ $file${NC} (missing from $location)"
        ((missing_files++))
    fi
done

echo -e "\n${BOLD}Summary:${NC}"
echo -e "  ${GREEN}Existing: $existing_files${NC}"
echo -e "  ${RED}Missing: $missing_files${NC}\n"

if [ $missing_files -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ All configuration files are in place!${NC}"
    echo -e "\nYou can now run:"
    echo -e "  ${GREEN}./scripts/setup.sh${NC}\n"
    exit 0
fi

echo -e "${YELLOW}${BOLD}⚠ Some configuration files are missing${NC}\n"
echo -e "${BOLD}To fix this:${NC}\n"
echo -e "1. From Claude's artifacts, copy each missing file:"
echo -e "   ${BLUE}Look for artifacts named:${NC}"

for file in "${!CONFIG_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        artifact_name=$(basename "$file" | sed 's/\./-/g' | sed 's/-/_/g')
        echo -e "   - ${YELLOW}$file${NC}"
    fi
done

echo -e "\n2. Save each file to the correct location in your project:\n"

for file in "${!CONFIG_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        location="${CONFIG_FILES[$file]}"

        # Create directory if needed
        dir=$(dirname "$file")
        if [ "$dir" != "." ] && [ ! -d "$dir" ]; then
            echo -e "   ${YELLOW}mkdir -p $dir${NC}"
        fi

        echo -e "   ${YELLOW}# Save to: $file${NC} ($location)"
    fi
done

echo -e "\n3. Run this checker again:"
echo -e "   ${GREEN}./scripts/copy_config_files.sh${NC}\n"
echo -e "4. Once all files are in place, run:"
echo -e "   ${GREEN}./scripts/setup.sh${NC}\n"

# Optional: Create directories for missing files
echo -e "${BOLD}Create missing directories now? [y/N]${NC} "
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "\n${BOLD}Creating directories...${NC}"

    for file in "${!CONFIG_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            dir=$(dirname "$file")
            if [ "$dir" != "." ]; then
                mkdir -p "$dir"
                echo -e "${GREEN}✓ Created: $dir${NC}"
            fi
        fi
    done

    echo -e "\n${GREEN}Directories created!${NC}"
    echo -e "Now copy the configuration files to these locations.\n"
fi

exit 1
