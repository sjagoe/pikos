from collections import namedtuple

import numpy as np

from traits.api import HasTraits, Int, Instance, Enum, \
    Tuple, Either, List, Property, Event, Str
from chaco.api import ArrayPlotData

# from pikos.recorders.zeromq_recorder import RecordingStopped


Details = namedtuple('Details', ['field', 'value'])


class ModelRegistrationError(Exception): pass


class BaseModel(HasTraits):

    @classmethod
    def _get_model_class(cls, profile):
        if profile.lower() == 'memory':
            return cls
        raise ModelRegistrationError()

    @classmethod
    def create_model(cls, pid, profile, fields):
        klass = cls._get_model_class(profile)
        return klass(pid=pid, profile=profile, fields=fields)

    pid = Int
    profile = Str
    fields = Tuple
    plottable_fields = Tuple
    plottable_item_indices = Either(None, Tuple)

    plot_data = Instance(ArrayPlotData)

    index_item = Enum(values='plottable_fields')
    value_item = Enum(values='plottable_fields')

    data_items = List
    selected_index = Either(None, Int)
    selected_item = Property(depends_on='selected_index')

    updated = Event

    TRANSFORMS = {
        'RSS': 1./(1024**2),
        'VMS': 1./(1024**2),
        }

    UNITS = {
        'RSS': 'MB',
        'VMS': 'MB',
        }

    def _plot_data_default(self):
        return ArrayPlotData(
            x=[],
            y=[],
            )

    def _get_selected_item(self):
        if self.selected_index is not None:
            values = self.data_items[self.selected_index]
            return [Details(f, v) for f, v in zip(self.fields, values)]
        return []

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

    def _update_index(self):
        self.__update_plot_values('x', self.index_item)
        if self.index_item in self.UNITS:
            title = '{0} ({1})'.format(
                self.index_item, self.UNITS[self.index_item])
        else:
            title = self.index_item
        # self.plot.x_axis.title = title

    def _update_value(self):
        self.__update_plot_values('y', self.value_item)
        if self.value_item in self.UNITS:
            title = '{0} ({1})'.format(
                self.value_item, self.UNITS[self.value_item])
        else:
            title = self.value_item
        # self.plot.y_axis.title = title

    def _index_item_changed(self):
        self._update_index()

    def _value_item_changed(self):
        self._update_value()

    def _add_data_item(self, name, value):
        exitsing = self.plot_data.get_data(name)
        if name in self.TRANSFORMS:
            value = value * self.TRANSFORMS[name]
        if exitsing is None:
            new = [value]
        else:
            new = np.hstack([exitsing, [value]])
        self.plot_data.set_data(name, new)

    def _calculate_plottable_item_indices(self, item):
        self.plottable_item_indices = tuple(
            [i for i in xrange(len(item))
             if isinstance(item[i], int) or isinstance(item[i], float)])

    def add_data(self, data):
        pid, profile, data = data
        self.data_items.append(data)
        if self.plottable_item_indices is None:
            self._calculate_plottable_item_indices(data)
        for index in self.plottable_item_indices:
            self._add_data_item(self.fields[index], data[index])
        self._update_index()
        self._update_value()
        self.updated = True

    # def _receive_batch(self):
    #     data = []
    #     while True:
    #         socks = dict(self.poller.poll(timeout=0))
    #         if self.data_socket not in socks or \
    #                 socks[self.data_socket] != zmq.POLLIN:
    #             break
    #         item = pickle.loads(self.data_socket.recv())
    #         print item
    #         if isinstance(item, RecordingStopped):
    #             break
    #         data.append(item)
    #     else:
    #         self._add_data(data)
    #         GUI.invoke_later(self._receive_batch)
    #         return
    #     self._add_data(data)
    #     GUI.invoke_after(500, self._receive_batch)
