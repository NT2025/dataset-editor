DESCRIPTION='''
データセットに用いるファイルを扱うためのプログラム群。
----------------------------------------------------------------------
`numbering`:画像データを５桁の番号の名前に変更して新たに保存する関数。
`repair`:ファイル名が変更されたファイル(numbering2org.json等)に基づいて、対象画像ファイルをオリジナルの名前として新たに保存するプログラム.
`mkdir`:
`ext_latest`:データセット群からxmlファイルを一つディレクトリにコピーしてまとめる。
'''


import os
from argparse import ArgumentParser, _SubParsersAction
import subprocess

CURR_DIR = os.path.abspath(os.path.curdir)
FILE_DIR = os.path.abspath(os.path.dirname(__file__))
PYTHON_PATH = "python"

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    subparsers = parser.add_subparsers()

    add_numbering(subparsers)
    add_repair(subparsers)
    add_mkdir(subparsers)
    add_extract_latest(subparsers)

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args, parser)
    else:
        parser.print_help()


def add_numbering(subparsers:_SubParsersAction):
    description='''
    画像データを５桁の番号の名前に変更して新たに保存する関数.  
    '''
    epilog='''
    <詳細>-------------------------------------
    複数の画像ファイルを所有しているフォルダから画像ファイルのpathを読み込みリストに保存する。
    シャッフルフラグがONの場合ランダムにリストをシャッフルする。
    次に画像ディレクトリの親ディレクトリ上に`numberings`ディレクトリを作成する。
    画像ファイルを５桁の番号の名前にリネームしながら、`numberings`ディレクトリにコピーする。
    （この際に`prefix`引数が設定してある場合は`[prefix]_xxxxxx.jpg`のように数字の前にテキストが挿入される。)
    また、リネーム情報を辞書に記録する。`dict={number:org}`のように
    全てのファイルがコピーされた後にリネーム情報を`numbering2org.json`として画像ディレクトリの親ディレクトリに保存する。
    modeによってシンボリックリンクを作成するか、純粋にコピーするか選択する。
    '''
    parser:ArgumentParser = subparsers.add_parser(
        "numbering", description=description, epilog=epilog)
    parser.add_argument("img_dir", type=str)
    parser.add_argument("out_dir", type=str)
    parser.add_argument("-m", "--mode", choices=["absolute", "relative", "copy"], default="copy",
                        help="choosing safe mode . default is '''copy'''. '''copy''' mean copying file. \
                            '''absolute''' mean symlink that use absolute path. \
                            '''relative''' mean symlink that use relative path")
    parser.add_argument("-p", "--prefix", type=str, default="", 
                        help="add prefix for filename. Example is [prefix]_00001.jpg. default is ''")
    parser.add_argument("-s", "--shuffle", action="store_true", help="shuffle flag. default is False")

    def call(*args):
        _args = args[0]
        command = []
        command += [PYTHON_PATH]
        command += ["numbering_filename.py"]
        command += [os.path.abspath(_args.img_dir)]
        command += [os.path.abspath(_args.out_dir)]
        command += ["-p", _args.prefix]
        command += ["-s"] if _args.shuffle else []
        command += ["-m", _args.mode]
        subprocess.run(command, cwd=f"{FILE_DIR}")
    
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


if __name__ == "__main__":
    main()    
