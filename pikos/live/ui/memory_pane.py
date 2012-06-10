# Enthought library imports.
from chaco.chaco_plot_editor import ChacoPlotItem
from pyface.tasks.api import TraitsTaskPane
from traits.api import Dict, Enum, Instance, List, Property, \
     Unicode, on_trait_change
from traitsui.api import EnumEditor, HGroup, Item, Label, View


class MemoryPane(TraitsTaskPane):

    #### 'ITaskPane' interface ################################################

    id = 'pikos.live.memory_pane'
    name = 'Memory Plot Pane'

    #### 'MemoryPane' interface ###############################################

    view = View(Label('Model'), resizable = True)

    model = Instance('pikos.live.models.memory_model.MemoryModel')
