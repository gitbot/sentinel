#! /usr/bin/env python3
"""
A simple command line application that allows easy access to common tasks.
"""

import os

from commando import Application, command, subcommand, store
from fswrap import File

import unittest

class Sentinel(Application):
    """The commando application"""

    @command(
        description='sentinel - Common sentinel tasks',
        epilog='Use %(prog)s {command} -h to get help on individual commands')
    def main(self, args):
        pass

    @subcommand('test',
        help='Runs unit tests.')
    @store('what', default='sentinel/tests', nargs="?",
        help="Path or module to be tested")
    def test(self, args):
        start = None
        pattern = 'test*.py'
        name = None
        if os.sep in args.what:
            what = File(File(args.what).fully_expanded_path)
            if what.path.endswith('.py'):
                start = what.parent.path
                pattern = what.name
            else:
                start = what.path
        else:
            name = args.what

        if name:
            testsuite = unittest.TestLoader().loadTestsFromName(name)
        else:
            testsuite = unittest.TestLoader().discover(start, pattern)
        unittest.TextTestRunner(verbosity=1).run(testsuite)

if __name__ == '__main__':
    Sentinel(raise_exceptions=True).run()