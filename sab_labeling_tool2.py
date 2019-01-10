import os
import cv2
import numpy as np
 
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import xml.etree.ElementTree as ET

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

class ImageFrame(Frame):
	def __init__(self,root=None,main=True,name='Image Frame'):
		super().__init__(root,main,name)

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

class PopUp(Frame):
	def __init__(self,root=None,main=False,name='Pop Up'):
		super().__init__(root,main,name)

		# Set focus only on the pop up. Disable all other
		# windows while the popup is open
		self.frame.wait_visibility()
		self.frame.grab_set()
		self.create_content()
		self.set_initial_position()

	def create_content(self):
		self.entry = tk.Entry(self.frame)
		self.entry.grid(row=1,column=1)

		self.btn_ok = tk.Button(self.frame,text='Ok')

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

class LabelsFrame(Frame):
	def __init__(self,root=None,main=True,name='Labels Frame'):
		super().__init__(root,main,name)

		self.create_content()

	def create_content(self):
		self.tree = ttk.Treeview(self.frame)
		self.tree.grid(row=1,column=1,rowspan=4)
		
		self.entry = tk.Entry(self.frame)
		self.entry.grid(row=1,column=2)

		self.tree.insert('',tk.END,text='Person1')
		self.tree.insert('',tk.END,text='Person2')
		self.tree.insert('',tk.END,text='Person3')

		self.tree.bind('<Double-1>',self.test_click)
		

	def test_click(self,event):
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
		popup = PopUp(self.root)
		print(popup)
		


class SABLabelingToolMainGUI:
	def __init__(self,def_class=None,lb_loader_fmt='txt',main=True):
		# Args:
		#    def_class (str): Name of the default class.
		#    lb_loader_fmt (str): Function to load files. The two available
		#        options as of right now are:
		#           - 'txt': Found on KITTI database.
		#           - 'xml': Found on ImageNet database.
		#    main (bool): Indicate if it is the main window or if 
		#        something else is controlling it.
		
		self.main = main

		# Creates root
		self.root = tk.Tk()

		# Creates content
		self.create_content()

	def create_content(self):
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
		self.lbsFrame = LabelsFrame(self.root,main=False)
		self.lbsFrame.frame.update()
		iml_width = self.lbsFrame.frame.winfo_width()
		iml_height = self.lbsFrame.frame.winfo_height()
		x = int(screen_width/2) + int(imf_width/2)
		self.lbsFrame.set_frame_location(x,y)


	def run(self):
		# Runs the main loop needed for the GUI to work
		while True:
			# Checks the destruction of the frames
			if self.imFrame.close_frame or self.lbsFrame.close_frame:
				break

			# Update GUI
			self.root.update_idletasks()
			self.root.update()

if __name__=='__main__':
	lbt = SABLabelingToolMainGUI()
	lbt.run()