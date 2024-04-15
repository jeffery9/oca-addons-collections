#!/bin/sh 
cwd=$(pwd)
branch=$(cat $cwd/ver)

for f in $(cat $cwd/repos) 
do  
echo git subtree add --squash --prefix=$f  https://github.com/oca/$f $branch


done 
# git subtree 