#!/bin/bash

# Define colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
LOGS_DIR="$(pwd)/logs"
if [ ! -d "$LOGS_DIR" ]; then
    echo -e "${BLUE}Creating logs directory...${NC}"
    mkdir -p "$LOGS_DIR"
fi

# Function to handle script termination
cleanup() {
    echo -e "${BLUE}Shutting down all services...${NC}"
    # Kill all child processes
    pkill -P $$
    exit 0
}

# Set trap for SIGINT (Ctrl+C)
trap cleanup SIGINT

echo -e "${GREEN}Starting LocalAI_Bench services...${NC}"

# Start Python backend with UV in the background
echo -e "${BLUE}Starting Python backend with UV...${NC}"
(cd "$(pwd)/app" && uv run main.py > "$LOGS_DIR/backend.log" 2>&1) &
BACKEND_PID=$!
echo -e "${BLUE}Python backend started with PID: ${BACKEND_PID}${NC}"

# Start frontend in UI folder in the background
echo -e "${BLUE}Starting frontend application...${NC}"
(cd "$(pwd)/ui" && npm run dev > "$LOGS_DIR/frontend.log" 2>&1) &
FRONTEND_PID=$!
echo -e "${BLUE}Frontend application started with PID: ${FRONTEND_PID}${NC}"

echo -e "${GREEN}All services started. Press Ctrl+C to stop all services.${NC}"
echo -e "${BLUE}Backend logs: $LOGS_DIR/backend.log${NC}"
echo -e "${BLUE}Frontend logs: $LOGS_DIR/frontend.log${NC}"

# Wait a moment for services to start
echo -e "${BLUE}Waiting for services to initialize...${NC}"
sleep 3

echo -e "${BLUE}Please open http://localhost:5173 for UI in your browser.${NC}"
echo -e "${BLUE}Please open http://localhost:8000 for backend in your browser.${NC}"


# Wait for user to press Ctrl+C
wait