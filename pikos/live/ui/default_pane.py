# Enthought library imports.
from chaco.chaco_plot_editor import ChacoPlotItem
from pyface.tasks.api import TraitsTaskPane
from traits.api import Dict, Enum, Instance, List, Property, \
     Unicode, on_trait_change
from traitsui.api import EnumEditor, HGroup, Item, Label, View


class DefaultPane(TraitsTaskPane):

    #### 'ITaskPane' interface ################################################

    id = 'pikos.live.default_pane'
    name = 'Default Pane'

    #### 'Plot2dPane' interface ###############################################

    view = View(Label('Model'), resizable = True)
