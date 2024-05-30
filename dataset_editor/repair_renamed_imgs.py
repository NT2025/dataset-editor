""" ファイル名が変更されたファイル(numbering2org.json等)に基づいて、対象画像ファイルをオリジナルの名前として新たに保存するプログラム.
"""
from __future__ import annotations
DESCRIPTION=__doc__
EPILOG='''
<詳細>------------------------------------------------------
リネーム情報(numbering2org.json)を読み込む。
画像ディレクトリの親ディレクトリ上に保存用ディレクトリを作成する。
画像ファイルをコピーして、リネーム情報を使って数字ネームから元ネームに変換して保存用ディレクトリに保存する。
画像ディレクトリ内にリネーム情報のファイルが見つからない場合は無視される。
'''

import json
from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter
import shutil
import glob
from typing import List, Dict
import sys
from xml.dom import NotFoundErr

import tqdm


def add_arguments(parser: ArgumentParser):
    parser.add_argument("imgdir", type=str, help="img dir")
    parser.add_argument("json", type=str, help="renamed2org.json")

    return parser


def main(*args , **kwargs):
    imgdir = Path(kwargs['imgdir']).absolute()
    check_input_path(imgdir)
    rename_info_file = Path(kwargs['json']).absolute()
    check_input_path(rename_info_file)
    
    save_dir = imgdir.parent / Path("org_imgs")
    assert not save_dir.exists(), save_dir
    save_dir.mkdir()

    try:
        renamed2org = load_renamed2org_json(rename_info_file)

        copy_as_orgname(renamed2org, imgdir, save_dir)
    except Exception as e:
        print(e)
        print(f"[Warning] remove {save_dir}")
        print("[Warning] system exists")
        sys.exit(1)


def check_input_path(path:Path):
    assert path.exists(), path
    print(f"[Info] use {path}")


def load_renamed2org_json(path:Path) -> Dict[str, str]:
    rename2org = load_json(path)
    return rename2org


def load_json(path:Path):
    assert path.exists(), path
    with path.open("r") as f:
        json_data = json.load(f)
    return json_data



def copy_as_orgname(renamed2org:Dict[str, str], imgdir:Path, save_dir:Path):
    """ # copy as orgname
    ファイル名が変更された情報(renamed2org)に基づいて、対象画像ファイルをオリジナルの名前として保存する.  
    コレはアノテーション作業用に元のファイルの名前をナンバリングした名前に変更する処理を行った際に行われた処理を巻き戻す処理である。

    Args:
        renamed2org (Dict[str, str]): 変更された名前からオリジナルの名前への辞書. renamed2org.jsonファイルから読み込んだデータ。
        imgdir (Path): 対象元ディレクトリ
        save_dir (Path): 保存先ディレクトリ
    """
    # 名前変更済みファイルのパス群を取得
    suffixes = set([Path(key).suffix for key in renamed2org.keys()])
    img_paths:List[Path] = [] 
    for suffix in suffixes:
        img_paths += [Path(p) for p in glob.glob(f"{imgdir}/*{suffix}")]
    if len(img_paths) == 0:
        raise FileNotFoundError(f"{imgdir}/*{suffixes}")
    
    # オリジナルの名前としてコピーする
    for img_path in tqdm.tqdm(img_paths):
        if img_path.name not in renamed2org.keys():
            print(f"[Info] not Found {img_path} in renamed2org")
            continue
        org_name = renamed2org[img_path.name]
        save_path = Path(f"{save_dir}/{org_name}")
        shutil.copy(img_path, save_path)


if __name__ == "__main__":
    parser = ArgumentParser(description=DESCRIPTION, epilog=EPILOG, formatter_class=RawTextHelpFormatter)
    parser = add_arguments(parser)
    main(**vars(parser.parse_args()))

