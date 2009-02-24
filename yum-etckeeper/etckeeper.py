#!/usr/bin/env python
# 
# author: jtang@tchpc.tcd.ie
# 
# this plugin is based on the hello world example 
# from http://yum.baseurl.org/wiki/WritingYumPlugins
# 
# to install, copy this file to /usr/lib/yum-plugins/etckeeper.py
# and then create /etc/yum/pluginconf.d/etckeeper.conf with the contents
# below.
# 
#  /etc/yum/pluginconf.d/etckeeper.conf:
#   [main]
#   enabled=1
#
# this was also needed in /etc/etckeeper/list-installed.d/60list-installed
#if [ "$LOWLEVEL_PACKAGE_MANAGER" = rpm ]; then
#	rpm -qa --queryformat "%{name} %{version} %{arch}\n" | sort
#fi

import os
from glob import fnmatch

import yum
from yum.plugins import TYPE_CORE

requires_api_version = '2.1'
plugin_type = (TYPE_CORE,)

def pretrans_hook(conduit):
    conduit.info(2, 'etckeeper: pre transaction commit')
    servicecmd = conduit.confString('main', 'servicecmd', '/usr/sbin/etckeeper')
    command = '%s %s' % (servicecmd, " pre-install")
    os.system(command)

def posttrans_hook(conduit):
    conduit.info(2, 'etckeeper: post transcation commit')
    servicecmd = conduit.confString('main', 'servicecmd', '/usr/sbin/etckeeper')
    command = '%s %s' % (servicecmd, "post-install")
    os.system(command)
