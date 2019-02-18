import cv2
import warnings
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# TODO: Re-write the PopUp method

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

class PopUp(Frame):
	# Pop Up object that will be reused instead of being
	# complitly destroyed each time it's closed.
	def __init__(self,root=None,main=False,name='Pop Up'):
		"""
		Args:
		  root ():
		  main ():
		"""
		self.root = root; self.main = main; self.name = name
		self.bbox_label = ''
		self.tmp_bbox_label = self.bbox_label

		self.edited_object = None

	def create_content(self):
		"""
		"""
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

	def pop(self,obj,text=''):
		"""
		"""
		self.create_content()

		self.frame.bind('<Return>',self._ok_keyboard)
		self.frame.bind('<Escape>',self._cancel_keyboard)
		
		self.edited_object = obj
		self.change_bbox_label(self.edited_object.name)
				
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
		self.edited_object.name = self.tmp_bbox_label
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
		print('Rectangle Pressed')
		self.set_selection_on()
		self.previous_mouse_possition = np.array([event.x,event.y])

	def __object_unclicked(self,event):
		"""
		"""
		print('Rectangle unPressed')
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


class ImageFrame(Frame):
	"""
	"""
	def __init__(self,root=None,main=False,name='Image Frame',
		def_rect_name='New_Object',popup=None):
		"""
		Args:
		  root ():
		  main (bool): Indicates if this is the main Frame.
		  name (str): Name of the frame.
		  def_rect_name (str): Default rectangles name.
		  popup (PopUp): Pop Up window
		"""
		super().__init__(root,main,name)
		self.objects = [] # Contains all the rectangles
		self.previous_mouse_possition = None #[x,y]
		self.tmp_rectangle = None
		self.popup = popup

		# Original coord of the rectangles when first loaded
		self.original_objs = None 

		# Functionality for the main GUI
		self.FLAG_NEXT = False 
		self.FLAG_PREV = False

		self.def_rect_name = def_rect_name

		self.create_content()

	def create_content(self):
		"""
		Creates all the content of the image frame
		"""
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

		# Fixes frame size
		self.frame.resizable(width=False, height=False)

		#self.canvas.tag_bind(self.image,'<Button-1>',self.__image_pressed)

		self.canvas.tag_bind(self.image,'<Button-1>',self.__object_clicked)
		self.canvas.tag_bind(self.image,'<ButtonRelease-1>',self.__object_unclicked)
		self.canvas.tag_bind(self.image,'<B1-Motion>',self.__object_moving)

		# Standard binds across Frames
		self.frame.bind('a',self.__add)
		self.frame.bind('m',self.__modify)
		self.frame.bind('x',self.__remove)
		self.frame.bind('r',self.__reset)
		self.frame.bind('n',self.__next)
		self.frame.bind('p',self.__previous)

	def __object_clicked(self,event):
		"""
		"""
		print('Canvas Pressed')
		self.previous_mouse_possition = np.array([event.x,event.y])

	def __object_unclicked(self,event):
		"""
		"""
		# Destroy the tmp_rectangle if the canvas was clicked and
		# unclicked at the same position
		if (self.tmp_rectangle is not None and 
			self.previous_mouse_possition[0]-event.x==0 and
			self.previous_mouse_possition[1]-event.y==0):
			
			self.tmp_rectangle.destroy()
			self.tmp_rectangle = None
		
		if (self.previous_mouse_possition[0]-event.x==0 and
			self.previous_mouse_possition[1]-event.y==0):

			self.deselect_all_objects()

		# Erase the previous mouse position
		self.previous_mouse_possition = None

	def __object_moving(self,event):
		"""
		"""
		# In order to have a smooth animation, destroy 
		# the previous tmp_rectangle
		if self.tmp_rectangle is not None:
			self.tmp_rectangle.destroy()

		# Order the parameters so they are in the following
		# format: [x_min,y_min,x_max,y_max]
		coord = [0,0,0,0]
		if self.previous_mouse_possition[0]>event.x:
			coord[0] = event.x
			coord[2] = self.previous_mouse_possition[0]
		else:
			coord[2] = event.x
			coord[0] = self.previous_mouse_possition[0]

		if self.previous_mouse_possition[1]>event.y:
			coord[3] = event.y
			coord[1] = self.previous_mouse_possition[1]
		else:
			coord[1] = event.y
			coord[3] = self.previous_mouse_possition[1]

		# Ensure that the rectangle is inside the canvas
		canvas_shape = [self.canvas.winfo_width(),self.canvas.winfo_height()]
		canvas_shape = np.array(canvas_shape)

		if coord[2]>(canvas_shape[0]-1):
			# If we are trying to move ouside the right limit
			coord[2] = canvas_shape[0]-1

		if coord[3]>(canvas_shape[1]-1):
			# If we are trying to move ouside the bottom limit
			coord[3] = canvas_shape[1]-1

		if coord[0]<0:
			# If we are trying to move ouside the left limit
			coord[0] = 0

		if coord[1]<0:
			# If we are trying to move ouside the top limit
			coord[1] = 0

		# Create a new tmp_rectangle
		self.tmp_rectangle = Rectangle(self.canvas,coord,name=self.def_rect_name)

	def __add(self,event):
		"""
		Adds the tmp_rectangle to the list of objects
		"""
		self.objects.append(self.tmp_rectangle)
		self.tmp_rectangle = None
		print('ADD')

	def __modify(self,event):
		"""
		Modify the name of the selected object
		"""
		if self.popup is not None:
			for obj in self.objects:
				if obj.selected:
					self.popup.pop(obj)

		print('MODIFY')

	def __remove(self,event):
		"""
		Removes and objects from the canvas
		"""
		for obj in self.objects:
			if obj.selected:
				obj.destroy()
				obj.set_selection_off()
				obj.set_removed_on()

		print('REMOVE')

	def __reset(self,event):
		"""
		Resets the objects in the canvas to the original ones that where loaded
		at first with the image.
		"""
		self.destroy_all_objects()
		if self.original_objs is not None:
			self.draw_new_objects(self.original_objs)
		print('RESET')
	
	def __next(self,event):
		"""
		"""
		self.set_next_image_on()
		print('NEXT')

	def __previous(self,event):
		"""
		"""
		self.set_prev_image_on()
		print('PREVIOUS')

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

	def deselect_all_objects(self):
		"""
		"""
		for obj in self.objects:
			obj.set_selection_off()

	def load_new_data(self,im,objs=None):
		"""
		Displays new data into the canvas
		Args:
		  im (np.ndarray): Canvas Image
		  objs (None|list): List of coordenates of rectangles with
		    format [x_min,y_min,x_max,y_max]. If None, it will ignore
		    the drawing of objects method.
		"""
		self.set_new_image_on_canvas(im)
		self.original_objs = objs # 
		if objs is not None:
			self.draw_new_objects(objs)

	def set_new_image_on_canvas(self,im):
		"""
		Converst the image to a format that tkinter can handle
		"""
		self.shape = (im.shape[0],im.shape[1])
		self.canvas.config(height=im.shape[0],width=im.shape[1])
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
		self.destroy_all_objects()
		for obj in objs:
			self.objects.append(Rectangle(self.canvas,obj,self.def_rect_name))

		#print(self.objects[0].object.cget("text"))

	def destroy_all_objects(self):
		"""
		Destroy all objects in the canvas.
		"""
		for obj in self.objects:
			obj.destroy()

		self.objects = []

if __name__=='__main__':
	im_path = '../dog.jpg'
	im = cv2.imread(im_path)[...,::-1]

	root = tk.Tk()
	popup = PopUp(root=root)
	imFrame = ImageFrame(root=root,main=True,popup=popup)
	imFrame.load_new_data(im)

	while True:
		# Update GUI
		imFrame.root.update_idletasks()
		imFrame.root.update()