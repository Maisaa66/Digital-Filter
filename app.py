from bokeh.layouts import row,column
from bokeh.models.layouts import Row
from bokeh.models.widgets.buttons import Button 
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, output_file, show, Column,curdoc
from bokeh.models import DataTable, TableColumn, PointDrawTool, ColumnDataSource,CDSView, IndexFilter,Dropdown,Select , Toggle, CustomJS
from math import *
from scipy.signal import freqz
import numpy as np
from scipy.signal import zpk2ss, ss2zpk, tf2zpk, zpk2tf
from cmath import *
from bokeh.models.widgets import RadioButtonGroup
from bokeh.events import DoubleTap, Tap,Press,PanEnd,Pan,SelectionGeometry


x_co = [0,6.28]
y_co = [0,0]

output_file('index.html')

#plot the z-plane with the unit circle
unit = figure(plot_width=350, plot_height=350, x_range=(-2, 2), y_range=(-2, 2), title="zplane") 
unit.circle(x=[0], y=[0], color="green",radius=1,alpha=0.1)
show(unit)

#plot frequency response with two graphs(magnitude & phase)
freqGraph= figure (x_range=(0,6.28), y_range=(-10,10),toolbar_location="right",
title='Frequency response',plot_width=560, plot_height=350)
freqGraph.line(x_co,y_co, legend_label="Mag",line_color="red")
freqGraph.line(x_co,y_co, legend_label="Phase", color="black" )
show(freqGraph)

#plot filter frequency response with two graphs(magnitude & phase)
filterGraph= figure (x_range=(0,6.28), y_range=(-10,10),toolbar_location="right",
title='All Pass Filter',plot_width=560, plot_height=350)
filterGraph.line(x_co,y_co, legend_label="Mag",line_color="red")
filterGraph.line(x_co,y_co, legend_label="Phase", color="black" )

######################################################################

#contains the columns you just referenced for the x_pole and y_pole
source_1 = ColumnDataSource(data=dict(x_of_poles=[], y_of_poles=[]))
#drow poles as asterisk
renderer = unit.star(x="x_of_poles", y="y_of_poles", source=source_1, color='red', size=10)
#table shows (x,y) for each pole 
columns_1 = [TableColumn(field="x_of_poles", title="x_of_poles"),
           TableColumn(field="y_of_poles", title="y_of_poles")]
table = DataTable(source=source_1, columns=columns_1, editable=True, height=200)


#contains the columns you just referenced for the x_zero and y_zero 
source_2 = ColumnDataSource(data=dict(x_of_zeros=[], y_of_zeros=[]))
#drow zeros as circle
renderer_2 = unit.scatter(x='x_of_zeros', y='y_of_zeros', source=source_2, color='green', size=10)
#table shows (x,y) for each zero
columns_2 = [TableColumn(field="x_of_zeros", title="x_of_zeros"),
           TableColumn(field="y_of_zeros", title="y_of_zeros")]
table_2 = DataTable(source=source_2, columns=columns_2, editable=True, height=200)

#####################################################################

new_source_1= ColumnDataSource({
    'h':[], 'w':[]
})
freqGraph.line(x='h',y='w',source=new_source_1)

new_source_2= ColumnDataSource({
    'w':[], 'p':[]
})
freqGraph.line(x='w',y='p',source=new_source_2)


def MagAndPhase():
    new_source_2.data={
    'w':[], 'p':[]
    }

    new_source_1.data={
    'h': [], 'w': []
    }
   
    num, den=zpk2tf(Zero,Pole,1)
    w,h=freqz(num,den,worN=10000)
    MagAndPhase=np.sqrt(h.real**2+h.imag**2) #calc mag , ** means power 2 bs 3shan float num
    
    phase=np.arctan(h.imag/h.real) #calc phase
    if len(Zero)==0 and len(Pole)==0:
        MagAndPhase=[]
        w=[]
        phase=[]
        new_source_1.data={'w': [], 'h': [] }
    new_source_1.stream({
    'h': w, 'w': MagAndPhase
    })
    new_source_2.stream({
        'w':w, 'p':phase
    })

def ZeorsAndPoles(a):
    global Zero,Pole
    Zero = []
    Pole = []
    
    for i in range(len(source_1.data['x_of_poles'])):
        Pole.append(source_1.data['x_of_poles'][i]+source_1.data['y_of_poles'][i]*1j*a) # convert to complex form
    for i in range(len(source_2.data['x_of_zeros'])): 
        Zero.append(source_2.data['x_of_zeros'][i]+source_2.data['y_of_zeros'][i]*1j*a) 

    MagAndPhase()
    print(Zero)


def update(attr, old, new): #on click
    ZeorsAndPoles(1)

source_1.on_change('data',update)
source_2.on_change('data',update)

def clear_all():
    source_1.data['x_of_poles'].clear()
    source_1.data['y_of_poles'].clear()
    new_data={'x_of_poles':source_1.data['x_of_poles'],'y_of_poles':source_1.data['y_of_poles'],}
    source_1.data=new_data

    source_2.data['x_of_zeros'].clear()
    source_2.data['y_of_zeros'].clear()
    new_data_2={'x_of_zeros':source_2.data['x_of_zeros'],'y_of_zeros':source_2.data['y_of_zeros'],}
    source_2.data=new_data_2


def clear_zeros():
    source_2.data['x_of_zeros'].clear()
    source_2.data['y_of_zeros'].clear()
    new_data_2={'x_of_zeros':source_2.data['x_of_zeros'],'y_of_zeros':source_2.data['y_of_zeros'],}
    source_2.data=new_data_2

def clear_poles():
    source_1.data['x_of_poles'].clear()
    source_1.data['y_of_poles'].clear()
    new_data={'x_of_poles':source_1.data['x_of_poles'],'y_of_poles':source_1.data['y_of_poles'],}
    source_1.data=new_data


#buttons
toggle = Toggle(label="Conjugate", button_type="success", width=90)
toggle.js_on_click(CustomJS(code="""console.log('toggle: active=' + this.active, this.toString())"""))
filterMenu = Select(options=['Choose Filter','Filter 1', 'Filter 2', 'Filter 3'],value='None' ,title='Filters')
# filterMenu.on_change('value', 'function of filters') 
ClearAll_button=Button(label="Clear All" ,button_type="success",width=70)
ClearP_button=Button(label="Clear Poles" ,button_type="success",width=70)
ClearZ_button=Button(label="Clear Zeros" ,button_type="success",width=70)
ClearAll_button.on_click(clear_all)
ClearP_button.on_click(clear_poles)
ClearZ_button.on_click(clear_zeros)
######################################################################

draw_tool = PointDrawTool(renderers=[renderer], empty_value='red')
draw_tool_2 = PointDrawTool(renderers=[renderer_2], empty_value='green')


unit.add_tools(draw_tool,draw_tool_2)
unit.toolbar.active_tap = draw_tool
unit.toolbar.logo= None
freqGraph.toolbar.logo = None
filterGraph.toolbar.logo = None
plot=Row(unit, freqGraph,filterGraph)
plot2=Row(table,table_2)
menu=Row(filterMenu)
buttons=Row(toggle, ClearP_button, ClearZ_button,ClearAll_button)
curdoc().add_root(column(plot , buttons, menu, plot2))
