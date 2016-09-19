#!/bin/bash
branch=`git rev-parse --abbrev-ref HEAD`
if [ $branch == "master" ];then
    #echo "Resolving master"
    masterTag=`git tag --points-at HEAD | grep \\\-mas- | xargs`
    if [[ -z "${masterTag// }" ]]; then
        # Get the nearest tag and add Desc
        headCommit=`git rev-parse HEAD`
        CASA_VERSION_DESC="No tag found for the head commit. Nearest tag: $branchTag, HEAD commit: $headCommit "
        masterTag=`git describe --abbrev=0 | grep \\\-mas- | xargs`
    fi
    # Return only the revision number
    echo "${masterTag##*-};$CASA_VERSION_DESC"
else
    #echo "Resolving branch"
    # Using parameter expansion to split the strings
    b1=${branch%/*} # part before the slash
    b2=${branch##*/} # rpart after the slash
    tagMatcher=$b1-$b2
    branchTag=`git tag --points-at HEAD | grep \\\-$tagMatcher- | xargs`
    if [[ -z "${branchTag// }" ]]; then
        # Get the nearest tag and add Desca
        headCommit=`git rev-parse HEAD`
        branchTag=`git describe --abbrev=0 | grep \\\-$tagMatcher- | xargs`
        CASA_VERSION_DESC="No tag found for the head commit. Nearest tag: $branchTag, HEAD commit: $headCommit "
    else
        CASA_VERSION_DESC="$branchTag"
    fi
    # Remove the feature information
    mTag=${branchTag%-feature-*}
    #echo $mTag
    # Return the master tag version
    echo "${mTag##*-};$CASA_VERSION_DESC"
fi
