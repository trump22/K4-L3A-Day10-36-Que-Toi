from pathlib import Path
import sys

# Ensure src directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pipelines.phase1 import main


if __name__ == "__main__":
    main()
