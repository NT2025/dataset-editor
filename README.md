# README

dataset 編集ツール

## usage

v0.4.0の時の例

```bash
dataset-editor.sh --help
```
```console
usage: dataset_editor [-h]
                      {numbering,repair,mkdir,ext_latest,separate_train,reduce,choice,group,diff_copy,for_rsync,move_into}
                      ...

 データセットに用いるファイルを扱うためのプログラム群。

positional arguments:
  {numbering,repair,mkdir,ext_latest,separate_train,reduce,choice,group,diff_copy,for_rsync,move_into}
    numbering            画像データを５桁の番号の名前に変更して新たに保存する関数.  
    repair               ファイル名が変更されたファイル(numbering2org.json等)に基づいて、対象画像ファイルをオリジナルの名前として新たに保存するプログラム.
    mkdir                ナンバリングされたファイルを所持するディレクトリを指定のファイル数ごとに分割するプログラム。
    ext_latest           データセット群からxmlファイルを一つのディレクトリにコピーしてまとめる
    separate_train       データ群を学習用、テスト用、検証用に分割する。
    reduce               データセットを何個か飛ばしで抽出することでデータセットを削減する。
                        主に動画を画像化した際にあまり変化のないフレームが発生するので、削減する目的で使用する。
                        抽出されたデータセットは対象ディレクトリ_reducedという名称のディレクトリに保存される
    choice               対象ディレクトリのファイル群をランダムに抽出する
    group                '_'区切りの画像群を前２つの単語のディレクトリにまとめる
    diff_copy            ２つのディレクトリの差分を求めてコピーする
    for_rsync           アノテーション用データセットから保存用のモノを抽出してsymlinkで繋げる
    move_into            ディレクトリAにディレクトリを作成してファイルを全て移動させる。

optional arguments:
  -h, --help            show this help message and exit
```

## 環境構築


```bash
python -m venv .venv
source .venv/bin/activate

pip install -U pip setuptools
pip install -e .

bash scripts/make_bashfile.sh

dataset-editor.sh --help
```