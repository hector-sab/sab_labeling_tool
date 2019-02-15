import os
import cv2
import numpy as np
import warnings
 
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import xml.etree.ElementTree as ET

def bboxes_loader_xml_imagenet(path,args=None):
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

	tree = ET.parse(path)
	root = tree.getroot()
	for obj in root.findall('object'):
		# Read the class label
		label = obj.find('name').text

		# Read the bbox
		bbox = obj.find('bndbox')
		x_left = float(bbox.find('xmin').text)
		y_top = float(bbox.find('ymin').text)
		x_right = float(bbox.find('xmax').text)
		y_bottom = float(bbox.find('ymax').text)

		if orig_shape is not None and new_shape is not None:
			x_left = x_left*new_shape[1]/orig_shape[1]
			y_top = y_top*new_shape[0]/orig_shape[0]
			x_right = x_right*new_shape[1]/orig_shape[1]
			y_bottom = y_bottom*new_shape[0]/orig_shape[0]

		bbox = [int(x_left),int(y_top),int(x_right),int(y_bottom),label]
		bboxes.append(bbox)
	return(bboxes)

def bboxes_loader_txt_kitti(path,args=None):
	# args (tuple): Not needed. If provided:
	#      args[0] (tuple): Shape of the image 
	#         from where the labels where taken.
	#         (height,width)
	#      args[1] (tuple): Shape of the desired 
	#         image  where the labels will be placed.
	#         (height,width)
	#
	# Returns:
	#    bboxes (list): A list containing lists which represent
	#        individual objects. Its format is:
	#           [[x_left,y_top,x_right,y_bottom,label]]
	#        and the data type is:
	#           [int,int,int,int,str]

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

def condition_image(im):
	im = im[...,::-1]
	im = im.astype(np.uint8)
	return(im)

def load_image(path):
	im = cv2.imread(path)
	return(im)

class Frame:
	def __init__(self,root=None,main=True,name='Frame',nomain_destroy=False):
		# Args:
		#    root ():
		#    main (bool): Indicates if it's the main window
		#    name (str): Name of the window
		#    nomain_destroy (bool): If True and if it's not the main window
		#        destroy only the window if WM_DELETE_WINDOW action detected
		#        on the window.
		self.nomain_destroy = nomain_destroy
		# Indicates root
		if root is None: self.root = tk.Tk()
		else: self.root = root

		# Indicates if this is the main frame or not
		self.ismain = main
		if self.ismain: self.frame = self.root
		else: self.frame = tk.Toplevel(self.root)

		# Set the frame name
		self.frame.title(name)

		# Canch the close event and handle it our way
		self.frame.protocol("WM_DELETE_WINDOW",self._on_closing)
		self.close_frame = False

	def rename_frame(self,name):
		# Renames the frame
		self.frame.title(name)

	def set_frame_location(self,x,y):
		# https://stackoverflow.com/questions/11156766/placing-child-window-relative-to-parent-in-tkinter-python
		# Sets a specific location of the frame
		geometry = '+%d+%d'%(x,y)
		self.frame.geometry(geometry)

	def _on_closing(self):
		# Closes the frame, or set a flag to close the frame
		self.close_frame = True
		if not self.ismain and self.nomain_destroy:
			# Destroy the windows if it's not the main window
			# but has been requested.
			self.frame.destroy()
		elif self.ismain:
			# Destroy the window only if its the main window.
			self.root.destroy()

class Point:
	def __init__(self,canvas,rectangle,coord,pt_diam=6):
		# Args:
		#    coord (list): [x,y]
		self.FLAG_SELECTED = False

		self.canvas = canvas
		self.rectangle = rectangle
		self.object = self.canvas.create_oval(coord[0],coord[1],coord[0],coord[1],
			width=pt_diam,fill='black')

		self.canvas.tag_bind(self.object,'<Button-1>',self._clicked)
		self.canvas.tag_bind(self.object,'<B1-Motion>',self._moved)
		self.canvas.tag_bind(self.object,'<ButtonRelease-1>',self._unclicked)

	def get_coord(self):
		# coords: [x,y,x,y]
		# coords: [x,y,x,y]
		coord = self.canvas.coords(self.object)
		return(coord)

	def set_coord(self,coord):
		# coord: [x,y]
		self.canvas.coords(self.object,coord[0],coord[1],coord[0],coord[1])

	def _clicked(self,event):
		self.FLAG_SELECTED = True
		# Registers the current location
		self.original_click = np.array([event.x,event.y])
		self.canvas.itemconfig(self.rectangle.object,outline='yellow')

	def _moved(self,event):
		now_click = np.array([event.x,event.y])
		movement = self.original_click - now_click
		self.original_click = np.array([event.x,event.y])

		# Calculate new location
		coord = np.array(self.get_coord(),dtype=np.int32)
		new_coord = np.copy(coord)
		new_coord[0] -= movement[0]
		new_coord[1] -= movement[1]

		# Ensure a correct movement
		if movement[0]!=0:
			# If horizontal movement
			if new_coord[0]<0 or new_coord[2]>self.canvas.winfo_width()-1:
				# If moving outside the canvas
				new_coord[0] = coord[0]
		if movement[1]!=0:
			# If vertical movement
			if new_coord[1]<0 or new_coord[3]>self.canvas.winfo_height()-1:
				# If moving outside the canvas
				new_coord[1] = coord[1]

		self.canvas.coords(self.object,new_coord[0],new_coord[1],new_coord[0],new_coord[1])

		self.rectangle._update_rectangle()
		

	def _unclicked(self,event):
		self.FLAG_SELECTED = False
		# Registers the current location
		self.canvas.itemconfig(self.rectangle.object,outline='red')

class Rectangle:
	def __init__(self,canvas,bbox,width_line=3):
		# Args:
		#    bbox (list|np.ndarray): bbox coord. [x_left,y_top,x_right,_y_bottom]
		self.canvas = canvas
		self.object = self.canvas.create_rectangle(bbox[0],bbox[1],bbox[2],bbox[3],
			width=width_line,outline='red')
		
		self.corners = []
		self._draw_corners()

		self.canvas.tag_bind(self.object,'<Button-1>',self._clicked)
		self.canvas.tag_bind(self.object,'<B1-Motion>',self._moved)
		self.canvas.tag_bind(self.object,'<ButtonRelease-1>',self._unclicked)
	
	def _draw_corners(self):
		# coords: [x_min,y_min,x_max,y_max]
		# coords: [x_left,y_top,x_right,y_bottom]
		coord = self.canvas.coords(self.object)
		points = [[coord[0],coord[1]], # Top left
		          [coord[2],coord[1]], # Top right
		          [coord[0],coord[3]], # Bottom left
		          [coord[2],coord[3]], # Bottom right
		          #[coord[0],int(coord[1]+(coord[3]-coord[1])/2)], # Middle left
		          #[coord[2],int(coord[1]+(coord[3]-coord[1])/2)], # Middle right
		          #[int(coord[0]+(coord[2]-coord[0])/2),coord[1]], # Top middle
		          #[int(coord[0]+(coord[2]-coord[0])/2),coord[3]], # Bottom middle
		          ]
		pts_pos = ['tleft','tright','bleft','bright','mleft','mright',
		            'tmiddle','bmiddle']
		for i in range(len(points)):
			pt = points[i]
			pt_pos = pts_pos[i]
			self.corners.append(Point(self.canvas,self,pt))

	def _update_rectangle(self):
		# Calculate new shape
		x_left = None
		y_top = None
		x_right = None
		y_bottom = None

		x_left_lock = False
		x_right_lock = False
		y_top_lock = False
		y_bottom_lock = False
		
		for corner in self.corners:
			coord = corner.get_coord()

			if x_left is None:
				x_left = coord[0]
				if coord.FLAG_SELECTED: x_left_lock = True
			elif coord[0]>=x_left and x_right is None:
				x_right = coord[0]
			elif coord[0]>x_left and coord[0]>x_right:
				x_right = coord[0]
			elif coord[0]<x_left:
				x_left = coord[0]

			if y_top is None:
				y_top = coord[1]
			elif coord[1]>=y_top and y_bottom is None:
				y_bottom = coord[1]
			elif coord[1]>y_top and coord[1]>y_bottom:
				y_bottom = coord[1]
			elif coord[1]<y_top:
				y_top = coord[1]

		coord = np.array([x_left,y_top,x_right,y_bottom])
		# Update rectangle position
		self.set_coord(coord)

		self._update_corners()

	def _update_corners(self):
		coord = self.canvas.coords(self.object)
		points = [[coord[0],coord[1]], # Top left
		          [coord[2],coord[1]], # Top right
		          [coord[0],coord[3]], # Bottom left
		          [coord[2],coord[3]], # Bottom right
		          #[coord[0],int(coord[1]+(coord[3]-coord[1])/2)], # Middle left
		          #[coord[2],int(coord[1]+(coord[3]-coord[1])/2)], # Middle right
		          #[int(coord[0]+(coord[2]-coord[0])/2),coord[1]], # Top middle
		          #[int(coord[0]+(coord[2]-coord[0])/2),coord[3]], # Bottom middle
		          ]
		corn_coord = []
		
		for corner,pt in zip(self.corners,points):
			if not corner.FLAG_SELECTED:
				corner.set_coord(pt)


	def get_coord(self):
		# coords: [x_min,y_min,x_max,y_max]
		# coords: [x_left,y_top,x_right,y_bottom]
		coord = self.canvas.coords(self.object)
		return(coord)

	def set_coord(self,coord):
		# coords: [x_min,y_min,x_max,y_max]
		# coords: [x_left,y_top,x_right,y_bottom]
		self.canvas.coords(self.object,coord[0],coord[1],coord[2],coord[3])

	def _clicked(self,event):
		# Registers the current location
		self.original_click = np.array([event.x,event.y])
		self.canvas.itemconfig(self.object,outline='yellow')

	def _moved(self,event):
		now_click = np.array([event.x,event.y])
		movement = self.original_click - now_click
		self.original_click = np.array([event.x,event.y])

		# Calculate new location
		coord = np.array(self.get_coord(),dtype=np.int32)
		new_coord = np.copy(coord)
		new_coord[::2] -= movement[0]
		new_coord[1::2] -= movement[1]

		# Ensure a correct movement
		if movement[0]!=0:
			# If horizontal movement
			if new_coord[0]<0 or new_coord[2]>self.canvas.winfo_width()-1:
				# If moving outside the canvas
				new_coord[::2] = coord[::2]
		if movement[1]!=0:
			# If vertical movement
			if new_coord[1]<0 or new_coord[3]>self.canvas.winfo_height()-1:
				# If moving outside the canvas
				new_coord[1::2] = coord[1::2]

		#self.canvas.coords(self.object,new_coord[0],new_coord[1],new_coord[2],new_coord[3])
		self.set_coord(new_coord)

	def _unclicked(self,event):
		# Registers the current location
		self.canvas.itemconfig(self.object,outline='red')

	def remove(self):
		# Remove from canvas
		self.canvas.delete(self.draw)


class ImageFrame(Frame):
	def __init__(self,root=None,main=True,name='Image Frame'):
		super().__init__(root,main,name)
		self.objects = [] # Contains all the rectangles

		self.create_content()

	def create_content(self):
		# Creates all the content of the image frame
		shape = (480,640) # Default shape
		# Creates the canvas where everything will be displayed
		self.canvas = tk.Canvas(self.frame,width=shape[1],height=shape[0],
			bg='black')
		# Positions the canvas
		self.canvas.grid(row=0,column=0)

		# Creates a black image. Not actually needed at this point due to
		# bg='black' parameter at self.canvas.
		im = np.zeros(shape)
		# Converst the image to a format that tkinter can handle
		self.im_data = ImageTk.PhotoImage(image=Image.fromarray(im))
		# Initialize the image in the canvas
		self.image = self.canvas.create_image(0,0,anchor=tk.NW,image=self.im_data)

		# Fix frame size
		self.frame.resizable(width=False, height=False)

	def load_new_data(self,im,objs):
		# 
		self._set_new_image_on_canvas(im)
		self._draw_new_objects(objs)

	def _set_new_image_on_canvas(self,im):
		# Converst the image to a format that tkinter can handle
		self.shape = (im.shape[0],im.shape[1])
		self.canvas.config(height=im.shape[0],width=im.shape[1])
		self.im_data = ImageTk.PhotoImage(image=Image.fromarray(im))
		# Initialize the image in the canvas
		self.canvas.itemconfig(self.image,image=self.im_data)

	def _draw_new_objects(self,objs):
		for obj in objs:
			self.objects.append(Rectangle(self.canvas,obj))

		#print(self.objects[0].object.cget("text"))

class PopUp2(Frame):
	# Pop Up object that will be reused instead of being
	# complitly destroyed each time it's closed.
	def __init__(self,root=None,main=False,name='Pop Up'):
		self.root = root; self.main = main; self.name = name
		self.bbox_label = ''
		self.tmp_bbox_label = self.bbox_label
		self.object_edited = None

	def create_content(self):
		super().__init__(self.root,self.main,self.name)
		self.entry = tk.Entry(self.frame)
		self.entry.grid(row=0,column=0,columnspan=2)

		self.btn_ok = tk.Button(self.frame,text='Ok',command=self._ok)
		self.btn_ok.grid(row=1,column=0)
		self.btn_cancel = tk.Button(self.frame,text='Cancel',command=self._cancel)
		self.btn_cancel.grid(row=1,column=1)

		self.entry.insert(0,self.bbox_label)

	def set_initial_position(self):
		# Locates the PopUp window in the center of the screen
		#self.root.update() # Forces to generate the shapes

		# Gets frame shape
		frame_width = self.frame.winfo_width()
		frame_height = self.frame.winfo_height()

		# Gets screen resolution
		screen_width = self.root.winfo_screenwidth()
		screen_height = self.root.winfo_screenheight()
		x = int(screen_width/2) - int(frame_width/2)
		y = int(screen_height/2) - int(frame_height/2)
		self.set_frame_location(x,y)

	def pop(self,obj_id=None,text=''):
		self.create_content()

		self.frame.bind('<Return>',self._ok_keyboard)
		self.frame.bind('<Escape>',self._cancel_keyboard)

		self.change_bbox_label(text)
		self.object_edited = obj_id
		self.close_frame = False
		# Pops the frame
		self.frame.deiconify()
		# Set focus only on the pop up. Disable all other
		# windows while the popup is open
		self.frame.wait_visibility()
		self.frame.grab_set()
		self.set_initial_position()

		self.entry.focus()

	def change_bbox_label(self,new_text):
		self.entry.delete(0, tk.END)
		self.entry.insert(0,new_text)
		self.tmp_bbox_label = new_text

	def get_bbox_label(self):
		#
		return(self.tmp_bbox_label)

	def _ok(self):
		# Saves the label
		self.tmp_bbox_label = self.entry.get()
		self._on_closing()

	def _ok_keyboard(self,event):
		# Ok callback for the keyboard binding
		self._ok()

	def _cancel_simple(self):
		# Just cancel the operation,
		# it does not close the frame
		self.entry.delete(0, tk.END)
		self.entry.insert(0,self.tmp_bbox_label)

	def _cancel(self):
		# Does not save any change, and closes the window
		self._cancel_simple()
		self._on_closing()

	def _cancel_keyboard(self,event):
		# Cancel callback for the keyboard binding
		self._cancel()

	def _on_closing(self):
		# Closes the frame and set a flag to close the frame
		self._cancel_simple()
		self.close_frame = True
		#self.frame.withdraw()
		self.frame.grab_release()
		
		self.frame.destroy()

class PopUp(Frame):
	# Pop Up just to display information
	def __init__(self,root=None,main=False,name='Pop Up'):
		super().__init__(root,main,name)

		# Set focus only on the pop up. Disable all other
		# windows while the popup is open
		self.frame.wait_visibility()
		self.frame.grab_set()
		self.create_content()
		self.set_initial_position()

	def create_content(self):
		self.btn_ok = tk.Button(self.frame,text='Ok')
		self.btn_ok.grid(row=0,column=0)

	def set_initial_position(self):
		# Locates the PopUp window in the center of the screen
		self.root.update()

		frame_width = self.frame.winfo_width()
		frame_height = self.frame.winfo_height()

		screen_width = self.root.winfo_screenwidth()
		screen_height = self.root.winfo_screenheight()
		x = int(screen_width/2) - int(frame_width/2)
		y = int(screen_height/2) - int(frame_height/2)
		self.set_frame_location(x,y)

	def _on_closing(self):
		# Closes the frame and set a flag to close the frame
		self.frame.grab_release()
		self.close_frame = True
		# Destroy the windows if it's not the main window
		# but has been requested.
		self.frame.destroy()

class LabelObject:
	def __init__(self,tree,popup_dialog,text,root=None):
		self.root = root
		self.tree = tree
		self.popup_dialog = popup_dialog
		self.object = self.tree.insert('',tk.END,text=text)
		self.tree.bind('<Double-1>',self.clicked_access)

	def edit(self,obj_id=None):
		# Edit label
		if obj_id is None:
			# If no item id provided, get it
			obj_id = self.get_object_id()

		# Activate the popup frame to edit the label
		self.popup_dialog.pop(obj_id,self.tree.item(obj_id,"text"))
		# Wait until the popup is destroyed
		self.root.wait_window(self.popup_dialog.frame)
		# Which item was edited
		new_text = self.popup_dialog.get_bbox_label()

		# Change text of the treeview item
		self.tree.item(obj_id,text=new_text)

	def clicked_access(self,event):
		"""
		item = self.tree.selection()[0]
		print(item)
		print("you clicked on", self.tree.item(item,"text"))

		# Which row and col was clicked
		rowid = self.tree.identify_row(event.y)
		colid = self.tree.identify_column(event.x)
		print(rowid,colid)

		# get column position info
		x,y,width,height = self.tree.bbox(rowid, colid)
		print(x,y,width,height)

		# y-axis offset
		pady = int(height/2)

		# place Entry popup properly         
		url = self.tree.item(rowid, 'text')
		print(url)
		#popup = PopUp(self.root)
		#print(popup)
		"""
		#print('---',self.object)# self.object and obj_id return the same
		#                        # but does not work well somehow.
		obj_id = self.tree.identify('item', event.x, event.y)
		self.edit(self.tree.selection()[0])

	def keyboard_access(self):
		# Accesing
		self.edit()

	def get_object_id(self):
		# Returns the object id str. E.G. 'I001'
		return(self.object.title())

	def remove(self):
		obj_id = self.object.title()
		self.tree.delete(obj_id)

class LabelsFrame(Frame):
	def __init__(self,root=None,main=True,name='Labels Frame',def_label='new_obj',
		multiple=False):
		super().__init__(root,main,name)
		self.objects = []
		self.removed_objects_id = []
		self.def_label = def_label

		self.FLAG_SAVE = False
		self.FLAG_NEXT = False
		self.FLAG_PREV = False
		# Creates the pop up frame
		self.popup_dialog = PopUp2(self.root)

		# Creates the base content of the frame
		self.create_content(multiple)

		# Fix frame size
		self.frame.resizable(width=False, height=False)

	def create_content(self,multiple=False):
		# DisplaysCreates a list/Treeview to display
		# all the labels
		self.tree = ttk.Treeview(self.frame)
		self.tree.grid(row=1,column=1,rowspan=4)
		
		# Adds buttons
		self.btn_add = tk.Button(self.frame,text='Add',command=self._add)
		self.btn_remove = tk.Button(self.frame,text='Remove',command=self._remove)
		self.btn_edit = tk.Button(self.frame,text='Edit',command=self._edit)
		self.btn_save = tk.Button(self.frame,text='Save',command=self._save)

		# Keyboard binding
		self.frame.bind('a',self._add)
		self.frame.bind('e',self._edit)
		self.frame.bind('s',self._save)

		# Configure shape
		self.btn_add.config(height=2,width=10)
		self.btn_remove.config(height=2,width=10)
		self.btn_edit.config(height=2,width=10)
		self.btn_save.config(height=2,width=10)

		self.btn_add.grid(row=1,column=3)
		self.btn_remove.grid(row=2,column=3)
		self.btn_edit.grid(row=3,column=3)
		self.btn_save.grid(row=4,column=3)

		if multiple:
			self.btn_next = tk.Button(self.frame,text='Next',command=self._next)
			self.btn_prev = tk.Button(self.frame,text='Prev',command=self._prev)
			self.btn_next.config(height=2,width=10)
			self.btn_prev.config(height=2,width=10)
			self.btn_next.grid(row=5,column=3)
			self.btn_prev.grid(row=6,column=3)

			self.frame.bind('n',self._next)
			self.frame.bind('p',self._prev)

		# TMP
		#self.load_new_objs([[1,1,1,1,'P1'],[1,1,1,1,'P2']])

	def _add_object(self,tree,popup_dialog,def_label,root=None):
		# Adds a single label
		self.objects.append(LabelObject(tree,popup_dialog,def_label,root))

	def _add(self,event=None):
		# Callback function
		self._add_object(self.tree,self.popup_dialog,self.def_label,self.root)
		print('Implement add fully')

	def _remove(self):
		obj_id = self.tree.selection()[0]
		self.tree.delete(obj_id)
		self.removed_objects_id.append(obj_id)

	def _edit(self,event=None):
		if len(self.tree.selection())==1:
			# When only one item is selected
			item_id = self.tree.selection()[0]
			for obj in self.objects:
				obj_id = obj.get_object_id()
				if obj_id==item_id:
					obj.keyboard_access()
					break
		elif len(self.tree.selection())==0:
			# When no item is selected
			print('Nothing selected to edit.')
		else:
			# When more than one elements are selected
			print('Select a single row to edit.')

	def _save(self,event=None):
		# 
		self.FLAG_SAVE = True

	def _next(self,event=None):
		# 
		self.FLAG_NEXT = True

	def _prev(self,event=None):
		# 
		self.FLAG_PREV = True

	def load_new_objs(self,objs):
		# Load the objects into the treeview
		#    objs is a list of list with the following format
		#        [[x_left,y_top,x_right,y_bottom,label]]
		self.clear_frame()
		for obj in objs:
			self._add_object(self.tree,self.popup_dialog,obj[-1],self.root)

	def clear_frame(self):
		# Removes all objects from the frame
		for obj in self.objects:
			# Remove all objects from treeview
			obj_id = obj.get_object_id()
			if obj_id not in self.removed_objects_id:
				# Make sure it hasn't been erased before
				obj.remove()

		self.objects = []
		self.removed_objects_id = []

	def set_save_to_false(self):
		# 
		self.FLAG_SAVE = False

	def set_next_to_false(self):
		# 
		self.FLAG_NEXT = False

	def set_prev_to_false(self):
		# 
		self.FLAG_PREV = False
		

class SABLabelingToolMainGUI:
	def __init__(self,def_class=None,lb_loader_fmt='txt',main=True,multiple=False):
		# Args:
		#    def_class (str): Name of the default class.
		#    lb_loader_fmt (str): Function to load files. The two available
		#        options as of right now are:
		#           - 'txt': Found on KITTI database.
		#           - 'xml': Found on ImageNet database.
		#    main (bool): Indicate if it is the main window or if 
		#        something else is controlling it.
		self.FLAG_CLOSE_WINDOW = False
		self.FLAG_NEXT = False
		self.FLAG_PREV = False

		self.main = main

		# Creates root
		self.root = tk.Tk()

		# Default format to load labels
		if lb_loader_fmt=='txt':
			self.lb_loader = bboxes_loader_txt_kitti
			self.lb_saver =  bboxes_saver_txt_kitti
		elif lb_loader_fmt=='xml':
			self.lb_loader = bboxes_loader_xml_imagenet
			self.lb_saver = None
			print('Implement xml saver.')
		else:
			self.lb_loader = bboxes_loader_txt_kitti
			warnings.warn('Warning: Default label format not found. Using "txt".')

		# Creates content
		self.create_content(multiple)

	def create_content(self,multiple=False):
		# Creates its content
		# Get screen resolution
		screen_width = self.root.winfo_screenwidth()
		screen_height = self.root.winfo_screenheight()

		# Create Image Frame
		self.imFrame = ImageFrame(self.root,main=True)
		# Force Image Frame update to calculate its shape
		self.imFrame.frame.update()
		# Get the shape of the Image Frame
		imf_width = self.imFrame.frame.winfo_width()
		imf_height = self.imFrame.frame.winfo_height()
		# Calculate desired position to appear
		x = int(screen_width/2) - int(imf_width/2)
		y = int(screen_height/2) - int(imf_height/2)
		# Indicate Image Frame where to appear
		self.imFrame.set_frame_location(x,y)

		# Create Labels Frame
		self.lbsFrame = LabelsFrame(self.root,main=False,multiple=multiple)
		self.lbsFrame.frame.update()
		iml_width = self.lbsFrame.frame.winfo_width()
		iml_height = self.lbsFrame.frame.winfo_height()
		x = int(screen_width/2) + int(imf_width/2)
		self.lbsFrame.set_frame_location(x,y)

	def load_data(self,im_path,lb_path=None):
		# Load image
		im = load_image(im_path)
		im = condition_image(im)

		# Load lbs
		if lb_path is not None:
			objs = self.lb_loader(lb_path)
		else:
			objs = []

		return(im,objs)

	def run(self,im_path=None,lb_path=None):
		# Runs the main loop needed for the GUI to work
		im,objs = self.load_data(im_path,lb_path)
		self.lbsFrame.load_new_objs(objs)
		self.imFrame.load_new_data(im,objs)
		while True:
			if self.imFrame.close_frame or self.lbsFrame.close_frame:
				# Checks the destruction of the frames
				self.FLAG_CLOSE_WINDOW = True
				break

			if self.lbsFrame.FLAG_NEXT:
				# 
				self.FLAG_NEXT = True

			if self.lbsFrame.FLAG_PREV:
				# 
				self.FLAG_PREV = True


			# Save labels
			if self.lbsFrame.FLAG_SAVE:
				print('Saving. ',end=' ')
				self.lbsFrame.set_save_to_false()
				if lb_path is None:
					lb_path = 'label.'+self.lb_loader_fmt
				print('Pending to fully implement')

				

			# Update GUI
			self.root.update_idletasks()
			self.root.update()



if __name__=='__main__':
	im_p = 'dog.jpg'
	lb_p = 'tst_lbl001.txt'
	lbt = SABLabelingToolMainGUI()
	lbt.run(im_p,lb_p)