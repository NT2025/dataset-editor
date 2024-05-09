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
    description='''
    ファイル名が変更されたファイル(numbering2org.json等)に基づいて、対象画像ファイルをオリジナルの名前として新たに保存するプログラム.
    '''
    epilog='''
    <詳細>----------------------------------------
    リネーム情報(numbering2org.json)を読み込む。
    画像ディレクトリの親ディレクトリ上に保存用ディレクトリを作成する。
    画像ファイルをコピーして、リネーム情報を使って数字ネームから元ネームに変換して保存用ディレクトリに保存する。
    画像ディレクトリ内にリネーム情報のファイルが見つからない場合は無視される。
    '''
    parser:ArgumentParser = subparsers.add_parser(
        "repair", description=description, epilog=epilog
    )
    parser.add_argument("imgdir", type=str, help="img dir")
    parser.add_argument("json", type=str, help="renamed2org.json")

    def call(*args):
        _args = args[0]
        print(_args)
        command = []
        command += [PYTHON_PATH]
        command += ["repair_renamed_imgs.py"]
        command += [os.path.abspath(_args.imgdir)]
        command += [os.path.abspath(_args.json)]
        subprocess.run(command, cwd=f"{FILE_DIR}")
    
    parser.set_defaults(handler=call)


def add_mkdir(subparsers:_SubParsersAction):
    description='''
    ナンバリングされたファイルを所持するディレクトリを指定のファイル数ごとに分割するプログラム。
    '''
    epilog='''
    ＜詳細説明＞------------------------------------------------
    まず`file_dir`で指定されたディレクトリ上のファイルを読み込む。
    （このディレクトリは`numbering_filename.py`によってナンバリングされている)
    読み込んだファイルを指定ファイル数ごとにグループにまとめる。
    次に引数`output`で指定されたディレクトリの下に`datasets`ディレクトリを作成する。
    その後`datasets`ディレクトリ下に`dataset_xxxxx_XXXXX`というディレクトリをグループ毎に作成する。
    （このディレクトリのxxxxxはグループの最小のナンバーでXXXXXは最大のナンバーである。）
    続けて`dataset_xxxxx_XXXXX`ディレクトリ下に`imgs_xxxxx_XXXXX`というディレクトリを作成する。
    そして`imgs_xxxxx_XXXXX`下にグループ内の画像ファイルのシンボリックリンクを作成する(参照リンクで)
    '''
    parser:ArgumentParser = subparsers.add_parser(
        "mkdir", description=description, epilog=epilog)
    parser.add_argument("file_dir", type=str)
    parser.add_argument("-n", "--devide_number", type=int, default=500, 
                        help="devided number for dataset. default is 500")
    parser.add_argument("-o", "--output", type=str, default=f"{CURR_DIR}",
                        help=f"output root dir. default {CURR_DIR}")

    def call(*args):
        _args = args[0]
        command = []
        command += [PYTHON_PATH] 
        command += ["separate_dataset_and_mkdir.py"]
        command += [os.path.abspath(_args.file_dir)]
        command += ["-n", str(_args.devide_number)]
        command += ["-o", os.path.abspath(_args.output)]
        subprocess.run(command, cwd=f"{FILE_DIR}")
    
    parser.set_defaults(handler=call)


def add_extract_latest(subparsers:_SubParsersAction):
    description='''
    <概要>
    データセット群からxmlファイルを一つのディレクトリにコピーしてまとめる
    '''
    epilog='''
    <詳細説明>-----------------------------------------------
    以下のようなディレクトリ構造を持つデータセット群を対象に最新のxmlファイルを一つのディレクトリにまとめる。
    [datasets/dataset_xxxxx_xxxxx/anns/all].
    コピー先はout_dirで指定されたディレクトリ上にannsというディレクトリを作成してソコにコピーを行う。
    同名のファイルは上書きされる。
    '''
    parser:ArgumentParser = subparsers.add_parser(
        "ext_latest", description=description, epilog=epilog)
    parser.add_argument("datasets", type=str)
    parser.add_argument("out_dir", type=str)

    def call(*args):
        _args = args[0]
        command = []
        command += [PYTHON_PATH] 
        command += ["extract_latest.py"]
        command += [os.path.abspath(_args.datasets)]
        command += [os.path.abspath(_args.out_dir)]
        subprocess.run(command, cwd=f"{FILE_DIR}")
    
    parser.set_defaults(handler=call)


def add_separate_traindata(subparsers:_SubParsersAction):
    description='''
    データ群を学習用、テスト用、検証用に分割する。
    '''
    epilog='''
    '''
    parser:ArgumentParser = subparsers.add_parser(
        "separate_train", description=description, epilog=epilog)
    parser.add_argument("dataset_dir", type=str, help="dataset dir path")
    parser.add_argument("output_dir", type=str, help="output dir path")
    parser.add_argument("--ratio", type=float, default=0.4, help="test ratio")
    parser.add_argument("--not_val", action="store_true")
    parser.add_argument("--random", action="store_true", help="ランダムフラグ. このフラグがONの時はデータに関係なくランダムに分割する")
    parser.add_argument("--log_level", type=str, choices=["info", "debug"], default="info", help="log level")

    def call(*args):
        _args = args[0]
        command = []
        command += [PYTHON_PATH] 
        command += ["separate_traindata.py"]
        command += [os.path.abspath(_args.dataset_dir)]
        command += [os.path.abspath(_args.output_dir)]
        command += ["--ratio", str(_args.ratio)]
        if _args.not_val:
            command += ["--not_val"]
        if _args.random:
            command += ["--random"]
        command += ["--log_level", _args.log_level]
        subprocess.run(command, cwd=f"{FILE_DIR}")
    
    parser.set_defaults(handler=call)


def add_reduce(subparsers:_SubParsersAction):
    description="""
        データセットを何個か飛ばしで抽出することでデータセットを削減する。
        主に動画を画像化した際にあまり変化のないフレームが発生するので、削減する目的で使用する。
        抽出されたデータセットは対象ディレクトリ_reducedという名称のディレクトリに保存される
        """
    epilog='''
    '''
    parser:ArgumentParser = subparsers.add_parser(
        "reduce", description=description, epilog=epilog)
    parser.add_argument("data_dir", type=str)
    parser.add_argument("--skip_num", type=int, default=2)


    def call(*args):
        _args = args[0]
        command = []
        command += [PYTHON_PATH] 
        command += ["reduce.py"]
        command += [os.path.abspath(_args.data_dir)]
        command += ["--skip_num", str(_args.skip_num)]
        subprocess.run(command, cwd=f"{FILE_DIR}")

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
