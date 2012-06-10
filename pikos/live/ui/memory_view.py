from traits.api import Any, Int, Bool
from traitsui.api import View, Item, UItem, VGroup, HGroup, Spring, \
    TabularEditor, HSplit, Group
from chaco.api import ScatterInspectorOverlay
from chaco.tools.api import ZoomTool, PanTool, ScatterInspector
from enable.component_editor import ComponentEditor

from pikos.live.ui.base_view import BaseView, DisableTrackingPlot, \
    DetailsAdapter


class MemoryView(BaseView):

    scatter = Any

    follow_plot = Bool(False)
    last_n_points = Int(100000)

    # Initialization

    def _plot_default(self):
        container = DisableTrackingPlot(
            self.model.plot_data,
            live_plot=self,
            )
        container.padding_left = 100
        container.plot(('x', 'y'), type='line')[0]

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

    # Handlers

    def _reset_view_button_fired(self):
        self.follow_plot = False
        self.plot.x_mapper.range.low_setting = 'auto'
        self.plot.x_mapper.range.high_setting = 'auto'

    def _metadata_changed(self, new):
        data_indices = self.scatter.index.metadata.get('selections', [])
        if len(data_indices) == 0:
            self.model.selected_index = None
            return
        self.model.selected_index = data_indices[0]

    def _last_n_points_changed(self):
        self.plot.x_mapper.range.tracking_amount = self.last_n_points

    def _follow_plot_changed(self):
        if self.follow_plot:
            self.plot.x_mapper.range.low_setting = 'track'
            self.plot.x_mapper.range.high_setting = 'auto'
            self.plot.x_mapper.range.tracking_amount = self.last_n_points
        else:
            self.plot.x_mapper.range.low_setting = self.plot.x_mapper.range.low
            self.plot.x_mapper.range.high_setting = \
                self.plot.x_mapper.range.high

    traits_view = View(
        Group(
            VGroup(
                HGroup(
                    Item('model.index_item'),
                    Item('model.value_item'),
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
                    ),
                ),
            HSplit(
                UItem('plot', editor=ComponentEditor()),
                UItem(
                    'model.selected_item',
                    editor=TabularEditor(adapter=DetailsAdapter()),
                    width=350),
                ),
            ),
        height=800,
        width=1100,
        resizable=True,
        title='Live Recording Plot'
        )
