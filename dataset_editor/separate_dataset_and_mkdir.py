DESCRIPTION='''
ナンバリングされたファイルを所持するディレクトリを指定のファイル数ごとに分割するプログラム。
'''
EPILOG='''
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

import os
from argparse import ArgumentParser
from pathlib import Path
import glob

from natsort import natsorted


CURR_DIR = Path(os.path.abspath(os.path.curdir))


def parse_args():

    parser = ArgumentParser(description=DESCRIPTION, epilog=EPILOG)
    parser.add_argument("file_dir", type=str)
    parser.add_argument("-n", "--devide_number", type=int, default=500, 
                        help="devided number for dataset. default is 500")
    parser.add_argument("-o", "--output", type=str, default=f"{CURR_DIR}",
                        help=f"output root dir. default {CURR_DIR}")

    args = vars(parser.parse_args())

    return args


def main(args):
    pass

    file_dir = Path(args['file_dir']).absolute()
    out_dir = Path(args['output']).absolute()
    check_path(file_dir)
    check_nn(args['devide_number'])
    check_path(out_dir.parent)

    # get file names and sort
    files = get_file_names(file_dir)

    # devide file with number into group
    file_groups, file_infos = devide_files(files, args['devide_number'])

    # mkdir group
    mkdir_groups(file_infos, out_dir)

    # make simbolic link
    link_files(file_groups, file_infos)


def check_path(path:Path):
    assert path.exists(), path


def check_nn(num:int):
    assert num > 0


def get_file_names(dir:Path, order='asc'):
    files = [ Path(p).absolute() for p in glob.glob(f"{dir}/*") ]

    assert order in ['asc', 'desc']
    if order=='asc':
        files = natsorted(files)
    else:
        files = natsorted(files, reverse=True)
    return files


def devide_files(files:list, devided_num:int):
    file_groups = []
    file_infos = []

    num_files = len(files)
    iter_num = (num_files // devided_num) + 1
    for i in range(iter_num):
        sidx = devided_num * (i)
        eidx = devided_num * (i+1)
        group = files[sidx:eidx]
        # start_number = Path(group[0]).stem
        # end_number = Path(group[-1]).stem
        start_number = f"{sidx + 1:05}"
        end_number = f"{eidx:05}"
        info = {'min':start_number, 'max':end_number}
        file_groups.append(group)
        file_infos.append(info)
    
    return file_groups, file_infos


def mkdir_groups(file_infos:list, out_dir:Path):
    mkdir_text = "make dir {}"
    out_dir = Path(f"{out_dir}/datasets")
    if not out_dir.exists():
        out_dir.mkdir()
        print(mkdir_text.format(out_dir))

    for info in file_infos:
        # make dataset dir
        dataset_dir_name = "dataset_{}_{}".format(info['min'], info['max'])
        dataset_dir = out_dir / Path(dataset_dir_name)
        if not dataset_dir.exists():
            dataset_dir.mkdir()
            print(mkdir_text.format(dataset_dir))
        info['dataset_dir'] = dataset_dir

        # make imgs dir
        imgs_dir_name = "imgs_{}_{}".format(info['min'], info['max'])
        imgs_dir = dataset_dir / Path(imgs_dir_name)
        if not imgs_dir.exists():
            imgs_dir.mkdir()
            print(mkdir_text.format(imgs_dir))
        info['imgs_dir'] = imgs_dir

    return


def link_files(file_groups:list, file_infos:list):
    for g, info in zip(file_groups, file_infos):
        imgs_dir = info['imgs_dir']
        for f in g:
            src_path = Path(os.path.relpath(f, imgs_dir)) # 参照パスの作成
            out_path = Path(f"{imgs_dir}/{Path(src_path.name)}")
            if out_path.exists():
                os.remove(out_path)
            os.symlink(src_path, out_path)


if __name__ == "__main__":
    args = parse_args()
    main(args)
