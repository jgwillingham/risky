from bokeh.plotting import figure, show
from bokeh.layouts import row, column, gridplot, Spacer
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import (
    Select, 
    Button, 
    ColumnDataSource, 
    Legend, 
    LegendItem, 
    FileInput, 
    Div )

import sys
sys.path.append("..")
from risky.analysis import Analysis

SIDEBAR_HEIGHT = 300

class RiskyAppBuilder:
    """
    Class for constructing the risky Bokeh app
    """
    def __init__(self, datadir):
        self.datadir = datadir
        self.pages = []
        self.page1 = self.build_page1()
        self.page2 = self.build_page2()
        self.page3 = self.build_page3()
        self.tabs = self.assemble_tabs(self.pages)
        self.fileinput, self.analyze_button = self.setup_fileinput()
        self.sidebar = self.build_sidebar(self.fileinput, self.analyze_button)
        self.complete_layout = self.get_complete_layout(self.sidebar, self.tabs)

        self.analysis = None
        

    def build_page1(self):
        """
        Build contents of tab 1 here
        """
        page1_name = 'Log-Return Distributions'
        page1 = column()
        panel1 = Panel(child=page1, title=page1_name)
        self.pages.append(panel1)
        return panel1


    def build_page2(self):
        """
        Build contents of tab 2 here
        """
        page2_name = 'Stationarity'
        page2 = column()
        panel2 = Panel(child=page2, title=page2_name)
        self.pages.append(panel2)
        return panel2


    def build_page3(self):
        """
        Build contents of tab 3 here
        """
        page3_name = 'Miscellaneous'
        page3 = column()
        panel3 = Panel(child=page3, title=page3_name)
        self.pages.append(panel3)
        return panel3

    
    def setup_fileinput(self):
        fileinput = FileInput(accept='.h5')
        analyze_button = Button(label='Open Dataset', button_type='primary', width=75)
        analyze_button.disabled = True

        fileinput.on_change('filename', self._callback_on_fileinput)
        analyze_button.on_click(self._callback_on_create_analysis)

        return fileinput, analyze_button

    
    def _callback_on_fileinput(self, attr, old, new):
        if attr != '':
            self.analyze_button.disabled = False
        filepath = self.datadir + self.fileinput.filename
        self.analysis = Analysis(filepath)
        self._update_sidebar_text()



    def _callback_on_create_analysis(self):
        pass


    def _update_sidebar_text(self):
        securities = self.analysis.securities
        securities = [sec + "    " for sec in securities]
        securities_format = "".join(securities)
        num_steps = self.analysis.num_steps
        numiter = self.analysis.num_iterations

        self.sidebar_text.text = "<h3>SUMMARY</h3>" + \
                                 f"<b>Securities : </b> {securities_format}<br>" + \
                                 f"<b>Ensemble Size : </b> {numiter}<br>" + \
                                 f"<b>Steps into Future : </b> {num_steps}<br>" + \
                                 f"<b>File : </b> {self.fileinput.filename}"


    def build_sidebar(self, fileinput, analyze_button):
        """
        Build contents of sidebar here
        """
        self.sidebar_text = Div()
        self.sidebar_text.text = "<h3>SUMMARY</h3>" + \
                                 "<b>Securities : </b><br>" + \
                                 "<b>Ensemble Size : </b><br>" + \
                                 "<b>Steps into Future : </b><br>" + \
                                 "<b>File :"
        sidebar = column(self.fileinput, Spacer(height=5), \
                        self.sidebar_text, Spacer(height=25), analyze_button, background='#add8e6', height=SIDEBAR_HEIGHT)
        return sidebar


    def assemble_tabs(self, pages):
        tabs = Tabs(tabs=pages)
        return column(tabs)

    
    def pad_layout(self, layout, padx, pady):
        padded_layout = row(Spacer(width=padx), layout, Spacer(width=padx))
        padded_layout = column(Spacer(height=pady), padded_layout, Spacer(height=pady))
        return padded_layout


    def get_complete_layout(self, sidebar, tabs, padx=25, pady=25):
        edgeL = column( Div(text=""), background='black', height=SIDEBAR_HEIGHT)
        edgeR = column( Div(text=""), background='black', height=SIDEBAR_HEIGHT)
        rowlayout = [edgeL, sidebar, edgeR, Spacer(width=50), tabs]
        layout = row(rowlayout)
        padded_layout = self.pad_layout(layout, padx, pady)
        return padded_layout