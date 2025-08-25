#!/usr/bin/env python3

import math

# this is working correctly and updating graph on tkwindow. 
# laser profiler - takes a snapshot and fits to gaussian

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
from os.path import exists # this is test video device


# Use Tkinter Agg
use_agg('TkAgg')


def func(x, a, x0, sigma,h): # Guassian function for the fit. 
	return (a*np.exp(-(x-x0)**2/(2*sigma**2)))+h



def gray(frame):
 global data # otherwise this returns empty data array
 print('converting to gray')
 array=np.asarray(frame) # convert to numpy array
 # convert to b/qw for analysis
 width,height=len(array),len(array[0])
 data=np.zeros((width,height))
 for i in range(width):
   for j in range(height):
      data[i][j]=(0.3*array[i][j][0]+0.3*array[i][j][1]+0.3*array[i][j][2])
   # I do this 0.3 multiplication to avoid overflow  
 print(np.shape(data))
 return data # returns the grayscale image    
            


def analysis(data):
# this will find the centroid, find x and y
# profiles at this point and fit both to 
# gaussian, using some initial guess. returns fit data
# analysis of the profile 
  global xrow, yrow, poptx, popty, xprofile, yprofile # global variables defined
  center_of_mass=centroid_com(data) #this is from photutils
  length=data.shape
  xlength=int(length[0])
  ylength=int(length[1])
  #print(center_of_mass,length)
  xcenter=int(center_of_mass[0])
  ycenter=int(center_of_mass[1])
  print('centers',xcenter,ycenter)

  #creating xrow and yrow for plotting. 
  xrow=[i for i in range(ylength)]
  xprofile=data[ycenter] # extracting line profile of Data for x
  yrow=[j for j in range(xlength-1)]
  yprofile=[]
  for j in range(xlength-1):
   #  yrow.append(j)
     yprofile.append(data[xcenter][j])  # this is the only way to create y profile
  
  xrow2=np.asarray(xrow)
  xprofile2=np.asarray(xprofile) # making array for easy analysis
  #initial guess
  p0=[1,xcenter,2,1]# initial guess for popt - amplitude, center, sigma and baseline.
  poptx, pcov = curve_fit(func, xrow, xprofile,p0) # the curve fit. 
  
           #print('fit parameters','xamp',xamp,'x0',x0,'xwidth',xwidth,'x_shift',x_shift)
   # initial guess for y 
  p0=[1,ycenter,2,1]# initial guess for popt y
  popty, pcov = curve_fit(func, yrow, yprofile,p0) # the curve fit. 
  yamp,y0,ywidth,y_shift=popty
  return xrow,yrow,poptx,popty,xprofile,yprofile


def display(poptx,popty):
  xamp,x0,xwidth,x_shift=poptx  # taking parameters from fit. 
  yamp,y0,ywidth,y_shift=popty
  print('Fit parameters - X')
  fitx=[['x amplitude',xamp],['x center',x0],['x_width',xwidth],['x_dc_shift',x_shift]]
  print(tabulate(fitx))
          
  print('fit parameters - Y')
  fity=[['y amplitude',yamp],['y center',y0],['y width',ywidth],['y_dc_shift',y_shift]]
  print(tabulate(fity))
  
  with open('fit_parameters.txt', 'w') as outputfile:
    outputfile.write(tabulate(fitx))
    outputfile.write(tabulate(fity))
  
  return


def plotting(xrow,yrow,poptx,popty,ax,fig,xprofile,yprofile):
 # plotting all. 
 # Reset ax
 ax[0,0].cla()
 ax[0,1].cla()
 ax[1,0].cla()
 ax[1,1].cla()
        
 ax[0,0].set_title("X Profile")
 ax[0,0].set_xlabel("X axis pixel no")
 ax[0,0].set_ylabel("Intensity")
 ax[1,1].set_title("Y Profile")
 ax[1,1].set_xlabel("Y axis pixel no")
 ax[1,1].set_ylabel("Intensity")
           
       
 ax[0,1].axis('off') # this removes the 3rd graph, which is otherwise empty axis. 
 ax[0,0].plot(xrow,xprofile,"o") # this is raw curve
 ax[0,0].plot(xrow,func(xrow, *poptx)) # this is the fit curve
 ax[1,0].imshow(data)
 ax[1,1].plot(yprofile,yrow,"o")
 ax[1,1].plot(func(yrow, *popty),yrow) # this is the fit curve
                                 
 fig.canvas.draw()   # Draw curve really
 fig.savefig('profile.png')
 sg.popup('Image saved as profile.png, ascii data saved as fit_parameters.txt')

# generate data for writing into file. 
 x_tuple=[]
 y_tuple=[]
 for i in range(len(xrow)):
    value=xrow[i]
    number=[value,xprofile[i],func(value,*poptx)]
    x_tuple.append(number)
  
 for j in range(len(yrow)):   
    valuey=yrow[j]
    number2=[valuey,yprofile[j],func(valuey,*popty)]
    y_tuple.append(number2)
    
 with open('data_x.csv','w') as outputfile:
   write_in=csv.writer(outputfile,delimiter='\t')
   write_in.writerows(x_tuple)
 with open('data_y.csv','w') as outputfile:
   write_in=csv.writer(outputfile,delimiter='\t')
   write_in.writerows(y_tuple)  
   
 return


###################################################
# the main program Begins 

# PySimplGUI window
layout = [[sg.Graph((640, 480), (0, 0), (640, 480), key='Graph')],
         #[sg.Image(filename='', size=(320,240), key='image')],
         [sg.Button('Single Shot'),
        # [sg.Button('Continous',button_color='green'),
	# sg.Button('Stop',button_color='red'),
          sg.Button('Exit'), ],
          [sg.Output(size=(50,5))],
          [sg.Text('Ashok Vudayagiri', size=(40, 1), font=('Times 9'))],
          [sg.Text('School of Physics',size=(20,1),font=('Times 9'))],
          [sg.Text('University of Hyderabad',size=(20,1),font=('Times 6'))],
          ]
          
window = sg.Window('Laser_profiler', layout, finalize=True)


# defining graphs
fig, ax = plt.subplots(2,2) # Default settings for matplotlib graphics
#ax.set_title("Profile")
ax[0,1].axis('off') # this removes the 3rd graph, which is otherwise empty axis.

# Link matplotlib to PySimpleGUI Graph
canvas = FigureCanvasTkAgg(fig, window['Graph'].Widget)
plot_widget = canvas.get_tk_widget()
plot_widget.grid(row=0, column=0)


#starting main program


# test which video capture we have 
k=0
for k in range(5):
   dev_name='/dev/video'+str(k)
   file_exists = exists(dev_name)
   if file_exists:
     print('using ',dev_name)
     dev_id=k
     #break
     cap = cv2.VideoCapture(k) # camera definition
     recording = False
     #result,image = cap.read()
     #if result:
     #   print("device",dev_name)
     #   cv2.imshow("Image", image)
     #   cv2.waitKey(0)
     #   destroyWindow("Image")
     #else:
     #  print("image could not be shot")
#cap = cv2.VideoCapture(k) # camera definition
cap = cv2.VideoCapture(0) # camera definition
recording = False

while True:

    event, values = window.read(timeout=10)
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    if event == 'Single Shot':
      ret, frame = cap.read() # capture image. 
      playsound('camera-shutter-click-01.mp3')
      
      width,height=len(frame),len(frame[0])
      
      data=np.zeros((width,height))
      element=len(frame[0][0])
      if element ==3:
        gray(frame)
      else:  
        data=frame
      analysis(data) # analyzes the data
      display(poptx,popty)
      plotting(xrow,yrow,poptx,popty,ax,fig,xprofile,yprofile)
    
      #saving file 
      
    
window.close()