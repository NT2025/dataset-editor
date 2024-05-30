""" 画像データを５桁の番号の名前に変更して新たに保存する関数.  
"""
from __future__ import annotations
DESCRIPTION=__doc__
EPILOG='''
<詳細>-------------------------------------
複数の画像ファイルを所有しているフォルダから画像ファイルのpathを読み込みリストに保存する。
シャッフルフラグがONの場合ランダムにリストをシャッフルする。
画像ファイルを５桁の番号の名前にリネームしながら、`numberings`ディレクトリにコピーする。
（この際に`prefix`引数が設定してある場合は`[prefix]_xxxxxx.jpg`のように数字の前にテキストが挿入される。)
また、リネーム情報を辞書に記録する。`dict={number:org}`のように
全てのファイルがコピーされた後にリネーム情報を`numbering2org.json`として画像ディレクトリの親ディレクトリに保存する。
modeによってシンボリックリンクを作成するか、純粋にコピーするか選択する。
'''

import os
from pathlib import Path
import shutil
import glob
from argparse import ArgumentParser, RawTextHelpFormatter
import random
import json 

import tqdm


def add_arguments(parser: ArgumentParser):
    parser.add_argument("img_dir", type=str)
    parser.add_argument("out_dir", type=str)
    parser.add_argument("-m", "--mode", choices=["absolute", "relative", "copy"], default="copy",
                        help="choosing safe mode . default is '''copy'''. '''copy''' mean copying file. \
                            '''absolute''' mean symlink that use absolute path. \
                            '''relative''' mean symlink that use relative path")
    parser.add_argument("-p", "--prefix", type=str, default="", 
                        help="add prefix for filename. Example is [prefix]_00001.jpg. default is ''")
    parser.add_argument("-s", "--shuffle", action="store_true", help="shuffle flag. default is False")

    return parser


def main(*args, **kwargs):

    # check_src_dir
    src_dir = Path(kwargs['img_dir']).absolute()
    assert src_dir.is_dir()

    # check out dir
    out_dir = Path(f"{kwargs['out_dir']}").absolute()
    if not out_dir.exists():
        assert out_dir.parent.exists()
        out_dir.mkdir()
    out_imgs_dir = Path(f"{kwargs['out_dir']}/numberings").absolute()
    if not out_imgs_dir.exists():
        out_imgs_dir.mkdir()

    # mode
    mode = kwargs['mode']
    print(f"save mode is {mode}")
    if mode == "absolute":
        save_func = link_as_absolute
    elif mode == "relative":
        save_func = link_as_relative
    else: # mode == "copy"
        save_func = copy_file

    # get img paths
    suffixes = [".jpg", ".JPG", ".png", ".PNG"]
    img_paths = []
    for suffix in suffixes:
        img_paths += [ Path(f) for f in glob.glob(f"{src_dir}/*{suffix}")]
    print(f"NumImages {len(img_paths)}")
    img_paths.sort()

    # shuffle
    if kwargs['shuffle']:
        random.shuffle(img_paths)

    # numbering
    filename_prefix = f"{kwargs['prefix']}" if f"{kwargs['prefix']}" == "" else f"{kwargs['prefix']}_"
    out_name2img_name = {}
    for num, img_path in enumerate(tqdm.tqdm(img_paths)):
        out_name = f"{num+1:>05}{img_path.suffix}"
        out_file = Path(f"{out_imgs_dir}/{filename_prefix}{out_name}")

        save_func(img_path, out_file)

        img_name = img_path.name
        out_name2img_name[out_file.name] = img_name
    txt = json.dumps(out_name2img_name, indent=2)
    json_file = Path(f"{out_dir}/numbering2org.json")
    with json_file.open("w") as f:
        f.write(txt)


def link_as_absolute(src_file:Path, dst_file:Path):
    _src = src_file.resolve()
    _dst = dst_file.absolute()
    os.symlink(_src, _dst)


def link_as_relative(src_file:Path, dst_file:Path):
    _src = src_file.absolute()
    _dst = dst_file.absolute()
    _src = os.path.relpath(_src, _dst.parent)
    os.symlink(_src, _dst)


def copy_file(src_file:Path, dst_file:Path):
    _src = src_file.absolute()
    _dst = dst_file.absolute()
    shutil.copy(_src, _dst)


if __name__ == "__main__":
    parser = ArgumentParser(description=DESCRIPTION, epilog=EPILOG, formatter_class=RawTextHelpFormatter)
    parser = add_arguments(parser)
    main(**vars(parser.parse_args()))
