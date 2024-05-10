#!/bin/bash

# ディレクトリの作成
TARGETDIR=$HOME/.local/bin
mkdir $TARGETDIR -p && \
    echo "ディレクトリ作成：$TARGETDIR"

# 実行ファイルの作成
FILENAME="dataset-editor.sh"
FILEPATH=$TARGETDIR/$FILENAME
PROJDIR=$(cd $(dirname $0);cd ../;pwd)
echo "#!/bin/bash" > $FILEPATH && \
    echo "PROJDIR=$PROJDIR" >> $FILEPATH && \
    echo "\$PROJDIR/.venv/bin/python \$PROJDIR/dataset_editor \${@}" >> $FILEPATH && \
    echo "以下の実行ファイルを作成しました。" && \
    echo "$FILEPATH" && \
    echo "以下を実行して確認してください。" && \
    echo "dataset-editor.sh --help"

# パーミッションの変更
chmod 775 $FILEPATH