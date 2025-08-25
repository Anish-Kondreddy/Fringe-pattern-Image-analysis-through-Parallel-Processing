from PIL import Image # type: ignore
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
import pandas as pd # type: ignore

import time 
 
# store starting time 
begin = time.time() 


#image_path = 'Pattern.png'
image_path = 'undisturbed.jpg'

    # Open the image
image = Image.open(image_path).convert('L')  # Ensure it's in grayscale ('L' mode)

    # Get image dimensions
width, height = image.size

    # Get pixel values
pixel_values = list(image.getdata())

    # Convert the pixel values to a list of lists (rows)
brightness_list = []

for i in range(height):
    row = pixel_values[i * width:(i + 1) * width]
    brightness_list.append(row)

# Example usage
#print(brightness_list)

newList = np.zeros(width)

for list in brightness_list:
    newList = newList + list

newList = newList/height

print(newList, '\n', len(newList))
print(width, height)

def localTurningPoints(newList):
    turningPoints = []
    minPoints = []
    maxPoints = []

    if newList[0] > newList[1]:
        turningPoints.append({0, 'max'})
        maxPoints.append(0)
    elif newList[0] < newList[1]:
        turningPoints.append({0, 'min'})
        minPoints.append(0)
    
    for i in range(1, width-1):
        if newList[i-1] < newList[i] > newList[i+1]:
            turningPoints.append({i, 'max'})
            maxPoints.append(i)
        elif newList[i-1] > newList[i] < newList[i+1]:
            turningPoints.append({i, 'min'})
            minPoints.append(i)

    if newList[-1] > newList[-2]:
        turningPoints.append({width-1, 'max'})
        maxPoints.append(width-1)
    elif newList[-1] < newList[-2]:
        turningPoints.append({width-1, 'min'})

    return turningPoints, maxPoints, minPoints

turningPoints, maxPoints, minPoints = localTurningPoints(newList)

tableData = [maxPoints, minPoints]

table = pd.DataFrame({'Local Maximums': maxPoints, 'Local Minimums': minPoints})

  
# store end time 
end = time.time() 
# total time taken 
print(f"Total runtime of the program is {end - begin}")

table.to_excel('Table.xlsx')

print(turningPoints)

plt.show()

