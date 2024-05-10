""" データセットに用いるファイルを扱うためのプログラム群。
"""
from __future__ import annotations
DESCRIPTION= __doc__


import os
from argparse import ArgumentParser, _SubParsersAction, RawTextHelpFormatter
import subprocess
from pathlib import Path

import __add_path

CURR_DIR = Path(os.path.curdir).absolute()
FILE_DIR = Path(os.path.dirname(__file__)).absolute()
PYTHON_PATH = FILE_DIR.joinpath("../.venv/bin/python")


def add_arguments(parser: ArgumentParser):
    subparsers = parser.add_subparsers()

    add_numbering(subparsers)
    add_repair(subparsers)
    add_mkdir(subparsers)
    add_extract_latest(subparsers)
    add_separate_traindata(subparsers)
    add_reduce(subparsers)
    add_choice(subparsers)
    add_group(subparsers)
    add_diff_copy(subparsers)
    add_for_rsync(subparsers)
    add_move_into(subparsers)

    return parser


def main(*args, **kwargs):
    if 'handler' in kwargs.keys():
        handler = kwargs.pop('handler')
        handler(**kwargs)
    else:
        parser = ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)
        add_arguments(parser)
        parser.print_help()


def add_numbering(subparsers:_SubParsersAction):
    from dataset_editor import numbering_filename
    parser:ArgumentParser = subparsers.add_parser(
        "numbering", help=numbering_filename.__doc__)
    parser = numbering_filename.add_arguments(parser)

    def call(*args, **kwargs):
        numbering_filename.main(**kwargs)

    parser.set_defaults(handler=call)


def add_repair(subparsers:_SubParsersAction):
    from dataset_editor import repair_renamed_imgs
    parser:ArgumentParser = subparsers.add_parser(
        "repair",
        help=repair_renamed_imgs.__doc__,
        description=repair_renamed_imgs.__doc__
    )
    parser = repair_renamed_imgs.add_arguments(parser)

    def call(*args, **kwargs):
        repair_renamed_imgs.main(**kwargs)

    parser.set_defaults(handler=call)


def add_mkdir(subparsers:_SubParsersAction):
    from dataset_editor import separate_dataset_and_mkdir
    parser:ArgumentParser = subparsers.add_parser(
        "mkdir",
        help=separate_dataset_and_mkdir.__doc__,
        description=separate_dataset_and_mkdir.__doc__,
    )
    parser = separate_dataset_and_mkdir.add_arguments(parser)

    def call(*args, **kwargs):
        separate_dataset_and_mkdir.main(**kwargs)

    parser.set_defaults(handler=call)


def add_extract_latest(subparsers:_SubParsersAction):
    from dataset_editor import extract_latest
    parser:ArgumentParser = subparsers.add_parser(
        "ext_latest",
        help=extract_latest.__doc__,
        description=extract_latest.__doc__,
    )
    parser = extract_latest.add_arguments(parser)

    def call(*args, **kwargs):
        extract_latest.main(**kwargs)

    parser.set_defaults(handler=call)


def add_separate_traindata(subparsers:_SubParsersAction):
    from dataset_editor import separate_traindata
    parser:ArgumentParser = subparsers.add_parser(
        "separate_train",
        help=separate_traindata.__doc__,
        description=separate_traindata.__doc__,
    )
    parser = separate_traindata.add_arguments(parser)

    def call(*args, **kwargs):
        separate_traindata.main(**kwargs)

    parser.set_defaults(handler=call)


def add_reduce(subparsers:_SubParsersAction):
    from dataset_editor import reduce
    parser:ArgumentParser = subparsers.add_parser(
        "reduce",
        help=reduce.__doc__,
        description=reduce.__doc__,
    )
    reduce.add_arguments(parser)

    def call(*args, **kwargs):
        reduce.main(**kwargs)

    parser.set_defaults(handler=call)


def add_choice(subparsers:_SubParsersAction):
    description="ファイル群をランダムに抽出"
    parser:ArgumentParser = subparsers.add_parser(
        "choice", description=description
    )
    parser.add_argument("dir", type=str)
    parser.add_argument("num", type=int)

    def call(*args):
        _args = args[0]
        command = []
        command += [PYTHON_PATH]
        command += ["choice_random.py"]
        command += [os.path.abspath(_args.dir)]
        command += [str(_args.num)]
        subprocess.run(command, cwd=f"{FILE_DIR}")

    parser.set_defaults(handler=call)


def add_group(subparsers:_SubParsersAction):
    description = "'_'区切りの画像群を前２つの単語のディレクトリにまとめる"
    parser:ArgumentParser = subparsers.add_parser(
        "group", description=description
    )
    parser.add_argument("dir", type=str, help="画像群のディレクトリ")

    def call(*args):
        _args = args[0]
        command = []
        command += [PYTHON_PATH]
        command += ["group_histgram.py"]
        command += [os.path.abspath(_args.dir)]
        subprocess.run(command, cwd=f"{FILE_DIR}")

    parser.set_defaults(handler=call)


def add_diff_copy(subparsers:_SubParsersAction):
    description = "２つのディレクトリの差分を求めてコピーする"
    parser:ArgumentParser = subparsers.add_parser(
        "diff_copy", description=description, help=description
    )
    parser.add_argument("dir1", type=str, help="dir1")
    parser.add_argument("dir2", type=str, help="dir2")
    parser.add_argument("mode", type=str, choices=["d1", "d2", "both"],
                        help="copy mode. d1 is dir1 only. d2 is dir2 only. both is both.")
    parser.add_argument("outdir", type=str, help="outdir")

    def call(*args):
        _args = args[0]
        command = []
        command += [PYTHON_PATH]
        command += ["diff_copy.py"]
        command += [os.path.abspath(_args.dir1)]
        command += [os.path.abspath(_args.dir2)]
        command += [_args.mode]
        command += [os.path.abspath(_args.outdir)]
        subprocess.run(command, cwd=f"{FILE_DIR}")

    parser.set_defaults(handler=call)


def add_for_rsync(subparsers:_SubParsersAction):
    description = "アノテーション用データセットから保存用のモノを抽出してsymlinkで繋げる"
    parser:ArgumentParser = subparsers.add_parser(
        "for_rsync", description=description, help=description
    )
    parser.add_argument("src_dir", type=str, help="dataset dir")

    def call(*args):
        _args = args[0]
        command = []
        command += [PYTHON_PATH]
        command += ["mkdirs_for_rsync_dataset.py"]
        command += [os.path.abspath(_args.src_dir)]
        subprocess.run(command, cwd=f"{FILE_DIR}")

    parser.set_defaults(handler=call)


def add_move_into(subparsers:_SubParsersAction):
    description = " ディレクトリAにディレクトリを作成してファイルを全て移動させる。"
    parser:ArgumentParser = subparsers.add_parser(
        "move_into", description=description, help=description
    )
    parser.add_argument("tgt_dir", type=str, help="target dir")
    parser.add_argument("name", type=str, help="new dir name")

    def call(*args):
        _args = args[0]
        command = []
        command += [PYTHON_PATH]
        command += ["move_into.py"]
        command += [os.path.abspath(_args.tgt_dir)]
        command += [_args.name]
        subprocess.run(command, cwd=f"{FILE_DIR}")

    parser.set_defaults(handler=call)

if __name__ == "__main__":
    parser = ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)
    parser = add_arguments(parser)
    main(**vars(parser.parse_args()))
