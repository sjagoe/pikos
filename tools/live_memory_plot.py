from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'

import time
import cPickle as pickle

import zmq

import numpy as np

from traits.api import HasTraits, Str, Any, Int, Instance, Bool, Button, Enum, \
    Tuple, Either, DelegatesTo, on_trait_change, WeakRef, List, Either, Property
from traitsui.api import View, Item, UItem, VGroup, HGroup, Spring, \
    TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from pyface.gui import GUI
from chaco.api import Plot, ArrayPlotData, ScatterInspectorOverlay
from chaco.tools.api import ZoomTool, PanTool, ScatterInspector
from chaco.tools.tool_states import SelectedZoomState
from enable.component_editor import ComponentEditor

from pikos.recorders.zeromq_recorder import RecordingStopped


class DetailsAdapter(TabularAdapter):

    columns = (
        ('Field', 0),
        ('Value', 1),
        )


class DisableTrackingPlot(Plot):

    live_plot = WeakRef('LivePlot')

    def dispatch(self, event, suffix):
        if 'mouse' not in suffix:
            self.live_plot.follow_plot = False
        super(DisableTrackingPlot, self).dispatch(event, suffix)


class LivePlot(HasTraits):

    context = Instance(zmq.Context, args=())
    prepare_socket = Any
    data_socket = Any

    poller = Any

    host = Str('127.0.0.1')
    port = Int(9001)

    ready = Bool(False)

    start_button = Button('Start')
    reset_view_button = Button('Reset View')

    plot_data = Instance(ArrayPlotData)

    plot = Instance(DisableTrackingPlot)
    scatter = Any

    zoom_tool = Instance(ZoomTool)
    pan_tool = Instance(PanTool)

    fields = Tuple
    plottable_fields = Tuple
    plottable_item_indices = Either(None, Tuple)

    index_item = Enum(values='plottable_fields')
    value_item = Enum(values='plottable_fields')

    data_items = List
    selected_index = Either(None, Int)
    selected_item = Property(depends_on='selected_index')

    follow_plot = Bool(False)
    last_n_points = Int(100000)

    TRANSFORMS = {
        'RSS': 1./(1024**2),
        'VMS': 1./(1024**2),
        }

    UNITS = {
        'RSS': 'MB',
        'VMS': 'MB',
        }

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

    def _plot_default(self):
        container = DisableTrackingPlot(
            self.plot_data,
            live_plot=self,
            )
        container.padding_left = 100
        plot = container.plot(('x', 'y'), type='line')[0]

        scatter = container.plot(
            ('x', 'y'),
            type='scatter',
            marker_size=1,
            show_selection=False,
            color='lightskyblue',
            )
        self.scatter = scatter[0]
        inspector = ScatterInspector(
            self.scatter,
            selection_mode='single',
            )
        self.scatter.tools.append(inspector)
        overlay = ScatterInspectorOverlay(self.scatter,
                                          hover_color="lightskyblue",
                                          hover_marker_size=2,
                                          selection_marker_size=3,
                                          selection_color="lightskyblue",
                                          selection_outline_color="black",
                                          selection_line_width=1)
        self.scatter.overlays.append(overlay)

        self.scatter.index.on_trait_change(
            self._metadata_changed, "metadata_changed")

        self.zoom_tool = ZoomTool(
            container,
            )
        container.underlays.append(self.zoom_tool)
        container.tools.append(self.zoom_tool)
        self.pan_tool = PanTool(
            container,
            )
        container.tools.append(self.pan_tool)

        return container

    def _metadata_changed(self, new):
        data_indices = self.scatter.index.metadata.get('selections', [])
        if len(data_indices) == 0:
            self.selected_index = None
            return
        self.selected_index = data_indices[0]

    def _get_selected_item(self):
        if self.selected_index is not None:
            values = self.data_items[self.selected_index]
            return zip(self.fields, values)
        return ()

    def _plottable_item_indices_changed(self, new):
        self.plottable_fields = [self.fields[i] for i in new]

    def _plottable_fields_changed(self, new):
        if len(new) >= 2:
            self.index_item = new[0]
            self.value_item = new[1]
            self._update_index()
            self._update_value()

    def __update_plot_values(self, axis, value_name):
        if value_name in self.plot_data.list_data():
            new_points = self.plot_data.get_data(value_name)
            self.plot_data.set_data(axis, new_points)

    def _last_n_points_changed(self):
        self.plot.x_mapper.range.tracking_amount = self.last_n_points

    def _follow_plot_changed(self):
        if self.follow_plot:
            self.plot.x_mapper.range.low_setting = 'track'
            self.plot.x_mapper.range.high_setting = 'auto'
            self.plot.x_mapper.range.tracking_amount = self.last_n_points
        else:
            self.plot.x_mapper.range.low_setting = self.plot.x_mapper.range.low
            self.plot.x_mapper.range.high_setting = self.plot.x_mapper.range.high

    def _reset_view_button_fired(self):
        self.follow_plot = False
        self.plot.x_mapper.range.low_setting = 'auto'
        self.plot.x_mapper.range.high_setting = 'auto'

    def _update_index(self):
        self.__update_plot_values('x', self.index_item)
        if self.index_item in self.UNITS:
            title = '{0} ({1})'.format(
                self.index_item, self.UNITS[self.index_item])
        else:
            title = self.index_item
        self.plot.x_axis.title = title

    def _update_value(self):
        self.__update_plot_values('y', self.value_item)
        if self.value_item in self.UNITS:
            title = '{0} ({1})'.format(
                self.value_item, self.UNITS[self.value_item])
        else:
            title = self.value_item
        self.plot.y_axis.title = title

    def _index_item_changed(self):
        self._update_index()

    def _value_item_changed(self):
        self._update_value()

    def _start_button_fired(self):
        self.data_socket.connect(
            'tcp://{0}:{1}'.format(self.host, self.port))
        self.data_socket.setsockopt(zmq.SUBSCRIBE, '')
        self.prepare_socket.connect(
            'tcp://{0}:{1}'.format(self.host, self.port+1))
        GUI.invoke_later(self._wait_for_ready)

    def _ready_changed(self):
        GUI.invoke_later(self._receive_batch)

    def _wait_for_ready(self, timeout=250):
        socks = dict(self.poller.poll(timeout=timeout))
        if self.prepare_socket not in socks or \
                socks[self.prepare_socket] != zmq.POLLIN:
            GUI.invoke_after(500, self._wait_for_ready)
            return
        fields = pickle.loads(self.prepare_socket.recv())
        self.prepare_socket.send(pickle.dumps(True))
        # FIXME
        self.fields = fields
        self.ready = True

    def _del_data_item(self, name):
        if name not in self.plot_data.list_data():
            return
        self.plot_data.del_data(name)

    def _add_data_item(self, name, values):
        exitsing = self.plot_data.get_data(name)
        if name in self.TRANSFORMS:
            values = np.array(values) * self.TRANSFORMS[name]
        if exitsing is None:
            new = values
        else:
            new = np.hstack([exitsing, values])
        self.plot_data.set_data(name, new)

    def _calculate_plottable_item_indices(self, data):
        item = data[0]
        self.plottable_item_indices = tuple(
            [i for i in xrange(len(item))
             if isinstance(item[i], int) or isinstance(item[i], float)])

    def _add_data(self, data):
        if len(data) == 0:
            return

        self.data_items = self.data_items + data

        if self.plottable_item_indices is None:
            self._calculate_plottable_item_indices(data)

        data = zip(*data)

        for index in self.plottable_item_indices:
            self._add_data_item(self.fields[index], data[index])

        self._update_index()
        self._update_value()

        self.plot.invalidate_and_redraw()

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
        VGroup(
            HGroup(
                Item('index_item'),
                Item('value_item'),
                ),
            HGroup(
                Item(
                    'follow_plot',
                    label='Follow plot',
                    ),
                Item(
                    'last_n_points',
                    label='Number of points to show',
                    enabled_when='follow_plot',
                    ),
                ),
            HGroup(
                Spring(),
                UItem('reset_view_button'),
                UItem(
                    'start_button',
                    enabled_when='not ready',
                    ),
                ),
            ),
        UItem('plot', editor=ComponentEditor()),
        UItem('selected_item', editor=TabularEditor(adapter=DetailsAdapter())),
        height=600,
        width=800,
        resizable=True,
        title='Live Recording Plot'
        )


if __name__ == '__main__':
    live_plot = LivePlot()
    live_plot.configure_traits()
