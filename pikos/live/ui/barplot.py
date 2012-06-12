import numpy as np

from traits.api import Bool, Str

from chaco.api import BarPlot
from chaco.tools.api import SelectTool


class SelectableBarPlot(BarPlot):

    def map_index(self, screen_pt, threshold=2.0, outside_returns_none=True,
                  index_only=False):
        """ Maps a screen space point to an index into the plot's index array(s).

        Overrides the BarPlot implementation
        """
        if not index_only:
            return super(SelectableBarPlot, self).map_index(
                screen_pt, threshold, outside_returns_none, index_only)

        if not self._cache_valid:
            self._gather_points()

        data_pt = self.map_data(screen_pt)
        if ((data_pt < self.index_mapper.range.low) or \
            (data_pt > self.index_mapper.range.high)) and outside_returns_none:
            return None
        index_data = self.index.get_data()
        value_data = self.value.get_data()
        if len(value_data) == 0 or len(index_data) == 0:
            return None

        bars = self._cached_data_pts[:,:2]
        screen_bars = self.map_screen(bars)
        screen_bars[:,1] = self.map_screen(bars[:,::-1])[:,0]

        x = screen_pt[0]

        possible_indices = np.where((screen_bars[:,0] < (x+threshold)) & \
                                        (screen_bars[:,1] > (x-threshold)))[0]
        if len(possible_indices) == 0:
            return None
        possibles = screen_bars[possible_indices]
        mids = possibles[:,0] + ((possibles[:,1] - possibles[:,0]) / 2)
        scores = np.abs(mids - x)
        return np.where(scores == np.min(scores))[0][0]


class BarSelectTool(SelectTool):
    """ A tool for inspecting scatter plots.

    It writes the index of the point under the cursor to the metadata of the
    index and value data sources, and allows clicking to select the point.
    Other components can listen for metadata updates on the data sources.

    By default, it writes the index of the point under the cursor to the "hover"
    key in metadata, and the index of a clicked point to "selection".
    """

    # If persistent_hover is False, then a point will be de-hovered as soon as
    # the mouse leaves its hittesting area.  If persistent_hover is True, then
    # a point does no de-hover until another point get hover focus.
    persistent_hover = Bool(False)

    # The names of the data source metadata for hover and selection.
    hover_metadata_name = Str('hover')
    selection_metadata_name = Str('selections')

    #------------------------------------------------------------------------
    # Override/configure inherited traits
    #------------------------------------------------------------------------

    # This tool is not visible
    visible = False

    # This tool does not have a visual reprentation
    draw_mode = "none"

    def normal_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'normal' state.

        If the cursor is within **threshold** of a data point, the method
        writes the index to the plot's data sources' "hover" metadata.
        """
        plot = self.component
        index = plot.map_index((event.x, event.y), threshold=self.threshold,
                               index_only=True)
        if index is not None:
            plot.index.metadata[self.hover_metadata_name] = [index]
            if hasattr(plot, "value"):
                plot.value.metadata[self.hover_metadata_name] = [index]
        elif not self.persistent_hover:
            plot.index.metadata.pop(self.hover_metadata_name, None)
            if hasattr(plot, "value"):
                plot.value.metadata.pop(self.hover_metadata_name, None)
        return

    def _get_selection_state(self, event):
        plot = self.component
        index = plot.map_index((event.x, event.y), threshold=self.threshold,
                               index_only=True)

        already_selected = False
        # FIXME: this is stupid
        for name in ('index', 'value'):
            if not hasattr(plot, name):
                continue
            md = getattr(plot, name).metadata
            if md is None or self.selection_metadata_name not in md:
                continue
            if index in md[self.selection_metadata_name]:
                already_selected = True
                break
        return already_selected, (index is not None)

    def _get_selection_token(self, event):
        plot = self.component
        index = plot.map_index((event.x, event.y), threshold=self.threshold,
                               index_only=True)
        return index

    def _deselect(self, index=None):
        """ Deselects a particular index.  If no index is given, then
        deselects all points.
        """
        plot = self.component
        for name in ('index', 'value'):
            if not hasattr(plot, name):
                continue
            md = getattr(plot, name).metadata
            if not self.selection_metadata_name in md:
                pass
            elif index in md[self.selection_metadata_name]:
                new_list = md[self.selection_metadata_name][:]
                new_list.remove(index)
                md[self.selection_metadata_name] = new_list
                getattr(plot, name).metadata_changed = True
        return

    def _select(self, index, append=True):
        plot = self.component
        for name in ('index', 'value'):
            if not hasattr(plot, name):
                continue
            md = getattr(plot, name).metadata
            selection = md.get(self.selection_metadata_name, None)

            # If no existing selection
            if selection is None:
                md[self.selection_metadata_name] = [index]
            # check for list-like object supporting append
            else:
                if append:
                    if index not in md[self.selection_metadata_name]:
                        new_list = md[self.selection_metadata_name] + [index]
                        md[self.selection_metadata_name] = new_list
                        # Manually trigger the metadata_changed event on
                        # the datasource.  Datasources only automatically
                        # fire notifications when the values inside the
                        # metadata dict change, but they do not listen
                        # for further changes on those values.
                        getattr(plot, name).metadata_changed = True
                else:
                    md[self.selection_metadata_name] = [index]
        return
