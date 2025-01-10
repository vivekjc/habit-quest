#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "${GREEN}Starting Python environment setup...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "${RED}Python3 is not installed. Installing via Homebrew...${NC}"
    if ! command -v brew &> /dev/null; then
        echo "${RED}Homebrew is not installed. Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python
fi

# Install python-tk if not already installed
echo "${GREEN}Installing python-tk...${NC}"
brew install python-tk@$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")

# Create and activate virtual environment
echo "${GREEN}Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Verify tkinter is working
python3 -c "import tkinter" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "${GREEN}✓ Setup completed successfully!${NC}"
    echo "${GREEN}To activate the virtual environment, run:${NC}"
    echo "source venv/bin/activate"
    echo "${GREEN}To run the time display, run:${NC}"
    echo "python time_display.py"
else
    echo "${RED}Error: tkinter installation failed${NC}"
    exit 1
fi 