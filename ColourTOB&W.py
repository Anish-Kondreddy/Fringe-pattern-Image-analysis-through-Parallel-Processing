# import opencv 
import cv2  # type: ignore
  
# Load the input image 
image = cv2.imread('C:\\Users\\info\\Desktop\\Coding\\Pattern.png') 
cv2.waitKey(0) 
  
# Use the cvtColor() function to grayscale the image 
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
  
cv2.imwrite('Grayscale.png', gray_image)
cv2.waitKey(0)   
  
# Window shown waits for any key pressing event 
cv2.destroyAllWindows()
