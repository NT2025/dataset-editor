""" ネストされたディレクトリをルートディレクトリに統合する
"""
from __future__ import annotations
from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter
import shutil


def add_arguments(parser: ArgumentParser):
    parser.add_argument("target_dir", type=str, help="ファイルを含むディレクトリ")
    parser.add_argument("-n", "--num_nest", type=int, default=1, help="ネスト回数")
    parser.add_argument("-s", "--save_dir", type=str, default="None", 
        help="Save dir. "
         + "Default is 'target_dir_break-nest'.\n"
         + "You can use existed dir. "
         + "If you use this option, Save format is 'save_dir/target_dir'!")

    return parser


def main(*args, **kwargs):

    show_kwargs(**kwargs)
    myargs = Args(**kwargs)

    print("対象パスを検索")
    paths: list[Path] = find_paths_from_nest(myargs.target_dir, myargs.num_nest)

    print("以下ディレクトリに書き込みます")
    print(f"・{myargs.save_dir}")
    write_paths(myargs.save_dir, paths)
    print("Finish!")
    print("──────")


def show_kwargs(*args, **kwargs):
    text: str = "\n"
    text += f"┌ kwargs ─────\n"
    for key, value in kwargs.items():
        text += f"│ - {key}\n"
        text += f"│    - {value}\n"
    text += f"└─────────\n"
    print(text)


class Args:
    def __init__(self, *args, **kwargs):
        self.target_dir: Path = self._parse_target_dir(**kwargs)
        self.num_nest: int = self._parse_num_nest(**kwargs)
        self.save_dir: Path = self._parse_save_dir(**kwargs)


    def _parse_target_dir(self, *args, **kwargs) -> Path:
        target_dir = Path(kwargs['target_dir'])
        assert target_dir.exists()
        assert target_dir.is_dir()
        curr_dir = Path(".")
        assert target_dir != curr_dir, "カレントディレクトリは対象にできません"
        return target_dir


    def _parse_num_nest(self, *args, **kwargs) -> int:
        num_nest: int = kwargs['num_nest']
        assert num_nest > 0
        return num_nest


    def _parse_save_dir(self, *args , **kwargs) -> Path:
        save_dir =  Path(kwargs['save_dir'])
        if save_dir.name == 'None':
            save_dir = Path(f"{self.target_dir}_break-nest")
            assert save_dir.parent.exists(), \
                f"Not Found SaveDirParent Path. That is {save_dir.parent}"
        else:
            save_dir: Path = Path(f"{save_dir}/{self.target_dir.name}")
            assert save_dir.parent.parent.exists(), \
                f"Not Found SaveDirParent Path. That is {save_dir.parent}"
        assert save_dir != self.target_dir, \
            f"Not Equal dir. Tgt is '{self.target_dir}', Save is '{save_dir}'."
        return save_dir


def find_paths_from_nest(tgt_path: Path, num_nest:int=1) -> list[Path]:
    files: list[Path] = []
    dirs: list[Path] = []

    dirs.append(tgt_path)
    new_files: list[Path]
    new_dirs: list[Path]
    for ni in range(num_nest+1):
        for dj in range(len(dirs)):
            d: Path = dirs.pop(0)
            new_files, new_dirs = find_file_and_dir(d)
            files = files + new_files
            dirs = dirs + new_dirs
    return files + dirs


def find_file_and_dir(path: Path) -> tuple[list[Path], list[Path]]:
    files: list[Path] = []
    dirs: list[Path] = []
    for p2 in path.glob("*"):
        if p2.is_file():
            files.append(p2)
        else:
            dirs.append(p2)
    return files, dirs


def write_paths(save_dir: Path, paths: list[Path]):
    save_dir.mkdir(exist_ok=True)
    for p in paths:
        if p.is_file():
            shutil.copy(str(p), str(save_dir))
        else:
            save_dir2 = Path(f"{save_dir}/{p.name}")
            shutil.copytree(str(p), str(save_dir2))


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser = add_arguments(parser)
    main(**vars(parser.parse_args()))