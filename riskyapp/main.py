
from .riskyappbuilder import RiskyAppBuilder
from bokeh.plotting import output_file, curdoc
import sys
import os


def main():

    if len(sys.argv) < 1:
        datadir = os.getcwd() + "\\"
    else:
        datadir = sys.argv[1]

    app = RiskyAppBuilder(datadir)
    curdoc().add_root(app.complete_layout)
    curdoc().title = 'risky'
    output_file('riskyapp.html')


main()
