"""アノテーション用データセットから保存用のモノを抽出してsymlinkで繋げる
"""
from __future__ import annotations
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path


keywords_for_file = [
    ".sqlite3",
    "README.txt",
]
keywords_for_dir = [
    "train",
    "test",
    "val",
    "invalid",
    "sub",
    "sample",
    "example"
]

def add_arguments(parser:ArgumentParser) -> ArgumentParser:
    parser.add_argument("src_dir", type=str, help="dataset dir")
    return parser


def main(*args, **kwargs):
    src_dir = Path(kwargs['src_dir'])
    assert src_dir.is_dir()

    paths: list[Path] = find_paths(src_dir)
    assert len(paths) > 0, f"Invalid dir is Dataset"

    # symlink
    out_dir: Path = src_dir.joinpath(f"for_rsync/{src_dir.name}")
    print(f"# mkdir for save '{out_dir}'")
    out_dir.mkdir(parents=True)
    print(f"# symlink '{len(paths)}' paths to'{out_dir}'")
    for p in paths:
        out_dir.joinpath(p.name).symlink_to(p)

    print("# *** finish !! *** ")


def find_paths(src_dir: Path) -> list[Path]:
    # find kwd file and dirs
    paths: list[Path] = []
    kwds_list: list[list[str]] = [keywords_for_file, keywords_for_dir]
    kwd2is_found: dict[str, bool] = {}
    for kwds in kwds_list:
        for kwd in kwds:
            finded_paths = list(src_dir.glob(f"*{kwd}*"))
            if len(finded_paths) == 0:
                kwd2is_found[kwd] = False
                continue
            kwd2is_found[kwd] = True
            paths += finded_paths
    print("is_found: keywords")
    print("------------------")
    for kwd, is_found in kwd2is_found.items():
        print(f"{is_found:<7}: {kwd}")
    print("------------------")

    # del equal
    paths = list(set(paths))
    print(f"# Num Found is {len(paths)}")
    return paths



if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser: ArgumentParser = add_arguments(parser)
    main(**vars(parser.parse_args()))

