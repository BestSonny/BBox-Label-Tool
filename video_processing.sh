#!/bin/sh
VIDEO_NAME="$1"
CODE_PATH=/data/panhe/FDOT/code/TruckMonitoring
python $CODE_PATH/video_processing.py -net $CODE_PATH/./cfg/yolo.cfg -weights \
$CODE_PATH/weights/yolo.weights --resume $CODE_PATH/models/resnet18_model_best.pth.tar -name $VIDEO_NAME  -vid ./Videos -out .
