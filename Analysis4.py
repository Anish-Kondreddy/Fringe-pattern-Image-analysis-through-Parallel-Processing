import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
from PIL import Image # type: ignore
import ipywidgets as widgets # type: ignore
from IPython.display import display # type: ignore
from matplotlib.widgets import Slider # type: ignore
import time

begin = time.time()

lists = []

for i in range(66):
    image_path = f'{i}.png'

        # Open the image
    image = Image.open(image_path).convert('L')  # Ensure it's in grayscale ('L' mode)

        # Get image dimensions
    width, height = image.size

        # Get pixel values
    pixel_values = list(image.getdata())

        # Convert the pixel values to a list of lists (rows)
    currentList = []

    for i in range(height):
        row = pixel_values[i * width:(i + 1) * width]
        currentList.append(row)
    
    lists.append(currentList)

# Function to Average out a list containing brightness pixel values as rows
def Average(list): 

    newList = np.zeros(width)

    for row in list:
        newList = newList + row

    newList = newList/height

    return newList

# empty list
secondLists = []

# For an image brightness value within all images do the average
for list in lists:

    secondLists.append(Average(list))

# getting x values are pixel range
xValues= range(width)

# plotting
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.15)
ax.plot(xValues, secondLists[0])

def update_wave(val):
    idx = int(sliderwave.val)
    ax.cla()
    ax.plot(xValues, secondLists[idx])
    fig.canvas.draw_idle()


# Sliders

axwave = plt.axes([0.25, 0.05, 0.5, 0.03])

sliderwave = Slider(axwave, 'Event No.', 0, 65, valinit=0, valfmt='%d')
sliderwave.on_changed(update_wave)

end = time.time()

print(end - begin)

plt.show()

