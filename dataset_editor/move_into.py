""" ディレクトリAにディレクトリを作成してファイルを全て移動させる。
"""
from __future__ import annotations
from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter
import shutil


def add_arguments(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument("tgt_dir", type=str, help="target dir")
    parser.add_argument("name", type=str, help="new dir name")
    return parser


def main(*args, **kwargs):
    tgt_dir = Path(kwargs['tgt_dir'])
    assert tgt_dir
    new_dir_name: str = kwargs['name']

    new_dir: Path = tgt_dir.joinpath(new_dir_name)

    tgt_files: list[Path] = [p for p in tgt_dir.glob("*") ]

    new_dir.mkdir(exist_ok=True)
    for p in tgt_files:
        shutil.move(str(p), new_dir)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser: ArgumentParser = add_arguments(parser)
    main(**vars(parser.parse_args()))
