from operator import itemgetter
from traits.api import Any, Dict, Property, List

from pikos.live.models.base_model import BaseModel

import numpy as np


class CProfileModel(BaseModel):

    data_items = Dict
    plot_keys = List
    selected_index = Any
    selected_item = Property(depends_on='selected_index')

    # def _TRANSFORMS_default(self):
    #     return {
    #         'RSS': 1./(1024**2),
    #         'VMS': 1./(1024**2),
    #         }

    # def _UNITS_default(self):
    #     return {
    #         'RSS': 'MB',
    #         'VMS': 'MB',
    #         }

    def _get_selected_item(self):
        return []
        # if self.selected_index is not None:
        #     values = self.data_items[self.selected_index]
        #     return [Details(f, v) for f, v in zip(self.fields, values)]
        # return []

    def _update_index(self):
        pass

    def _update_value(self):
        super(CProfileModel, self)._update_value()
        data_len = len(self.plot_data.get_data('y'))
        self.plot_data.set_data('x', range(data_len))

    def _rebuild_data(self):
        data = zip(*sorted(self.data_items.values(), key=itemgetter(6),
                           reverse=True))
        self.plot_keys = list(data[0])
        for index in self.plottable_item_indices:
            self.plot_data.set_data(self.fields[index], np.array(data[index]))

    def add_data(self, records):
        data = {}
        for record in reversed(records):
            id_ = record[0]
            if id_ in data:
                continue
            data[id_] = record
        self.data_items.update(data)
        if self.plottable_item_indices is None:
            self._calculate_plottable_item_indices(records[0])
        self._rebuild_data()
        self._update_index()
        self._update_value()
        self.updated = True
