#!/bin/bash

a=2
b=3

c=$(($a*$b))

let c=a*b

if [ $a -gt $b ]
then
    echo a greater than b
else
    echo b greater than a
fi