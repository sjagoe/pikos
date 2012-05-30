from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'

import time
import cPickle as pickle

import zmq

from traits.api import HasTraits, Str, Any, Int, Instance, Bool, Button
from traitsui.api import View, Item
from pyface.gui import GUI

from pikos.recorders.zeromq_recorder import RecordingStopped


class LivePlot(HasTraits):

    context = Instance(zmq.Context, args=())
    prepare_socket = Any
    data_socket = Any

    poller = Any

    host = Str('127.0.0.1')
    port = Int(9001)

    count = Int

    ready = Bool(False)

    start = Button('Start')

    def _prepare_socket_default(self):
        return self.context.socket(zmq.REQ)

    def _data_socket_default(self):
        return self.context.socket(zmq.SUB)

    def _poller_default(self):
        poller = zmq.Poller()
        poller.register(self.data_socket, zmq.POLLIN)
        poller.register(self.prepare_socket, zmq.POLLIN)
        return poller

    def _start_fired(self):
        self.data_socket.connect('tcp://{0}:{1}'.format(self.host, self.port))
        self.data_socket.setsockopt(zmq.SUBSCRIBE, '')
        self.prepare_socket.connect(
                'tcp://{0}:{1}'.format(self.host, self.port+1))
        GUI.invoke_later(self._wait_for_ready)

    def _ready_changed(self):
        GUI.invoke_later(self._receive_batch)

    def _wait_for_ready(self, timeout=5000):
        self.prepare_socket.send(pickle.dumps(True))
        socks = dict(self.poller.poll(timeout=timeout))
        if self.prepare_socket not in socks or \
                socks[self.prepare_socket] != zmq.POLLIN:
            raise Exception()
        ready = pickle.loads(self.prepare_socket.recv())
        if not ready:
            GUI.invoke_later(self._wait_for_ready)
        else:
            self.ready = ready

    def _receive_batch(self):
        while True:
            socks = dict(self.poller.poll(timeout=0))
            if self.data_socket not in socks or \
                    socks[self.data_socket] != zmq.POLLIN:
                break
            data = pickle.loads(self.data_socket.recv())
            self.count += 1
        GUI.invoke_later(self._receive_batch)

    traits_view = View(
        Item('ready'),
        Item('count'),
        Item('start'),
        )


if __name__ == '__main__':
    live_plot = LivePlot()
    live_plot.configure_traits()
