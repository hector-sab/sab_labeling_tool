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

class ImageFrame(Frame):
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

if __name__=='__main__':
	imFrame = ImageFrame(main=True)

	while True:
		# Update GUI
		imFrame.root.update_idletasks()
		imFrame.root.update()