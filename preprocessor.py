#!/usr/bin/env python3
import sys
from textx import metamodel_from_str, get_children_of_type

def main():
    pydf = sys.stdin.read()
    df = convert_pydf_to_df(pydf)
    sys.stdout.write(df)

# http://textx.github.io/textX/latest/grammar/
GRAMMAR = r"""
Root: commands+=(Comment EOL | FullCommand EOL | EMPTY);
EMPTY: /^\w*$/;
EOL: /[^\\]\n/;
FullCommand: PyDockerfileCommands | /.*/;
Comment: /^\w*$/ | /^\w*#.*$/;

PyDockerfileCommands: PIP;
PIP: 'PIP ' /.*/;
"""
# Comment: '^\w*$ | ^\w*#[^\n]*$

_GRAMMAR = """
Model: commands*=DrawCommand;
DrawCommand: MoveCommand | ShapeCommand;
ShapeCommand: LineTo | Circle;
MoveCommand: MoveTo | MoveBy;
MoveTo: 'move' 'to' position=Point;
MoveBy: 'move' 'by' vector=Point;
Circle: 'circle' radius=INT;
LineTo: 'line' 'to' point=Point;
Point: x=INT ',' y=INT;
"""

mm = metamodel_from_str(GRAMMAR, )#  classes=[Point])

model_str = """
FROM alpine
RUN this
# comment
RUN not a #comment
"""

# Meta-model knows how to parse and instantiate models.
model = mm.model_from_str(model_str)

if __name__ == '__main__':
    main()
