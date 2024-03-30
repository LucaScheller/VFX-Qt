# Source setup
if [ ! $REPO_SOURCED ]
then
    export REPO_SOURCED=1
    export REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && (pwd -W 2> /dev/null || pwd))
    # Source Python
    source $REPO_ROOT/external/python/bin/activate
    export PYTHONDONTWRITEBYTECODE=1 # Disable __pycache__ byte code generation
    # Add external Python packages
    export PYTHONPATH=$REPO_ROOT/src:$DEADLINE_INSTALL_ROOT/DeadlineRepository10/api/python:$DEADLINE_INSTALL_ROOT/DeadlineRepository10/custom/library/python:$PYTHONPATH
    # Source Houdini
    pushd /opt/hfs20.0 > /dev/null
    source houdini_setup
    popd > /dev/null
fi
