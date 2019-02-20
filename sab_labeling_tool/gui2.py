import os
import cv2
from copy import copy
import warnings
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import labels as ut_lbs

# TODO: Fix initial position on systems with multiple screens
# TODO: Remember order of selection, might be useful when changing names of rectangles
# TODO: Labels label tree object not working
class Frame:
	def __init__(self,root=None,main=False,name='Frame',nomain_destroy=False):
		# Args:
		#    root ():
		#    main (bool): Indicates if it's the main window
		#    name (str): Name of the window
		#    nomain_destroy (bool): If True and if it's not the main window
		#        destroy only the window if WM_DELETE_WINDOW action detected
		#        on the window.
		self.nomain_destroy = nomain_destroy
		# Indicates root
		if root is None: 
			self.root = tk.Tk()
		else: 
			self.root = root

		# Indicates if this is the main frame or not
		self.ismain = main
		if self.ismain: self.frame = self.root
		else: self.frame = tk.Toplevel(self.root)

		# Set the frame name
		self.frame.title(name)

		# Canch the close event and handle it our way
		self.frame.protocol("WM_DELETE_WINDOW",self._on_closing)
		self.frame_closed = False

	def rename_frame(self,name):
		# Renames the frame
		self.frame.title(name)

	def set_frame_location(self,x,y):
		# https://stackoverflow.com/questions/11156766/placing-child-window-relative-to-parent-in-tkinter-python
		# Sets a specific location of the frame
		geometry = '+%d+%d'%(x,y)
		self.frame.geometry(geometry)

	def hide(self):
		"""
		Hides frame.
		"""
		self.frame.withdraw()

	def expose(self):
		"""
		Shows the frame again.
		"""
		self.frame.deiconify()

	def _on_closing(self):
		"""
		Closes the frame, and sets a flag to close the frame
		"""
		self.frame_closed = True
		self.root.destroy()

class PopUp(Frame):
	"""
	Pop Up object that allow us to modify the name of a
	rectangle. It frame is reused instead of being completely
	erased an created each time it's needed.
	"""
	def __init__(self,root=None,main=False,frame_name='Pop Up'):
		"""
		Args:
		  - root ()
		  - main (bool): Indicates if it is the main frame.
		  - frame_name (str): Name of the ImageFrame frame that will 
		      appear in the top of the window.
		"""
		super().__init__(root,main,frame_name)
		self.create_content()
		self.set_initial_position()

		# Hide frame
		self.hide()
		
		# Text manipulation
		self.rect = None # Rectangle being manipulated

	def create_content(self):
		"""
		"""
		# Text input
		self.entry = tk.Entry(self.frame)
		self.entry.grid(row=0,column=0,columnspan=2)

		# Ok button
		self.btn_ok = tk.Button(self.frame,text='Ok',command=self._ok)
		self.btn_ok.grid(row=1,column=0)

		# Cancel button
		self.btn_cancel = tk.Button(self.frame,text='Cancel',command=self._cancel)
		self.btn_cancel.grid(row=1,column=1)
		
		# Set text 
		#self.set_entry_text(self.entry_text)

		# Bind reactions to keyboard actions
		self.frame.bind('<Return>',self._ok_keyboard)
		self.frame.bind('<Escape>',self._cancel_keyboard)

	def _ok(self):
		"""
		Reaction when the OK button is pressed.
		"""
		self.rect.set_name(self.get_entry_text())
		self._on_closing()

	def _cancel(self):
		"""
		Reaction when the Cancel button is pressed.
		"""
		self._on_closing()
		
	def _ok_keyboard(self,event):
		"""
		Reaction when the <Return> key is pressed.
		"""
		self._ok()

	def _cancel_keyboard(slef,event):
		"""
		Reaction when the <ESC> key is pressed.
		"""
		self._cancel()

	def set_entry_text(self,text):
		"""
		Sets the text in the entry widget
		Args:
		  - text (str): Text to be displayed.
		"""
		self.entry.delete(0,tk.END)
		self.entry.insert(0,text)

	def get_entry_text(self):
		"""
		Gets the text in the entry widget
		"""
		text = self.entry.get()
		return(text)

	def set_initial_position(self):
		"""
		Locates the frame at the center of the screen
		"""
		# Get frame shape
		frame_shape = np.array([self.frame.winfo_width(),self.frame.winfo_height()])

		# Get screen resolution
		screen_shape = np.array([self.root.winfo_screenwidth(),self.root.winfo_screenheight()])

		# Calculate its position
		center = (screen_shape/2 - frame_shape/2).astype(np.int32)

		# Sets its position
		self.set_frame_location(center[0],center[1])

	def pop(self,obj):
		"""
		Pops the pop up window.
		Args:
		  - obj (Rectangle):
		"""
		self.rect = obj

		# Shows the frame
		self.expose()

		# Set focus only on the pop up. Disable all other
		# windows while the popup is open
		self.frame.wait_visibility()
		self.frame.grab_set()

		# Set its position in the center of the screen
		#self.set_initial_position()

		# Set text to the entry
		self.set_entry_text(self.rect.get_name())

		# Focus the entry
		self.entry.focus()

	def _on_closing(self):
		"""
		"""
		self.frame.grab_release()
		self.hide()

class PopUp2(Frame):
	"""
	Pop Up object that allow us to modify the name of a
	rectangle. It frame is completely destroyed each time the
	pop up is closed.
	"""
	def __init__(self,root=None,main=False,frame_name='Pop Up'):
		"""
		Args:
		  - root ()
		  - main (bool): Indicates if it is the main frame.
		  - frame_name (str): Name of the ImageFrame frame that will 
		      appear in the top of the window.
		"""
		self.root = root
		self.main = main
		self.frame_name = frame_name
		# Text manipulation
		self.rect = None # Rectangle being manipulated

	def create_content(self):
		"""
		"""
		super().__init__(self.root,self.main,self.frame_name)
		# Text input
		self.entry = tk.Entry(self.frame)
		self.entry.grid(row=0,column=0,columnspan=2)

		# Ok button
		self.btn_ok = tk.Button(self.frame,text='Ok',command=self._ok)
		self.btn_ok.grid(row=1,column=0)

		# Cancel button
		self.btn_cancel = tk.Button(self.frame,text='Cancel',command=self._cancel)
		self.btn_cancel.grid(row=1,column=1)
		
		# Set text 
		#self.set_entry_text(self.entry_text)

		# Bind reactions to keyboard actions
		self.frame.bind('<Return>',self._ok_keyboard)
		self.frame.bind('<Escape>',self._cancel_keyboard)

	def _ok(self):
		"""
		Reaction when the OK button is pressed.
		"""
		self.rect.set_name(self.get_entry_text())
		self._on_closing()

	def _cancel(self):
		"""
		Reaction when the Cancel button is pressed.
		"""
		self._on_closing()
		
	def _ok_keyboard(self,event):
		"""
		Reaction when the <Return> key is pressed.
		"""
		self._ok()

	def _cancel_keyboard(self,event):
		"""
		Reaction when the <ESC> key is pressed.
		"""
		self._cancel()

	def set_entry_text(self,text):
		"""
		Sets the text in the entry widget
		Args:
		  - text (str): Text to be displayed.
		"""
		self.entry.delete(0,tk.END)
		self.entry.insert(0,text)

	def get_entry_text(self):
		"""
		Gets the text in the entry widget
		"""
		text = self.entry.get()
		return(text)

	def set_initial_position(self):
		"""
		Locates the frame at the center of the screen
		"""
		# Get frame shape
		frame_shape = np.array([self.frame.winfo_width(),self.frame.winfo_height()])

		# Get screen resolution
		screen_shape = np.array([self.root.winfo_screenwidth(),self.root.winfo_screenheight()])

		# Calculate its position
		center = (screen_shape/2 - frame_shape/2).astype(np.int32)

		# Sets its position
		self.set_frame_location(center[0],center[1])

	def pop(self,obj):
		"""
		Pops the pop up window.
		Args:
		  - obj (Rectangle):
		"""
		self.rect = obj

		self.create_content()

		# Set focus only on the pop up. Disable all other
		# windows while the popup is open
		self.frame.wait_visibility()
		self.frame.grab_set()

		# Set its position in the center of the screen
		self.set_initial_position()

		# Set text to the entry
		self.set_entry_text(self.rect.get_name())

		# Focus the entry
		self.entry.focus()

		# Wait until the popup is destroyed
		self.root.wait_window(self.frame)

	def _on_closing(self):
		"""
		"""
		self.frame.grab_release()
		self.frame.destroy()

class Point:
	"""
	Point to be drawn in a canvas
	"""
	def __init__(self,init_coord,canvas,parent=None,mode='corner',width=16):
		"""
		Args:
		  canvas (): Canvas where the object will be drawn
		  init_coord (tuple|list|np.ndarray): initial coordenates of
		    the point. [X,Y]
		  parent (Rectangle): Its object parent.
		  model (str|int): Way the point should behave. 
		    'corner' | 0: Moves freely
		    'h-edge' | 1: Moves verticaly
		    'v-edge' | 2: Moves horizontaly
		"""
		modes = {'corner':0,'h-edge':1,'v-edge':2}
		if isinstance(mode,str):
			self.mode = modes[mode]
		elif isinstance(mode,int):
			if mode>len(modes)-1:
				warnings.warn('Warning: Desired mode not found. Using "corner" instead.')
				self.mode = 0
			else:
				self.mode = mode
		
		self.canvas = canvas
		self.parent = parent
		self.selected = False
		self.draw = self.canvas.create_oval(init_coord[0],init_coord[1],init_coord[0],init_coord[1],
			width=width,outline='yellow',fill='')
		#self.canvas.itemconfig(self.draw, fill='red')

		self.canvas.tag_bind(self.draw,'<Button-1>',self.__object_clicked)
		self.canvas.tag_bind(self.draw,'<ButtonRelease-1>',self.__object_unclicked)
		self.canvas.tag_bind(self.draw,'<B1-Motion>',self.__object_moving)

	def __object_clicked(self,event):
		"""
		Reacts when the object is pressed
		Args:
		  event (): 
		"""
		self.set_selection_on()
		self.parent.hide_control_points()
	
	def __object_unclicked(self,event):
		"""
		Reacts when the objecet is unpressed
		"""
		self.set_selection_off()
		self.parent.expose_control_points()

	def __object_moving(self,event):
		"""
		Reacts when the objecet is pressed and the mouse is moving
		"""
		cur_coord = self.get_coord()
		new_coord = np.array([event.x,event.y],dtype=np.int32)

		# Adjust movement based on the mode of the point
		if self.mode==0:
			# corner. Moves freely
			coord = new_coord
		elif self.mode==1:
			# h-edge. Moves vertically
			coord = [cur_coord[0],new_coord[1]]
		elif self.mode==2:
			# v-edge. Moves horizontally
			coord = [new_coord[0],cur_coord[1]]

		# Ensure it moves only inside teh canvas
		canvas_shape = [self.canvas.winfo_width(),self.canvas.winfo_height()]
		canvas_shape = np.array(canvas_shape)
		
		mask_big = coord>(canvas_shape-1)
		mask_small = coord<np.array([0,0])

		if mask_big[0]:
			# If the width is bigger than the canvas
			coord[0] = canvas_shape[0]-1
		if mask_big[1]:
			# If the height is bigger than the canvas
			coord[1] = canvas_shape[1]-1

		if mask_small[0]:
			# If the width is smaller than the canvas
			coord[0] = 0
		if mask_small[1]:
			# If the height is smaller than the canvas
			coord[1] = 0

		self.parent.adjust_rectangle_from_point(coord)

		self.change_coord(coord)

	def set_selection_on(self):
		"""
		"""
		self.selected = True

	def set_selection_off(self):
		"""
		"""
		self.selected = False

	def get_coord(self):
		"""
		Return the coordenates where the point is located in the canvas
		[X,Y]
		"""
		coord = self.canvas.coords(self.draw)
		return(np.array([coord[0],coord[1]],dtype=np.int32))

	def change_coord(self,coord):
		"""
		Changes the location of the point.
		Args:
		  coord (tuple|list|np.ndarray): New coordenates of
		    the point. [X,Y]
		"""
		self.canvas.coords(self.draw,coord[0],coord[1],coord[0],coord[1])

	def hide(self):
		"""
		Hides the object
		"""
		self.canvas.itemconfigure(self.draw, state='hidden')

	def expose(self):
		"""
		Shows the object if previously hidden
		"""
		self.canvas.itemconfigure(self.draw, state='normal')

	def destroy(self):
		"""
		Destroy the object from the canvas
		"""
		self.canvas.delete(self.draw)

class Rectangle:
	"""
	Rectangle tp be drawn in the canvas as bounding box.
	"""
	def __init__(self,canvas,coord,name='New Object'):
		"""
		Args:
		  canvas (): Canvas where the object will be drawn.
		  coord (tuple|list|np.ndarray): Two points representing the
		    opposite corners of the rectangle. [x_min,y_min,x_max,y_max]
		"""
		self.name = name
		self.canvas = canvas
		self.selected = False
		self.exist = True # Indicates if it hasn't been removed

		self.previous_mouse_possition = None #[x,y]
		
		# Creates object in the canvas
		self.draw = self.canvas.create_rectangle(coord[0],coord[1],coord[2],coord[3],
			width=3,outline='red')
		self.points = self.create_control_points()
		
		self.canvas.tag_bind(self.draw,'<Button-1>',self.__object_clicked)
		self.canvas.tag_bind(self.draw,'<ButtonRelease-1>',self.__object_unclicked)
		self.canvas.tag_bind(self.draw,'<B1-Motion>',self.__object_moving)

	def __object_clicked(self,event):
		"""
		"""
		if not self.selected:
			self.set_selection_on()
		else:
			self.set_selection_off()
		self.previous_mouse_possition = np.array([event.x,event.y])

	def __object_unclicked(self,event):
		"""
		"""
		self.previous_mouse_possition = None

	def __object_moving(self,event):
		"""
		""" 
		# Calculate displacement
		disp = [0,0] # [x,y]
		disp[0] = event.x - self.previous_mouse_possition[0]
		disp[1] = event.y - self.previous_mouse_possition[1]

		# Calculate new coordenates 
		coord = self.get_coord()
		
		new_coord = np.copy(coord)
		new_coord[::2] += disp[0]
		new_coord[1::2] += disp[1]
		
		# Ensure that the rectangle is inside the canvas
		canvas_shape = [self.canvas.winfo_width(),self.canvas.winfo_height()]
		canvas_shape = np.array(canvas_shape)

		if new_coord[2]>(canvas_shape[0]-1) or event.x>canvas_shape[0]:
			# If we are trying to move ouside the right limit
			new_coord[::2] = coord[::2]

		if new_coord[3]>(canvas_shape[1]-1) or event.y>canvas_shape[1]:
			# If we are trying to move ouside the bpttom limit
			new_coord[1::2] = coord[1::2]

		if new_coord[0]<0 or event.x<0:
			# If we are trying to move ouside the left limit
			new_coord[::2] = coord[::2]

		if new_coord[1]<0 or event.y<0:
			# If we are trying to move ouside the top limit
			new_coord[1::2] = coord[1::2]

		# Change location
		self.change_coord(new_coord)
		self.adjust_control_points()

		self.previous_mouse_possition = np.array([event.x,event.y])

	def set_selection_on(self):
		"""
		"""
		self.canvas.itemconfig(self.draw, outline='blue')
		self.selected = True

	def set_selection_off(self):
		"""
		"""
		self.canvas.itemconfig(self.draw, outline='red')
		self.selected = False

	def get_coord(self):
		"""
		Returns the coord of the object in the canvas
		[x_min,y_min,x_max,y_max]
		"""
		coord = self.canvas.coords(self.draw)
		return(np.array(coord))

	def set_name(self,name):
		"""
		Set the name of the object
		"""
		self.name = name

	def get_name(self):
		"""
		Get the name of the object
		"""
		return(self.name)

	def change_coord(self,coord):
		"""
		Change the location of the object in the canvas
		Args:
		  coord (tuple|list|np.ndarray): New location of the obejct
		    in the canvas. [x_min,y_min,x_max,y_max]
		"""
		self.canvas.coords(self.draw,coord[0],coord[1],coord[2],coord[3])

	def create_control_points(self):
		"""
		Creates control points for the object

		Returns:
		  points (list): List of the Point objects created
		"""
		points = []
		coord = self.get_coord()
		center_x = int(coord[0]+(coord[2]-coord[0])/2)
		center_y = int(coord[1]+(coord[3]-coord[1])/2)
		# Top-Left
		points.append(Point([coord[0],coord[1]],self.canvas,self))
		# Top-Center
		points.append(Point([center_x,coord[1]],self.canvas,self,mode='h-edge'))
		# Top-Right
		points.append(Point([coord[2],coord[1]],self.canvas,self))
		# Center-Left
		points.append(Point([coord[0],center_y],self.canvas,self,mode='v-edge'))
		# Center-Right
		points.append(Point([coord[2],center_y],self.canvas,self,mode='v-edge'))
		# Bottom-Left
		points.append(Point([coord[0],coord[3]],self.canvas,self))
		# Bottom-Center
		points.append(Point([center_x,coord[3]],self.canvas,self,mode='h-edge'))
		# Bottom-Right
		points.append(Point([coord[2],coord[3]],self.canvas,self))

		return(points)

	def adjust_control_points(self):
		"""
		Moves the control points based on the movement of the whole rectangle
		when dragged.
		"""
		coord = self.get_coord()
		center_x = int(coord[0]+(coord[2]-coord[0])/2)
		center_y = int(coord[1]+(coord[3]-coord[1])/2)
		# Top-Left
		self.points[0].change_coord([coord[0],coord[1]])
		# Top-Center
		self.points[1].change_coord([center_x,coord[1]])
		# Top-Right
		self.points[2].change_coord([coord[2],coord[1]])
		# Center-Left
		self.points[3].change_coord([coord[0],center_y])
		# Center-Right
		self.points[4].change_coord([coord[2],center_y])
		# Bottom-Left
		self.points[5].change_coord([coord[0],coord[3]])
		# Bottom-Center
		self.points[6].change_coord([center_x,coord[3]])
		# Bottom-Right
		self.points[7].change_coord([coord[2],coord[3]])

	def hide_control_points(self):
		"""
		Hide all control points in the canvas of this object.
		"""
		for point in self.points:
			point.hide()

	def expose_control_points(self):
		"""
		Expose all control points in the canvas of this object.
		"""
		for point in self.points:
			point.expose()

	def adjust_rectangle_from_point(self,coord):
		"""
		Args:
		  coord (tuple|list|np.ndarray): Position of the pointer.
		    [x,y]
		"""
		for i,point in enumerate(self.points):
			selected = point.selected
			if selected:
				if i==0:
					"""
					Calculates the new position of the rectangle.
					Bottom right corner does not move.
					Points not affected -> [7]
					Moves -> [YES,YES,NO,NO]
					"""
					rect_coord = self.get_coord()
					rect_coord[0] = coord[0]
					rect_coord[1] = coord[1]
				elif i==1:
					"""
					Calculates the new position of the rectangle.
					All bottom points don't move.
					Points not affected = [5,6,7]
					Moves -> [NO,YES,NO,NO]
					"""
					rect_coord = self.get_coord()
					rect_coord[1] = coord[1]
				elif i==2:
					"""
					Calculates the new position of the rectangle.
					Bottom left corner does not move.
					Points not affected = [5]
					Moves -> [NO,YES,YES,No]
					"""
					rect_coord = self.get_coord()
					rect_coord[2] = coord[0]
					rect_coord[1] = coord[1]
				elif i==3:
					"""
					Calculates the new position of the rectangle.
					All right points don't move.
					Poinys not affected = [2,4,7]
					Moves -> [YES,NO,NO,NO]
					"""
					rect_coord = self.get_coord()
					rect_coord[0] = coord[0]
				elif i==4:
					"""
					Calculates the new position of the rectangle.
					All left points don't move.
					Points not affected = [0,3,5]
					Moves -> [NO,NO,YES,NO]
					"""
					rect_coord = self.get_coord()
					rect_coord[2] = coord[0]
				elif i==5:
					"""
					Calculates the new position of the rectangle.
					Top right corner does not move.
					Points not affected = [2]
					Moves -> [YES,NO,NO,YES]
					"""
					rect_coord = self.get_coord()
					rect_coord[0] = coord[0]
					rect_coord[3] = coord[1]
				elif i==6:
					"""
					Calculates the new position of the rectangle.
					All top points don't move.
					Point not affected = [0,1,2]
					Moves -> [NO,NO,NO,YES]
					"""
					rect_coord = self.get_coord()
					rect_coord[3] = coord[1]
				elif i==7:
					"""
					Calculates the new position of the rectangle.
					Top left corner does not move.
					Point not affected = [0]
					Moves -> [NO,NO,YES,YES]
					"""
					rect_coord = self.get_coord()
					rect_coord[2] = coord[0]
					rect_coord[3] = coord[1]

				self.change_coord(rect_coord)
				self.adjust_control_points()

	def hide(self):
		"""
		Hides the object
		"""
		self.hide_control_points()
		self.canvas.itemconfigure(self.draw, state='hidden')

	def expose(self):
		"""
		Shows the object if previously hidden
		"""
		self.canvas.itemconfigure(self.draw, state='normal')
		self.expose_control_points()

	def set_removed_on(self):
		"""
		It indicates that it has been removed from the existing objects
		and should not be considered in the following tasks.
		"""
		self.exist = False
	
	def destroy(self):
		"""
		Destroy the object
		"""
		for point in self.points:
			point.destroy()

		self.canvas.delete(self.draw)

class ObjectsTracker:
	"""
	Class that keeps track of all objects in the canvas.
	"""
	def __init__(self,popup):
		"""
		"""
		self.popup = popup
		self.objects = []

	def add_new_object(self,obj):
		"""
		Adds objects to the list of objects.
		"""
		self.objects.append(obj)

	def get_selected_objects(self):
		"""
		Returns the reference of the selected objects
		"""
		selected_objects = []
		for obj in self.objects:
			if obj.selected:
				selected_objects.append(obj)

		return(selected_objects)

	def get_selected_objects_list(self):
		"""
		"""
		selected_objects = []
		for i,obj in enumerate(self.objects):
			if obj.selected:
				selected_objects.append(i)

		return(selected_objects)

	def unselect_all_objects(self):
		"""
		Unselects all the objects
		"""
		for obj in self.objects:
			obj.set_selection_off()

	def get_list_of_objects(self):
		"""
		Returns a list with the bboxes and names of the canvas
		"""
		bboxes = []
		for obj in self.objects:
			coord = obj.get_coord()
			name = obj.get_name()
			bbox = [int(coord[0]),int(coord[1]),int(coord[2]),int(coord[3]),name]
			bboxes.append(bbox)

		return(bboxes)

	def modify_selected_objects(self):
		"""
		Modify the name of the selected object
		"""
		objects = self.get_selected_objects()
		for obj in objects:
			self.popup.pop(obj)

	def destroy_selected_objects(self):
		"""
		Destroys and deletes selected objects
		"""
		selected_obj = self.get_selected_objects_list()

		for i in selected_obj[::-1]:
			self.objects[i].destroy()
			del self.objects[i]

	def destroy_all(self):
		"""
		Destroys all objects in the canvas
		"""
		for obj in self.objects:
			obj.destroy()

		self.objects = []

class ImageFrame(Frame):
	"""
	Frame with the canvas where the images and all the 
	other objects will be displayed.
	"""
	def __init__(self,root=None,main=False,obj_tracker=None,
		default_name='New_Object',frame_name='Image Frame'):
		"""
		Args:
		  - root ():
		  - main (bool): Indicates if it is the main frame.
		  - obj_tracker (ObjectsTracker): Container of all objects
		  - popup (PopUp): PopUp frame used to change the name of 
		      objects.
		  - default_name (str): Default name of the objects.
		  - frame_name (str): Name of the ImageFrame frame that will 
		      appear in the top of the window.
		"""
		super().__init__(root,main,frame_name)

		self.default_name = default_name

		# Referene to the original list of coord used for each object
		self.original_objs_data = None

		# External objects
		self.obj_tracker = obj_tracker

		# Flags for external use
		self.FLAG_NEXT = False
		self.FLAG_PREV = False
		self.FLAG_SAVE = False

		# For temporal rectangle
		self.tmp_rectangle = None
		self.prev_mouse_pos = None

		# Creates content
		self.create_content()

	def create_content(self):
		"""
		Creates the content of the whole window
		"""
		# Define the default shape of the canvas when no image is loaded
		shape = (480,640) # [height,width]

		# Creates the canvas where everything will be displayed
		self.canvas = tk.Canvas(self.frame,width=shape[1],height=shape[0],
			bg='black')

		# Positions the canvas wrt the grid
		self.canvas.grid(row=0,column=0)

		# Creates a black image. Not actually needed at this point due to
		# bg='black' parameter at self.canvas. But it will come in handy
		# to allow us to create an image object that we can modify
		im = np.zeros(shape)

		# Converst the image to a format that tkinter can handle
		self.im_data = ImageTk.PhotoImage(image=Image.fromarray(im))

		# Initialize the image in the canvas
		self.image = self.canvas.create_image(0,0,anchor=tk.NW,image=self.im_data)

		# Fixes frame size
		self.frame.resizable(width=False, height=False)

		# Bind mouse interactions to reactions
		self.canvas.tag_bind(self.image,'<Button-1>',self.__object_clicked)
		self.canvas.tag_bind(self.image,'<ButtonRelease-1>',self.__object_unclicked)
		self.canvas.tag_bind(self.image,'<B1-Motion>',self.__object_moving)

		# Bind keyboard interactions to reactions
		self.frame.bind('a',self.__add)
		self.frame.bind('m',self.__modify)
		self.frame.bind('x',self.__remove)
		self.frame.bind('s',self.__save)
		self.frame.bind('r',self.__reset)
		self.frame.bind('n',self.__next)
		self.frame.bind('p',self.__previous)
		self.frame.bind('q',self._on_closing_keyboard)


	def __object_clicked(self,event):
		"""
		Reaction when the canvas is clicked.
		"""
		self.prev_mouse_pos = np.array([event.x,event.y])

	def __object_unclicked(self,event):
		"""
		Reaction when the canvas is unclicked.
		"""
		# Destroy the tmp_rectangle if the canvas was clicked and
		# unclicked at the same position
		if (self.tmp_rectangle is not None and 
			self.prev_mouse_pos[0]-event.x==0 and
			self.prev_mouse_pos[1]-event.y==0):
			
			self.tmp_rectangle.destroy()
			self.tmp_rectangle = None
		
		# Deselect all objects if the canvas was clicked and uncliked
		if (self.prev_mouse_pos[0]-event.x==0 and
			self.prev_mouse_pos[1]-event.y==0):

			self.obj_tracker.unselect_all_objects()

		# Erase the previous mouse position
		self.prev_mouse_pos = None

	def __object_moving(self,event):
		"""
		Reaction when the mouse is clicked and moving
		"""
		# Creates temporal rectangle
		self.__tmp_rectangle_creation(event)

	def __tmp_rectangle_creation(self,event):
		"""
		Handles the creation of the temporal rectanlge
		Args:
		  - event ():
		"""
		# In order to have a smooth animation, destroy 
		# the previous tmp_rectangle
		if self.tmp_rectangle is not None:
			self.tmp_rectangle.destroy()

		# Order the tmp_rectangle coord so they are in the following
		# format: [x_min,y_min,x_max,y_max]
		coord = [0,0,0,0]

		# For horizontal coord
		if self.prev_mouse_pos[0]>event.x:
			coord[0] = event.x
			coord[2] = self.prev_mouse_pos[0]
		else:
			coord[2] = event.x
			coord[0] = self.prev_mouse_pos[0]

		# For vertical coord
		if self.prev_mouse_pos[1]>event.y:
			coord[3] = event.y
			coord[1] = self.prev_mouse_pos[1]
		else:
			coord[1] = event.y
			coord[3] = self.prev_mouse_pos[1]

		# Ensure that the rectangle is inside the canvas
		canvas_shape = [self.canvas.winfo_width(),self.canvas.winfo_height()]
		canvas_shape = np.array(canvas_shape)

		# If we are trying to move ouside the right limit
		if coord[2]>(canvas_shape[0]-1):
			coord[2] = canvas_shape[0]-1

		# If we are trying to move ouside the bottom limit
		if coord[3]>(canvas_shape[1]-1):
			coord[3] = canvas_shape[1]-1

		# If we are trying to move ouside the left limit
		if coord[0]<0:
			coord[0] = 0

		# If we are trying to move ouside the top limit
		if coord[1]<0:
			coord[1] = 0

		# Create a new tmp_rectangle
		self.tmp_rectangle = Rectangle(self.canvas,coord,name=self.default_name)

	def __add(self,event):
		"""
		Adds the tmp_rectangle to the object tracker
		"""
		self.add_tmp_rectangle()

	def add_tmp_rectangle(self):
		"""
		"""
		if self.tmp_rectangle is not None:
			self.obj_tracker.add_new_object(self.tmp_rectangle)
		self.tmp_rectangle = None

	def __modify(self,event):
		"""
		Modify the name of the selected object
		"""
		#objects = self.obj_tracker.get_selected_objects()
		#for obj in objects:
		#	self.popup.pop(obj)
		self.obj_tracker.modify_selected_objects()

	def __remove(self,event):
		"""
		Removes objects from the canvas
		"""
		self.obj_tracker.destroy_selected_objects()

	def __save(self,event):
		"""
		Saves labels
		"""
		self.set_save_image_on()

	def __reset(self,event):
		"""
		Resets the objects in the canvas to the original ones that where loaded
		at first with the image.
		"""
		self.obj_tracker.destroy_all()

	def __next(self,event):
		"""
		"""
		self.set_next_image_on()

	def __previous(self,event):
		"""
		"""
		self.set_prev_image_on()

	def _on_closing_keyboard(self,event):
		"""
		Closes the window form keyboard
		"""
		self._on_closing()

	def set_next_image_on(self):
		"""
		"""
		self.FLAG_NEXT = True

	def set_next_image_off(self):
		"""
		"""
		self.FLAG_NEXT = False

	def set_prev_image_on(self):
		"""
		"""
		self.FLAG_PREV = True

	def set_prev_image_off(self):
		"""
		"""
		self.FLAG_PREV = False

	def set_save_image_on(self):
		"""
		"""
		self.FLAG_SAVE = True

	def set_save_image_off(self):
		"""
		"""
		self.FLAG_SAVE = False

	def set_new_data(self,im,objs=None):
		"""
		Displays new data into the canvas
		Args:
		  im (np.ndarray): Canvas Image
		  objs (None|list): List of coordenates of rectangles with
		    format [x_min,y_min,x_max,y_max]. If None, it will ignore
		    the drawing of objects method.
		"""
		self.set_image_on_canvas(im)
		self.original_objs = objs
		if objs is not None:
			self.draw_new_objects(objs)

	def set_image_on_canvas(self,im):
		"""
		Converst the image to a format that tkinter can handle
		"""
		# Get shape of the image
		self.shape = (im.shape[0],im.shape[1])
		
		# Change the size of the canvas to fit new image
		self.canvas.config(height=self.shape[0],width=self.shape[1])
		
		# Convert the image into a format that tkinter can handle
		self.im_data = ImageTk.PhotoImage(image=Image.fromarray(im))
		
		# Initialize the image in the canvas
		self.canvas.itemconfig(self.image,image=self.im_data)

	def draw_new_objects(self,objs):
		"""
		Adds new objects to the canvas.
		Args:
		  objs (list): Lost of coordenates of the rectangles with
		    format [x_min,y_min,x_max,y_max]
		"""
		self.obj_tracker.destroy_all()
		for obj in objs:
			self.obj_tracker.add_new_object(Rectangle(self.canvas,obj,obj[-1]))

class LabelObject:
	def __init__(self,tree,obj,obj_tracker):
		"""
		"""
		self.tree = tree
		#self.obj = copy(obj)
		self.obj = obj
		print(id(self.obj))
		self.obj_tracker = obj_tracker
		self.tree_object = self.tree.insert('',tk.END,text=obj.get_name())
		self.tree.bind('<Double-1>',self.__double_clicked)

	def __double_clicked(self,event):
		"""
		"""
		obj_id = self.tree.identify('item', event.x, event.y)
		print(obj_id)
		print(id(self.obj))
		print(self.obj.get_name())
		#self.edit(self.tree.selection()[0])
		self.obj.set_selection_on()
		self.obj_tracker.modify_selected_objects()

	def get_object_id(self):
		# Returns the object id str. E.G. 'I001'
		return(self.tree_object.title())

	def remove(self):
		obj_id = self.tree_object.title()
		self.tree.delete(obj_id)


class LabelsFrame(Frame):
	def __init__(self,root=None,main=False,obj_tracker=None,
		multi_files=False,default_name='New_Object',frame_name='Labels Frame'):
		"""
		"""
		super().__init__(root,main,frame_name)
		
		self.default_name = default_name
		
		# Tree names container
		self.objects = []

		# External Objects
		self.obj_tracker = obj_tracker

		# Flags
		self.FLAG_SAVE = False
		self.FLAG_NEXT = False
		self.FLAG_PREV = False
		self.FLAG_ADD = False # Add tmp rectangle
		self.FLAG_REMOVE = False

		self.create_content(multi_files)

	def create_content(self,multiple=False):
		"""
		"""
		# DisplaysCreates a list/Treeview to display all the labels
		self.tree = ttk.Treeview(self.frame)
		self.tree.grid(row=1,column=1,rowspan=4)

		# Adds buttons
		self.btn_add = tk.Button(self.frame,text='Add',command=self.__add)
		self.btn_modify = tk.Button(self.frame,text='Edit',command=self.__modify)
		self.btn_save = tk.Button(self.frame,text='Save',command=self.__save)
		self.btn_remove = tk.Button(self.frame,text='Remove',command=self.__remove)

		# Keyboard binding
		self.frame.bind('a',self.__add_keyboard)
		self.frame.bind('m',self.__modify_keyboard)
		self.frame.bind('s',self.__save_keyboard)
		self.frame.bind('x',self.__remove_keyboard)

		# Configure shape
		self.btn_add.config(height=2,width=10)
		self.btn_remove.config(height=2,width=10)
		self.btn_modify.config(height=2,width=10)
		self.btn_save.config(height=2,width=10)

		self.btn_add.grid(row=1,column=3)
		self.btn_modify.grid(row=2,column=3)
		self.btn_save.grid(row=3,column=3)
		self.btn_remove.grid(row=4,column=3)

		if multiple:
			self.btn_next = tk.Button(self.frame,text='Next',command=self.__next)
			self.btn_prev = tk.Button(self.frame,text='Prev',command=self.__prev)
			self.btn_next.config(height=2,width=10)
			self.btn_prev.config(height=2,width=10)
			self.btn_next.grid(row=5,column=3)
			self.btn_prev.grid(row=6,column=3)

			self.frame.bind('n',self.__next_keyboard)
			self.frame.bind('p',self.__prev_keyboard)

	def __add(self):
		"""
		"""
		self.set_add_bbox_on()

	def __modify(self):
		"""
		Modify the name of the selected object
		"""
		self.obj_tracker.modify_selected_objects()

	def __save(self):
		"""
		"""
		self.set_save_image_on()

	def __remove(self):
		"""
		"""
		self.obj_tracker.destroy_selected_objects()

	def __next(self):
		"""
		"""
		self.set_next_image_on()

	def __prev(self):
		"""
		"""
		self.set_prev_image_on()

	def __add_keyboard(self,event):
		"""
		"""
		self.__add()

	def __modify_keyboard(self,event):
		"""
		Modify the name of the selected object
		"""
		self.__modify()

	def __save_keyboard(self,event):
		"""
		"""
		self.__save()

	def __remove_keyboard(self,event):
		"""
		"""
		self.__remove()

	def __next_keyboard(self,event):
		"""
		"""
		self.__next()

	def __prev_keyboard(self,event):
		"""
		"""
		self.__prev()

	def set_add_bbox_on(self):
		"""
		"""
		self.FLAG_ADD = True

	def set_add_bbox_off(self):
		"""
		"""
		self.FLAG_ADD = False

	def set_next_image_on(self):
		"""
		"""
		self.FLAG_NEXT = True

	def set_next_image_off(self):
		"""
		"""
		self.FLAG_NEXT = False

	def set_prev_image_on(self):
		"""
		"""
		self.FLAG_PREV = True

	def set_prev_image_off(self):
		"""
		"""
		self.FLAG_PREV = False

	def set_save_image_on(self):
		"""
		"""
		self.FLAG_SAVE = True

	def set_save_image_off(self):
		"""
		"""
		self.FLAG_SAVE = False

	def draw_names(self):
		"""
		Draw the name of all the objects in the tree
		"""
		for obj in self.obj_tracker.objects:
			print(obj.get_name())
			self.objects.append(LabelObject(self.tree,copy(obj),self.obj_tracker))

	def remove_names(self):
		# Removes all objects from the frame
		for obj in self.objects:
			# Remove all objects from treeview
			obj.remove()

			#obj_id = obj.get_object_id()
			#if obj_id not in self.removed_objects_id:
			#	# Make sure it hasn't been erased before
			#	obj.remove()

		self.objects = []


class MainGUI:
	"""
	Primary class that ensembles everything.
	"""
	def __init__(self,lbs_saver='txt',lbs_loader='txt',multi_files=False):
		"""
		Args:
		  - lbs_saver (str): What file formate to save.
		  - lbs_loader (str): What file format to load.
		  - multi_files (bool): Indicates if multiple files will be 
		      displayed
		"""
		self.root = tk.Tk()

		self.multi_files = multi_files

		self.frame_closed = False

		self.create_content()

		if lbs_saver=='txt':
			self.lbs_saver = ut_lbs.bboxes_saver_txt_kitti
		elif callable(lbs_saver):
			self.lbs_saver = lbs_saver
		else:
			warnings.warn('Saver not found. Using txt insted')
			self.lbs_saver = ut_lbs.bboxes_saver_txt_kitti

		if lbs_loader=='txt':
			self.lbs_loader = ut_lbs.bboxes_loader_txt_kitti
		elif callable(lbs_loader):
			self.lbs_loader = lbs_loader
		else:
			warnings.warn('Loader not found. Using txt insted')
			self.lbs_loader = ut_lbs.bboxes_loader_txt_kitti

	def create_content(self):
		"""
		"""
		self.popup = PopUp2(self.root)
		self.objects = ObjectsTracker(popup=self.popup)
		self.im_frame = ImageFrame(self.root,main=True,obj_tracker=self.objects)
		self.lbs_frame = LabelsFrame(self.root,obj_tracker=self.objects)
		self.lbs_frame.hide()

	def run(self,im_path,lbs_path=None):
		"""
		"""
		# Load the image
		im = cv2.imread(im_path)[...,::-1]
		# Load the label
		if lbs_path is not None:
			lbs = self.lbs_loader(lbs_path) # Load labels
		else:
			# Find the last point in the string
			ind = im_path[::-1].find('.')
			# Replace whatever extention it has to txt
			lbs_path = im_path[:-ind]+'txt'
			print('Labels saving path not defined. Using:',lbs_path)

		self.im_frame.set_new_data(im,lbs)
		#self.lbs_frame.draw_names()

		while True:
			if self.im_frame.frame_closed or self.lbs_frame.frame_closed:
				self.frame_closed = True
				break

			if (self.multi_files and (self.im_frame.FLAG_NEXT or
				self.lbs_frame.FLAG_NEXT)):

				self.im_frame.set_next_image_off()
				self.lbs_frame.set_next_image_off()
				break

			if (self.multi_files and (self.im_frame.FLAG_PREV or
				self.lbs_frame.FLAG_PREV)):
				
				self.im_frame.set_prev_image_off()
				self.lbs_frame.set_prev_image_off()
				break

			if self.im_frame.FLAG_SAVE or self.lbs_frame.FLAG_SAVE:
				print('Saving at',lbs_path)
				objs = self.objects.get_list_of_objects()
				self.lbs_saver(lbs_path,objs)

				self.im_frame.set_save_image_off()
				self.lbs_frame.set_save_image_off()

			if self.lbs_frame.FLAG_ADD:
				self.im_frame.add_tmp_rectangle()
				self.lbs_frame.remove_names()
				self.lbs_frame.draw_names()

			self.root.update_idletasks()
			self.root.update()



if __name__=='__main__':
	im_path = '../dog.jpg'
	lbs_path = '../tst_lbl001.txt'
	gui = MainGUI()
	gui.run(im_path,lbs_path)