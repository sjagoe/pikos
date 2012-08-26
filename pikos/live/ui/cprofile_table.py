from traits.api import HasTraits, Any, Int, on_trait_change, \
    Str, Float, cached_property, Property
from traitsui.api import View, UItem, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from traitsui.api import ModelView


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

    data_items = Property(depends_on='model.data_items')

    @cached_property
    def _get_data_items(self):
        return [TableItem(*args) for args in self.model.data_items]

    traits_view = View(
        UItem(
            'data_items',
            editor=TabularEditor(adapter=CProfileTabularAdapter()),
        ),
        height=800,
        width=1100,
        resizable=True,
        title='CProfile Live',
    )
