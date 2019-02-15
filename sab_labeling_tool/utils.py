import cv2
import numpy as np
def load_im(path):
	"""
	Loads an image
	"""
	im = cv2.imread(path)
	return(im)

def preprocess_image(im):
	"""
	Preprocess image
	"""
	im = im[...,::-1]
	im = im.astype(np.uint8)
	return(im)