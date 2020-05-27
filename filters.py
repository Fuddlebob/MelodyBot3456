import cv2
import numpy as np
import sys
from os import path, listdir, replace, mkdir

outputFolder = "temp"


def fryImage(imagePath):
	"""
	Passes the image path, opens it with OpenCV and returns the image with drastic posterization
	:param imagePath: string | imagePath | Full image path
	"""
	try:
		mkdir(outputFolder)
	except OSError as error: 
		pass
	imageStart = cv2.imread(imagePath)
	imageColor = addColour(imageStart)
	imageFry = badPosterize(imageColor)
	outname = path.join(outputFolder, 'fryImage.jpg')
	cv2.imwrite(outname, imageFry, [int(cv2.IMWRITE_JPEG_QUALITY), 0])
	replace(outname, imagePath)


def addColour(imageNormal):
	return cv2.applyColorMap(imageNormal, cv2.COLORMAP_AUTUMN)

def badPosterize(imageNormal):
	"""
	Posterize the image through a color list, diving it and making a pallete.
	Finally, applying to the image and returning the image with a the new pallete
	:param imageNormal: CV opened image | imageNormal | The normal image opened with OpenCV
	"""
	colorList = np.arange(0, 256)
	colorDivider = np.linspace(0, 255,3)[1]
	colorQuantization = np.int0(np.linspace(0, 255, 2))
	colorLevels = np.clip(np.int0(colorList/colorDivider), 0, 1)
	colorPalette = colorQuantization[colorLevels]
	return colorPalette[imageNormal]