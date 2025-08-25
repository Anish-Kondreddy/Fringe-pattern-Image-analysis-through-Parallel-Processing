#!/usr/bin/env python3

import math
from matplotlib import use as use_agg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.optimize import curve_fit
from tabulate import tabulate
import matplotlib.pyplot as plt
import pandas as pd
import scipy.optimize as opt
import PySimpleGUI as sg
import cv2
import csv
from photutils.centroids import centroid_com, centroid_quadratic
import numpy as np
from playsound import playsound
from os.path import exists

# Use Tkinter Agg
use_agg('TkAgg')


def func(x, a, x0, sigma, h):
    return (a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))) + h


def gray(frame):
    global data
    print('Converting to grayscale')
    array = np.asarray(frame)
    width, height = len(array), len(array[0])
    data = np.zeros((width, height))
    for i in range(width):
        for j in range(height):
            data[i][j] = (0.3 * array[i][j][0] + 0.3 * array[i][j][1] + 0.3 * array[i][j][2])
    print(np.shape(data))
    return data


def analysis(data):
    try:
        global xrow, yrow, poptx, popty, xprofile, yprofile
        center_of_mass = centroid_com(data)
        xcenter, ycenter = int(center_of_mass[0]), int(center_of_mass[1])
        print('Centers:', xcenter, ycenter)

        xrow = np.arange(data.shape[1])
        xprofile = data[ycenter, :]
        yrow = np.arange(data.shape[0])
        yprofile = data[:, xcenter]

        p0 = [1, xcenter, 2, 1]
        poptx, _ = curve_fit(func, xrow, xprofile, p0)

        p0 = [1, ycenter, 2, 1]
        popty, _ = curve_fit(func, yrow, yprofile, p0)

        return xrow, yrow, poptx, popty, xprofile, yprofile
    except Exception as e:
        print(f"Error in analysis: {e}")
        sg.popup_error(f"Error in analysis: {e}")
        return None, None, None, None, None, None


def display(poptx, popty):
    try:
        xamp, x0, xwidth, x_shift = poptx
        yamp, y0, ywidth, y_shift = popty

        fitx = [['x amplitude', xamp], ['x center', x0], ['x_width', xwidth], ['x_dc_shift', x_shift]]
        fity = [['y amplitude', yamp], ['y center', y0], ['y width', ywidth], ['y_dc_shift', y_shift]]

        print('Fit parameters - X')
        print(tabulate(fitx))
        print('Fit parameters - Y')
        print(tabulate(fity))

        with open('fit_parameters.txt', 'w') as outputfile:
            outputfile.write(tabulate(fitx))
            outputfile.write(tabulate(fity))

    except Exception as e:
        print(f"Error in display: {e}")
        sg.popup_error(f"Error in display: {e}")


def plotting(xrow, yrow, poptx, popty, ax, fig, xprofile, yprofile):
    try:
        ax[0, 0].cla()
        ax[0, 1].cla()
        ax[1, 0].cla()
        ax[1, 1].cla()

        ax[0, 0].set_title("X Profile")
        ax[0, 0].set_xlabel("X axis pixel no")
        ax[0, 0].set_ylabel("Intensity")
        ax[1, 1].set_title("Y Profile")
        ax[1, 1].set_xlabel("Y axis pixel no")
        ax[1, 1].set_ylabel("Intensity")

        ax[0, 1].axis('off')
        ax[0, 0].plot(xrow, xprofile, "o")
        ax[0, 0].plot(xrow, func(xrow, *poptx))
        ax[1, 0].imshow(data, cmap='gray')
        ax[1, 1].plot(yprofile, yrow, "o")
        ax[1, 1].plot(func(yrow, *popty), yrow)

        fig.canvas.draw()
        fig.savefig('profile.png')
        sg.popup('Image saved as profile.png, ascii data saved as fit_parameters.txt')

        x_tuple = [[value, xprofile[i], func(value, *poptx)] for i, value in enumerate(xrow)]
        y_tuple = [[valuey, yprofile[j], func(valuey, *popty)] for j, valuey in enumerate(yrow)]

        with open('data_x.csv', 'w') as outputfile:
            write_in = csv.writer(outputfile, delimiter='\t')
            write_in.writerows(x_tuple)
        with open('data_y.csv', 'w') as outputfile:
            write_in = csv.writer(outputfile, delimiter='\t')
            write_in.writerows(y_tuple)
    except Exception as e:
        print(f"Error in plotting: {e}")
        sg.popup_error(f"Error in plotting: {e}")


# The main program begins

layout = [[sg.Graph((640, 480), (0, 0), (640, 480), key='Graph')],
          [sg.Button('Single Shot'), sg.Button('Exit')],
          [sg.Output(size=(50, 5))],
          [sg.Text('Ashok Vudayagiri', size=(40, 1), font=('Times 9'))],
          [sg.Text('School of Physics', size=(20, 1), font=('Times 9'))],
          [sg.Text('University of Hyderabad', size=(20, 1), font=('Times 6'))],
          ]

window = sg.Window('Laser_profiler', layout, finalize=True)

fig, ax = plt.subplots(2, 2)
ax[0, 1].axis('off')

canvas = FigureCanvasTkAgg(fig, window['Graph'].Widget)
plot_widget = canvas.get_tk_widget()
plot_widget.grid(row=0, column=0)

cap = cv2.VideoCapture(0)
recording = False

while True:
    event, values = window.read(timeout=10)

    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break

    ret, frame = cap.read()
    if ret:
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()
        window['Graph'].draw_image(data=imgbytes, location=(0, 0))

    if event == 'Single Shot':
        playsound('camera-shutter-click-01.mp3')
        if len(frame.shape) == 3:
            gray(frame)
        else:
            data = frame

        xrow, yrow, poptx, popty, xprofile, yprofile = analysis(data)
        if xrow is not None:
            display(poptx, popty)
            plotting(xrow, yrow, poptx, popty, ax, fig, xprofile, yprofile)

cap.release()
window.close()
