#!/bin/bash
PROJDIR=$(cd $(dirname $0);cd ../;pwd)

PYTHON=$PROJDIR/.venv/bin/python

$PYTHON $PROJDIR/dataset_editor ${@}
