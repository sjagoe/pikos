from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'

import time
import cPickle as pickle

import zmq

import numpy as np

from traits.api import HasTraits, Str, Any, Int, Instance, Bool, Button, Enum, \
    Tuple
from traitsui.api import View, Item, UItem
from pyface.gui import GUI
from chaco.api import Plot, ArrayPlotData
from enable.component_editor import ComponentEditor

from pikos.recorders.zeromq_recorder import RecordingStopped


class LivePlot(HasTraits):

    context = Instance(zmq.Context, args=())
    prepare_socket = Any
    data_socket = Any

    poller = Any

    host = Str('127.0.0.1')
    port = Int(9001)

    ready = Bool(False)

    start = Button('Start')

    plot_data = Instance(ArrayPlotData)

    memory_plot = Instance(Plot)

    fields = Tuple

    index_item = Enum(values='fields')
    value_item = Enum(values='fields')

    def _prepare_socket_default(self):
        return self.context.socket(zmq.REP)

    def _data_socket_default(self):
        return self.context.socket(zmq.SUB)

    def _poller_default(self):
        poller = zmq.Poller()
        poller.register(self.data_socket, zmq.POLLIN)
        poller.register(self.prepare_socket, zmq.POLLIN)
        return poller

    def _plot_data_default(self):
        return ArrayPlotData(
            x=[],
            y=[],
            )

    def _memory_plot_default(self):
        plot = Plot(self.plot_data)
        plot.plot(('x', 'y'), type='line')
        return plot

    def _fields_changed(self, new):
        if len(new) >= 2:
            self.index_item = new[0]
            self.value_item = new[1]
            self._update_index()
            self._update_value()

    def _update_index(self):
        if self.index_item in self.plot_data.list_data():
            self.plot_data.set_data(
                'x', self.plot_data.get_data(self.index_item))

    def _update_value(self):
        if self.value_item in self.plot_data.list_data():
            self.plot_data.set_data(
                'y', self.plot_data.get_data(self.value_item))

    def _index_item_changed(self):
        self._update_index()

    def _value_item_changed(self):
        self._update_value()

    def _start_fired(self):
        self.data_socket.connect(
            'tcp://{0}:{1}'.format(self.host, self.port))
        self.data_socket.setsockopt(zmq.SUBSCRIBE, '')
        self.prepare_socket.connect(
            'tcp://{0}:{1}'.format(self.host, self.port+1))
        GUI.invoke_later(self._wait_for_ready)

    def _ready_changed(self):
        GUI.invoke_later(self._receive_batch)

    def _wait_for_ready(self, timeout=5000):
        socks = dict(self.poller.poll(timeout=timeout))
        if self.prepare_socket not in socks or \
                socks[self.prepare_socket] != zmq.POLLIN:
            GUI.invoke_after(500, self._wait_for_ready)
            return
        fields = pickle.loads(self.prepare_socket.recv())
        self.prepare_socket.send(pickle.dumps(True))
        # FIXME
        self.fields = fields[0], fields[3], fields[4], fields[5]
        self.ready = True

    def _del_data_item(self, name):
        if name not in self.plot_data.list_data():
            return
        self.plot_data.del_data(name)

    def _add_data_item(self, name, values):
        exitsing = self.plot_data.get_data(name)
        if exitsing is None:
            new = values
        else:
            new = np.hstack([exitsing, values])
        self.plot_data.set_data(name, new)

    def _add_data(self, data):
        if len(data) == 0:
            return

        indexes, types, functions, rss, vms, lineNos, filenames = \
            zip(*data)

        self._add_data_item('index', indexes)
        self._add_data_item('RSS', rss)
        self._add_data_item('VMS', vms)
        self._add_data_item('lineNo', lineNos)

        self._update_index()
        self._update_value()

        self.memory_plot.invalidate_and_redraw()

    def _receive_batch(self):
        data = []
        while True:
            socks = dict(self.poller.poll(timeout=0))
            if self.data_socket not in socks or \
                    socks[self.data_socket] != zmq.POLLIN:
                break
            item = pickle.loads(self.data_socket.recv())
            if isinstance(item, RecordingStopped):
                break
            data.append(item)
        else:
            self._add_data(data)
            GUI.invoke_later(self._receive_batch)
            return
        self._add_data(data)
        GUI.invoke_after(500, self._receive_batch)

    traits_view = View(
        Item('index_item'),
        Item('value_item'),
        UItem('memory_plot', editor=ComponentEditor()),
        Item('start', enabled_when='not ready'),
        )


if __name__ == '__main__':
    live_plot = LivePlot()
    live_plot.configure_traits()
