import os
import sys
from pathlib import Path

APP_NAME = "StoreFlowAnalytics"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_resource_path(*parts: str) -> str:
    """
    Path to bundled read-only resources.
    """
    if _is_frozen() and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = _project_root()
    return str(base.joinpath(*parts))


def get_data_root() -> Path:
    """
    Path to writable data directory.
    In dev, use project ./assets for convenience.
    In a bundled app, use an OS-specific app data folder.
    """
    if not _is_frozen():
        return _project_root() / "assets"

    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    root = base / APP_NAME / "assets"
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_data_path(*parts: str) -> str:
    root = get_data_root()
    return str(root.joinpath(*parts))


def resolve_camera_video_path(
    stored_path: str,
    database_videos_dir: str | None = None,
) -> str:
    """
    Resolve persisted camera video paths across dev, bundled, and legacy records.
    """
    path = Path(stored_path).expanduser()
    if path.is_absolute():
        return str(path.resolve(strict=False))

    candidates = [
        Path.cwd() / path,
        Path(get_resource_path()).joinpath(path),
    ]

    if database_videos_dir:
        db_dir = Path(database_videos_dir)
        candidates.append(db_dir / path)
        candidates.append(db_dir / path.name)

    for candidate in candidates:
        if candidate.exists():
            return str(candidate.resolve(strict=False))

    if database_videos_dir:
        return str((Path(database_videos_dir) / path.name).resolve(strict=False))

    return str((Path.cwd() / path).resolve(strict=False))
