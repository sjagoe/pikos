# Standard library imports.
import os.path

# Enthought library imports.
from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory
from traits.api import List, Instance


class PikosPlugin(Plugin):
    """ The chaotic attractors plugin.
    """

    # Extension point IDs.
    # PREFERENCES       = 'envisage.preferences'
    # PREFERENCES_PANES = 'envisage.ui.tasks.preferences_panes'
    TASKS             = 'envisage.ui.tasks.tasks'

    #### 'IPlugin' interface ##################################################

    # The plugin's unique identifier.
    id = 'pikos.live'

    # The plugin's name (suitable for displaying to the user).
    name = 'Pikos Live Profiling'

    #### Contributions to extension points made by this plugin ################

    # preferences = List(contributes_to=PREFERENCES)
    # preferences_panes = List(contributes_to=PREFERENCES_PANES)
    tasks = List(contributes_to=TASKS)

    ###########################################################################
    # Protected interface.
    ###########################################################################

    # def _preferences_default(self):
    #     filename = os.path.join(os.path.dirname(__file__), 'preferences.ini')
    #     return [ 'file://' + filename ]

    # def _preferences_panes_default(self):
    #     from attractors_preferences import AttractorsPreferencesPane
    #     return [ AttractorsPreferencesPane ]

    def _tasks_default(self):
        from pikos.live.pikos_task import PikosTask
        return [
            TaskFactory(
                id='pikos.live.pikos_task',
                name='Pikos Live Plotting',
                factory=PikosTask,
                ),
            ]

    def start(self):
        self._zmq_provider.start()

    def stop(self):
        self._zmq_provider.stop()

    ###########################################################################
    # Private interface.
    ###########################################################################

    _zmq_provider = Instance('pikos.live.zmq_provider.ZmqProvider', args=())
