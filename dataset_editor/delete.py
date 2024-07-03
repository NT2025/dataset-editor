""" データの指定ナンバー範囲を削除する
"""
from __future__ import annotations
from argparse import ArgumentParser
from pathlib import Path
import shutil


EPILOG = """
対象データは '*_00100.jpg' のようなファイル名のみ。
その他のファイルデータはそのままコピーする。
"""


def add_arguments(parser: ArgumentParser) -> ArgumentParser:
    parser.epilog = EPILOG
    parser.add_argument("dir", type=str, help="ファイルを含むディレクトリ")
    parser.add_argument("start", type=int, help="start number")
    parser.add_argument("end", type=int, help="end number")
    return parser


def main(*args, **kwargs):
    ### parse args
    data_dir = Path(kwargs['dir'])
    assert data_dir.exists()
    start_num = int(kwargs['start'])
    end_num = int(kwargs['end'])

    ### get file paths
    datum_paths: list[Path] = [p for p in data_dir.glob("*") if p.is_file()]
    if len(datum_paths) == 0:
        print(f"Not Data in {data_dir}")
        return

    ### delete paths
    print(f"Pre Delete num file = {len(datum_paths)}")
    datum_paths: list[Path] = delete(datum_paths, start_num, end_num)
    print(f"Post Delete num file = {len(datum_paths)}")

    ### save paths
    out_dir = Path(f"{data_dir}_deleted")
    save_paths(datum_paths, out_dir)

    print("finish ! ! !")


def delete(paths: list[Path], start_num: int, end_num: int):
    dst_paths: list[Path] = []
    stem2path: dict[str, Path] = {p.stem:p for p in paths}

    for stem in stem2path.keys():
        words = stem.split("_")
        word = words[-1]
        try:
            num = int(word)
        except:
            dst_paths.append(stem2path[stem])
        else:
            if start_num <= num <= end_num:
                continue
            dst_paths.append(stem2path[stem])

    dst_paths.sort()
    return dst_paths


def save_paths(paths: list[Path], out_dir: Path):
    assert out_dir.parent.exists()
    out_dir.mkdir(exist_ok=True)
    for p in paths:
        shutil.copy(str(p), str(out_dir))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser = add_arguments(parser)
    main(**vars(parser.parse_args()))