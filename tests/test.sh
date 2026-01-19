# Install curl
apt-get update
apt-get install -y curl

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for current session
export PATH="$HOME/.local/bin:$PATH"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verify uv installation
if ! command -v uv &> /dev/null; then
    echo "Error: uv installation failed"
    exit 1
fi

# Don't change anything below this line
uvx \
  -p 3.11 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  -w datetime==5.5 \
  -w numpy==2.0.2 \
  -w pandas==2.3.3 \
  -w docker==7.1.0 \
  pytest --ctrf /logs/verifier/ctrf.json ${SCRIPT_DIR}/test_outputs.py -rA

# Check test results and write reward
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi