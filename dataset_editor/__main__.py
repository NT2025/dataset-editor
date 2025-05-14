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
    break_nest(subparsers)
    delete(subparsers)
    add_intersection(subparsers)

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
    from dataset_editor import choice_random
    parser:ArgumentParser = subparsers.add_parser(
        "choice",
        help=choice_random.__doc__,
        description=choice_random.__doc__
    )
    parser = choice_random.add_arguments(parser)

    def call(*args, **kwargs):
        choice_random.main(**kwargs)

    parser.set_defaults(handler=call)


def add_group(subparsers:_SubParsersAction):
    from dataset_editor import group_histgram
    parser:ArgumentParser = subparsers.add_parser(
        "group",
        help=group_histgram.__doc__,
        description=group_histgram.__doc__
    )
    parser = group_histgram.add_arguments(parser)

    def call(*args, **kwargs):
        group_histgram.main(**kwargs)

    parser.set_defaults(handler=call)


def add_diff_copy(subparsers:_SubParsersAction):
    from dataset_editor import diff_copy
    parser:ArgumentParser = subparsers.add_parser(
        "diff_copy",
        help=diff_copy.__doc__,
        description=diff_copy.__doc__
    )
    parser = diff_copy.add_arguments(parser)

    def call(*args, **kwargs):
        diff_copy.main(**kwargs)

    parser.set_defaults(handler=call)


def add_for_rsync(subparsers:_SubParsersAction):
    from dataset_editor import mkdirs_for_rsync_dataset
    parser:ArgumentParser = subparsers.add_parser(
        "for_rsync", 
        help=mkdirs_for_rsync_dataset.__doc__,
        description=mkdirs_for_rsync_dataset.__doc__
    )
    parser = mkdirs_for_rsync_dataset.add_arguments(parser)

    def call(*args, **kwargs):
        mkdirs_for_rsync_dataset.main(**kwargs)

    parser.set_defaults(handler=call)


def add_move_into(subparsers:_SubParsersAction):
    from dataset_editor import move_into
    parser:ArgumentParser = subparsers.add_parser(
        "move_into",
        help=move_into.__doc__,
        description=move_into.__doc__,
    )
    parser = move_into.add_arguments(parser)

    def call(*args, **kwargs):
        move_into.main(**kwargs)

    parser.set_defaults(handler=call)


def break_nest(subparsers:_SubParsersAction):
    from dataset_editor import break_nest
    parser:ArgumentParser = subparsers.add_parser(
        "break_nest",
        help=break_nest.__doc__,
        description=break_nest.__doc__,
    )
    parser = break_nest.add_arguments(parser)

    def call(*args, **kwargs):
        break_nest.main(**kwargs)

    parser.set_defaults(handler=call)


def delete(subparsers:_SubParsersAction):
    from dataset_editor import delete
    parser:ArgumentParser = subparsers.add_parser(
        "delete",
        help=delete.__doc__,
        description=delete.__doc__,
    )
    parser = delete.add_arguments(parser)

    def call(*args, **kwargs):
        delete.main(**kwargs)

    parser.set_defaults(handler=call)


def add_intersection(subparsers:_SubParsersAction):
    from dataset_editor import intersection
    parser:ArgumentParser = subparsers.add_parser(
        "intersection",
        help=intersection.__doc__,
        description=intersection.__doc__,
    )
    parser = intersection.add_arguments(parser)

    def call(*args, **kwargs):
        intersection.main(**kwargs)

    parser.set_defaults(handler=call)

if __name__ == "__main__":
    parser = ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)
    parser = add_arguments(parser)
    main(**vars(parser.parse_args()))
