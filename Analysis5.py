pixelWidth = input("Pixel Width")
realWidth = input("Real Width")
scale = realWidth/pixelWidth

wavelength = input("wavelength")
thickness = input("thickness of material")
nAir = input("refractive index of air")

fringeShift = input("fringe shift")

refractiveIndex = ( (fringeShift + wavelength) / (2 * thickness)) + nAir