#!/bin/bash

set -x

if [ -z ${1+x} ]; then
    echo "This command requires one argument, the directory to store log files";
    exit 1;
fi

if [ -z ${2+x} ]; then
    echo "Execute the full benchmark with no extra arguments." ;
    DEBUG_ARGUMENTS="";
else
    echo "Execute the debug mode with extra arguments '$2'.";
    DEBUG_ARGUMENTS=$2;
fi

LOG_DIRECTORY=$1
RUNS_PER_DATA=5

if [ -z ${DISPLAY+x} ]; then echo "DISPLAY is not set"; else echo "DISPLAY is set to '$DISPLAY'"; fi

datasets=(
     "datasets/ICL_NUIM/living_room_traj0_loop.slam"
    # "datasets/ICL_NUIM/living_room_traj1_loop.slam"
    # "datasets/ICL_NUIM/living_room_traj2_loop.slam"
    # "datasets/ICL_NUIM/living_room_traj3_loop.slam"
    # "datasets/TUM/freiburg1/rgbd_dataset_freiburg1_rpy.slam"
    # "datasets/TUM/freiburg1/rgbd_dataset_freiburg1_xyz.slam"
    # "datasets/TUM/freiburg2/rgbd_dataset_freiburg2_rpy.slam"
    # "datasets/TUM/freiburg2/rgbd_dataset_freiburg2_xyz.slam"
)

run_prepare () {
    
    if [ -z ${SKIP_CLEAN+x} ]; then
        #make clean
        #make cleandatasets	
        echo "Skip clean"
    else
	    echo "WARNING !! We will skip the cleaning step.";
    fi

    make -j slambench APPS=orbslam2
    
    for i in "${datasets[@]}"
    do
    dataset_name=`basename -s .slam ${i}`
    mkdir -p ${LOG_DIRECTORY}/rgbd_multi/$dataset_name
    mkdir -p ${LOG_DIRECTORY}/mono_multi/$dataset_name
    mkdir -p ${LOG_DIRECTORY}/rgbd_single/$dataset_name
    mkdir -p ${LOG_DIRECTORY}/mono_single/$dataset_name
	make $i
    done
}

run_bench () {
    for i in "${datasets[@]}"
    do
        dataset=$i
        dataset_name=`basename -s .slam ${dataset}`
        current_time=$(date "+%Y-%m-%d_%H-%M-%S")
        
        if [ ! -f ${dataset}    ]; then continue          ; fi

        ./build/bin/slambench  -i ${dataset}  -load  build/lib/liborbslam2-original-library.so ${DEBUG_ARGUMENTS} -m rgbd >> ${LOG_DIRECTORY}/rgbd_multi/$dataset_name/orbslam2_${current_time}.log  || exit 1
        ./build/bin/slambench  -i ${dataset}  -load  build/lib/liborbslam2-original-library.so ${DEBUG_ARGUMENTS} -m mono >> ${LOG_DIRECTORY}/mono_multi/$dataset_name/orbslam2_${current_time}.log  || exit 1
        taskset 1 ./build/bin/slambench  -i ${dataset}  -load  build/lib/liborbslam2-original-library.so ${DEBUG_ARGUMENTS} -m rgbd >> ${LOG_DIRECTORY}/rgbd_single/$dataset_name/orbslam2_${current_time}.log  || exit 1
        taskset 1 ./build/bin/slambench  -i ${dataset}  -load  build/lib/liborbslam2-original-library.so ${DEBUG_ARGUMENTS} -m mono >> ${LOG_DIRECTORY}/mono_single/$dataset_name/orbslam2_${current_time}.log  || exit 1
    done
}

run_prepare

for i in $(eval echo "{1..$RUNS_PER_DATA}")
do
    run_bench
done
