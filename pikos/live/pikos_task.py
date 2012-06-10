# Enthought library imports.
from pyface.tasks.action.api import SGroup, SMenu, SMenuBar, \
    TaskToggleGroup
from pyface.tasks.api import Task, TaskLayout, Tabbed, PaneItem
from traits.api import Any, List

from pikos.live.ui.memory_pane import MemoryPane


class PikosTask(Task):

    #### 'Task' interface #####################################################

    id = 'pikos.live.pikos_task'
    name = 'Pikos Live Plotting'

    menu_bar = SMenuBar(SMenu(id='File', name='&File'),
                        SMenu(id='Edit', name='&Edit'),
                        SMenu(TaskToggleGroup(),
                              id='View', name='&View'))

    #### 'PikosTask' interface ################################################

    ###########################################################################
    # 'Task' interface.
    ###########################################################################

    def create_central_pane(self):
        """ Create a plot pane with a list of models. Keep track of which model
            is active so that dock panes can introspect it.
        """
        pane = MemoryPane()
        return pane

    # def create_dock_panes(self):
    #     return [ ModelConfigPane(model=self.active_model),
    #              ModelHelpPane(model=self.active_model) ]

    ###########################################################################
    # Protected interface.
    ###########################################################################

    #### Trait initializers ###################################################

    # def _default_layout_default(self):
    #     return TaskLayout(
    #         left=Tabbed(PaneItem('example.attractors.model_config_pane'),
    #                     PaneItem('example.attractors.model_help_pane')))

    # def _models_default(self):
    #     from model.henon import Henon
    #     from model.lorenz import Lorenz
    #     from model.rossler import Rossler
    #     return [ Henon(), Lorenz(), Rossler() ]

    #### Trait change handlers ################################################

    # def _update_active_model(self):
    #     self.active_model = self.window.central_pane.active_model
    #     for dock_pane in self.window.dock_panes:
    #         dock_pane.model = self.active_model
