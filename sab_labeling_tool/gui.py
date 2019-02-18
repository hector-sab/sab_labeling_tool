import cv2
import warnings
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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
		self.selected = True

	def set_selection_off(self):
		"""
		"""
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

	def destroy(self):
		"""
		Destroy the object
		"""
		self.canvas.delete(self.draw)


class ImageFrame(Frame):
	"""
	"""
	def __init__(self,root=None,main=False,name='Image Frame'):
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

		self.canvas.tag_bind(self.image,'<Button-1>',self.__image_pressed)

	def __image_pressed(self,event):
		print('Canvas Pressed')
		#Point(self.canvas,[200,200],mode='v-edge')
		Rectangle(self.canvas,[200,200,400,400])

	def load_new_data(self,im,objs):
		# 
		self.set_new_image_on_canvas(im)
		self.draw_new_objects(objs)

	def set_new_image_on_canvas(self,im):
		# Converst the image to a format that tkinter can handle
		self.shape = (im.shape[0],im.shape[1])
		self.canvas.config(height=im.shape[0],width=im.shape[1])
		self.im_data = ImageTk.PhotoImage(image=Image.fromarray(im))
		# Initialize the image in the canvas
		self.canvas.itemconfig(self.image,image=self.im_data)

	def draw_new_objects(self,objs):
		for obj in objs:
			self.objects.append(Rectangle(self.canvas,obj))

		#print(self.objects[0].object.cget("text"))

if __name__=='__main__':
	im_path = '../dog.jpg'
	im = cv2.imread(im_path)[...,::-1]

	imFrame = ImageFrame(main=True)
	imFrame.set_new_image_on_canvas(im)

	while True:
		# Update GUI
		imFrame.root.update_idletasks()
		imFrame.root.update()