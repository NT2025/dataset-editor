"""
データ群を学習用、テスト用、検証用に分割する。
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import datetime
import logging
from pathlib import Path
import random
from typing import Any, Dict, List, Tuple, Union, Optional
import shutil


DATETIME2PATHS = Dict[str, List[Path]]

def parse_args() -> Dict[str, Any]:
    parser = ArgumentParser(epilog=__doc__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("dataset_dir", type=str, help="dataset dir path")
    parser.add_argument("output_dir", type=str, help="output dir path")
    parser.add_argument("--ratio", type=float, default=0.4, help="test ratio. train:test = (1-ratio):ratio.")
    parser.add_argument("--not_val", action="store_true")
    parser.add_argument("--random", action="store_true", help="ランダムフラグ. このフラグがONの時はデータに関係なくランダムに分割する")
    parser.add_argument("--log_level", type=str, choices=["info", "debug"], default="info", help="log level")

    cli_args = vars(parser.parse_args())
    return cli_args


def main(*args, **kwargs):
    show_cli_args(kwargs)

    configure_loggging(kwargs["log_level"])

    check_path(kwargs["dataset_dir"])
    check_path(Path(kwargs["output_dir"]).parent)
    check_ratio(kwargs["ratio"])

    # データ群のパスの検索
    dataset_paths = find_dataset(kwargs['dataset_dir'])

    if kwargs['random']:
        train_paths, test_paths, val_paths = separate_random(dataset_paths, kwargs["not_val"], kwargs["ratio"])
    else:
        # 有効なデータ群か調査する
        check_valid_dataset(dataset_paths)
        # データ群を学習用、テスト用、検証用に分割する
        train_paths, test_paths, val_paths = separate_dataset(dataset_paths, kwargs['not_val'], kwargs["ratio"])

    # 分割されたデータ群をそれぞれコピーして保存する。
    copy_paths(train_paths, kwargs['output_dir'], "trains")
    copy_paths(test_paths, kwargs['output_dir'], "tests")
    if val_paths is not None: copy_paths(val_paths, kwargs['output_dir'], "vals")


def show_cli_args(cli_args:Dict[str, Any]):
    print(f"{'-'*3} args {'-'*15}")
    for k, v in cli_args.items():
        print(f"--{k}")
        print(f"\t{v}")
    print(f"{'-'*20}")


def configure_loggging(log_level:str):
    log_level2level = {"info":logging.INFO, "debug":logging.DEBUG}
    try:
        level = log_level2level[log_level]
    except:
        level = log_level2level["info"]
    logging.basicConfig(
        level=level,
        format="%(asctime)s:%(filename)s:%(lineno)s:[%(levelname)s]:%(message)s"
    )


def add_log_function_start_end_with_debug(func):
    def wrapper(*args, **kwargs):
        logging.debug(f"start func {func.__name__}")
        res = func(*args, **kwargs)
        logging.debug(f"finish func {func.__name__}")
        return res
    return wrapper


@add_log_function_start_end_with_debug
def check_path(path:Union[str, Path]):
    _path = Path(path)
    assert _path.exists(), f"Not Found {_path}"


@add_log_function_start_end_with_debug
def check_ratio(ratio:float):
    assert 0.0 < ratio < 1.0


@add_log_function_start_end_with_debug
def find_dataset(path:Union[str, Path]) -> List[Path]:
    # データ群のパスの検索
    _path = Path(path)

    img_fmts = [".jpg", ".png", ".jpeg"]
    img_fmts += list(map(lambda fmt:fmt.upper(), img_fmts))
    img_paths = [Path(p) for fmt in img_fmts for p in _path.glob(f"*{fmt}")]
    dataset_paths = img_paths
    logging.debug(f"num img paths is {len(img_paths)}")

    ann_fmts = [".xml"]
    ann_paths = [Path(p) for fmt in ann_fmts for p in _path.glob(f"*{fmt}")]
    if len(dataset_paths) < len(ann_paths):
        dataset_paths = ann_paths
    logging.debug(f"num ann paths is {len(ann_paths)}")

    assert len(dataset_paths) > 0, f"Not Found file in {_path}"

    return dataset_paths


@add_log_function_start_end_with_debug
def separate_random(paths:List[Path], is_not_use_val:bool, test_ratio:float=0.4) -> Tuple[List[Path], List[Path], Optional[List[Path]]]:
    random.shuffle(paths)
    num_all_paths:int = len(paths)
    separate_idx:int = int(round(num_all_paths * (1-test_ratio)))

    train_paths:List[Path] = paths[:separate_idx]
    test_paths:List[Path] = paths[separate_idx:]
    val_paths:Optional[List[Path]] = None

    if not is_not_use_val:
        num_test_paths:int = len(test_paths)
        separate_idx:int = int(round(num_test_paths) * 0.5)
        val_paths = test_paths[:separate_idx]
        test_paths = test_paths[separate_idx:]

    return train_paths, test_paths, val_paths


@add_log_function_start_end_with_debug
def check_valid_dataset(dataset_paths:List[Path]):
    # 有効なデータ群か調査する
    ## データ群のstem名が'*yyyymmdd_*_hhmmss*'等の形になっていれば有効
    for p in dataset_paths:
        is_cond1 = False
        is_cond2 = False
        words = p.stem.split("_")
        # check date
        word = words[-3]
        try:
            datetime.datetime(year=int(word[:4]), month=int(word[4:6]), day=int(word[6:]))
            is_cond1 = True
            continue
        except Exception as e:
            pass
        # check time
        word = words[-2]
        try:
            datetime.time(hour=int(word[:2]), minute=int(word[2:4]), second=int(word[4:]))
            is_cond2 = True
        except Exception as e:
            pass

        assert (is_cond1 and is_cond2), f"Invald data conntained. Example:{p.stem}"


@add_log_function_start_end_with_debug
def separate_dataset(dataset_paths:List[Path], is_not_use_val:bool, test_ratio:float=0.4)-> Tuple[List[Path], List[Path], Optional[List[Path]]]:
    # データ群を学習用、テスト用、検証用に分割する
    ## まずはデータ群を撮影日時の共通点でグループ化する
    ## 撮影日時グループを撮影日時に関して昇順ソートする
    ## 撮影日時グループの最も古いデータと新しいデータを抽出して学習用グループに配属させる
        ## （古いデータと新しいデータはアノテーション依頼の際に分割されるから）
    ## 撮影日時グループを画像枚数に関して昇順ソートする
    ## 撮影日時グループを３分割する。これによりデータ数が多、中間、少のグループに分けられる。
    ## 中間グループからランダムにデータ群を抽出してテスト用グループに配属させる。
    ### この作業はテスト用グループが一定のデータ数(全データが3~4割程度？)になると終わるようにする
    ## 学習用、テスト用に配属されなかったデータ群は学習用グループに配属させる
    ## 検証用データへの分割が必要な場合はテスト用データを半分に分割して検証用データとする。

    # 想定されるデータセット対象
    # *_yyyymmdd_hhmmss_XXXXXX.suffix

    # 撮影日時グループ(yyyymmdd_hhmmss)の作成
    date_time2paths:Dict[str, List[Path]] = {}
    for p in dataset_paths:
        words = p.stem.split("_")
        _date = words[-3] # yyyymmdd
        _time = words[-2] # hhmmss
        date_time = f"{_date}_{_time}" # yyyymmdd_hhmmss
        if date_time not in date_time2paths.keys():
            date_time2paths[date_time] = []
        date_time2paths[date_time].append(p)
    show_datasets(date_time2paths, "all")

    date_time_list = list(date_time2paths.keys())
    assert len(date_time_list) > 2, "3 > num data group that 'yyyymmdd_hhmmss' "

    train_date_time_list:List[str] = []
    logging.debug(f"num all date_time list {len(date_time_list)}")

    # 撮影日時グループから端っこを学習用に配属
    date_time_list.sort() # sort date_time
    train_date_time_list.append(date_time_list.pop(0))
    train_date_time_list.append(date_time_list.pop(-1))

    # データ数に関してソートした後、5分割して、端のデータを学習用に分類、残りをテスト候補に
    date_time_list = sorted(date_time_list, key=lambda k:len(date_time2paths[k])) # sort num data
    sep_num = len(date_time_list) // 5
    train_date_time_list += date_time_list[:sep_num]
    if sep_num > 1 :train_date_time_list += date_time_list[-sep_num:]
    date_time_list = list(set(date_time_list) - set(train_date_time_list))
    logging.debug(f"num middle date_time list {len(date_time_list)}")

    # 指定数のテストデータをテスト候補からランダムに抽出
    num_datasets = len(dataset_paths)
    num_required_test_datasets = int(round(num_datasets * test_ratio))
    logging.debug(f"num datasets is {len(dataset_paths)}, and num required test datasets is {num_required_test_datasets}")
    idxes = list(range(len(date_time_list)))
    random.shuffle(idxes)
    num_test_datasets = 0
    test_date_time_list:List[str] = []
    for idx in idxes:
        date_time = date_time_list[idx]
        pre_num_test_datasets = num_test_datasets
        num_test_datasets += len(date_time2paths[date_time])
        if num_test_datasets > num_required_test_datasets:
            num_test_datasets = pre_num_test_datasets
            continue
        test_date_time_list.append(date_time)
    logging.debug(f"num test date time list {len(test_date_time_list)}")

    # 余りを学習用に配属
    date_time_list = list(set(date_time_list) - set(test_date_time_list))
    train_date_time_list += date_time_list
    train_date_time2paths = {k:date_time2paths[k] for k in train_date_time_list}
    test_date_time2paths = {k:date_time2paths[k] for k in test_date_time_list}

    show_datasets(train_date_time2paths, "trains")
    train_paths = [ p for paths in train_date_time2paths.values() for p in paths ]

    if is_not_use_val:
        show_datasets(test_date_time2paths, "tests")
        test_paths = [ p for paths in test_date_time2paths.values() for p in paths ]
        return train_paths, test_paths, None

    test_date_time_list = list(test_date_time2paths.keys())
    if len(test_date_time_list) < 2:
        show_datasets(test_date_time2paths, "tests")
        test_paths = [ p for paths in test_date_time2paths.values() for p in paths ]
        print("Don't Separate for val datasets, Because test data datetime is 1")
        return train_paths, test_paths, None

    # val用の確保(テスト用を二分割する)
    test_date_time_list = sorted(test_date_time_list, key=lambda k:len(test_date_time2paths[k])) # sort num data
    idxes = list(range(len(test_date_time_list)))
    random.shuffle(idxes)
    num_test_datasets = sum(map(lambda v:len(v), test_date_time2paths.values()))
    num_required_val_datasets = int(round(num_test_datasets * 0.5))
    num_val_datasets = 0
    val_date_time_list:List[str] = []
    for idx in idxes:
        date_time = test_date_time_list[idx]
        pre_num_val_datasets = num_val_datasets
        num_val_datasets += len(test_date_time2paths[date_time])
        if num_val_datasets > num_required_val_datasets: # valデータの数がtestデータの数より少なくなるようにする。
            num_val_datasets = pre_num_val_datasets
            continue
        val_date_time_list.append(date_time)
    val_date_time2paths = {k:test_date_time2paths.pop(k) for k in val_date_time_list}

    show_datasets(test_date_time2paths, "tests")
    show_datasets(val_date_time2paths, "vals")

    test_paths = [ p for paths in test_date_time2paths.values() for p in paths ]
    val_paths = [ p for paths in val_date_time2paths.values() for p in paths ]

    return train_paths, test_paths, val_paths


@add_log_function_start_end_with_debug
def show_datasets(date_time2paths:Dict[str, List[Path]], _type:str):
    """ show detail datasets

    Parameters
    ----------
    date_time2paths : Dict[str, List[Path]]
        _description_
    _type : str
        _description_

    Visualize:
    >>> --- tests --------------------
    >>> nums  | date_time
    >>>    78 | 20211201_173428
    >>>    76 | 20211201_173643
    >>>    74 | 20211201_174742
    >>>    64 | 20211201_174224
    >>>    60 | 20211201_173208
    >>>    58 | 20211201_174044
    >>>    47 | 20211201_174856
    >>>    43 | 20211201_172102
    >>> num data is 500
    >>> ------------------------------
    """
    date_times = [k for k in date_time2paths.keys()]
    date_times = sorted(date_times, key=lambda k:len(date_time2paths[k]), reverse=True) # desc order

    print(f"{'-'*3} {_type} {'-'*20}")
    print(f"{'nums':5} | date_time")
    num_all_paths = 0
    for date_time in date_times:
        num_paths = len(date_time2paths[date_time])
        print(f"{num_paths:>5} | {date_time}")
        num_all_paths += num_paths
    print(f"num data is {num_all_paths}")
    print(f"{'-'*30}")


def copy_paths(paths:List[Path], out_dir:str, _type:str):
    assert _type in ["train", "test", "val"]

    _out_dir = Path(out_dir).joinpath(_type)
    _out_dir.mkdir(exist_ok=True)
    logging.info(f"mkdir {_out_dir}")

    for pi, path in enumerate(paths, start=1):
        print(f"\r{pi:>4}:{path.name} -> {_out_dir}", end="")
        shutil.copy(path, _out_dir)
    print("")

if __name__ == "__main__":
    cli_args = parse_args()
    main(**cli_args)