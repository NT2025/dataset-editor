"""
データセットを何個か飛ばしで抽出することでデータセットを削減する。
主に動画を画像化した際にあまり変化のないフレームが発生するので、削減する目的で使用する。
抽出されたデータセットは対象ディレクトリ_reducedという名称のディレクトリに保存される
"""

from pathlib import Path
import shutil
from argparse import ArgumentParser, RawTextHelpFormatter


def parse_args():
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument("data_dir", type=str)
    parser.add_argument("--skip_num", type=int, default=2)
    return vars(parser.parse_args())


def main(*args, **kwargs):
    # 対象データディレクトリの存在確認
    data_dir = Path(kwargs["data_dir"]).absolute()
    assert data_dir.absolute()
    # 飛ばし数の確認
    skip_num = int(kwargs["skip_num"])
    assert skip_num > 1

    # データの読み込み
    data_paths = [ data for data in data_dir.glob("*") if data.is_file() ]
    assert len(data_paths) > 0
    data_paths.sort()
    num_data = len(data_paths)

    # 保存用ディレクトリの作成
    save_dir = Path(f"{data_dir}_reduced")
    save_dir.mkdir(exist_ok=True)

    # 保存用ディレクトリにコピー
    print("copying...")
    for id, data_path in enumerate(data_paths[::skip_num], start=1):
        shutil.copy(data_path, save_dir)
        print(f"\r{id:>5}/{num_data:>5}, {data_path}->{save_dir}", end="")
    print("\ndone")


if __name__ == "__main__":
    main(**parse_args())