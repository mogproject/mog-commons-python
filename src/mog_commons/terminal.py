from __future__ import division, print_function, absolute_import, unicode_literals

import os
import sys
import codecs
import subprocess
import locale
import platform
import time

if os.name == 'nt':
    # for Windows
    import msvcrt
else:
    # for Unix/Linux/Mac/CygWin
    import termios
    import tty

from mog_commons.case_class import CaseClass
from mog_commons.string import to_unicode

__all__ = [
    'TerminalHandler',
]

DEFAULT_GETCH_REPEAT_THRESHOLD = 0.3  # in seconds


class TerminalHandler(CaseClass):
    """
    IMPORTANT: When you use this class in POSIX environment, make sure to set signal function for restoring terminal
    attributes. The function `restore_terminal` is for that purpose. See the example below.

    :example:
            import signal

            t = TerminalHandler()
            signal.signal(signal.SIGTERM, t.restore_terminal)

            try:
                (do your work)
            finally:
                t.restore_terminal(None, None)
    """

    def __init__(self, term_type=None, encoding=None,
                 stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
                 getch_repeat_threshold=DEFAULT_GETCH_REPEAT_THRESHOLD):
        CaseClass.__init__(self,
                           ('term_type', term_type or self._detect_term_type()),
                           ('encoding', encoding or self._detect_encoding(stdout)),
                           ('stdin', stdin),
                           ('stdout', stdout),
                           ('stderr', stderr),
                           ('getch_repeat_threshold', getch_repeat_threshold)
                           )
        self.restore_terminal = self._get_restore_function()  # binary function for restoring terminal attributes
        self.last_getch_time = 0.0
        self.last_getch_char = '..'

    @staticmethod
    def _detect_term_type():
        """
        Detect the type of the terminal.
        """
        if os.name == 'nt':
            if os.environ.get('TERM') == 'xterm':
                # maybe MinTTY
                return 'mintty'
            else:
                return 'nt'
        if platform.system().upper().startswith('CYGWIN'):
            return 'cygwin'
        return 'posix'

    @staticmethod
    def _detect_encoding(stdout):
        """
        Detect the default encoding for the terminal's output.
        :return: string: encoding string
        """
        if stdout.encoding:
            return stdout.encoding

        if os.environ.get('LANG'):
            encoding = os.environ.get('LANG').split('.')[-1]

            # validate the encoding string
            ret = None
            try:
                ret = codecs.lookup(encoding)
            except LookupError:
                pass
            if ret:
                return encoding

        return locale.getpreferredencoding()

    def _get_restore_function(self):
        """
        Return the binary function for restoring terminal attributes.
        :return: function (signal, frame) => None:
        """
        if os.name == 'nt':
            return lambda signal, frame: None

        assert hasattr(self.stdin, 'fileno'), 'Invalid input device.'
        fd = self.stdin.fileno()

        try:
            initial = termios.tcgetattr(fd)
        except termios.error:
            return lambda signal, frame: None

        return lambda signal, frame: termios.tcsetattr(fd, termios.TCSADRAIN, initial)

    def clear(self):
        """
        Clear the terminal screen.
        """
        if self.stdout.isatty() or self.term_type == 'mintty':
            cmd, shell = {
                'posix': ('clear', False),
                'nt': ('cls', True),
                'cygwin': (['echo', '-en', r'\ec'], False),
                'mintty': (r'echo -en "\ec', False),
            }[self.term_type]
            subprocess.call(cmd, shell=shell, stdin=self.stdin, stdout=self.stdout, stderr=self.stderr)

    def clear_input_buffer(self):
        """
        Clear the input buffer.
        """
        if self.stdin.isatty():
            if os.name == 'nt':
                while msvcrt.kbhit():
                    msvcrt.getch()
            else:
                try:
                    self.stdin.seek(0, 2)  # may fail in some unseekable file object
                except IOError:
                    pass

    def getch(self):
        """
        Read one character from stdin.

        If stdin is not a tty, read input as one line.
        :return: unicode:
        """
        ch = self._get_one_char()
        self.clear_input_buffer()

        try:
            # accept only unicode characters (for Python 2)
            uch = to_unicode(ch, 'ascii')
        except UnicodeError:
            return ''

        return uch if self._check_key_repeat(uch) else ''

    def _get_one_char(self):
        if not self.stdin.isatty():  # pipeline or MinTTY
            return self.gets()[:1]
        elif os.name == 'nt':  # Windows
            return msvcrt.getch()
        else:  # POSIX
            try:
                tty.setraw(self.stdin.fileno())
                return self.stdin.read(1)
            finally:
                self.restore_terminal(None, None)

    def _check_key_repeat(self, ch):
        if self.getch_repeat_threshold <= 0.0:
            return True

        t = time.time()
        if ch == self.last_getch_char and t < self.last_getch_time + self.getch_repeat_threshold:
            return False

        self.last_getch_time = t
        self.last_getch_char = ch
        return True

    def gets(self):
        """
        Read line from stdin.

        The trailing newline will be omitted.
        :return: string:
        """
        ret = self.stdin.readline()
        if ret == '':
            raise EOFError  # To break out of EOF loop
        return ret.rstrip('\n')
