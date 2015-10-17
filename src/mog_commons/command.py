from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
import errno
import subprocess
from mog_commons.string import is_unicode
from mog_commons.functional import oget


#
# Process operations
#
def __convert_args(args, shell, cmd_encoding):
    xs = []
    if shell:
        args = [subprocess.list2cmdline(args)]
    if shell and sys.version_info[:2] == (3, 2) and not sys.platform == 'win32':
        # Note: workaround for http://bugs.python.org/issue8513
        xs = ['/bin/sh', '-c']
        shell = False
    for a in args:
        assert is_unicode(a), 'cmd must be unicode string, not %s' % type(a).__name__
        xs.append(a.encode(cmd_encoding))
    return xs, shell


def execute_command(args, shell=False, cwd=None, env=None, stdin=None, stdout=None, stderr=None, cmd_encoding='utf-8'):
    """
    Execute external command
    :param args: command line arguments : [unicode]
    :param shell: True when using shell : boolean
    :param cwd: working directory : string
    :param env: environment variables : dict
    :param stdin: standard input
    :param stdout: standard output
    :param stderr: standard error
    :param cmd_encoding: command line encoding: string
    :return: return code
    """
    args, shell = __convert_args(args, shell, cmd_encoding)
    return subprocess.call(args=args, shell=shell, cwd=cwd, env=dict(os.environ, **(oget(env, {}))),
                           stdin=stdin, stdout=stdout, stderr=stderr)


def capture_command(args, shell=False, cwd=None, env=None, stdin=None, cmd_encoding='utf-8'):
    """
    Execute external command and capture output
    :param args: command line arguments : [string]
    :param shell: True when using shell : boolean
    :param cwd: working directory : string
    :param env: environment variables : dict
    :param stdin: standard input
    :param cmd_encoding: command line encoding: string
    :return: tuple of return code, stdout data and stderr data
    """
    args, shell = __convert_args(args, shell, cmd_encoding)
    p = subprocess.Popen(
        args, shell=shell, cwd=cwd, env=dict(os.environ, **(oget(env, {}))),
        stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_data, stderr_data = p.communicate()
    return p.returncode, stdout_data, stderr_data


def execute_command_with_pid(args, pid_file=None, shell=False, cwd=None, env=None,
                             stdin=None, stdout=None, stderr=None, cmd_encoding='utf-8'):
    if pid_file is None:
        return execute_command(args, shell, cwd, env, stdin, stdout, stderr, cmd_encoding)
    else:
        try:
            args, shell = __convert_args(args, shell, cmd_encoding)
            p = subprocess.Popen(
                args, shell=shell, cwd=cwd, env=dict(os.environ, **(oget(env, {}))),
                stdin=stdin, stdout=stdout, stderr=stderr)
            with open(pid_file, 'w') as f:
                f.write(str(p.pid))
            ret = p.wait()
        finally:
            # clean up pid file
            if pid_file is not None and os.path.exists(pid_file):
                os.remove(pid_file)
        return ret


def pid_exists(pid):
    # stole from https://github.com/giampaolo/psutil/blob/master/psutil/_psposix.py
    """Check whether pid exists in the current process table."""
    if pid == 0:
        # According to "man 2 kill" PID 0 has a special meaning:
        # it refers to <<every process in the process group of the
        # calling process>> so we don't want to go any further.
        # If we get here it means this UNIX platform *does* have
        # a process with id 0.
        return True
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            # ESRCH == No such process
            return False
        elif err.errno == errno.EPERM:
            # EPERM clearly means there's a process to deny access to
            return True
        else:
            # According to "man 2 kill" possible error values are
            # (EINVAL, EPERM, ESRCH) therefore we should never get
            # here. If we do let's be explicit in considering this
            # an error.
            raise err
    else:
        return True
