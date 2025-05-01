#!/bin/sh 
cwd=$(pwd)
branch=$(cat $cwd/ver)

# 检查是否提供了 repo 参数
if [ "$#" -eq 1 ]; then
    repos=$1
    # 将逗号分隔的 repo 名称转换为数组
    IFS=',' read -r -a repo_array <<< "$repos"
    for repo in "${repo_array[@]}"; do
        echo "Pulling specified repo: $repo"
        cd $cwd
        echo git subtree pull -q --squash --prefix=$repo https://github.com/oca/$repo $branch
        git subtree pull -q --squash --prefix=$repo https://github.com/oca/$repo $branch -m "merge with upstream"
    done
else
    # 如果没有提供参数，则 pull 所有 repos
    for f in $(cat $cwd/repos); do  
        cd $cwd
        echo git subtree pull -q --squash --prefix=$f https://github.com/oca/$f $branch
        git subtree pull -q --squash --prefix=$f https://github.com/oca/$f $branch -m "merge with upstream"
    done
fi