def __add_path():
    import sys
    from pathlib import Path

    file_dir = Path(__file__).absolute().parent
    root_dir = file_dir.parent

    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))


__add_path()