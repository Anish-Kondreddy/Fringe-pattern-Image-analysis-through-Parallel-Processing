import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.widgets import Slider
import concurrent.futures
import time

begin = time.time()

def process_image(index):
    image_path = f'{index}.png'
    image = Image.open(image_path).convert('L')
    pixel_values = np.array(image)
    return pixel_values.mean(axis=0)

# Process images in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    lists = list(executor.map(process_image, range(66)))

xValues = range(len(lists[0]))

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.15)
line, = ax.plot(xValues, lists[0])

def update_wave(val):
    idx = int(sliderwave.val)
    line.set_ydata(lists[idx])
    fig.canvas.draw_idle()

axwave = plt.axes([0.25, 0.05, 0.5, 0.03])
sliderwave = Slider(axwave, 'Event No.', 0, 65, valinit=0, valfmt='%d')
sliderwave.on_changed(update_wave)

end = time.time()

print(end - begin)
plt.show()