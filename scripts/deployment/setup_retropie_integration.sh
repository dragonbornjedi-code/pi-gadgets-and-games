#!/bin/bash
# setup_retropie_integration.sh
# Integrates the Memory Game into RetroPie's Ports menu

set -euo pipefail

GAME_DIR="/home/pi/pi-gadgets-and-games"
PORTS_DIR="/home/pi/RetroPie/roms/ports"
SCRIPT_PATH="$PORTS_DIR/MemoryGame.sh"

echo "Creating RetroPie Port entry..."

# Ensure ports directory exists
mkdir -p "$PORTS_DIR"

# Create the launch script in RetroPie ports
cat <<EOF > "$SCRIPT_PATH"
#!/bin/bash
cd "$GAME_DIR"
source .venv/bin/activate
python3 main.py
EOF

chmod +x "$SCRIPT_PATH"

echo "Integration complete! You can now find 'MemoryGame' under the 'Ports' section in EmulationStation."
echo "Note: Ensure you have run scripts/deployment/install_dependencies.sh first."
