# Enthought library imports.
from chaco.chaco_plot_editor import ChacoPlotItem
from pyface.tasks.api import TraitsTaskPane
from traits.api import HasTraits, Dict, Enum, Instance, List, Property, \
     Unicode, on_trait_change, Int, Str
from traitsui.api import EnumEditor, HGroup, UItem, Label, View, ListEditor

from pikos.live.utils import get_view_for_profile


class IntroTab(HasTraits):
    pid = Int
    title = Str('Placeholder')
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

    def _make_new_tab_title(self, model):
        return str(model.pid)

    def add_tab(self, model):
        title = self._make_new_tab_title(model)
        view_class = get_view_for_profile(model.profile)
        tab = view_class(title=str(model.pid), model=model)
        self.tabs.append(tab)

    traits_view = View(
        UItem(
            'tabs@',
            editor=ListEditor(
                use_notebook=True,
                deletable=False,
                page_name='.title',
                ),
            ),
        resizable=True,
        )
