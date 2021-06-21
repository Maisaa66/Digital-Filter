from bokeh.models import *
from bokeh.plotting import *
from bokeh.layouts import *
from bokeh.palettes import *
from bokeh.events import *
from bokeh.models.widgets import *

import random
import decimal

from scipy import signal
import math
import cmath
import numpy as np
from numpy import pi, log10

x_co = [0, 3.14]
y_co = [0, 0]
z, p, apf_z, apf_p, new_a, new_b, tf_b, tf_a, a_values, nums_a, dens_a = [
], [], [], [], [], [], [], [], [], [], []

output_file('index.html')

''' Initializations '''
p_source = ColumnDataSource(data=dict(x_of_poles=[], y_of_poles=[]))
z_source = ColumnDataSource(data=dict(x_of_zeros=[], y_of_zeros=[]))

p_sourceFilter = ColumnDataSource(data=dict(x_of_polesFilter=[], y_of_polesFilter=[]))
z_sourceFilter = ColumnDataSource(data=dict(x_of_zerosFilter=[], y_of_zerosFilter=[]))

mag_source = ColumnDataSource({'h': [], 'w': []})
phase_source = ColumnDataSource({'w': [], 'p': []})

# apf_source_1 = ColumnDataSource({'x': [], 'y': []})
# apf_source_2 = ColumnDataSource({'x': [], 'y': []})

p_columns = [TableColumn(field="x_of_poles", title="x_of_poles"),
             TableColumn(field="y_of_poles", title="y_of_poles")]
z_columns = [TableColumn(field="x_of_zeros", title="x_of_zeros"),
             TableColumn(field="y_of_zeros", title="y_of_zeros")]

# plot the z-plane with the unit circle
unit = figure(plot_width=250, plot_height=250,
              x_range=(-2, 2), y_range=(-2, 2), title="zplane")
unit.circle(x=[0], y=[0], color="green", radius=1,
            alpha=0.1, line_color="black")


# plot the z-plane with the unit circle
unit_filter = figure(plot_width=250, plot_height=250,
              x_range=(-2, 2), y_range=(-2, 2), title="zplane")
unit_filter.circle(x=[0], y=[0], color="green", radius=1,
            alpha=0.1, line_color="black")

# plot frequency response with two graphs(magnitude & phase)
freqGraph = figure(x_range=(0, 3.14), y_range=(-10, 10), toolbar_location="right",
                   title='Frequency response', plot_width=600, plot_height=250)
# plot filter frequency response with two graphs(magnitude & phase)
filterGraph = figure(x_range=(0, 3.14), y_range=(-10, 10), toolbar_location="right",
                     title='All Pass Filter', plot_width=600, plot_height=250)

show(freqGraph)
show(filterGraph)
show(unit)
show(unit_filter)

# create dropmenu selections
filterlist = [0]*21
for i in range(21):
    filterlist[i] = f'Filter {i}'
filterlist[0] = 'None'
# print("filterlist: ", filterlist)

# drow zeros as circle, drow poles as asterisk
z_renderer = unit.scatter(x='x_of_zeros', y='y_of_zeros',
                          source=z_source, color='green', size=10)
p_renderer = unit.star(x="x_of_poles", y="y_of_poles",
                       source=p_source, color='red', size=10)

# drow zeros as circle, drow poles as asterisk for filter
zFilter_renderer = unit_filter.scatter(x='x_of_zerosFilter', y='y_of_zerosFilter',
                          source=z_sourceFilter, color='green', size=10)
pFilter_renderer = unit_filter.star(x="x_of_polesFilter", y="y_of_polesFilter",
                       source=p_sourceFilter, color='red', size=10)

# table shows (x,y) for each zero, pole
z_table = DataTable(source=z_source, columns=z_columns,
                    editable=True, height=200)
p_table = DataTable(source=p_source, columns=p_columns,
                    editable=True, height=200)
''' ####################### '''


def ZeorsAndPoles(a):
    ''' Fetch zeros and poles from user''' 
    global Zero, Pole
    Zero = []
    Pole = []

    for i in range(len(p_source.data['x_of_poles'])):
        # convert to complex form
        Pole.append(p_source.data['x_of_poles'][i] +
                    p_source.data['y_of_poles'][i]*1j*a)
    for i in range(len(z_source.data['x_of_zeros'])):
        Zero.append(z_source.data['x_of_zeros'][i] +
                    z_source.data['y_of_zeros'][i]*1j*a)
    MagAndPhase()


def MagAndPhase():
    # Create keys in both dictionaries to store data
    # Values are cleared before each update
    phase_source.data = {'w': [], 'p': []}
    mag_source.data = {'h': [], 'w': []}
    if Zero or Pole:
        tf_b, tf_a = signal.zpk2tf(Zero, Pole, 1)
        w, h_response = signal.freqz(tf_b, tf_a)

        mag = 20*np.log10(abs(h_response))
        phase = np.angle(h_response)
        
        mag_source.stream({'h': w, 'w': mag})
        phase_source.stream({'w': w, 'p': phase})


# Plot phase and magnitude response with latest source values.
freqGraph.line(x='h', y='w', source=mag_source,
            legend_label="Mag", line_color="red", name="magResponse")

freqGraph.line(x='w', y='p', source=phase_source,
            legend_label="Phase", color="blue", name="phaseResponse")


def update(attr, old, new):  # on click
    ZeorsAndPoles(1)


# filterGraph.line(x='x', y='y', source=apf_source_1,
#                  legend_label="Magnitude response", line_color="red")
# filterGraph.line(x='x', y='y', source=apf_source_2,
#                  legend_label="APF phase", line_color="green")


def random_values_generator():
    # Generatre random 'a' complex number for APF design, in unit circle
    for i in range(10):
        x, y, a = 0, 0, 0
        # create 10 random complex numbers
        x = float(decimal.Decimal(random.randrange(-100, 100))/100)
        y = float(decimal.Decimal(random.randrange(-100, 100))/100)
        a = x + y*1j
        if np.abs(a) > 1:
            x, y, a = 0, 0, 0
            x = float(decimal.Decimal(random.randrange(-100, 100))/100)
            y = float(decimal.Decimal(random.randrange(-100, 100))/100)
            a = x + y*1j
        a_values.append(a)

    for a in a_values:
        # iterate over each number and create a tf using it
        num = np.array([-a.conjugate(), 1])
        den = np.array([1, - a])
        nums_a.append(num)
        dens_a.append(den)

def plot_filters ():
    show(unit_filter)
    pass

def testfunc (filter_idx):
    temp_source1 = ColumnDataSource({'x': [], 'y': []})
    temp_source2 = ColumnDataSource({'x': [], 'y': []})
    
    apf_w, apf_h = signal.freqz(dens_a[filter_idx], nums_a[filter_idx])
    apf_mag = 20*np.log10(abs(apf_h))
    apf_phase = np.angle(apf_h)
    

def filters_generator():
    # current index = i
    #on change with current index int
    for i in range(1, len(filterlist)):
        filterMenu.on_change('Filter {i}', testfunc(i))
        pass
    if filterMenu.value == "Filter 1":

        w3, h3 = signal.freqz(dens_a[0], nums_a[0])
        apf_mag = 20*np.log10(abs(h3))
        apf_phase = np.angle(h3)

        apf_source_1.stream({'x': w3, 'y': apf_mag})
        apf_source_2.stream({'x': w3, 'y': apf_phase})

    # if user selected filter 2:
    # a plot will be shown of zplane and phase response to a particular a number which is random_a[2]
    # if current index is selected go to that tf and plot it
    # for i in range(len(filterlist)):
    #     pass
    #     filterMenu.on_change("Filter {i}", plot_apf())


def custom_apf_creator(a):
    # create TF
    num = np.array([-a.conjugate(), 1])
    den = np.array([1, - a])
    # add to library
    apf_z.append(num)
    apf_p.append(den)


p_source.on_change('data', update)
z_source.on_change('data', update)


def clear_all():
    p_source.data['x_of_poles'].clear()
    p_source.data['y_of_poles'].clear()
    new_data = {'x_of_poles': p_source.data['x_of_poles'],
                'y_of_poles': p_source.data['y_of_poles'], }
    p_source.data = new_data

    z_source.data['x_of_zeros'].clear()
    z_source.data['y_of_zeros'].clear()
    new_data_2 = {
        'x_of_zeros': z_source.data['x_of_zeros'], 'y_of_zeros': z_source.data['y_of_zeros'], }
    z_source.data = new_data_2


def clear_zeros():
    z_source.data['x_of_zeros'].clear()
    z_source.data['y_of_zeros'].clear()
    new_data_2 = {
        'x_of_zeros': z_source.data['x_of_zeros'], 'y_of_zeros': z_source.data['y_of_zeros'], }
    z_source.data = new_data_2


def clear_poles():
    p_source.data['x_of_poles'].clear()
    p_source.data['y_of_poles'].clear()
    new_data = {'x_of_poles': p_source.data['x_of_poles'],
                'y_of_poles': p_source.data['y_of_poles'], }
    p_source.data = new_data


# buttons
toggle = Toggle(label="Conjugate", button_type="success", width=90)
toggle.js_on_click(CustomJS(
    code="""console.log('toggle: active=' + this.active, this.toString())"""))
filterMenu = Select(options=filterlist, value='None', title='Filters')
# filterMenu.on_change('value', 'function of filters')
ClearAll_button = Button(label="Clear All", button_type="success", width=70)
ClearP_button = Button(label="Clear Poles", button_type="success", width=70)
ClearZ_button = Button(label="Clear Zeros", button_type="success", width=70)
ClearAll_button.on_click(clear_all)
ClearP_button.on_click(clear_poles)
ClearZ_button.on_click(clear_zeros)


addFilter_button = Button(label="Add Filter", button_type="success", width=70)
clearFilter_button = Button(label="Delete Filter", button_type="success", width=70)
# addFilter_button.on_click(addFilter)
# clearFilter_button.on_click(deleteFilter)
######################################################################

draw_tool = PointDrawTool(renderers=[p_renderer], empty_value='red')
draw_tool_2 = PointDrawTool(renderers=[z_renderer], empty_value='green')

draw_tool_filter = PointDrawTool(renderers=[pFilter_renderer], empty_value='red')
draw_tool_filter2 = PointDrawTool(renderers=[zFilter_renderer], empty_value='green')

unit.add_tools(draw_tool, draw_tool_2)
unit.toolbar.active_tap = draw_tool
unit.toolbar.logo = None
unit_filter.add_tools(draw_tool_filter, draw_tool_filter2)
unit_filter.toolbar.active_tap = draw_tool_filter
unit_filter.toolbar.logo = None
freqGraph.toolbar.logo = None
filterGraph.toolbar.logo = None
plot = Row(unit, freqGraph)
plot2 = Row(unit_filter, filterGraph)
plot3 = Row(p_table, z_table)
menu = Row(filterMenu)
buttons = Row(toggle, ClearP_button, ClearZ_button, ClearAll_button)
filterButtons = Row(addFilter_button, clearFilter_button)
curdoc().add_root(column(plot,buttons, plot2, filterButtons, menu, plot3))
