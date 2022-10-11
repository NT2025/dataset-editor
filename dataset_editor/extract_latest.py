DESCRIPTION='''
<概要>
データセット群からxmlファイルを一つのディレクトリにコピーしてまとめる
'''
EPILOG='''
<詳細説明>-----------------------------------------------
以下のようなディレクトリ構造を持つデータセット群を対象に最新のxmlファイルを一つのディレクトリにまとめる。
[datasets/dataset_xxxxx_xxxxx/anns/latest].
コピー先はout_dirで指定されたディレクトリ上にannsというディレクトリを作成してソコにコピーを行う。
同名のファイルは上書きされる。
'''
import os
import shutil
import sys
from pathlib import Path
from argparse import ArgumentParser
import logging
import glob

logging.basicConfig(level=logging.INFO)

def parse_args():
    parser = ArgumentParser(description=DESCRIPTION, epilog=EPILOG)
    parser.add_argument("datasets", type=str)
    parser.add_argument("out_dir", type=str)

    dict_args = vars(parser.parse_args())
    return dict_args

def main(dict_args):
    # 対象datasetsディレクトリの存在確認
    datasets_dir = Path(dict_args['datasets']).absolute()
    if not datasets_dir.exists():
        logging.error(f"not found {datasets_dir}")
        sys.exit(0)

    # セーブディレクトリの作成
    out_dir = Path(dict_args['out_dir']).absolute()
    if not out_dir.exists():
        logging.error(f"not found {out_dir}")
        sys.exit(0)
    save_dir = Path(f"{out_dir}/anns")
    if not save_dir.exists():
        save_dir.mkdir()
        logging.info(f"mkdir {save_dir}")

    # 対象ディレクトリの下位にdatasetディレクトリを所持しているか確認
    dataset_dirs = [Path(p) for p in glob.glob(f"{datasets_dir}/dataset_*", )]
    if len(dataset_dirs) == 0:
        logging.error(f"{datasets_dir} does not have dirs")
        sys.exit(0)

    # アノテーションディレクトリ`latest`からxmlをコピーを用いて抽出
    for _dir in dataset_dirs:
        try:
            anns_dir = Path(glob.glob(f"{_dir}/ann*")[0]) # ann or anns
        except:
            logging.info(f"{_dir} not have anns dir")
            continue

        ann_dir = Path(f"{anns_dir}/latest")
        if not ann_dir.exists():
            logging.info(f"{anns_dir} not have latest dir")
            continue

        xml_paths = [ Path(p) for p in glob.glob(f"{ann_dir}/*")]
        if len(xml_paths) == 0:
            logging.info(f"{ann_dir} not have xml")
            continue

        for p in xml_paths:
            shutil.copy(p, save_dir)
            logging.info(f"copy {p} -> {save_dir}")


if __name__ == "__main__":
    dict_args = parse_args()
    main(dict_args)
