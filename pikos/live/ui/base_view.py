from traits.api import Str, Instance, Button, \
    WeakRef, on_trait_change
from traitsui.api import ModelView
from traitsui.tabular_adapter import TabularAdapter
from chaco.api import Plot
from chaco.tools.api import ZoomTool, PanTool


class DisableTrackingPlot(Plot):

    live_plot = WeakRef('BaseView')

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


class BaseView(ModelView):

    title = Str

    reset_view_button = Button('Reset View')

    plot = Instance(DisableTrackingPlot)

    zoom_tool = Instance(ZoomTool)
    pan_tool = Instance(PanTool)

    # Handlers

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
