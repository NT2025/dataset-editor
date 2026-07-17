"""日時別画像群からアノテーション用に画像データセットを構築する(make_img_dataset)
"""
from typing import List, Dict, Literal
from argparse import ArgumentParser
from pathlib import Path
import math
import pprint
import os
import tqdm
import logging
import json


from libs import devide


def add_arguments(parser: ArgumentParser) -> ArgumentParser:
    # 引数をここに記述
    parser.description = "画像群をYYYYMMDD_HHMMSS毎に平等に抜き出してグループ化してデータセットとして再構成する"
    parser.add_argument('img_dir', type=str, help='img dir')
    parser.add_argument('-n', '--num_ann', type=int, default=500, help='一つのグループに含まれるファイルの目安.デフォルト500')
    parser.add_argument('-d', '--dst_root_dir', type=str, default=os.curdir, help='出力のルートディレクトリ。デフォルトは./')
    parser.add_argument("-p", "--prefix", type=str, default="", help="リネームされる際の接頭辞。デフォルトは''")
    parser.add_argument('--debug', action="store_true", help="デバック情報表示モード")
    return parser


def main(*args, **kwargs):
    if kwargs['debug']:
        logging.basicConfig(level=logging.DEBUG, force=True)
    else:
        logging.basicConfig(level=logging.INFO, force=True)

    # 引数関係の処理
    logging.info("<-kwargs-----")
    logging.info(pprint.pformat(kwargs))
    logging.info("-----kwargs->")
    kwargs['img_dir']
    img_dir: Path = Path(kwargs['img_dir'])
    assert img_dir.exists()
    assert img_dir.is_dir()
    dst_root_dir: Path = Path(kwargs['dst_root_dir'])
    assert dst_root_dir.exists()
    assert dst_root_dir.is_dir()
    num_ann = kwargs['num_ann']
    assert num_ann > 0
    prefix = kwargs['prefix']


    ## 対象ディレクトリ内から画像ファイルを取得
    img_paths: List[Path] = get_img_paths(img_dir, sort='asc')

    ## 分割グループ毎に画像パスをまとめる
    ext_group2paths= grouping(img_paths, num_ann)

    ## 抽出グループにナンバリング(gropuN_NUMBER)する。
    ## ナンバリングと元データの紐付けを行っておく
    name2new_name: Dict[str, str] = make_name2new_name(ext_group2paths, prefix)
    logging.debug(pprint.pformat(name2new_name))

    ## 最終的にデータセットディレクトリを作成してソコに保存する。
    copy_for_new_dir_with_rename(ext_group2paths, dst_root_dir, name2new_name)

    ## ナンバリング紐づけを保存する。
    ## これはdataset_editor/repairで元に戻す用
    new_name2name: Dict[str, str] = {v:k for k,v in name2new_name.items()}
    numbering_json_path = dst_root_dir.joinpath("new_name2name.json")
    with numbering_json_path.open("w") as f:
        json.dump(new_name2name, f, indent="\t")

    print("プログラムを終了します。")


def get_img_paths(img_dir:Path, sort:Literal['asc', 'desc']='asc'):
    """ディレクトリから画像ファイルのパスを取得する。
    対応フォーマットは`jpg`, `png`.
    """
    if sort not in ['asc', 'desc']:
        raise ValueError(f"arguments")
    img_paths: List[Path] = []
    fmts = ['png', 'jpg']
    for fmt in fmts:
        img_paths += list(img_dir.glob(f"*.{fmt}"))
    assert len(img_paths) > 0
    is_reverse = False if sort == 'asc' else True
    img_paths.sort(reverse=is_reverse)

    return img_paths


def grouping(img_paths: List[Path], num_ann: int):
    """ 画像パスをYYYYMMDD_HHMMSSごとにグループ分けして、その後そこから合計がnum_annに近づくように平等に抽出する。
    """
    num_img_paths = len(img_paths)
    ## 対象画像をグループ分けする
    ## 対象画像ファイル名の想定はYYYYMMDD_HHMMSS_frame-numberとする
    ## なのでグループ分けはYYYYMMDD_HHMMSSの毎になる
    img_group2paths: Dict[str, List[Path]] = grouping_datetime_filename(img_paths)

    ## 1グループあたりの目安枚数に基づいてストライド数を決定して各グループから抽出して抽出グループとしてまとめる
    num_img_paths: int = sum([len(v) for v in img_group2paths.values()])
    stride_num: int = math.ceil(num_img_paths/num_ann)
    ext_group2paths: Dict[str, List[Path]] = regroup_by_stride(img_group2paths, stride_num)

    ### 確認用
    logging.info("group番号:画像数")
    sum_v = 0
    for k, v in ext_group2paths.items():
        logging.info(f"\t{k}: {len(v)}")
        sum_v += len(v)
    logging.info("以下は元画像数とグループされた数が同一になるか確認用出力。")
    logging.info(f"\t元画像数、グループ分後の総数 = {len(img_paths)}, {sum_v}")

    return ext_group2paths


def grouping_datetime_filename(img_paths: List[Path]):
    '''対象画像をグループ分けする.
    対象画像ファイル名の想定はYYYYMMDD_HHMMSS_frame-numberとする.
    なのでグループ分けはYYYYMMDD_HHMMSSの毎になる.
    '''
    img_group2paths: Dict[str, List[Path]] = {}
    for img_path in img_paths:
        stem_words: List[str] = img_path.stem.split("_")
        assert len(stem_words) >= 3
        yyyymmdd_hhmmss = "{}_{}".format(stem_words[0], stem_words[1])
        if yyyymmdd_hhmmss not in img_group2paths.keys():
            img_group2paths[yyyymmdd_hhmmss] = []
        img_group2paths[yyyymmdd_hhmmss].append(img_path)
    img_group_names: List[str] = [k for k in img_group2paths.keys()]
    img_group_names.sort()
    logging.debug(f"img_group_names, {img_group_names}")
    return img_group2paths


def regroup_by_stride(img_group2paths:Dict[str, List[Path]], stride_num: int):
    '''アノテーション単位に基づいて各グループから抽出して抽出グループとしてまとめる
    '''
    ext_group2paths: Dict[str, List[Path]] = {}
    ## グループ名順にグループをストライド数で再グループする
    img_group_names: list[str] = list(img_group2paths.keys())
    img_group_names.sort()
    for ign in img_group_names:
        paths: List[Path] = img_group2paths[ign]
        ### １つのグループをストライドで最グループ
        id2paths: Dict[int ,List[Path]] = devide.step_devide(paths, stride_num)
        ### ストライド毎に名前をグループ名を決めて追加していく
        for i in range(stride_num):
            group_name: str = f"group-{i:03}"
            if group_name not in ext_group2paths.keys():
                ext_group2paths[group_name] = []
            ext_group2paths[group_name] += id2paths[i]
    return ext_group2paths


def make_name2new_name(ext_group2paths: Dict[str, List[Path]], prefix: str):
    name2new_name: Dict[str, str] = {}
    ext_group_names: List[str] = list(ext_group2paths.keys())
    ext_group_names.sort()
    for n in ext_group_names:
        number = 1
        for p in ext_group2paths[n]:
            new_name = f"{prefix}_{n}_{number:04}{p.suffix}"
            name2new_name[p.name] = new_name
            number += 1
    return name2new_name


def copy_for_new_dir_with_rename(ext_group2paths:Dict[str, List[Path]], dst_root_dir: Path, name2new_name:Dict[str, str]):
    logging.info("データをグループ毎に抽出しながらディレクトリに保存しています。")
    logging.info(f"以下に保存しています。: {dst_root_dir}/datasets")
    ext_group_names: List[str] = list(ext_group2paths.keys())
    ext_group_names.sort()
    for n in tqdm.tqdm(ext_group_names):
        copyer = Copyer(dst_root_dir.joinpath(f"datasets/dataset_{n}/imgs_{n}_num_{len(ext_group2paths[n])}"))
        for p in ext_group2paths[n]:
            new_name: str = name2new_name[p.name]
            copyer.copy_with_rename(p, new_name)


import shutil
class Copyer:
    def __init__(self, tgt_dir: Path):
        self.tgt_dir: Path = tgt_dir
        self.tgt_dir.mkdir(parents=True)


    def copy_with_rename(self, src_path: Path, dst_name: str):
        dst_path = self.tgt_dir.joinpath(f"{dst_name}")
        shutil.copy(src_path, dst_path)


if __name__ == '__main__':
    logging.info("aaaa")
    parser: ArgumentParser = ArgumentParser()
    psrser = add_arguments(parser)
    main(**vars(parser.parse_args()))