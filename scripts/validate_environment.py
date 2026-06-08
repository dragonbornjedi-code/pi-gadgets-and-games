import sys
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from framework.diagnostics import pi_profile
from framework.timing import performance_manager

def validate():
    print("--- Running System Validation ---")
    
    # 1. Hardware/Profile
    pi_profile.get_pi_profile()
    
    # 2. Pygame Init
    try:
        pygame.init()
        print("✅ Pygame initialized")
        pygame.quit()
    except Exception as e:
        print(f"❌ Pygame init failed: {e}")
        sys.exit(1)
        
    # 3. Memory/File Permissions (Write test)
    try:
        test_file = "testing/write_test.json"
        with open(test_file, 'w') as f:
            f.write('{"status": "ok"}')
        print("✅ Filesystem write test passed")
    except Exception as e:
        print(f"❌ Filesystem write failed: {e}")
        sys.exit(1)

    print("--- Validation Complete ---")

if __name__ == "__main__":
    validate()
