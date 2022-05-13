#!/bin/bash

read -p "m1?(y/n):" m1

if [ $m1 == "y" ]
then
    docker run -it -v $PWD/csdepts:/home/jovyan/notebooks --rm -p 8888:8888 jmct/cmsc320:m1
else
    docker run -it -v $PWD/csdepts:/home/jovyan/notebooks --rm -p 8888:8888 jmct/cmsc320
fi
