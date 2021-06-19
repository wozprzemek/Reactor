# Reactor
A group university project. Simulation of a nuclear reactor using the PID controller. Implemented in Python with the use of Bokeh live server.

## Theory

For the theory behind the program, go to the documentation folder.

## Getting started

To run the application you need to have Python 3 installed along with the required libraries.

## Setup

Clone the repository to your local machine or download the python file. Make sure you have installed the libraries needed to run the application.
The interactive web application is created using Bokeh live server. For more information visit https://docs.bokeh.org/en/latest/docs/user_guide/server.html.
To run the application, open the folder contatining the source file in the terminal and type the following command:

```bokeh serve --show name_of_the_file.py```

This command should open the interactive web application in your browser. To stop it, close the browser and kill the process from the terminal.

## Usage

You can change the desired temperature of the core as well as the temperature of the coolant using the sliders. Current data can be read from the graphs.
