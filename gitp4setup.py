#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import getpass
import logging
import os
import shutil
import socket
import subprocess
import sys

from string import Template
from subprocess import check_call, Popen, PIPE, STDOUT
from time import gmtime, strftime

# Configure logger
_logger = logging.getLogger(os.path.basename(__file__))
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
_logger.addHandler(handler)


class GitP4Workspace(object):
    P4CLIENT_SPEC_TEMPLATE = """
# A Perforce Client Specification.
#
# Use 'p4 help client' to see more about client views and options.

Client: $p4client
Update: $update
Access: $access
Owner:  $user
Host:   $host

Description:
    Created by $user.

Root:   $root_dir
Options:    noallwrite noclobber compress unlocked nomodtime rmdir
SubmitOptions:  leaveunchanged
LineEnd:    local
Stream: $depot
View:
  $depot/... //$p4client/...
"""

    def __init__(self, args):
        self.__args = args
        current_work_dir = os.getcwd()
        current_time = strftime("%Y/%m/%d %H:%M:%S")

        self.__p4client_spec_vars = {
                                     'p4client': args.P4CLIENT + '-git',
                                     'depot':    args.P4DEPOT,
                                     'update':   current_time,
                                     'access':   current_time,
                                     'user':     getpass.getuser(),
                                     'host':     socket.gethostname(),
                                     'root_dir': os.path.join(current_work_dir, 'perforce', args.P4CLIENT + '-git'),
                                     'git_root_dir': os.path.join(current_work_dir, 'git', args.P4CLIENT) }

    def create(self):
        # TODO: do p4 login
        self.__create_git_workspace()
        self.__create_git_p4_client()

    def __create_git_p4_client(self):
        p4client_content = Template(GitP4Workspace.P4CLIENT_SPEC_TEMPLATE).safe_substitute(self.__p4client_spec_vars)

        client_dir = self.__p4client_spec_vars['root_dir']

        if not self.__args.update:
            os.makedirs(client_dir)

        self.__store_p4config(client_dir)
        self.__call_p4client(template_content)

    def __store_p4config(self, dir):
        with open(os.path.join(dir, '.p4config'), 'w+') as file:
            file.write("P4CLIENT=" + self.__p4client_spec_vars['p4client'] + "\n")

    def __call_p4client(self, p4client_spec):
        _logger.debug(p4client_spec)
        p = Popen(['p4', 'client', '-i'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        stdout = p.communicate(input=p4client_spec)[0]
        _logger.debug(stdout)

    def __replace(self, content, key, value):
        _logger.debug("Replace " + key + " with " + value)
        return content.__replace('$' + key + '$', value)

    def __create_git_workspace(self):
        git_dir = self.__p4client_spec_vars['git_root_dir']

        if not self.__args.update:
            os.makedirs(git_dir)

        self.__store_p4config(git_dir)

        p = Popen(['git', 'p4', 'clone', '--verbose',
                   self.__p4client_spec_vars['depot'] + '/...@all',
                   self.__p4client_spec_vars['git_root_dir']], stdout=PIPE, stderr=STDOUT)

        # TODO: Check whether git p4 is supported
        # TODO: Check whether git p4 clone was successful
        for line in p.stdout:
            _logger.info(line.strip())

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="CLI tool for creating git-p4 workspaces.")
    parser.add_argument("P4CLIENT", action="store", help="Name of the Perforce client (eg. dev-mystream-myname-myhost)")
    parser.add_argument("P4DEPOT", action="store", help="Name of th Perforce depot (eg. //depot-foo/dev-mystream")
    parser.add_argument("--update", action="store_true", help="Update existing local Git repository and Perforce workspace.")
    parser.add_argument("--verbose", action="store_true", help="Increase verbosity")

    args = parser.parse_args()

    _logger.setLevel(level=(logging.DEBUG if args.verbose else logging.INFO))

    try:
        gitp4 = GitP4Workspace(args)
        gitp4.create()
    except Exception as e:
        _logger.exception(e)
        sys.exit(1)
    sys.exit(0)
