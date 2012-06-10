from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = 'qt4'

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from pikos.live.pikos_application import PikosApplication
from pikos.live.pikos_plugin import PikosPlugin


def main(argv):
    plugins = [CorePlugin(), TasksPlugin(), PikosPlugin()]
    app = PikosApplication(plugins)
    app.run()


if __name__ == '__main__':
    import sys
    main(sys.argv)
