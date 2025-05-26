from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[0]
IT_boost_release = str(REPO_ROOT / "nexullance" / "IT_boost" / "build" / "release" / "") + "/"
IT_boost_debug = str(REPO_ROOT / "nexullance" / "IT_boost" / "build" / "debug" / "") + "/"