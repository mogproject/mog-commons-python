# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import time
import threading
from mog_commons.command import *
from mog_commons import unittest


class TestCommand(unittest.TestCase):
    def test_execute_command(self):
        self.assertEqual(execute_command(['exit', '2'], shell=True), 2)
        self.assertEqual(execute_command('exit 3', shell=True), 3)
        self.assertEqual(execute_command(['/bin/sh', '-c', 'exit 4'], shell=False), 4)

        with self.withAssertOutputFile(os.path.join('tests', 'resources', 'sjis_ja.txt'),
                                       expect_file_encoding='sjis', output_encoding='sjis') as out:
            execute_command('echo "あいうえお"', shell=True, cmd_encoding='sjis', stdout=out)

    def test_capture_command(self):
        self.assertEqual(capture_command(['echo', 'あいう'], shell=True), (0, 'あいう\n'.encode('utf-8'), b''))

    def test_execute_command_with_pid(self):
        pid_file = '/tmp/mog-commons-python-test.pid'

        class RunSleep(threading.Thread):
            def run(self):
                execute_command_with_pid(['sleep', '2'], pid_file, True)

        th = RunSleep()
        th.start()
        time.sleep(1)

        with open(pid_file, 'r') as f:
            pid = int(f.read())

        self.assertTrue(pid_exists(pid))
        time.sleep(2)
        self.assertFalse(pid_exists(pid))

        self.assertEqual(execute_command_with_pid(['exit', '2'], None, shell=True), 2)

    def test_pid_exists(self):
        self.assertTrue(pid_exists(0))
