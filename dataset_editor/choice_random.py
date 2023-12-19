""" 対象ディレクトリのファイル群をランダムに抽出する
"""
from pathlib import Path
from argparse import ArgumentParser
import random
import shutil

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("dir", type=str, help="ファイルを含むディレクトリ")
    parser.add_argument("num", type=int, help="ランダム抽出数")

    return vars(parser.parse_args())


def main(*args, **kwargs):
    data_dir = Path(kwargs["dir"]).absolute()
    assert data_dir.exists()
    num_choice = int(kwargs["num"])

    print(f"{num_choice} 個のデータを以下のディレクトリから抽出します")
    print(f"\t{data_dir}")

    data_paths = [ p for p in data_dir.glob("*") if p.is_file() ]
    assert len(data_paths) > 0
    assert len(data_paths) >= num_choice

    data_paths = random.sample(data_paths, num_choice)

    out_dir = Path(f"{data_dir}_random_{num_choice}")
    print("抽出したデータを以下のディレクトリに保存します。")
    print(f"\t{out_dir}")
    assert not out_dir.exists()
    out_dir.mkdir()
    for path in data_paths:
        shutil.copy(path, out_dir)

    print("終了しました。")


if __name__ == "__main__":
    main(**parse_args())