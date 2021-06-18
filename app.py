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

x_co = [0, 6.28]
y_co = [0, 0]
z, p, apf_z, apf_p, new_a, new_b, tf_b, tf_a = [], [], [], [], [], [], [], []

output_file('index.html')

# plot the z-plane with the unit circle
unit = figure(plot_width=350, plot_height=350,
              x_range=(-2, 2), y_range=(-2, 2), title="zplane")
unit.circle(x=[0], y=[0], color="green", radius=1, alpha=0.1)
show(unit)

# plot frequency response with two graphs(magnitude & phase)
freqGraph = figure(x_range=(0, 6.28), y_range=(-10, 10), toolbar_location="right",
                   title='Frequency response', plot_width=560, plot_height=350)

show(freqGraph)

# plot filter frequency response with two graphs(magnitude & phase)
filterGraph = figure(x_range=(0, 6.28), y_range=(-10, 10), toolbar_location="right",
                     title='All Pass Filter', plot_width=560, plot_height=350)
show(filterGraph)

# create dropmenu selections
filterlist = [0]*21
for i in range(21):
    filterlist[i] = f'Filter {i}'
filterlist[0] = 'Choose Filter'
# print("filterlist: ", filterlist)

# contains the columns you just referenced for the x_pole and y_pole
source_1 = ColumnDataSource(data=dict(x_of_poles=[], y_of_poles=[]))
# drow poles as asterisk
renderer = unit.star(x="x_of_poles", y="y_of_poles",
                     source=source_1, color='red', size=10)
# table shows (x,y) for each pole
columns_1 = [TableColumn(field="x_of_poles", title="x_of_poles"),
             TableColumn(field="y_of_poles", title="y_of_poles")]
table = DataTable(source=source_1, columns=columns_1,
                  editable=True, height=200)


# contains the columns you just referenced for the x_zero and y_zero
source_2 = ColumnDataSource(data=dict(x_of_zeros=[], y_of_zeros=[]))
# drow zeros as circle
renderer_2 = unit.scatter(x='x_of_zeros', y='y_of_zeros',
                          source=source_2, color='green', size=10)
# table shows (x,y) for each zero
columns_2 = [TableColumn(field="x_of_zeros", title="x_of_zeros"),
             TableColumn(field="y_of_zeros", title="y_of_zeros")]
table_2 = DataTable(source=source_2, columns=columns_2,
                    editable=True, height=200)

#####################################################################

new_source_1 = ColumnDataSource({
    'h': [], 'w': []
})
freqGraph.line(x='h', y='w', source=new_source_1,
               legend_label="Mag", line_color="red", name="magResponse")

new_source_2 = ColumnDataSource({
    'w': [], 'p': []
})
freqGraph.line(x='w', y='p', source=new_source_2,
               legend_label="Phase", color="blue", name="phaseResponse")


def MagAndPhase():
    new_source_2.data = {
        'w': [], 'p': []
    }

    new_source_1.data = {
        'h': [], 'w': []
    }

    tf_b, tf_a = signal.zpk2tf(Zero, Pole, 1)
    w, h_response = signal.freqz(tf_b, tf_a)

    mag = 20*np.log10(abs(h_response))
    phase = np.angle(h_response)

    if len(Zero) == 0 and len(Pole) == 0:
        mag = []
        w = []
        phase = []
        new_source_1.data = {'w': [], 'h': []}

    new_source_1.stream({
        'h': w, 'w': mag
    })
    new_source_2.stream({
        'w': w, 'p': phase
    })


def ZeorsAndPoles(a):
    global Zero, Pole
    Zero = []
    Pole = []

    for i in range(len(source_1.data['x_of_poles'])):
        # convert to complex form
        Pole.append(source_1.data['x_of_poles'][i] +
                    source_1.data['y_of_poles'][i]*1j*a)
    for i in range(len(source_2.data['x_of_zeros'])):
        Zero.append(source_2.data['x_of_zeros'][i] +
                    source_2.data['y_of_zeros'][i]*1j*a)

    MagAndPhase()
    print(Zero)


apf_source_1 = ColumnDataSource({'x': [], 'y': []})  # mag data
apf_source_2 = ColumnDataSource({'x': [], 'y': []})  # phase data


def update(attr, old, new):  # on click
    ZeorsAndPoles(1)


filterGraph.line(x='x', y='y', source=apf_source_1,
                 legend_label="Magnitude response", line_color="red")
filterGraph.line(x='x', y='y', source=apf_source_2,
                 legend_label="APF phase", line_color="green")


def generate_filters():

    random_a = []
    nums_a = []
    dens_a = []
    # Generatre random 'a' complex number for APF design
    for i in range(10):
        # create 10 random complex numbers
        x = float(decimal.Decimal(random.randrange(-100, 100))/100)
        y = float(decimal.Decimal(random.randrange(-100, 100))/100)
        a = x + y*1j
        if np.abs(a) > 1:
            x, y, a = 0, 0, 0
            x = float(decimal.Decimal(random.randrange(-100, 100))/100)
            y = float(decimal.Decimal(random.randrange(-100, 100))/100)
            a = x + y*1j
        random_a.append(a)

    for a in random_a:
        # iterate over each number and create a tf using it
        num = np.array([-a.conjugate(), 1])
        den = np.array([1, - a])
        nums_a.append(num)
        dens_a.append(den)

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


source_1.on_change('data', update)
source_2.on_change('data', update)


def clear_all():
    source_1.data['x_of_poles'].clear()
    source_1.data['y_of_poles'].clear()
    new_data = {'x_of_poles': source_1.data['x_of_poles'],
                'y_of_poles': source_1.data['y_of_poles'], }
    source_1.data = new_data

    source_2.data['x_of_zeros'].clear()
    source_2.data['y_of_zeros'].clear()
    new_data_2 = {
        'x_of_zeros': source_2.data['x_of_zeros'], 'y_of_zeros': source_2.data['y_of_zeros'], }
    source_2.data = new_data_2


def clear_zeros():
    source_2.data['x_of_zeros'].clear()
    source_2.data['y_of_zeros'].clear()
    new_data_2 = {
        'x_of_zeros': source_2.data['x_of_zeros'], 'y_of_zeros': source_2.data['y_of_zeros'], }
    source_2.data = new_data_2


def clear_poles():
    source_1.data['x_of_poles'].clear()
    source_1.data['y_of_poles'].clear()
    new_data = {'x_of_poles': source_1.data['x_of_poles'],
                'y_of_poles': source_1.data['y_of_poles'], }
    source_1.data = new_data


# buttons
toggle = Toggle(label="Conjugate", button_type="success", width=90)
toggle.js_on_click(CustomJS(
    code="""console.log('toggle: active=' + this.active, this.toString())"""))
filterMenu = Select(options=['Choose Filter', 'Filter 1',
                             'Filter 2', 'Filter 3'], value='None', title='Filters')
# filterMenu.on_change('value', 'function of filters')
ClearAll_button = Button(label="Clear All", button_type="success", width=70)
ClearP_button = Button(label="Clear Poles", button_type="success", width=70)
ClearZ_button = Button(label="Clear Zeros", button_type="success", width=70)
ClearAll_button.on_click(clear_all)
ClearP_button.on_click(clear_poles)
ClearZ_button.on_click(clear_zeros)
######################################################################

draw_tool = PointDrawTool(renderers=[renderer], empty_value='red')
draw_tool_2 = PointDrawTool(renderers=[renderer_2], empty_value='green')


unit.add_tools(draw_tool, draw_tool_2)
unit.toolbar.active_tap = draw_tool
unit.toolbar.logo = None
freqGraph.toolbar.logo = None
filterGraph.toolbar.logo = None
plot = Row(unit, freqGraph, filterGraph)
plot2 = Row(table, table_2)
menu = Row(filterMenu)
buttons = Row(toggle, ClearP_button, ClearZ_button, ClearAll_button)
curdoc().add_root(column(plot, buttons, menu, plot2))
