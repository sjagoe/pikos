from traits.api import List, Int, Either, Property

import numpy as np

from pikos.live.models.base_model import BaseModel, Details


class MemoryModel(BaseModel):

    data_items = List
    selected_index = Either(None, Int)
    selected_item = Property(depends_on='selected_index')

    def _TRANSFORMS_default(self):
        return {
            'RSS': 1./(1024**2),
            'VMS': 1./(1024**2),
            }

    def _UNITS_default(self):
        return {
            'RSS': 'MB',
            'VMS': 'MB',
            }

    def _get_selected_item(self):
        if self.selected_index is not None:
            values = self.data_items[self.selected_index]
            return [Details(f, v) for f, v in zip(self.fields, values)]
        return []

    def _add_data_item(self, name, values):
        exitsing = self.plot_data.get_data(name)
        if name in self.TRANSFORMS:
            values = np.array(values) * self.TRANSFORMS[name]
        if exitsing is None:
            new = values
        else:
            new = np.hstack([exitsing, values])
        self.plot_data.set_data(name, new)

    def add_data(self, records):
        self.data_items.extend(records)
        if self.plottable_item_indices is None:
            self._calculate_plottable_item_indices(records[0])
        data = zip(*records)
        for index in self.plottable_item_indices:
            self._add_data_item(self.fields[index], data[index])
        self._update_index()
        self._update_value()
        self.updated = True
