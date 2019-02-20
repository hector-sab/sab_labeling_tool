import os
import xml.etree.ElementTree as ET

def bboxes_loader_xml_imagenet(path,args=None):
	"""
	Loads bbox labels in the xml format.
	
	Args 
	  args (tuple): Not needed. If provided:
	    args[0] (tuple): Shape of the image 
	      from where the labels where taken.
	      (height,width)
	    args[1] (tuple): Shape of the desired 
	      image  where the labels will be placed.
	      (height,width)

	Returns:
	  bboxes (list): A list containing lists which represent
	    individual objects. Its format is:
	      [[x_left,y_top,x_right,y_bottom,label]]
	    and the data type is:
	      [int,int,int,int,str]
	"""

	if not os.path.exists(path):
		return(None)

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
	"""
	Load bboxes from txt files with the kitti format.
	
	Args:
	  - path (str): Location of the file.
	  - args (tuple): Not needed. If provided:
	      args[0] (tuple): Shape of the image 
	        from where the labels where taken.
	        (height,width)
	      args[1] (tuple): Shape of the desired 
	        image  where the labels will be placed.
	        (height,width)
	
	Returns:
	  - bboxes (list): A list containing lists which represent
	      individual objects. Its format is:
	        [[x_left,y_top,x_right,y_bottom,label]]
	      and the data type is:
	        [int,int,int,int,str]
	"""
	if not os.path.exists(path):
		return(None)

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
	"""
	Saves bboxes to a file with the kitti format.
	
	Args:
	  path (str): Name and location where the file will be placed.
	  bboxes (tuple|list|np.ndarray): [[x_left,y_top,x_right,y_bottom,class_name]]
	"""
	line = '{} 0.0 0 0.0 {} {} {} {} 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
	if len(bboxes)>0:
		with open(path,'w') as f:
			for i,bbox in enumerate(bboxes):
				f.write(line.format(bbox[4],int(bbox[0]),int(bbox[1])
					,int(bbox[2]),int(bbox[3])))
				if i<len(bboxes)-1:
					f.write('\n')
