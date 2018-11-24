from sab_labeling_tool import SABLabelingTool
from sab_labeling_tool import SABLabelingToolMainGUI

if __name__=='__main__':
	if False:
		# For one image
		main = SABLabelingToolMainGUI()
		im_path = 'dog.jpg'
		lbs_path = 'tst_lbl001.txt'
		main.load_image_label(im_path,lbs_path)

		main.run()
	else:
		# For multiple images
		lt = SABLabelingTool()

		im1_path = 'dog.jpg'
		im2_path = 'cat.jpg'
		lbs_path = 'tst_lbl001.txt'

		im_paths = [im1_path,im2_path,im1_path,im2_path]
		lb_paths = [lbs_path,lbs_path,lbs_path,lbs_path]

		lt.run(im_paths,lb_paths)