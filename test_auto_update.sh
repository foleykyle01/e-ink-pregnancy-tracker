#!/bin/bash

# Test script for auto-update functionality
# Run this to verify the update mechanism works correctly

echo "Auto-Update Test Script"
echo "======================="
echo

# Test configuration
TEST_DIR="/tmp/test-pregnancy-tracker"
TEST_LOG="/tmp/test-update.log"

# Clean up any previous test
rm -rf "$TEST_DIR" 2>/dev/null
rm -f "$TEST_LOG" 2>/dev/null

echo "1. Creating test environment..."
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Clone the repository
echo "2. Cloning repository..."
git clone https://github.com/foleykyle01/e-ink-pregnancy-tracker.git . 2>/dev/null || {
    echo "   Note: Could not clone from GitHub"
    echo "   Using current directory for testing instead..."
    cp -r "$(dirname "$0")"/* "$TEST_DIR/"
    git init
    git add .
    git commit -m "Initial test commit" >/dev/null 2>&1
}

# Copy and modify the auto_update script for testing
cp "$(dirname "$0")/auto_update.sh" "$TEST_DIR/auto_update_test.sh"
sed -i "s|REPO_DIR=.*|REPO_DIR=\"$TEST_DIR\"|" "$TEST_DIR/auto_update_test.sh"
sed -i "s|LOG_FILE=.*|LOG_FILE=\"$TEST_LOG\"|" "$TEST_DIR/auto_update_test.sh"
sed -i "s|python3 main.py|echo 'Would run: python3 main.py'|" "$TEST_DIR/auto_update_test.sh"
chmod +x "$TEST_DIR/auto_update_test.sh"

echo "3. Running auto-update script..."
bash "$TEST_DIR/auto_update_test.sh"

echo
echo "4. Checking results..."
if [ -f "$TEST_LOG" ]; then
    echo "   Log file created: ✓"
    echo
    echo "   Log contents:"
    echo "   -------------"
    cat "$TEST_LOG" | sed 's/^/   /'
else
    echo "   Log file created: ✗"
fi

echo
echo "5. Testing error conditions..."

# Test with non-existent directory
sed -i "s|REPO_DIR=.*|REPO_DIR=\"/nonexistent/directory\"|" "$TEST_DIR/auto_update_test.sh"
bash "$TEST_DIR/auto_update_test.sh" 2>/dev/null
if grep -q "ERROR: Could not navigate" "$TEST_LOG"; then
    echo "   Invalid directory handling: ✓"
else
    echo "   Invalid directory handling: ✗"
fi

echo
echo "Test Summary:"
echo "============="
if [ -f "$TEST_LOG" ] && grep -q "Auto-update check completed" "$TEST_LOG"; then
    echo "✓ Auto-update script is working correctly"
    echo
    echo "Next steps on your Raspberry Pi:"
    echo "1. Transfer these files to your Pi:"
    echo "   - auto_update.sh"
    echo "   - setup_auto_update.sh"
    echo "   - monitor_updates.sh"
    echo
    echo "2. Run the setup script on the Pi:"
    echo "   bash setup_auto_update.sh"
    echo
    echo "3. Monitor updates with:"
    echo "   bash monitor_updates.sh"
else
    echo "✗ Issues detected with auto-update script"
    echo "  Check the log file for details: $TEST_LOG"
fi

# Cleanup
echo
read -p "Clean up test files? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$TEST_DIR"
    rm -f "$TEST_LOG"
    echo "Test files cleaned up."
fi