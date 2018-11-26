from sab_labeling_tool import SABLabelingTool
from sab_labeling_tool import SABLabelingToolMainGUI
from sab_labeling_tool import SABLabelingToolMainGUI2

if __name__=='__main__':
	if True:
		# For one image
		main = SABLabelingToolMainGUI2()
		im_path = 'dog.jpg'
		lbs_path = 'tst_lbl001_cp.txt'
		main.load_data(im_path,lbs_path)

		main.run()
	else:
		# For multiple images
		lt = SABLabelingTool()

		im1_path = 'dog.jpg'
		im2_path = 'cat.jpg'
		lbs_path = 'tst_lbl001_cp.txt'

		im_paths = [im1_path,im2_path,im1_path,im2_path]
		lb_paths = [lbs_path,lbs_path,lbs_path,lbs_path]

		lt.run(im_paths,lb_paths)