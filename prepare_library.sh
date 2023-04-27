#!/bin/bash

if [ -z ${1+x} ]; then
    echo "Needs an argument with the name of the directory of the saved library"
    exit 1
fi

cd build/lib
NAME_DESTINY=saved_libs/$1

if [ ! -d $NAME_DESTINY ]; then
    echo "ERROR: Directory does not exists."
    exit 1
fi

for library_file in $NAME_DESTINY/*; do
    ln -s $library_file $(basename $library_file)
done

