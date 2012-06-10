from collections import namedtuple

from traits.api import HasTraits, Int, Instance, Enum, \
    Tuple, Either, Event, Str, Dict
from chaco.api import ArrayPlotData

# from pikos.recorders.zeromq_recorder import RecordingStopped


Details = namedtuple('Details', ['field', 'value'])


class ModelRegistrationError(Exception): pass


class BaseModel(HasTraits):

    pid = Int
    profile = Str
    fields = Tuple
    plottable_fields = Tuple
    plottable_item_indices = Either(None, Tuple)

    plot_data = Instance(ArrayPlotData)

    index_item = Enum(values='plottable_fields')
    value_item = Enum(values='plottable_fields')

    updated = Event

    TRANSFORMS = Dict
    UNITS = Dict

    def _plot_data_default(self):
        return ArrayPlotData(
            x=[],
            y=[],
            )

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

    def _update_value(self):
        self.__update_plot_values('y', self.value_item)

    def _index_item_changed(self):
        self._update_index()

    def _value_item_changed(self):
        self._update_value()

    def _add_data_item(self, name, value):
        raise NotImplementedError()

    def _calculate_plottable_item_indices(self, item):
        self.plottable_item_indices = tuple(
            [i for i in xrange(len(item))
             if isinstance(item[i], int) or isinstance(item[i], float)])

    def add_data(self, records):
        raise NotImplementedError()
