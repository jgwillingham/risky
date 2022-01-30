
from .riskyappbuilder import RiskyAppBuilder
from bokeh.plotting import output_file, curdoc


def main():
    app = RiskyAppBuilder()
    curdoc().add_root(app.complete_layout)
    curdoc().title = 'Model Validator'
    output_file('riskyapp.html')


main()
