from typing import List, Dict
from pathlib import Path
import math


def step_devide(src_paths: List[Path], devide_num: int):
    """ 配列を分割するがその時に分割数を元に添字をステップして分割する。
    examples:
        分割数3の場合は、以下の3つのグループに分割する。
        g1=[a[0], a[3], a[6]],.., g2=[a[1], a[4], a[7],...], g3=[a[2], a[5], a[8],...]。
        なお、この時a[x]は配列の要素を参照していることを表す。
    """
    id2paths: Dict[int, List[Path]] = {}
    start_idx = 0
    step_num: int = devide_num
    while(start_idx<step_num):
        count = 0
        ext_paths: List[Path] = []
        idx: int = start_idx
        while(idx<len(src_paths)):
            p = src_paths[idx]
            ext_paths.append(p)
            count += 1
            idx = idx + step_num
        id2paths[start_idx] = ext_paths
        start_idx += 1
    assert len(src_paths) == sum(len(paths) for paths in id2paths.values())
    return id2paths


def make_dummy_paths(num:int):
    return [Path('') for n in range(num)]



if __name__ == "__main__":
    num_ann = 250
    num_all = 749
    paths = make_dummy_paths(100)
    devide_num = int(math.ceil(num_all / num_ann))
    print(devide_num)

    step_devide(paths, devide_num)
