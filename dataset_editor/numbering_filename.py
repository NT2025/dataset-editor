DESCRIPTION='''
画像データを５桁の番号の名前に変更して新たに保存する関数.  
'''
EPILOG='''
<詳細>-------------------------------------
複数の画像ファイルを所有しているフォルダから画像ファイルのpathを読み込みリストに保存する。
シャッフルフラグがONの場合ランダムにリストをシャッフルする。
次に画像ディレクトリの親ディレクトリ上に`numberings`ディレクトリを作成する。
画像ファイルを５桁の番号の名前にリネームしながら、`numberings`ディレクトリにコピーする。
（この際に`prefix`引数が設定してある場合は`[prefix]_xxxxxx.jpg`のように数字の前にテキストが挿入される。)
また、リネーム情報を辞書に記録する。`dict={number:org}`のように
全てのファイルがコピーされた後にリネーム情報を`numbering2org.json`として画像ディレクトリの親ディレクトリに保存する。
'''

import os
from pathlib import Path
import shutil
import glob
from argparse import ArgumentParser
import random
import json 

import tqdm


def parse_args():
    parser = ArgumentParser(description=DESCRIPTION, epilog=EPILOG)

    parser.add_argument("img_dir", type=str)
    parser.add_argument("-p", "--prefix", type=str, default="", 
                        help="add prefix for filename. Example is [prefix]_00001.jpg. default is ''")
    parser.add_argument("-s", "--shuffle", action="store_true", help="shuffle flag. default is False")
    parser.add_argument("-o", "--out", type=str, default=os.curdir, help="save directory")
    parser.add_argument("-m", "--mode", choices=["absolute", "relative", "copy"])

    args = vars(parser.parse_args())
    return args


def main(args):

    # check_src_dir
    src_dir = Path(args['img_dir']).absolute()
    assert src_dir.is_dir()

    # check out dir
    out_dir = Path(f"{args['out']}/numberings").absolute()
    if not out_dir.exists():
        assert out_dir.parent.exists()
        out_dir.mkdir()
    print(f"save for {out_dir}")

    # get img paths
    suffixes = [".jpg", ".JPG", ".png", ".PNG"]
    img_paths = []
    for suffix in suffixes:
        img_paths += [ Path(f) for f in glob.glob(f"{src_dir}/*{suffix}")]
    print(f"NumImages {len(img_paths)}")
    img_paths.sort()

    # shuffle
    if args['shuffle']:
        random.shuffle(img_paths)

    # numbering
    filename_prefix = str(args['prefix'])
    out_name2img_name = {}
    for num, img_path in enumerate(tqdm.tqdm(img_paths)):
        out_name = f"{num+1:>05}{img_path.suffix}"
        out_file = f"{out_dir}/{filename_prefix}_{out_name}"
        os.symlink(img_path, out_file)

        img_name = img_path.name
        out_name2img_name[out_name] = img_name
    txt = json.dumps(out_name2img_name, indent=2)
    json_file = Path(f"{out_dir.parent}/numbering2org.json")
    with json_file.open("w") as f:
        f.write(txt)


if __name__ == "__main__":
    args = parse_args()
    main(args)
