# Enthought library imports.
from chaco.chaco_plot_editor import ChacoPlotItem
from pyface.tasks.api import TraitsTaskPane
from traits.api import HasTraits, Dict, Enum, Instance, List, Property, \
     Unicode, on_trait_change, Int, Str
from traitsui.api import EnumEditor, HGroup, Item, Label, View, ListEditor


class IntroTab(HasTraits):
    pid = Int
    name = Str('Placeholder')
    traits_view = View(
        Label('A new tab will be created for each profiled process started'),
        )


class PikosTaskPane(TraitsTaskPane):

    #### 'ITaskPane' interface ################################################

    id = 'pikos.live.ui.pikos_task_pane'
    name = 'Pikos Task Pane'

    #### 'MemoryPane' interface ###############################################

    tabs = List

    def _tabs_default(self):
        return [IntroTab()]

    def add_tab(self, model):
        tab = IntroTab(name=str(model.pid))
        self.tabs.append(tab)

    traits_view = View(
        Item(
            'tabs@',
            editor=ListEditor(
                use_notebook=True,
                deletable=False,
                page_name='.name',
                ),
            ),
        resizable=True,
        )
