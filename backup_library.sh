#!/bin/bash

if [ $# -eq 3 ]; then
    echo "Needs two arguments. Name of the slambench generated library and destiny name"
    exit 1
fi

NAME_SLAMBENCH=$1
NAME_DESTINY=build/lib/saved_libs/$2

libraries_extra_name=(
     ".so"
     "-original.so"
     "-original-library.so"
)

if [ -d $NAME_DESTINY ]; then
    echo "ERROR: Destiny directory already exists."
    exit 1
fi

mkdir $NAME_DESTINY

for extra_name in "${libraries_extra_name[@]}"
do
    lib_name=$NAME_SLAMBENCH$extra_name
    mv build/lib/$lib_name $NAME_DESTINY/$lib_name
done


