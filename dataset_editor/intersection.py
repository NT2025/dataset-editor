""" ２つのディレクトリに存在する同名ファイルを抽出する
"""
from __future__ import annotations
from pathlib import Path
from argparse import ArgumentParser
import shutil


def add_arguments(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument("dir1", type=str, help="dir")
    parser.add_argument("dir2", type=str, help="dir")
    parser.add_argument("--dst_dir", type=str, help="dst dir. Default 'intersection_dir1-and-dir2'")
    return parser


def main(*args, **kwargs):
    ### 引数確認
    dir1 = Path(kwargs['dir1'])
    assert dir1.exists()
    dir2 = Path(kwargs['dir2'])
    assert dir2.exists()
    dst_dir: Path
    if kwargs['dst_dir'] is None:
        dst_dir = Path(f"intersection-{dir1.stem}-and-{dir2.stem}")
    else:
        dst_dir = Path(kwargs['dst_dir'])
    assert dst_dir.parent.exists(), f"{dst_dir}"

    ### make process instance
    process = Process(dir1, dir2, dst_dir)

    ### main process run
    process.run()


class Process:
    def __init__(
            self,
            dir1: Path,
            dir2: Path,
            dst_dir: Path,
    ):
        self._dir1: Path = dir1
        self._dir2: Path = dir2
        self._dst_dir: Path = dst_dir


    def run(self):
        ### Found file paths
        file_paths_list: list[list[Path]] = []
        for dir in [self._dir1, self._dir2]:
            file_paths: list[Path] = self._find_files(dir)
            if len(file_paths) == 0:
                raise ValueError(f"Not Found files in '{dir}'")

            file_paths_list.append(file_paths)

        ### get insersection
        file_paths = self._intersection(file_paths_list[0], file_paths_list[1])
        if len(file_paths) == 0:
            raise Exception(f"Not Intersection FileName")

        ### write
        self._dst_dir.mkdir()
        for path in file_paths:
            shutil.copy(path, self._dst_dir)

        ### show result
        print("Results:")
        print("Src:")
        print(f"\t {self._dir1}")
        print(f"\t {self._dir2}")
        print("Dst:")
        print(f"\t {self._dst_dir}")
        print(f"Num Intersections:{len(file_paths)}")


    def _find_files(self, dir: Path) -> list[Path]:
        file_paths: list[Path] = []
        for file_path in dir.glob(f"*"):
            if file_path.is_file():
                file_paths.append(file_path)
        return file_paths


    def _intersection(self, paths1: list[Path], paths2: list[Path]) -> list[Path]:
        """ 重複したファイル名を持つPathを抽出
        """
        dst_paths: list[Path] = []
        names2: list[str] = [p.name for p in paths2]
        for p in paths1:
            if p.name in names2:
                dst_paths.append(p)

        return dst_paths


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser = add_arguments(parser)
    main(**vars(parser.parse_args()))
