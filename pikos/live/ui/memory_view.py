from traits.api import Any, Str, Int, Instance, Bool, Button, \
    WeakRef, on_trait_change
from traitsui.api import ModelView, View, Item, UItem, VGroup, HGroup, Spring, \
    TabularEditor, HSplit, Group
from traitsui.tabular_adapter import TabularAdapter
from chaco.api import Plot, ScatterInspectorOverlay
from chaco.tools.api import ZoomTool, PanTool, ScatterInspector
from enable.component_editor import ComponentEditor


class DisableTrackingPlot(Plot):

    live_plot = WeakRef('MemoryView')

    def dispatch(self, event, suffix):
        if 'mouse' not in suffix:
            self.live_plot.follow_plot = False
        super(DisableTrackingPlot, self).dispatch(event, suffix)


class DetailsAdapter(TabularAdapter):

    columns = (
        ('Field', 'field'),
        ('Value', 'value'),
        )

    def get_width(self, *args):
        return 150


class MemoryView(ModelView):

    title = Str

    reset_view_button = Button('Reset View')

    plot = Instance(DisableTrackingPlot)
    scatter = Any

    zoom_tool = Instance(ZoomTool)
    pan_tool = Instance(PanTool)

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
            self.plot.x_mapper.range.high_setting = self.plot.x_mapper.range.high

    @on_trait_change('model.updated')
    def _model_updated(self):
        self.plot.invalidate_and_redraw()

    @on_trait_change('model.index_item')
    def _on_model_index_item_change(self, index_item):
        if index_item is None:
            return
        if index_item in self.model.UNITS:
            index_title = '{0} ({1})'.format(
                index_item, self.model.UNITS[index_item])
        else:
            index_title = index_item
        self.plot.x_axis.title = index_title

    @on_trait_change('model.value_item')
    def _on_model_value_item_change(self, value_item):
        if value_item is None:
            return
        if value_item in self.model.UNITS:
            value_title = '{0} ({1})'.format(
                value_item, self.model.UNITS[value_item])
        else:
            value_title = value_item
        self.plot.y_axis.title = value_title

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
