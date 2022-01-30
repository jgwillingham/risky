from bokeh.plotting import figure, show
from bokeh.layouts import row, column, gridplot, Spacer
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import Select, Button, ColumnDataSource, TextInput, Legend, LegendItem



class RiskyAppBuilder:
    def __init__(self):
        self.pages = []
        self.page1 = self.build_page1()
        self.page2 = self.build_page2()
        self.page3 = self.build_page3()
        self.tabs = self.assemble_tabs(self.pages)
        self.sidebar = self.build_sidebar()
        self.complete_layout = self.get_complete_layout(self.sidebar, self.tabs)
        

    def build_page1(self):
        """
        Build contents of tab 1 here
        """
        page1 = column()
        panel1 = Panel(child=page1, title='Page 1')
        self.pages.append(panel1)
        return panel1


    def build_page2(self):
        """
        Build contents of tab 2 here
        """
        page2 = column()
        panel2 = Panel(child=page2, title='Page 2')
        self.pages.append(panel2)
        return panel2


    def build_page3(self):
        """
        Build contents of tab 3 here
        """
        page3 = column()
        panel3 = Panel(child=page3, title='Page 3')
        self.pages.append(panel3)
        return panel3


    def build_sidebar(self):
        """
        Build contents of sidebar here
        """
        loadfile_button = Button(label='Open Simulation File', button_type='success')
        sidebar = column(loadfile_button)
        return sidebar


    def assemble_tabs(self, pages):
        tabs = Tabs(tabs=pages)
        return column(tabs)


    def get_complete_layout(self, sidebar, tabs):
        rowlayout = [sidebar, Spacer(width=50), tabs]
        complete_layout = row(rowlayout)
        return complete_layout