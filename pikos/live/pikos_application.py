# Enthought library imports.
from envisage.ui.tasks.api import TasksApplication
from pyface.tasks.api import TaskWindowLayout
from traits.api import Bool, Instance, List, Property

# # Local imports.
# from pikos.live.preferences import PikosPreferences, \
#     PikosPreferencesPane


class PikosApplication(TasksApplication):

    id = 'pikos.live'

    name = 'Pikos Live Profiling'

    default_layout = List(TaskWindowLayout)

    def _default_layout_default(self):
        tasks = [factory.id for factory in self.task_factories]
        return [TaskWindowLayout(*tasks, size=(1024, 768))]
