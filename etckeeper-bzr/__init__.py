#
# Bazaar plugin that runs etckeeper pre-commit when necessary

"""Runs etckeeper pre-commit when necessary."""

from bzrlib.errors import BzrError
import os

def etckeeper_startcommit_hook(tree):
    abspath = getattr(tree, "abspath", None)
    if abspath is None or not os.path.exists(abspath(".etckeeper")):
        # Only run the commit hook when this is an etckeeper branch
        return
    import subprocess
    ret = subprocess.call(["etckeeper", "pre-commit", abspath(".")])
    if ret != 0:
        raise BzrError("etckeeper pre-commit failed")

try:
    from bzrlib.hooks import install_lazy_named_hook
except ImportError:
    from bzrlib.mutabletree import MutableTree
    MutableTree.hooks.install_named_hook('start_commit',
        etckeeper_startcommit_hook, 'etckeeper')
else:
    install_lazy_named_hook(
        "bzrlib.mutabletree", "MutableTree.hooks",
        'start_commit', etckeeper_startcommit_hook, 'etckeeper')

if __name__ == "__main__":
    from distutils.core import setup
    setup(name="bzr-etckeeper", 
          packages=["bzrlib.plugins.etckeeper"],
          package_dir={"bzrlib.plugins.etckeeper":"etckeeper-bzr"})
