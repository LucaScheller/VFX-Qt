# Repo Setup
> export REPO_ROOT=$PROJECT/VFX-Qt
## Sub-Modules
> git submodule add https://github.com/LucaScheller/NodeGraphQt.git external/NodeGraphQt
## Python
> python3.9 -m venv $REPO_ROOT/external/python
Manually edit shell line prefix to "VFX-Qt-Python" in:
$REPO_ROOT/external/python/bin/activate
### Dependency Links
> ln -s -r external/NodeGraphQt/NodeGraphQt external/python/lib/python3.9/site-packages/NodeGraphQt
### Pip Installs
> source $REPO_ROOT/external/python/bin/activate
> pip install -r requirements.txt 
### Stubs ###
stubgen -o external/python/stubs