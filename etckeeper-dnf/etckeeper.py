# etckeeper.py, support etckeeper for dnf
#
# Copyright (C) 2014 Peter Listiak
# https://github.com/plistiak/dnf-etckeeper
#
# Later modifications by Petr Spacek:
# Distutils code below was copied from etckeeper-bzr distributed with v1.15
#

from dnfpluginscore import logger

import os
import dnf


class Etckeeper(dnf.Plugin):

    name = 'etckeeper'

    def _out(self, msg):
        logger.debug('Etckeeper plugin: %s', msg)

    def resolved(self):
        self._out('pre transaction commit')
        command = '%s %s' % ('etckeeper', " pre-install")
        ret = os.system(command)
        if ret != 0:
            raise dnf.exceptions.Error('etckeeper returned %d' % (ret >> 8))

    def transaction(self):
        self._out('post transaction commit')
        command = '%s %s > /dev/null' % ('etckeeper', "post-install")
        os.system(command)

if __name__ == "__main__":
    from distutils.core import setup
    setup(name="dnf-etckeeper",
          packages=["dnf-plugins"],
          package_dir={"dnf-plugins":"etckeeper-dnf"})
