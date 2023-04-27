#!/bin/bash

if [ -z ${1+x} ]; then
    echo "Needs an argument with the name of the directory of the saved libraries"
    exit 1
fi


DIRECTORY_DESTINY=build/lib/saved_libs/$1

if [ ! -d $NAME_DESTINY ]; then
    echo "ERROR: Directory does not exists."
    exit 1
fi

for library_directory in $DIRECTORY_DESTINY/*/; do
    mutex_name=$(basename $library_directory)
    results_dir=results/$1/$mutex_name

    printf "\e[36mLibrary: $mutex_name\e[0m\n"
    rm -rf $results_dir
    mkdir -p $results_dir

    #./prepare_library.sh $(realpath --relative-to=build/lib/saved_libs $library_directory)
    perf record -F 997 -g -o $results_dir/output.dat ./build/bin/slambench -i datasets/ICL_NUIM/living_room_traj0_loop.slam -load build/lib/liborbslam2-original-library.so > $results_dir/output.log
    perf script -i $results_dir/output.dat -F +pid > $results_dir/slambench_script.log
done

