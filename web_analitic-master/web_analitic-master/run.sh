# Path to the Python venv
VENV_PATH="venv"
# Check if the venv directory exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_PATH"
    
    # Activate the virtual environment
    source "$VENV_PATH/bin/activate"
else
    source "$VENV_PATH/bin/activate"
fi

# Install packages from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip install -r requirements.txt --verbose
    pip install -e tgcrawl_lib
else
    echo "No requirements.txt found."
fi

# Set the Python venv executable path to a variable
PYTHON_VENV_EXECUTABLE="$(pwd)/$VENV_PATH/bin/python3"

echo "Python virtual environment setup completed in $PYTHON_VENV_EXECUTABLE"

# Function to start backend service
start_backend() {

    $PYTHON_VENV_EXECUTABLE -m streamlit run Главная.py --server.port=8502 --server.address=0.0.0.0 &
    BACKEND_PID=$!
    echo "Backend service started with PID: $BACKEND_PID"
}

# Function to check if a process is running
is_process_running() {
    kill -0 $1 2>/dev/null
}

# Function to kill both services
kill_services() {
    echo "One of the services died. Killing both services..."
    kill $BACKEND_PID
    exit 1
}

# Start the services
start_backend

# Trap any exit signals to ensure proper cleanup
trap 'kill_services' SIGINT SIGTERM

# Monitor the services
while true; do
    if ! is_process_running $BACKEND_PID; then
        kill_services
        exit
    fi
    sleep 1
done
