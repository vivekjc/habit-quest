#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "${GREEN}Starting Habit Tracker Setup...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "${RED}Python3 is not installed. Installing via Homebrew...${NC}"
    if ! command -v brew &> /dev/null; then
        echo "${RED}Homebrew is not installed. Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade pip
echo "${GREEN}Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install dependencies
echo "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create instance directory if it doesn't exist
if [ ! -d "instance" ]; then
    echo "${GREEN}Creating instance directory...${NC}"
    mkdir instance
fi

# Start the application
echo "${GREEN}Starting the application...${NC}"
echo "${GREEN}Visit http://localhost:5000 in your web browser${NC}"
python wsgi.py 