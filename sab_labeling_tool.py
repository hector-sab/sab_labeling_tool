import os
import cv2
import copy
import numpy as np

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

OBJECT_LABELS = {
	  'aeroplane':(0,'Vehicle'),
	  'bicycle':(1,'Vehicle'),
	  'bird':(2,'Animal'),
	  'boat':(3,'Vehicle'),
	  'bottle':(4,'Indoor'),
	  'bus':(5,'Vehicle'),
	  'car':(6,'Vehicle'),
	  'cat':(7,'Animal'),
	  'chair':(8,'Indoor'),
	  'cow':(9,'Animal'),
	  'diningtable':(10,'Indoor'),
	  'dog':(11,'Animal'),
	  'horse':(12,'Animal'),
	  'motorbike':(13,'Vehicle'),
	  'person':(14,'Person'),
	  'pottedplant':(15,'Indoor'),
	  'sheep':(16,'Animal'),
	  'sofa':(17,'Indoor'),
	  'train':(18,'Vehicle'),
	  'tvmonitor':(19,'Indoor')}


# TODO: Allow modification to the bboxes on the canvas via click events

class ImageFrame:
	# Contains the GUI correspondig to the image and bboxes vizualization
	def __init__(self,root,shape=(480,640),main=False,name='Image'):
		# Defines the root
		self.root = root

		# Indicates if this is the main window or not
		if main: self.window = self.root
		else: self.window = tk.Toplevel(self.root)

		# Set the window name
		self.window.title(name)

		# Canch the close event and handle it our way
		self.window.protocol("WM_DELETE_WINDOW",self._on_closing)
		self.closed_window = False

		# Store the bboxes currently drawn
		self.current_bboxes = [] # List of lists
		self.canvas_current_bboxes = [] # Rectangle objects
		self.canvas_current_corners_bboxes = [] # Point objects
		
		# Stores the clicked bboxes on the image
		self.clicked_bboxes = []

		# Sets the canvas/image shape
		self.shape = shape

		# Creates the GUI
		self.__content()

		# Fix window size
		self.window.resizable(width=False, height=False)


	def __content(self):
		# Creates all the content in the frame

		# Creates the main canvas
		self.canvas = tk.Canvas(self.window,width=self.shape[1],height=self.shape[0],
			bg='black')
		
		# Position the canvas 
		self.canvas.grid(row=1,column=1)

		# Creates a black image. Not actually needed at this point due to
		# bg='black' parameter at self.canvas.
		im = np.zeros(self.shape)

		# Converst the image to a format that tkinter can handle
		self.orig_im_data = ImageTk.PhotoImage(image=Image.fromarray(im)) # Original
		self.im_data = ImageTk.PhotoImage(image=Image.fromarray(im)) # To be edited

		# Initialize the image in the canvas
		self.image = self.canvas.create_image(self.shape[1]//2,self.shape[0]//2,
			image=self.im_data)

		self.canvas.bind('<Button-1>',self.__click)
		
	def __load_image(self,path):
		# Loads the images 
		im = cv2.imread(path)
		im = im[...,::-1]
		im = im.astype(np.uint8)
		return(im)

	def __condition_image(self,im):
		# Used for previously loaded images with cv2
		im = im[...,::-1]
		im = im.astype(np.uint8)
		return(im)		

	def change_image(self,path=None,im=None):
		# Change the image in the canvas
		# If the path of the image is provided, it will load it.
		# In case the image per se is provided, it will condition 
		# it and use it.
		if path is not None:
			im = self.__load_image(path)
		elif im is not None:
			im = self.__condition_image(im)

		self.__set_new_image_on_canvas(im)
		self.__reset_current_bboxes()
		self.__reset_canvas_current_bboxes()

	def __set_new_image_on_canvas(self,im):
		# Converst the image to a format that tkinter can handle
		self.orig_im_data = ImageTk.PhotoImage(image=Image.fromarray(im)) # Original
		self.im_data = ImageTk.PhotoImage(image=Image.fromarray(im)) # To be edited
		# Initialize the image in the canvas
		self.canvas.itemconfig(self.image,image=self.im_data)
		#self.image = self.canvas.create_image(self.shape[1]//2,self.shape[0]//2,
		#	image=self.im_data)

	def __reset_image_on_canvas(self):
		self.canvas.itemconfig(self.image,image=self.orig_im_data)

	def __reset_current_bboxes(self):
		self.current_bboxes = []

	def __reset_canvas_current_bboxes(self):
		# Removes all bboxes created on the canvas
		for bbox,corners in zip(self.canvas_current_bboxes,self.canvas_current_corners_bboxes):
			self.canvas.delete(bbox)
			for corner in corners:
				self.canvas.delete(corner)

	def draw_bboxes(self,bboxes):
		# Draw the bboxes on the canvas
		# bboxes (list): [[x_min,y_min,x_max,y_max,label]]
		if bboxes!=self.current_bboxes:
			self.__reset_canvas_current_bboxes()
			for bbox in bboxes:
				self.canvas_current_bboxes.append(self.canvas.create_rectangle(bbox[0],
					bbox[1],bbox[2],bbox[3],width=3,outline='red'))
				self.canvas_current_corners_bboxes.append(self.draw_bbox_corners(bbox))
			self.current_bboxes = copy.copy(bboxes)

	def draw_bbox_corners(self,bbox):
		# Draw the corners of a bbox
		points = [(bbox[0],bbox[1]), # top_left (x,y)
				  (bbox[2],bbox[1]), # top_right (x,y)
				  (bbox[0],bbox[3]), # bottom_left (x,y)
				  (bbox[2],bbox[3])] # bottom_right (x,y)
		objects = []
		for pt in points:
			ob = self.canvas.create_oval(pt[0],pt[1],pt[0],pt[1],width=4,fill='white')
			objects.append(ob)

		return(objects)

	def __click(self,event):
		print('Clicked at {} {}'.format(event.x,event.y))
		click = (event.x,event.y)

		bbox_selected = False
		for i,bbox in enumerate(self.current_bboxes):
			is_clicked = self.__check_click_close_to_bbox(click,bbox)
			if is_clicked:
				bbox_selected = True
				self.clicked_bboxes = [i]
				break

		if not bbox_selected:
			self.clicked_bboxes = []



	def __check_click_close_to_bbox(self,click,bbox):
		# Checks if a click is close to a bbox
		# Args:
		#    click (tuple): Coordenates of the click. (x,y)
		#    bbox (list): [x_min,y_min,x_max,y_max,label]

		min_dist = 5
		clicked_on = None
		# Vertical lines
		if click[1]>=bbox[1] and click[1]<=bbox[3]:
			if click[0]>=(bbox[0]-min_dist) and click[0]<=(bbox[0]+min_dist):
				# Left line
				clicked_on = 'left'
			elif click[0]>=(bbox[2]-min_dist) and click[0]<=(bbox[2]+min_dist):
				# Right line
				clicked_on = 'right'
		#Horizontal lines
		elif click[1]>=(bbox[1]-min_dist) and click[1]>=(bbox[1]+min_dist):
			# Top 
			if click[0]>=bbox[0] and click[0]<=bbox[2]:
				clicked_on = 'top'
		elif click[1]>=(bbox[3]-min_dist) and click[1]>=(bbox[3]+min_dist):
			# Bottom
			if click[0]>=bbox[0] and click[0]<=bbox[2]:
				clicked_on = 'bottom'

		if clicked_on in ['left','right','top','bottom']:
			return(True)
		else:
			return(False)




	def _on_closing(self):
		self.closed_window = True




class LabelsFrame:
	def __init__(self,root,main=False,name='Labels'):
		# Defines the root
		self.root = root

		# Indicates if this is the main window or not
		if main: self.window = self.root
		else: self.window = tk.Toplevel(self.root)

		# Set the window name
		self.window.title(name)

		# Canch the close event and handle it our way
		self.window.protocol("WM_DELETE_WINDOW",self._on_closing)
		self.closed_window = False

		# Indicates if the labels should be saved
		self.save_lbs = False

		# Indicates that the next image should be loaded
		self.next_im = False

		# Indicates that the previous image should be loaded
		self.prev_im = False

		self.current_selections = []

		self.bboxes = [] # Contains the bboxes [[x_min,y_min,x_max,y_max,label]]
		self.__content()

	def __content(self):
		self.listbox = tk.Listbox(self.window,selectmode=tk.EXTENDED)
		self.listbox.grid(row=1,column=1,rowspan=3)
		
		# TODO: Fix scrollbar not going all the way down
		self.scrollbar = tk.Scrollbar(self.window,orient='vertical')
		self.scrollbar.config(command=self.listbox.yview)
		self.scrollbar.grid(row=1,column=2,rowspan=3,sticky=tk.N+tk.S+tk.W)

		self.btn_add = tk.Button(self.window,text='Add',command=self.__add_lbl)
		self.btn_remove = tk.Button(self.window,text='Remove',command=self.__remove_lbl)
		self.btn_modify = tk.Button(self.window,text='Modify',command=self.__modify_lbl)
		self.btn_save = tk.Button(self.window,text='Save',command=self.__save_lbs)
		self.btn_next = tk.Button(self.window,text='Next',command=self.__next_im)
		self.btn_prev = tk.Button(self.window,text='Prev',command=self.__prev_im)

		self.btn_add.config(height=2,width=10)
		self.btn_remove.config(height=2,width=10)
		self.btn_modify.config(height=2,width=10)
		self.btn_save.config(height=2,width=10)
		self.btn_next.config(height=2,width=10)
		self.btn_prev.config(height=2,width=10)

		self.btn_add.grid(row=1,column=3)
		self.btn_remove.grid(row=2,column=3)
		self.btn_modify.grid(row=3,column=3)
		self.btn_save.grid(row=4,column=3)
		self.btn_next.grid(row=5,column=3)
		self.btn_prev.grid(row=6,column=3)

	def __add_lbl(self):
		print('IMPLEMENT ADD')
		#self.listbox.insert(tk.END,'new_label')
		#self.bboxes.append([0,0,0,0,'new_label'])

	def __remove_lbl(self):
		elems = sorted(list(self.listbox.curselection()))[::-1]
		for elem in elems:
			del self.bboxes[elem]
		self.__refresh_lbs() 

	def __modify_lbl(self):
		print('IMPLEMENT MODIFY')
		#a = self.listbox.get(self.listbox.curselection())
		#elems = self.listbox.curselection()
		#if len(elems)>0:
		#	print('Cannot modify more than one element at a time.')
		#else:
		#	pass
		#	print(elems)

	def __save_lbs(self):
		# Indicates that the labels should be saved
		self.save_lbs = True

	def __next_im(self):
		# Indicates that the next image should be loaded
		self.next_im = True

	def __prev_im(self):
		# Indicates that the prev image should be loaded
		self.prev_im = True

	def set_save_lbs_to_false(self):
		self.save_lbs = False

	def set_next_prev_im_to_false(self):
		self.next_im = False
		self.prev_im = False


	def load_lbs(self,path):
		self.listbox.delete(0,tk.END)
		self.bboxes = self.__load_bboxes_from_txt(path,ob_lbs=OBJECT_LABELS)

		for bbox in self.bboxes:
			self.listbox.insert(tk.END,bbox[-1])

	def __refresh_lbs(self):
		self.listbox.delete(0,tk.END)
		for bbox in self.bboxes:
			self.listbox.insert(tk.END,bbox[-1])

	def __load_bboxes_from_txt(self,path,ob_lbs,orig_shape=None,new_shape=None):
		# Returns the objects found in each file as a list of lists with the form
		# [[x_left,y_top,x_right,y_bottom,class]]
		#   y_top -> Meaning top in the image space, the smallest of both y's
		#
		# Args:
		#   path (str): Location of the lbl file in kitti format.
		#   ob_lbs: OBJECT_LABELS, from constants.
		#   orig_shape (int tuple): Indicates the original size of the image
		#      from where the labels were taken. (height,width)
		#   new_shape (int tuple): What's the new 'im' size that the labels
		#      should be adjusted to. (height,width)
		#   
		#   i.e. If we have a label that its original image had a shape of (480,640)
		#      and we now have that same image but in a shape of (416,416) to allow the
		#      labels to fit the new image we use orig_shape and new_shape

		targets = []
		with open(path,'r') as f:
			file = f.readlines()
			for line in file:
				line = line.strip('\n')
				line = line.split(' ')
				
				label = line[0]
				x_left = float(line[4])
				y_top = float(line[5])
				x_right = float(line[6])
				y_bottom = float(line[7])

				if orig_shape is not None and new_shape is not None:
					x_left = int(x_left*new_shape[1]/orig_shape[1])
					y_top = int(y_top*new_shape[0]/orig_shape[0])
					x_right = int(x_right*new_shape[1]/orig_shape[1])
					y_bottom = int(y_bottom*new_shape[0]/orig_shape[0])

				[x_left,y_top,x_right,y_bottom,label]

				targets.append([x_left,y_top,x_right,y_bottom,label])

			return(targets)

	def set_selections(self,inds):
		# Select all the listbox items that are indicated in inds
		# inds (list): list of indices to be selected
		if inds!=self.current_selections:
			self.__reset_selection()
			for i in inds:
				self.listbox.select_set(i)

			self.current_selections = copy.copy(inds)

	def __reset_selection(self):
		# Unselect all selected items in the listbox
		self.listbox.selection_clear(0,tk.END)

	def _on_closing(self):
		self.closed_window = True



class SABLabelingToolMainGUI:
	# Creates a GUI to label objects on images. It uses txt files
	# with the KITTI format.
	#
	# How to use it:
	# lt = SABLabelingToolMainGUI() # Create an object of the GUI
	# lt.load_image_label(im_path,lbs_path) # Load image and/or labels
	# lt.set_out_label_path(lbs_path) # Set the path of labels to be saved
	#                                   in case labels where not loaded
	# lt.run() # Run the GUI
	def __init__(self):
		# Creates root
		self.root = tk.Tk()
		# Creates content
		self.__content()
		
		# Location of the labels file
		self.lbs_path = None

		# Indicates that the next image should be loaded
		self.load_next_im = False
		# Indicates that the previous image should be loaded
		self.load_prev_im = False

		self.closed_windows = False

	def load_image_label(self,im_path,lbs_path=None):
		# Loads the image and label file .
		# In case lbs_path is not defined you must use
		# set_out_label_path to indicate where to save 
		# the added labels
		#
		# Args:
		#     im_path (str): Path of the image to be loaded
		#     lbs_path (str): Path of the labels file
		self.set_load_next_prev_im_to_false()
		self.imFrame.change_image(im_path)
		if lbs_path is not None:
			self.lbs_path = lbs_path
			if os.path.exists(lbs_path):
				self.lbsFrame.load_lbs(lbs_path)
			else:
				print('Label file does not exist. Using it as path for saving the labels')

	def set_out_label_path(self,lbs_path):
		# Set where to save the labels
		self.lbs_path = lbs_path

	def set_load_next_prev_im_to_false(self):
		self.load_next_im = False
		self.load_prev_im = False

	def run(self):
		# Runs the main loop needed for the GUI to work
		#self.root.mainloop()
		while True:
			self.root.update_idletasks()
			self.root.update()

			# Close all windows when any of them is closed
			if self.imFrame.closed_window or self.lbsFrame.closed_window:
				self.closed_windows = True
				break

			# Draws the modifications to the bboxes when removed
			self.imFrame.draw_bboxes(self.lbsFrame.bboxes)

			# 
			self.lbsFrame.set_selections(self.imFrame.clicked_bboxes)

			# Save labels when save clicked
			if self.lbsFrame.save_lbs:
				print('Saving')
				bboxes = self.imFrame.current_bboxes
				if len(bboxes)>0:
					self.save_bbox2file(self.lbs_path,bboxes)
					print('File saved')
				else:
					print('File removed')
					if os.path.exists(self.lbs_path):
						os.remove(self.lbs_path)

				self.lbsFrame.set_save_lbs_to_false()

			# Indicates that the next image should be loaded
			if self.lbsFrame.next_im:
				self.lbsFrame.set_next_prev_im_to_false()
				self.load_next_im = True
				break

			# Indicates that the previous image should be loaded
			if self.lbsFrame.prev_im:
				self.lbsFrame.set_next_prev_im_to_false()
				self.load_prev_im = True
				break

	def save_bbox2file(self,path,bboxes):
		# [x_left,y_top,x_right,y_bottom]
		line = '{} 0.0 0 0.0 {} {} {} {} 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
		if len(bboxes)>0:
			with open(path,'w') as f:
				for i,bbox in enumerate(bboxes):
					f.write(line.format(bbox[4],bbox[0],bbox[1],bbox[2],bbox[3]))
					if i<len(bboxes)-1:
						f.write('\n')

	def __content(self):
		self.imFrame = ImageFrame(self.root,main=True)
		self.lbsFrame = LabelsFrame(self.root)




class SABLabelingTool:
	def __init__(self):
		self.main = SABLabelingToolMainGUI()

	def run(self,im_paths,lb_paths=None):
		i = 0
		while True:
			im_path = im_paths[i]
			if lb_paths is not None:
				lb_path = lb_paths[i]
			else:
				lbs_path = None
			self.main.load_image_label(im_path,lb_path)
			self.main.run()
			
			if self.main.load_next_im:
				i += 1
				print('Loading next image! {}/{}'.format(i,len(im_paths)))
				if i>len(im_paths)-1:
					i = len(im_paths)-1
					print('End of ims reached.')
			if self.main.load_prev_im:
				i -= 1;
				print('Loading previous image! {}/{}'.format(i,len(im_paths)))
				if i<0:
					i = 0
					print('Begining of ims reached.')

			if self.main.closed_windows:
				print('Bye!')
				self.main.root.destroy()
				break