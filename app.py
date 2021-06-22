from operator import index
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
np.seterr(divide='ignore', invalid='ignore')
x_co = [0, 3.14]
y_co = [0, 0]
a_values, nums_a, dens_a = [], [], []
Zero, Pole = [], []
filterlist = []


output_file('index.html')


def random_values_generator():

    # Generatre random 'a' complex number for APF design, in unit circle
    for i in range(21):
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
        # create dropmenu selections
    for i in range(len(a_values)):
        filterlist.append(f"Filter {i}")
    filterlist[0] = 'None'


''' Initializations '''
random_values_generator()
p_source = ColumnDataSource(data=dict(x_of_poles=[], y_of_poles=[]))
z_source = ColumnDataSource(data=dict(x_of_zeros=[], y_of_zeros=[]))

p_sourceFilter = ColumnDataSource(
    data=dict(x_of_polesFilter=[], y_of_polesFilter=[]))
z_sourceFilter = ColumnDataSource(
    data=dict(x_of_zerosFilter=[], y_of_zerosFilter=[]))

mag_source = ColumnDataSource({'h': [], 'w': []})
phase_source = ColumnDataSource({'w': [], 'p': []})
apf_p_source = ColumnDataSource(data=dict(x_of_poles=[], y_of_poles=[]))
apf_z_source = ColumnDataSource(data=dict(x_of_zeros=[], y_of_zeros=[]))
apf_phase_source = ColumnDataSource({'w': [], 'p': []})


filterMenu = Select()
filterMenu.title = 'Filters'
filterMenu.options = filterlist


p_columns = [TableColumn(field="x_of_poles", title="x_of_poles"),
             TableColumn(field="y_of_poles", title="y_of_poles")]
z_columns = [TableColumn(field="x_of_zeros", title="x_of_zeros"),
             TableColumn(field="y_of_zeros", title="y_of_zeros")]

# plot the z-plane with the unit circle
unit = figure(plot_width=300, plot_height=300,
              x_range=(-2, 2), y_range=(-2, 2), title="zplane")
unit.circle(x=[0], y=[0], color="green", radius=1,
            alpha=0.1, line_color="black")


# plot the z-plane with the unit circle
unit_filter = figure(plot_width=300, plot_height=300,
                     x_range=(-2, 2), y_range=(-2, 2), title="APF zplane")
unit_filter.circle(x=[0], y=[0], color="green", radius=1,
                   alpha=0.1, line_color="black")

# plot frequency response with two graphs(magnitude & phase)
freqGraph = figure(x_range=(0, 3.14), y_range=(-20, 20), toolbar_location="right",
                   title='Frequency response', plot_width=600, plot_height=300)
# plot filter frequency response with two graphs(magnitude & phase)
filterGraph = figure(x_range=(0, 3.14), y_range=(-20, 20), toolbar_location="right",
                     title='All Pass Filter', plot_width=600, plot_height=300)

show(freqGraph)
show(filterGraph)
show(unit)
show(unit_filter)

# draw zeros as circle, drow poles as asterisk
z_renderer = unit.scatter(x='x_of_zeros', y='y_of_zeros',
                          source=z_source, color='green', size=10)
p_renderer = unit.x(x="x_of_poles", y="y_of_poles",
                       source=p_source, color='red', size=10)

# zConj_renderer = unit.scatter(x='x_of_zeros', y='y_of_zeros',
#                           source=zConj_source, color='green', size=10)
# pConj_renderer = unit.star(x="xConj_of_poles", y="yConj_of_poles",
#                        source=pConj_source, color='red', size=10)
# table shows (x,y) for each zero, pole
z_table = DataTable(source=z_source, columns=z_columns,
                    editable=True, height=200)
p_table = DataTable(source=p_source, columns=p_columns,
                    editable=True, height=200)
''' ####################### '''


def ZeorsAndPoles(a):
    ''' Fetch zeros and poles from user'''
    global Zero, Pole
    

    for i in range(len(p_source.data['x_of_poles'])):
        # convert to complex form
        Pole.append(p_source.data['x_of_poles'][i] +
                    p_source.data['y_of_poles'][i]*1j*a)
    for i in range(len(z_source.data['x_of_zeros'])):
        Zero.append(z_source.data['x_of_zeros'][i] +
                    z_source.data['y_of_zeros'][i]*1j*a)
    print("zeros without conj: ", Zero)
    print("poles without conj: ", Pole)
    MagAndPhase()


def conjugates(): 
    ZeorsAndPoles(-1)


    MagAndPhase()


def MagAndPhase():
    print(len(Zero), len(Pole))
    global tf_a, tf_b
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
    # conjugates()



def filters_generator(attr, old, new):
    ''' Each filter is associated with a randomly generated number of a that constructs APF'''
    # Clear source data each time.
    apf_phase_source.data = {'w': [], 'p': []}
    apf_p_source.data = dict(x_of_poles=[], y_of_poles=[])
    apf_z_source.data = dict(x_of_zeros=[], y_of_zeros=[])

    for i in range(len(filterMenu.options)):
        if filterMenu.value == f"Filter {i}":
            print(f"user selected Filter {i}")
            # Fetch current value of a
            a = a_values[i]
            # Enable plot widgets
            unit_filter.disabled = False
            freqGraph.disabled = False

            # Fetch zeros and poles from H(apf) with randomly selected value of a
            z, p, k = signal.tf2zpk(nums_a[i], dens_a[i])
            # plot zeros and poles on unit circle ( zeros arr: z, poles arr: p )

            # extract zeros and poles coordinates of each filter
            for pole in range(len(p)):
                apf_p_source.data['x_of_poles'].append(p[pole].real)
                apf_p_source.data['y_of_poles'].append(p[pole].imag)

            for zero in range(len(z)):
                apf_z_source.data['x_of_zeros'].append(z[zero].real)
                apf_z_source.data['y_of_zeros'].append(z[zero].imag)

            print(f"APF of a= {a}")

            unit_filter.scatter(x='x_of_zeros', y='y_of_zeros',
                                source=apf_z_source, color='green', size=10)
            unit_filter.star(x="x_of_poles", y="y_of_poles",
                             source=apf_p_source, color='red', size=10)
            # get frequency response of H(apf)
            w, h = signal.freqz_zpk(z, p, k)
            phase = np.angle(h)
            # Plot phase response
            apf_phase_source.stream({'w': w, 'p': phase})
            break

            # plt.plot(w, phase)
        elif filterMenu.value == "None":
            print("user selected None")
            # Disable plot widgets
            unit_filter.disabled = True
            freqGraph.disabled = True
            break


temp_num = []
temp_den = []


def add_apf():
    global temp_num, temp_den

    phase_source.data = {'w': [], 'p': []}
    mag_source.data = {'h': [], 'w': []}
    selected_filter = filterMenu.value  # string

    if selected_filter != "None":
        # extract filter index from library
        idx = ''.join(char for char in selected_filter if char.isdigit())
        idx = int(idx)

        temp_num.append(nums_a[idx])
        temp_den.append(dens_a[idx])

    # initial values = 1
    APFs_num = [1]
    APFs_den = [1]
    # multiply all filters coeff. together. (polynomial)
    for i in range(len(temp_num)):
        APFs_num = np.polymul(APFs_num, temp_num[i])

    for j in range(len(temp_den)):
        APFs_den = np.polymul(APFs_den, temp_den[j])

    # Get frequency response of combined added APFs
    new_TF_a = np.polymul(APFs_den, tf_a)
    new_TF_b = np.polymul(APFs_num, tf_b)

    w, h = signal.freqz(new_TF_b, new_TF_a)

    mag = 20*np.log10(abs(h))
    phase = np.angle(h)

    mag_source.stream({'h': w, 'w': mag})
    phase_source.stream({'w': w, 'p': phase})

    if selected_filter == "None":
        ''' plot original response without APF addition '''
        # clear data
        phase_source.data = {'w': [], 'p': []}
        mag_source.data = {'h': [], 'w': []}

        # get original freq response without APFs
        w, h_original = signal.freqz(tf_b, tf_a)

        mag = 20*np.log10(abs(h_original))
        phase = np.angle(h_original)
        # plot
        mag_source.stream({'h': w, 'w': mag})
        phase_source.stream({'w': w, 'p': phase})


# plot zeros,poles and phase response of each selected item from dropdown menu.
filterMenu.on_change('value', filters_generator)

filterGraph.line(x='w', y='p', source=apf_phase_source,
                 legend_label="APF phase", line_color="green")


def custom_apf_generator(a):
    real = real_input.value
    imag = imag_input.value
    a = float(real) + float(imag) *1j
    print("user added: ", a)
    
    ''' A button will send a value of a (complex number) here, construct a filter using this value, add it to library, and plot it.
        Parameters: a , type(complex)
        Returns: added filter in filtersList
    '''
    # add a value to a.values list
    a_values.append(a)
    # create TF
    num = np.array([-a.conjugate(), 1])
    den = np.array([1, - a])
    # add to library
    nums_a.append(num)
    dens_a.append(den)
    # create new filter name in filterlist
    length = len(filterMenu.options)
    new_list = [""] * (length+1)
    for x in range(length):
        new_list[x] = filterMenu.options[x]
    new_list[length] = f"Filter {length}"
    filterMenu.update(options=new_list)


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
    
    mag_source.data = {k: [] for k in mag_source.data}
    phase_source.data = {k: [] for k in phase_source.data}


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


apf_button = Button(label="Add APF", button_type="success", width=90)
Conjugate_button = Button(label="Conjugate", button_type="success", width=90)
add_filter_button = Button(label="Add Custom Filter", button_type="success", width=150)
ClearAll_button = Button(label="Clear All", button_type="success", width=90)
ClearP_button = Button(label="Clear Poles", button_type="success", width=90)
ClearZ_button = Button(label="Clear Zeros", button_type="success", width=90)
ClearAll_button.on_click(clear_all)
ClearP_button.on_click(clear_poles)
ClearZ_button.on_click(clear_zeros)
Conjugate_button.on_click(conjugates)

apf_button.on_click(add_apf)

add_filter_button.on_click(custom_apf_generator)
callback = CustomJS(args={}, code='alert("Added new custom filter! ");')
add_filter_button.js_on_click(callback)
##########

real_input = TextInput(value="", title="Enter real part for your custom filter:",placeholder="ex: 0.5" )
imag_input = TextInput(value="", title="Enter imag part for your custom filter (WITHOUT the letter j):",placeholder="ex: 0.2j" )

text_widget = widgetbox(real_input, imag_input)
show(text_widget)

#############################################

draw_tool = PointDrawTool(renderers=[p_renderer], empty_value='red')
draw_tool_2 = PointDrawTool(renderers=[z_renderer], empty_value='green')


unit.add_tools(draw_tool, draw_tool_2)
unit.toolbar.active_tap = draw_tool
unit.toolbar.logo = None


freqGraph.toolbar.logo = None
filterGraph.toolbar.logo = None
plot = Row(unit, freqGraph)
filter_plot = Row(unit_filter, filterGraph)
tables = Row(p_table, z_table)

menu = Row(filterMenu, real_input, imag_input)
buttons = Row(Conjugate_button, ClearP_button, ClearZ_button,  ClearAll_button)
filters_buttons = Row(add_filter_button, apf_button)
curdoc().add_root(column(plot, buttons, menu, filter_plot,filters_buttons, tables))
