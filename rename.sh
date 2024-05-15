#!/bin/bash

for DIR in "$@"
do
    COUNT=1
    COMMAND="ls -1 $DIR"
    for FILE in `eval $COMMAND`
    do
        PREVNAME=$DIR/$FILE
        NAME=$DIR"_frames"/$COUNT.jpg
        echo "cp $PREVNAME $NAME"
        cp $PREVNAME $NAME
        COUNT=$(($COUNT + 1))
    done
    echo "$DIR raw frames folder generated"
done
