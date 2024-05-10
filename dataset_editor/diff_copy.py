""" ２つのディレクトリの差分を求めてコピーする
"""
from __future__ import annotations
from typing import List
from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter
import shutil

import tqdm

def add_arguments(parser:ArgumentParser) -> ArgumentParser:
    parser.add_argument("dir1", type=str, help="dir1")
    parser.add_argument("dir2", type=str, help="dir2")
    parser.add_argument("mode", type=str, choices=["d1", "d2", "both"],
                        help="copy mode. d1 is dir1 only. d2 is dir2 only. both is both.")
    parser.add_argument("outdir", type=str, help="outdir")
    return parser


def main(*args, **kwargs):
    dir1 = Path(kwargs['dir1']).absolute()
    assert dir1.exists(), f"Not Found dir {dir1}"
    dir2 = Path(kwargs['dir2']).absolute()
    assert dir2.exists(), f"Not Found dir {dir2}"
    out_root_dir = Path(kwargs['outdir']).absolute()
    assert out_root_dir.exists(), f"Not Found dir {out_root_dir}"

    # find file paths
    file_paths_dir1 = [p for p in dir1.glob("*") if p.is_file()]
    file_paths_dir2 = [p for p in dir2.glob("*") if p.is_file()]

    # diff file paths dir1 and dir2
    name2path_dir1 = {p.name:p for p in file_paths_dir1}
    name2path_dir2 = {p.name:p for p in file_paths_dir2}
    set_of_file_names_dir1 = set([name for name in name2path_dir1.keys()])
    set_of_file_names_dir2 = set([name for name in name2path_dir2.keys()])
    file_names_only_dir1 = list(set_of_file_names_dir1 - set_of_file_names_dir2)
    file_names_only_dir2 = list(set_of_file_names_dir2 - set_of_file_names_dir1)
    file_paths_only_dir1 = [name2path_dir1[name] for name in file_names_only_dir1]
    file_paths_only_dir2 = [name2path_dir2[name] for name in file_names_only_dir2]

    # extract
    paths_list = []
    if kwargs['mode'] in ["d1", "both"]: paths_list.append(file_paths_only_dir1)
    if kwargs['mode'] in ["d2", "both"]: paths_list.append(file_paths_only_dir2)
    for file_paths in paths_list:
        extract_files(file_paths, out_root_dir)


def extract_files(file_paths:List[Path], out_root_dir:Path):
    if len(file_paths) == 0:
        return
    for file_path in tqdm.tqdm(file_paths):
        dir_name = "_".join(file_path.parts[-3:-1])
        out_dir: Path = out_root_dir.joinpath(dir_name)
        if not out_dir.exists(): out_dir.mkdir()
        shutil.copy(str(file_path), str(out_dir))
    print(f"extract {len(file_paths)} files to {out_dir}")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser = add_arguments(parser)
    main(**vars(parser.parse_args()))
