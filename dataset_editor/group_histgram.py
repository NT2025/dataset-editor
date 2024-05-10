""" '_'区切りの画像群を前２つの単語のディレクトリにまとめる
"""
from __future__ import annotations
import os
from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter
import shutil
import subprocess
import time


def add_arguments(parser: ArgumentParser):
    parser.add_argument("dir", type=str, help="画像群のディレクトリ")

    return parser


def main(*args, **kwargs):
    src_dir = Path(kwargs["dir"]).absolute()
    assert src_dir.exists()

    data_paths = [ p for p in src_dir.glob("*") if p.is_file() ]
    assert len(data_paths) > 0

    name2paths = grouping_histgram(data_paths)
    show_name2paths2(name2paths)

    is_exe = ask_exe()
    if is_exe:
        print("分割を実行します。")
        move_files(name2paths)
    print("\n正常に終了します。")


def grouping_histgram(data_paths):
    name2paths = {}
    for path in data_paths:
        name = "_".join(path.stem.split("_")[:2])
        if name not in name2paths.keys():
            name2paths[name] = []
        name2paths[name].append(path)
    return name2paths


def show_name2paths(name2paths):
    pre_name = "None"
    for name, paths in name2paths.items():
        for path in paths:
            if name == pre_name:
                num_name = len(name)
                name = " "*num_name
            print(f"{name} : {path}")
            pre_name = name


def show_name2paths2(name2paths):
    pre_name = "None"
    txt = ""
    for name, paths in name2paths.items():
        for path in paths:
            if name == pre_name:
                num_name = len(name)
                name = " "*num_name
            txt += f"{name} : {path}\n"
            pre_name = name
    log_dir = Path("/tmp/move_histgram_log.txt")
    with log_dir.open("w") as f:
        f.write(txt)
    print("分割情報に関しては less で表示します。操作は less を参照してください。")
    time.sleep(3)
    subprocess.run(["less", log_dir])


def move_files(name2paths):
    print("分割情報に沿って分割を実行します。")
    for name, paths in name2paths.items():
        hist_dir = paths[0].parent.joinpath(name)
        if not hist_dir.exists():
            hist_dir.mkdir()
        for path in paths:
            shutil.move(str(path), hist_dir)


def ask_exe():
    while(True):
        try:
            print("分割情報を参照に実行に移しますか？(y/n) >>", end="")
            recv = input()
        except KeyboardInterrupt:
            is_exe = False
            break
        else:
            if recv in ["y", "yes", "Y"]:
                is_exe = True
                break
            elif recv in ["n", "no", "N"]:
                is_exe = False
                break
    return is_exe


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser = add_arguments(parser)
    main(**vars(parser.parse_args()))
