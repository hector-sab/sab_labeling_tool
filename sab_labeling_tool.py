import os
import cv2
import copy
import numpy as np

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


# TODO: Allow changing the class when clicking the label.
# Todo: Allow preset of labels from where to choose the default.
# TODO: Issue with the storing the corners of the unregistered corner
#       As of right now, you have to draw the rectangle from top-left to bottom-right
#       to get it done without issues.

class Point:
	def __init__(self,canvas,coord):
		# coord (tuple): (x,y)
		self.selected = False
		self.canvas = canvas
		self.draw = self.canvas.create_oval(coord[0],coord[1],coord[0],coord[1],
			width=6,fill='white')
		self.canvas.tag_bind(self.draw,'<Button-1>',self.__set_selected)

	def __set_selected(self,event):
		# coord: [x,y,x,y]
		self.selected = True
		coord = self.canvas.coords(self.draw)

	def get_coord(self):
		coord = self.canvas.coords(self.draw)
		return([coord[0],(coord[1])])

	def set_setected_off(self):
		# 
		self.selected = False

	def change_coord(self,coord):
		# Defines new location of the point
		self.canvas.coords(self.draw,coord[0],coord[1],coord[0],coord[1])

	def destroy(self):
		# Destroy the rectangle from the canvas
		self.canvas.delete(self.draw)

class Rectangle:
	def __init__(self,canvas,bbox,element,clss='New Object'):
		self.clss = clss
		self.element = None # Which number of element in canvas
		self.selected = False
		self.canvas = canvas
		self.draw = self.canvas.create_rectangle(bbox[0],bbox[1],bbox[2],bbox[3],
			width=3,outline='red')
		self.corners = self.__draw_corners(bbox)
		self.canvas.tag_bind(self.draw,'<ButtonRelease-1>',self.__set_selected)

	def __draw_corners(self,bbox):
		# Draw the corners of a bbox
		points = [(bbox[0],bbox[1]), # top_left (x,y)
				  (bbox[2],bbox[1]), # top_right (x,y)
				  (bbox[0],bbox[3]), # bottom_left (x,y)
				  (bbox[2],bbox[3])] # bottom_right (x,y)
		corners = {}
		for pt,name in zip(points,['tleft','tright','bleft','bright']):
			corner = Point(self.canvas,pt)
			corners[name] = corner
		return(corners)

	def __change_corners_coord(self,bbox):
		# Draw the corners of a bbox
		coords = [(bbox[0],bbox[1]), # top_left (x,y)
				  (bbox[2],bbox[1]), # top_right (x,y)
				  (bbox[0],bbox[3]), # bottom_left (x,y)
				  (bbox[2],bbox[3])] # bottom_right (x,y)

		for coord,name in zip(coords,['tleft','tright','bleft','bright']):
			self.corners[name].change_coord(coord)

	def __set_selected(self,event):
		# Indicates that this rectangle has been selected
		self.selected = True

	def set_setected_off(self):
		# 
		self.selected = False

	def change_coord(self,bbox):
		# Defines new location of bbox
		self.canvas.coords(self.draw,bbox[0],bbox[1],bbox[2],bbox[3])
		self.__change_corners_coord(bbox)

	def get_coord(self):
		# coords: [x_min,y_min,x_max,y_max]
		coord = self.canvas.coords(self.draw)
		return(coord)

	def check_corner_selection(self):
		coord = None
		for key in self.corners:
			corner = self.corners[key]
			if corner.selected:
				coord = corner.get_coord()
				break
		if coord is None:
			key = None
		
		return([key,coord])

	def deselect_corners(self):
		for key in self.corners:
			corner = self.corners[key]
			corner.set_setected_off()

	def change_class(self,new_class):
		self.clss = new_class

	def destroy(self):
		# Destroy the rectangle from the canvas
		for key in self.corners:
			corner = self.corners[key]
			corner.destroy()
		self.canvas.delete(self.draw)

class ImageFrame:
	# Contains the GUI correspondig to the image and bboxes vizualization
	def __init__(self,root,shape=(480,640),main=False,name='Image'):
		# Define root
		self.root = root

		# Indicates if this is the main window or not
		if main: self.window = self.root
		else: self.window = tk.Toplevel(self.root)

		self.window.bind('<B1-Motion>',self.__canvas_pressed)
		self.window.bind('<ButtonRelease-1>',self.__canvas_unpressed)
		self.window.bind('<Button-1>',self.__canvas_clicked)

		# Set the window name
		self.window.title(name)

		# Canch the close event and handle it our way
		self.window.protocol("WM_DELETE_WINDOW",self._on_closing)
		self.closed_window = False

		# Store the bboxes currently drawn
		self.bboxes = [] # Rectangles

		# Flag indicating the coord of the bboxes have changed
		self.bboxes_changed = False

		# Stores the selected bboxes on the image
		self.selected_bboxes = []

		# Flag for selected corner
		self.bbox_corner_selected = False # 
		self.bbox_corner_location = None # 'tleft','bleft','tright','bright'
		self.bbox_corner_ind = None # bbox where the selected corner is

		# Contains the unregistered bbox
		self.unregistered_bbox = None
		self.unregistered_bbox_corner_selected = False
		self.unregistered_bbox_location = None
		self.unregistered_bbox_start = None

		# Store selected bboxes
		self.bboxes_selected = []

		# Sets the canvas/image shape
		self.shape = shape

		# Creates the GUI
		self.__content()

		# Fix window size
		self.window.resizable(width=False, height=False)

	def __content(self):
		# Creates all the content of the image frame

		# Creates the main canvas
		self.canvas = tk.Canvas(self.window,width=self.shape[1],height=self.shape[0],
			bg='black')

		# Position the canvas 
		self.canvas.grid(row=0,column=0)

		# Creates a black image. Not actually needed at this point due to
		# bg='black' parameter at self.canvas.
		im = np.zeros(self.shape)

		# Converst the image to a format that tkinter can handle
		self.im_data = ImageTk.PhotoImage(image=Image.fromarray(im))

		# Initialize the image in the canvas
		self.image = self.canvas.create_image(self.shape[1]//2,self.shape[0]//2,
			image=self.im_data)

		self.canvas.tag_bind(self.image,'<Button-1>',self.__image_unpressed)

	def __condition_image(self,im):
		# Uses a previously loaded image with cv2
		im = im[...,::-1]
		im = im.astype(np.uint8)
		return(im)

	def __load_image(self,path):
		# Loads the images 
		im = cv2.imread(path)
		im = self.__condition_image(im)
		return(im)

	def __set_new_image_on_canvas(self,im):
		# Converst the image to a format that tkinter can handle
		self.im_data = ImageTk.PhotoImage(image=Image.fromarray(im))
		# Initialize the image in the canvas
		self.canvas.itemconfig(self.image,image=self.im_data)

	def __remove_bboxes_on_canvas(self):
		# Removes all the bboces created on the canvas
		for bbox in self.bboxes:
			bbox.destroy()
		self.bboxes = []

	def __moving_corner(self,coord,event,corner_location):
		# Place the coord in the order they should be
		if corner_location=='tleft':
			coord[0] = int(event.x)
			coord[1] = int(event.y)
		elif corner_location=='bleft':
			coord[0] = int(event.x)
			coord[3] = int(event.y)
		elif corner_location=='tright':
			coord[2] = int(event.x)
			coord[1] = int(event.y)
		elif corner_location=='bright':
			coord[2] = int(event.x)
			coord[3] = int(event.y)

		# To avoid the corners disappear on the borders
		if coord[0]<1: coord[0] = 1
		if coord[1]<1: coord[1] = 1
		if coord[2]>self.shape[1]: coord[2] = self.shape[1]-1
		if coord[3]>self.shape[0]: coord[3] = self.shape[0]-1

		return(coord)

	def __canvas_pressed(self,event):
		if self.bbox_corner_selected:
			obj = self.bboxes[self.bbox_corner_ind]
			coord = obj.get_coord()
			coord = self.__moving_corner(coord,event,
				self.bbox_corner_location)
			obj.change_coord(coord)

		elif self.unregistered_bbox_corner_selected:
			obj = self.unregistered_bbox
			coord = obj.get_coord()
			coord = self.__moving_corner(coord,event,
				self.unregistered_bbox_location)
			obj.change_coord(coord)

		elif self.unregistered_bbox_start is not None:
			coord = self.unregistered_bbox_start+[event.x,event.y]
			if self.unregistered_bbox is None:
				self.unregistered_bbox = Rectangle(self.canvas,coord,len(self.bboxes))
			else:
				self.unregistered_bbox.change_coord(coord)

	def __canvas_clicked(self,event):
		if self.unregistered_bbox_start is None:
			self.unregistered_bbox_start = [event.x,event.y]

	def __canvas_unpressed(self,event):
		self.__deselect_corners()
		if self.bbox_corner_selected:
			self.bboxes_changed = True
		self.bbox_corner_selected = False
		self.unregistered_bbox_corner_selected = False
		if self.unregistered_bbox_start==[event.x,event.y]:
			if self.unregistered_bbox is not None:
				self.unregistered_bbox.destroy()
				self.unregistered_bbox = None
				self.unregistered_bbox_location = None
		self.unregistered_bbox_start = None

	def __image_unpressed(self,event):
		if self.unregistered_bbox is not None:
			self.unregistered_bbox.destroy()
			self.unregistered_bbox = None
			self.unregistered_bbox_location = None
		self.__deselect_bboxes()

	def __deselect_bboxes(self):
		for bbox in self.bboxes:
			bbox.set_setected_off()

	def __deselect_corners(self):
		for obj in self.bboxes:
			obj.deselect_corners()
		if self.unregistered_bbox is not None:
			self.unregistered_bbox.deselect_corners()

	def change_image(self,path=None,im=None):
		# Change the image in the canvas
		# If the path of the image is provided, it will load it.
		# In case the image per se is provided, it will condition 
		# it and use it.
		self.__remove_bboxes_on_canvas()

		if path is not None:
			im = self.__load_image(path)
		elif im is not None:
			im = self.__condition_image(im)

		self.__set_new_image_on_canvas(im)

	def draw_bboxes(self,bboxes):
		# Draw the bboxes on the canvas
		# bboxes (list): [[x_min,y_min,x_max,y_max,label]]
		self.__remove_bboxes_on_canvas()
		for i,bbox in enumerate(bboxes):
			obj = Rectangle(self.canvas,bbox[:4],i,clss=bbox[4])
			self.bboxes.append(obj)

	def destroy_unregistered_bbox(self):
		if self.unregistered_bbox is not None:
			self.unregistered_bbox.destroy()
		self.unregistered_bbox = None
		self.unregistered_bbox_start = None
		self.unregistered_bbox_location = None

	def check_rectangle_selection(self):
		self.bboxes_selected = []
		for i,obj in enumerate(self.bboxes):
			if obj.selected:
				self.bboxes_selected.append(i)

	def check_corner_selection(self):
		if not self.bbox_corner_selected:
			for i,obj in enumerate(self.bboxes):
				location,coord = obj.check_corner_selection()
				if location is not None:
					self.bbox_corner_selected = True
					self.bbox_corner_location = location
					self.bbox_corner_ind = i
					break

		if not self.unregistered_bbox_corner_selected: 
			if self.unregistered_bbox is not None:
				obj = self.unregistered_bbox
				location,coord = obj.check_corner_selection()
				if location is not None:
					self.unregistered_bbox_corner_selected = True
					self.unregistered_bbox_location = location

	def set_bboxes_changed_to_false(self):
		#
		self.bboxes_changed = False

	def get_bboxes(self):
		bboxes = []
		for bbox in self.bboxes:
			bboxes.append(bbox.get_coord()+[bbox.clss])

		return(bboxes)

	def _on_closing(self):
		self.closed_window = True

def bboxes_loader_txt_kitti(path,args=None):
	# args (tuple): Not needed. If provided:
	#      args[0] (tuple): Shape of the image 
	#         from where the labels where taken.
	#         (height,width)
	#      args[1] (tuple): Shape of the desired 
	#         image  where the labels will be placed.
	#         (height,width)

	orig_shape = None
	new_shape = None

	if args is not None:
		orig_shape = args[0]
		new_shape = args[1]

	bboxes = []
	
	# Reshape the bboxes if needed

	with open(path,'r') as f:
		file = f.readlines()

	# Iterate over all bboxes
	for line in file:
		line = line.strip('\n')
		line = line.split(' ')
		
		label = line[0]
		x_left = float(line[4])
		y_top = float(line[5])
		x_right = float(line[6])
		y_bottom = float(line[7])

	
		if orig_shape is not None and new_shape is not None:
			x_left = x_left*new_shape[1]/orig_shape[1]
			y_top = y_top*new_shape[0]/orig_shape[0]
			x_right = x_right*new_shape[1]/orig_shape[1]
			y_bottom = y_bottom*new_shape[0]/orig_shape[0]

		bbox = [int(x_left),int(y_top),int(x_right),int(y_bottom),label]
		bboxes.append(bbox)

	return(bboxes)

def bboxes_saver_txt_kitti(path,bboxes,args=None):
	# bboxes: [[x_left,y_top,x_right,y_bottom]]
	line = '{} 0.0 0 0.0 {} {} {} {} 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
	if len(bboxes)>0:
		with open(path,'w') as f:
			for i,bbox in enumerate(bboxes):
				f.write(line.format(bbox[4],int(bbox[0]),int(bbox[1])
					,int(bbox[2]),int(bbox[3])))
				if i<len(bboxes)-1:
					f.write('\n')

class LabelsFrame:
	def __init__(self,root,main=False,lb_loader=None,lb_saver=None,
		def_class=None,name='Labels'):
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

		# Format of the file
		if lb_loader is None:
			self.lb_loader = bboxes_loader_txt_kitti
		else:
			self.lb_loader = lb_loader

		# Saver
		if lb_saver is None:
			self.lb_saver = bboxes_saver_txt_kitti
		else:
			self.lb_saver = lb_saver

		# Default class for new objects
		if def_class is None:
			self.def_class = 'new_object'
		else:
			self.def_class = def_class

		# Indicates that the unregistered bbox should be added
		self.add_lb = False

		# Indicates if the labels should be saved
		self.save_lbs = False

		# Indicates that the next image should be loaded
		self.next_im = False

		# Indicates that the previous image should be loaded
		self.prev_im = False

		# Indicate if the bboxes have changed
		self.bboxes_changed = False

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
		# 
		self.add_lb = True

	def __remove_lbl(self):
		#
		#print('IMPLEMENT REMOVE')
		elems = sorted(list(self.listbox.curselection()))[::-1]
		for elem in elems:
			self.bboxes_changed = True
			del self.bboxes[elem]
		self.__refresh_lbs()

	def __modify_lbl(self):
		#
		print('IMPLEMENT MODIFY')

	def __save_lbs(self):
		# Indicates that the labels should be saved
		self.save_lbs = True

	def __next_im(self):
		# Indicates that the next image should be loaded
		self.next_im = True

	def __prev_im(self):
		# Indicates that the prev image should be loaded
		self.prev_im = True

	def __refresh_lbs(self):
		self.listbox.delete(0,tk.END)
		for bbox in self.bboxes:
			self.listbox.insert(tk.END,bbox[-1])

	def __reset_selection(self):
		# Unselect all selected items in the listbox
		self.listbox.selection_clear(0,tk.END)

	def set_save_lbs_to_false(self):
		#
		self.save_lbs = False

	def set_next_prev_im_to_false(self):
		self.next_im = False
		self.prev_im = False

	def load_lbs(self,path,lb_loader=None,args=None):
		# lb_loader (function): Reference to a function that knows
		#   how to deal with the labels in the uncomming file
		# args (tuple): Args in a tuple if needed.
		if lb_loader is None:
			lb_loader = self.lb_loader
		else:
			lb_loader = lb_loader

		self.change_bboxes(lb_loader(path,args))
		"""
		self.bboxes = lb_loader(path,args)
		self.listbox.delete(0,tk.END)

		# Insert labels in list
		for bbox in self.bboxes:
			self.listbox.insert(tk.END,bbox[-1])
		"""

	def change_bboxes(self,bboxes):
		self.bboxes = bboxes
		self.listbox.delete(0,tk.END)

		# Insert labels in list
		for bbox in self.bboxes:
			self.listbox.insert(tk.END,bbox[-1])

	def reset_lbs(self):
		self.bboxes = []
		self.__refresh_lbs()

	def append_lb(self,bbox):
		self.bboxes_changed = True
		self.bboxes.append(bbox)
		self.__refresh_lbs()

	def save_lbs_to_file(self,path,lb_saver=None,args=None):
		# Saves the bboxes and its labels
		# lb_saver (function): Reference to a function that knows
		#   how to save the bboxes into a file.
		# args (tuple): Args in a tuple if needed.
		if lb_saver is None:
			lb_saver = self.lb_saver
		else:
			lb_saver = lb_saver

		lb_saver(path,self.bboxes,args)

	def set_bboxes_changed_to_false(self):
		# 
		self.bboxes_changed = False

	def set_add_lb_to_false(self):
		# 
		self.add_lb = False

	def set_selections(self,inds):
		# Select all the listbox items that are indicated in inds
		# inds (list): list of indices to be selected
		if inds!=self.current_selections:
			self.__reset_selection()
			for i in inds:
				self.listbox.select_set(i)

			self.current_selections = copy.copy(inds)

	def _on_closing(self):
		# 
		self.closed_window = True

class SABLabelingToolMainGUI:
	def __init__(self,def_class=None):
		# Creates root
		self.root = tk.Tk()
		
		# Default Class
		if def_class is None:
			self.def_class = 'person'
		else:
			self.def_class = def_class
		
		# Creates content
		self.__content()


		# Location of the labels file
		self.lb_path = None

		# Indicates that the next image should be loaded
		self.load_next_im = False
		# Indicates that the previous image should be loaded
		self.load_prev_im = False

		self.closed_windows = False

	def __content(self):
		self.imFrame = ImageFrame(self.root,main=True)
		self.lbsFrame = LabelsFrame(self.root,def_class=self.def_class)

	def load_data(self,im_path,lb_path=None):
		# Loads the image and label file.
		# In case lbs_path is not defined you must use
		# set_out_label_path to indicate where to save 
		# the added labels
		#
		# Args:
		#     im_path (str): Path of the image to be loaded
		#     lbs_path (str): Path of the labels file
		self.imFrame.destroy_unregistered_bbox()
		self.imFrame.change_image(path=im_path)
		if lb_path is not None:
			self.lbsFrame.reset_lbs()
			self.lb_path = lb_path

			if os.path.exists(lb_path):
				self.lbsFrame.load_lbs(lb_path)
			else:
				print('Label file does not exist. ',end=' ')
				print('Using it as path for saving the labels')

	def set_out_label_path(self,lb_path):
		# Set where to save the labels
		self.lb_path = lb_path

	def set_load_next_prev_im_to_false(self):
		self.load_next_im = False
		self.load_prev_im = False

	def run(self):
		# Runs the main loop needed for the GUI to work
		#self.root.mainloop()
		# Draws the modifications to the bboxes when removed
		self.imFrame.draw_bboxes(self.lbsFrame.bboxes)
		while True:
			# Update GUI
			self.root.update_idletasks()
			self.root.update()

			# Close all windows when any of them is closed
			if self.imFrame.closed_window or self.lbsFrame.closed_window:
				self.closed_windows = True
				break

			# 
			self.imFrame.check_rectangle_selection()
			self.imFrame.check_corner_selection()

			# Highlight the selected bboxes
			self.lbsFrame.set_selections(self.imFrame.bboxes_selected)

			# Check if the bboxes have changed in the lbsFrame
			if self.lbsFrame.bboxes_changed:
				self.lbsFrame.set_bboxes_changed_to_false()
				self.imFrame.draw_bboxes(self.lbsFrame.bboxes)

			# Check if the bboxes in imFrame  have changed
			if self.imFrame.bboxes_changed:
				self.imFrame.set_bboxes_changed_to_false()
				bboxes = self.imFrame.get_bboxes()
				self.lbsFrame.change_bboxes(bboxes)

			# Add label to lbsFrame
			if self.lbsFrame.add_lb:
				self.lbsFrame.set_add_lb_to_false()
				if self.imFrame.unregistered_bbox is not None:
					coord = self.imFrame.unregistered_bbox.get_coord()
					coord += [self.lbsFrame.def_class]
					self.lbsFrame.append_lb(coord)
					self.imFrame.destroy_unregistered_bbox()



			# Save labels when save clicked
			if self.lbsFrame.save_lbs:
				print('Saving. ', end =" ")
				self.lbsFrame.set_save_lbs_to_false()
				if len(self.lbsFrame.bboxes)>0:
					self.lbsFrame.save_lbs_to_file(self.lb_path)
					print('File saved.')
				else:
					print('File removed.')
					if os.path.exists(self.lb_path):
						os.remove(self.lb_path)

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
			self.main.load_data(im_path,lb_path)
			self.main.run()
			
			if self.main.load_next_im:
				i += 1
				print('Loading next image! {}/{}'.format(i+1,len(im_paths)))
				if i>len(im_paths)-1:
					i = len(im_paths)-1
					print('End of ims reached.')
			if self.main.load_prev_im:
				i -= 1;
				print('Loading previous image! {}/{}'.format(i+1,len(im_paths)))
				if i<0:
					i = 0
					print('Begining of ims reached.')

			self.main.set_load_next_prev_im_to_false()

			if self.main.closed_windows:
				print('Bye!')
				self.main.root.destroy()
				break


