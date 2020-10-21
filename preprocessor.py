#!/usr/bin/env python3
import sys
from textx import metamodel_from_str, get_children_of_type
from textx.exceptions import TextXSyntaxError
from dataclasses import dataclass
import textwrap

def main():
    pydf = sys.stdin.read()
    df = convert_pydf_to_df(pydf)
    sys.stdout.write(df)

class Node:
    def __init__(self, **kw):
        del self.parent



# http://textx.github.io/textX/latest/grammar/
GRAMMAR = r"""
Root: root+=VirtualLine;
VirtualLine: (comment=Comment_ | command=FullCommand | empty=EMPTY);
EMPTY: /^\s*\n/;
//EOL: /[^\\]\n/;
FullCommand: /[ \t]*/ (pycommand=PyDockerfileCommands | !PyDockerfileCommandsKeywords originalcommand=/\S(\n|.)*?[^\\]\n/ );
Comment_: /^\s*#.*\n/;


PyDockerfileCommandsKeywords: /(?i)(PIP|APT|PYENVS)\b/;
PyDockerfileCommands: PyDockerfileCommandsKeywords /(\n|.)*?(?<!\\)\n/;
"""

def convert_pydf_to_df(pydf):
    root = parse_pydf(pydf)
    stringifier = Stringifier(preprocess=True)
    return stringifier(root)

def stringify_pycommand(node):
    assert isinstance(node, str)
    return node

def preprocess_pycommand(node):
    assert isinstance(node, str)
    command, *args = node.replace('\\\n', ' ').split()
    command = command.lower()
    wrap = lambda t: textwrap.fill(t, width=70, subsequent_indent='  ',
            break_long_words=False, break_on_hyphens=False).strip().replace('\n', ' \\\n') + '\n'

    if command == 'pip':
        out = f"RUN --mount=type=cache,target=/root/.cache/pip/,id=pip pip install {' '.join(args)}"
        return wrap(out)
    elif command == 'apt':
        out = f"""RUN --mount=type=cache,target=/var/lib/apt,id=apt_lists
                --mount=type=cache,target=/var/cache/apt,id=apt_archives
                apt-get update && apt-get install -y {' '.join(args)} """
        return wrap(out)
    elif command == 'pyenvs':
        assert not args , 'PYENVS should have no arguments'
        return wrap('ENV PIP_NO_PYTHON_VERSION_WARNING=1 PYTHONDONTWRITEBYTECODE=1')
    assert False, node

@dataclass
class Stringifier:
    preprocess: bool

    def __call__(self, node,):
        if isinstance(node, list): return '\n'.join(self(i) for i in node)
        if node is None: return ''
        elif isinstance(node, str): return node
        elif isinstance(node, VirtualLine):
            return self(node.comment) + self(node.command) + self(node.empty)
        elif isinstance(node, FullCommand):
            if node.pycommand:
                return preprocess_pycommand(node.pycommand) if self.preprocess else stringify_pycommand(node.pycommand)
            if node.originalcommand: return self(node.originalcommand)
            assert False, node
        else:
            assert False, node

class VirtualLine(Node): pass
class FullCommand(Node): pass

def parse_pydf(pydf):
    MM = metamodel_from_str(GRAMMAR, skipws=False, debug=False, classes=[VirtualLine, FullCommand, ])
    try:
        model = MM.model_from_str(pydf)
    except TextXSyntaxError as e:
        sys.stderr.write(f"ERROR at Dockerfile {pydf!r} - {e} \n")
        exit(1)
    root = model.root
    return root

def test_preprocessor():
    pydf = r"""
FROM alpine
RUN this
# comment
RUN long \
run

RUN not a #comment
PiP fred
"""
    root = parse_pydf(pydf)
    assert root[0].empty
    assert root[1].command
    assert root[2].command
    assert root[3].comment
    assert root[4].command
    assert root[5].empty
    assert root[6].command
    assert root[7].command.pycommand

    stringifier = Stringifier(preprocess=False)
    assert ''.join(stringifier(n) for n in root) == pydf

def test_preprocessor_pip_apt():
    pydf = r"""
FROM python:alpine
PYENVS
PiP fred lib1 \
        lib2 lib3 lib4 lib5 lib6 lib7 lib8 lib9 lib10 lib11  lib12 lib13 lib14  lib15 lib16 lib17
APT htop
"""
    OUT = (r'''
FROM python:alpine
ENV PIP_NO_PYTHON_VERSION_WARNING=1 PYTHONDONTWRITEBYTECODE=1
RUN --mount=type=cache,target=/root/.cache/pip/,id=pip pip install \
  fred lib1 lib2 lib3 lib4 lib5 lib6 lib7 lib8 lib9 lib10 lib11 lib12 \
  lib13 lib14 lib15 lib16 lib17
RUN --mount=type=cache,target=/var/lib/apt,id=apt_lists \
  --mount=type=cache,target=/var/cache/apt,id=apt_archives \
  apt-get update && apt-get install -y htop
''')

    root = parse_pydf(pydf)

    stringifier = Stringifier(preprocess=False)
    assert ''.join(stringifier(n) for n in root) == pydf
    stringifier.preprocess = True
    assert ''.join(stringifier(n) for n in root).strip() == OUT.strip()

def test_stringify_normal_dockerfiles():
    import glob
    for file in glob.glob('tests/sample*.dockerfile'):
        with open(file) as f: pydf = f.read()
        root = parse_pydf(pydf)
        stringifier = Stringifier(preprocess=False)
        assert ''.join(stringifier(n) for n in root) == pydf


if __name__ == '__main__':
    main()
