from functools import partial
from datetime import date
from random import randint
from bokeh.layouts import column, row, gridplot
from threading import Thread
import time
import numpy as np
from bokeh.models import ColumnDataSource, Slider, Div
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.plotting import curdoc, figure
from tornado import gen

# REACTOR CODE HERE
class Reactor(object):
    Fuel_Volume = np.double(5)
    Control_Volume = np.double(0.027)
    Step = np.double(0.1)

    Microscopic_CS_Uranium = np.double(583 * np.float_power(10, -1))
    Microscopic_CS_Boron = np.double(3840 * np.float_power(10, -1))
    N_Uranium = Fuel_Volume * np.double(380000) * np.longdouble(np.longdouble(6.022) / 238)
    N_Boron = Control_Volume * np.double(468000) * np.longdouble(np.longdouble(6.022) / 10.811)
    Macroscopic_CS_Uranium = Microscopic_CS_Uranium * N_Uranium
    Macroscopic_CS_Boron = Microscopic_CS_Boron * N_Boron

    Fission_Energy = np.double(200)

    Temperature_Exchange_Area = np.double(5)
    Conductivity_Zircon = np.double(21500)
    Water_Temperature = np.double(350)
    Rod_Wall_Thickness = np.double(0.01)

    States = []

    # regulator = Regulator()



    def __init__(self):
        self.Rod_Percent = 0.623
        self.regulator = Regulator()
        i = 1
        self.States.append(ReactorState(self, np.double(self.Rod_Percent)))
        # print('Neutron_Absorption', self.States[0].Neutron_Absorption)
        # print('Heat_Generated', self.States[0].Heat_Generated)
        # print('Fuel_Temperature', self.States[0].Fuel_Temperature)
        # print('Neutron_Flux_dt', self.States[0].Neutron_Flux_dt)
        # print('Neutron_Flux', self.States[0].Neutron_Flux)

        # self.States.append(ReactorState(self, np.double(u)))
        # self.States.append(ReactorState(self, np.double(u)))

    def update_state(self):
        self.States.append(ReactorState(self, np.double(self.Rod_Percent), self.States[-1]))
        self.Rod_Percent = self.regulator.regulate(self.States[-1])
        print('Rod_Percent after regulate: ', self.Rod_Percent, '\n')


class ReactorInitialState(object):
    Rod_Percent = 0.623
    Neutron_Flux = 1.2 * (10 ** 13)
    Fuel_Temperature = np.double(413)


class ReactorState(object):
    def __init__(self, R: Reactor, ControlPosition: np.double, PS=ReactorInitialState):
        self.Neutron_Absorption = np.double((R.Macroscopic_CS_Boron * ControlPosition) / R.Macroscopic_CS_Uranium)
        self.Heat_Generated = R.Step * R.Fission_Energy * (
                    PS.Neutron_Flux * (1 - self.Neutron_Absorption)) * R.Macroscopic_CS_Uranium
        self.Heat_Generated *= np.double(1.602 * np.float_power(10, -13))  # MeV/s -> J/s
        self.Heat_Flux = R.Step * (R.Conductivity_Zircon * R.Temperature_Exchange_Area * (
                    PS.Fuel_Temperature - R.Water_Temperature)) / R.Rod_Wall_Thickness
        self.Fuel_Temperature = PS.Fuel_Temperature + (self.Heat_Generated - self.Heat_Flux) / (
                    R.Fuel_Volume * np.double(2280000))
        self.Neutron_Flux_dt = PS.Neutron_Flux * (1 - self.Neutron_Absorption) * 2.5  # Neutron Flux Change in 1s
        self.Neutron_Flux = PS.Neutron_Flux - (PS.Neutron_Flux - self.Neutron_Flux_dt) * R.Step


class Regulator(object):

    def __init__(self):
        self.Td = 0.0001
        self.Ti = 0.5
        self.Kp = 0.01
        self.Temp_z = 413
        self.Tp = 0.001
        self.e = [0]

    def regulate(self, state: ReactorState):
        e_n = (self.Temp_z - state.Fuel_Temperature)
        print('temp_z', self.Temp_z)
        print('e_n: ', e_n)
        print('temp: ', state.Fuel_Temperature)
        print("neutron flux: ", state.Neutron_Flux)
        print("Rod percent", R.Rod_Percent)
        print("Heat_Generated", state.Heat_Generated)
        self.e.append(e_n)
        if (len(self.e) == 1):
            self.delta = e_n
        else:
            # self.delta = self.e[-2] - e_n
            self.delta = e_n - self.e[-2]
        u = self.Kp * (e_n + self.Tp / self.Ti * sum(self.e) + self.Td / self.Tp * self.delta)
        print('u regulatora', u)
        if (u > 1):
            u = 1
        if (u < -1):
            u = -1

        if (u>0):
            Pr = 0.62 - u * 0.62
        else:
            Pr = 0.62 - u * 0.38
        print("Rod percent przed ograniczeniem", Pr)
        # if abs(Pr - R.Rod_Percent) > 0.02:
        #     if Pr > R.Rod_Percent:
        #         Pr = R.Rod_Percent + 0.02
        #     else:
        #         Pr = R.Rod_Percent - 0.02



        print('% pretow', Pr)
            # Pr = u * -32.94

        return Pr


# END OF REACTOR CODE


# this must only be modified from a Bokeh session callback
source = ColumnDataSource(data=dict(x=[0], y=[ReactorInitialState.Fuel_Temperature]))
source2 = ColumnDataSource(data=dict(x=[0], y=[ReactorInitialState.Rod_Percent]))
source3 = ColumnDataSource(data=dict(x=[0], y=[ReactorInitialState.Neutron_Flux]))
source4 = ColumnDataSource(data=dict(x=[0], y=[0]))


# This is important! Save curdoc() to make sure all threads
# see the same document.
doc = curdoc()
R = Reactor()
temp_slider = Slider(start=400, end=1000, value=413, step=.5, title="Temperature", width=500, margin=50, height=50)
@gen.coroutine
def update(x, y):
    source.stream(dict(x=[x], y=[y]), rollover=500)

def update2(x, y):
    source2.stream(dict(x=[x], y=[y]), rollover=500)

def update3(x, y):
    source3.stream(dict(x=[x], y=[y]), rollover=500)

def update4(x, y):
    source4.stream(dict(x=[x], y=[y]), rollover=500)


def blocking_task():
    x = 0
    while True:
        # do some blocking computation
        time.sleep(0.1)
        x += 0.1
        R.update_state()
        y = R.States[-1].Fuel_Temperature
        y2 = R.Rod_Percent
        y3 = R.States[-1].Neutron_Flux
        y4 = R.States[-1].Heat_Generated
        # but update the document from callback
        doc.add_next_tick_callback(partial(update, x=x, y=y))
        doc.add_next_tick_callback(partial(update2, x=x, y=y2))
        doc.add_next_tick_callback(partial(update3, x=x, y=y3))
        doc.add_next_tick_callback(partial(update4, x=x, y=y4))

def callback(attr, old, new):
    R.regulator.Temp_z = new
    print(new)
# temp_slider.js_on_change('value', callback)
temp_slider.on_change('value', callback)

p = figure(title="Temperature", y_range=(300, 1100),plot_width=1200, plot_height=420)

p2 = figure(title="Control rod position", y_range=(-0.1, 1.1),plot_width=600, plot_height=420)

p3 = figure(title="Neutron flux", y_range=(0, 200000000000000),plot_width=600, plot_height=420)

p4 = figure(title="Heat generated", y_range=(0, 1500000000),plot_width=600, plot_height=420)

p.line('x', 'y', source=source)

p2.line('x', 'y', source=source2)

p3.line('x', 'y', source=source3)

p4.line('x', 'y', source=source4)

div = Div(text="Reactor Simulation", style={'font-size': '36px', 'position': 'relative', 'left': 'calc(50% - 100px)'}, width=600)
div2 = Div(text="Real time simulation of a nuclear reactor.\n"
                " Use the slider below to change the desired temperature of the core. \n"
                " Thy system will automatically adjust to the desired temperature by controlling the position of control rods.",
           style={'font-size': '14px', 'position': 'relative', 'top': '18px', 'left': '30px', 'width': '550px'})
div3 = Div(text="Reactor parameters", style={'font-size': '32px', 'position': 'relative', 'left': 'calc(50% + 25px)', 'top': '50px'}, width=600)


data = dict(
        dates=['Fuel type', 'Control rod type', 'Fuel volume [m^3]', 'Control rods volume [m^3]', 'Water temperature[C]', 'Fuel cell wall thickness [mm]'],
        downloads=['Uranium', 'Boron', 5, 0.027, 350, 1],
    )
source_table = ColumnDataSource(data)

columns = [
        TableColumn(field="dates", title=""),
        TableColumn(field="downloads", title="")
    ]
data_table = DataTable(source=source_table, columns=columns, width=400, height=280, margin=100)

grid = gridplot([[ column([div, div2, temp_slider, data_table]),column([row(p), row(p2,p4)])]])

doc.add_root(grid)

thread = Thread(target=blocking_task)
thread.start()