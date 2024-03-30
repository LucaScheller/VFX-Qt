# Source setup
if [ ! $REPO_SOURCED ]
then
    export REPO_SOURCED=1
    export REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && (pwd -W 2> /dev/null || pwd))
    # Source Houdini
    pushd /opt/hfs20.0 > /dev/null
    source houdini_setup
    popd > /dev/null
fi
