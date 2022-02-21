# Takes stdin from recvfrom() and passes it along

import sys


def PassAlong(args):
    return args


def PassAlongRead(args):

    stdin = ''
    for line in args.readlines():
        stdin += line

    return stdin


stdinput = sys.stdin
print(PassAlong(stdinput))


