from operator import attrgetter

from traits.api import Any, Int, Bool, on_trait_change, Dict, Button, Str, \
    HasTraits, cached_property, Property, Event, Either, Float, Instance
from traitsui.api import View, Item, UItem, VGroup, HGroup, Spring, \
    TabularEditor, HSplit, Group, ModelView
from traitsui.tabular_adapter import TabularAdapter
from chaco.api import Plot, LabelAxis
from chaco.tools.api import ZoomTool, PanTool
from chaco.ticks import ShowAllTickGenerator
from enable.component_editor import ComponentEditor

from pikos.live.ui.base_view import BaseView
from pikos.live.ui.barplot import SelectableBarPlot, BarSelectTool


class TableItem(HasTraits):

    id = Int
    filename = Str
    line_number = Any
    function_name = Str

    callcount = Int
    per_call = Float
    total_time = Float
    cumulative_time = Float

    def __init__(self, id, filename, line_number, function_name, callcount,
                 per_call, total_time, cumulative_time, **traits):
        kwargs = {}
        kwargs.update(traits)
        kwargs.update(dict(
            id=id,
            filename=filename,
            function_name=function_name,
            line_number=line_number,
            callcount=callcount,
            per_call=per_call,
            total_time=total_time,
            cumulative_time=cumulative_time,
        ))
        super(TableItem, self).__init__(**kwargs)


class CProfileTabularAdapter(TabularAdapter):

    columns = (
        ('Filename', 'filename'),
        ('Function Name', 'function_name'),
        ('Line Number', 'line_number'),

        ('Number of Calls', 'callcount'),
        ('Per Call', 'per_call'),
        # ('Per Call (Cumulative)', 'cumulative_percall'),
        ('Total Time', 'total_time'),
        ('Cumulative Time', 'cumulative_time'),
    )


class CProfileTableView(ModelView):

    title = Str

    data_items = Property(depends_on='model.data_items,sort_column,ascending')

    adapter = Any

    column_clicked = Event
    sort_column = Either(None, Int)
    ascending = Bool(False)

    def _column_clicked_changed(self, event):
        if event is None:
            self.sort_column = None
        elif self.sort_column == event.column:
            self.ascending = not self.ascending
        else:
            self.sort_column = event.column
            self.ascending = False

    def _adapter_default(self):
        return CProfileTabularAdapter()

    @cached_property
    def _get_data_items(self):
        items = [TableItem(*args) for args in self.model.data_items]
        if self.sort_column is None:
            return items
        attr = self.adapter.columns[self.sort_column][1]
        return sorted(items, key=attrgetter(attr), reverse=self.ascending)

    def default_traits_view(self):
        return View(
            UItem(
                'data_items',
                editor=TabularEditor(
                    adapter=self.adapter,
                    column_clicked='column_clicked',
                ),
            ),
            height=800,
            width=1100,
            resizable=True,
            title='CProfile Live',
        )



class CProfileView(BaseView):

    # Initialization

    plotted = Bool(False)

    barplot = Any

    sort_values_button = Button('Sort')

    FORMATS = Dict({
            'id': '0x{0:x}',
            })

    def _plot_default(self):
        container = Plot(
            self.model.plot_data,
            )
        container.renderer_map['bar'] = SelectableBarPlot
        container.padding_left = 100
        container.padding_bottom = 150
        # container.plot(('x', 'y'), type='bar')

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

    # @on_trait_change('model.index_item')
    # def _on_model_index_item_change(self, index_item):
    #     super(CProfileView, self)._on_model_index_item_change(index_item)
    #     # self.plot.x_axis.tick_generator = ShowAllTickGenerator(
    #     #     positions=self.model.plot_data.get_data('x'))

    # @on_trait_change('model.value_item')
    # def _on_model_value_item_change(self, value_item):
    #     super(CProfileView, self)._on_model_value_item_change(value_item)

    # Handlers

    @on_trait_change('model.updated')
    def _on_model_update_fired(self):
        if not self.plotted:
            x = self.model.plot_data.get_data('x')
            y = self.model.plot_data.get_data('y')
            if len(x) == 0 or len(y) == 0:
                return
            self.barplot = self.plot.plot(('x', 'y'), type='bar',
                                          bar_width=0.8)[0]
            self.barplot.index.sort_order = 'ascending'
            select = BarSelectTool(
                self.barplot,
                selection_mode='single',
                )
            self.barplot.tools.append(select)
            self.barplot.index.on_trait_change(
                self._metadata_changed, "metadata_changed")
            self.plotted = True
        self.plot.y_mapper.range.low_setting = 'auto'
        self.plot.y_mapper.range.high_setting = 'auto'

    def _format_key(self, key):
        format_ = self.FORMATS.get(self.model.index_item)
        if format_ is None:
            return str(key)
        try:
            return format_.format(key)
        except ValueError:
            return str(key)

    @on_trait_change('model.plot_keys')
    def _on_model_plot_keys_changed(self):
        positions = self.model.plot_data.get_data('x')
        label_axis = LabelAxis(
            self.plot, orientation='bottom',
            title='Keys',
            title_spacing=100,
            positions=positions,
            labels=[self._format_key(i)
                    for i in self.model.plot_keys],
            small_haxis_style=True,
            label_rotation=90,
            tick_generator=ShowAllTickGenerator(
                positions=positions,
                ),
            )

        self.plot.underlays.remove(self.plot.index_axis)
        self.plot.index_axis = label_axis
        self.plot.underlays.append(label_axis)

    def _sort_values_button_fired(self):
        self.model.sort_by_current_value()
        self.plot.invalidate_and_redraw()

    def _metadata_changed(self, new):
        self.plot.invalidate_and_redraw()
        # data_indices = self.scatter.index.metadata.get('selections', [])
        # if len(data_indices) == 0:
        #     self.model.selected_index = None
        #     return
        # self.model.selected_index = data_indices[0]

    # def _last_n_points_changed(self):
    #     self.plot.x_mapper.range.tracking_amount = self.last_n_points

    # def _follow_plot_changed(self):
    #     if self.follow_plot:
    #         self.plot.x_mapper.range.low_setting = 'track'
    #         self.plot.x_mapper.range.high_setting = 'auto'
    #         self.plot.x_mapper.range.tracking_amount = self.last_n_points
    #     else:
    #         self.plot.x_mapper.range.low_setting = self.plot.x_mapper.range.low
    #         self.plot.x_mapper.range.high_setting = \
    #             self.plot.x_mapper.range.high

    traits_view = View(
        Group(
            VGroup(
                HGroup(
                    Item('model.index_item'),
                    Item('model.value_item'),
                #     ),
                # HGroup(
                    Spring(),
                    UItem('sort_values_button'),
                    UItem('reset_view_button'),
                    ),
                ),
            HSplit(
                UItem('plot', editor=ComponentEditor()),
                # UItem(
                #     'model.selected_item',
                #     editor=TabularEditor(adapter=DetailsAdapter()),
                #     width=350),
                ),
            ),
        height=800,
        width=1100,
        resizable=True,
        title='Live Recording Plot'
        )


class CProfileMixedView(ModelView):

    title = Str

    table_view = Instance(CProfileTableView)
    plot_view = Instance(CProfileView)

    def _table_view_default(self):
        return CProfileTableView(title=self.title, model=self.model)

    def _plot_view_default(self):
        return CProfileView(title=self.title, model=self.model)

    traits_view = View(
        VGroup(
            UItem('table_view', style='custom'),
            UItem('plot_view', style='custom'),
        ),
        height=800,
        width=1100,
        resizable=True,
        title='Live CProfile',
    )
