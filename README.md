# Sab Labeling Tool

GUI used for facilitating the labiling of images in python.


## How it works

There's two main classes in ```sab_labeling_tool```: ```SABLabelingTool``` and ```SABLabelingToolMainGUI```.

- ```SABLabelingToolMainGUI```: Contains the main functionality. Is to this class that you are going to provide single paths for your image and label.
- ```SABLabelingTool```: In case you have multiple images, use this class to be able to use the "Next" and "Prev" buttons.

File labels that are accepted right now are just the txt (KITTI) ones.

### Example: Single image
When you provide both, image and label path.

```python
# Creates the GUI object
main = SABLabelingToolMainGUI()

# Indicates paths to be used
im_path = 'dog.jpg'
lbs_path = 'tst_lbl001.txt'

# loads both image and labels
main.load_image_label(im_path,lbs_path)
main.run()
```

**Note 1:** As of today, if ```lbs_path``` does not exists, you only will see a warning that the file does not exists and it will use that path as the path to save the label.

**Note 2:** ```lbs_path``` can be ```None```.

----

When you only provide image path and the expected path for the output label.

```python
# Creates the GUI object
main = SABLabelingToolMainGUI()

# Indicates paths to be used
im_path = 'dog.jpg'
lbs_path = 'tst_lbl001.txt'

# Loads image
main.load_image_label(im_path)

# Sets output path for the labels
main.set_out_label_path(lbs_path)
main.run()
```

### Example: Multiple files
When you have mulptiple files to iterate through.

```python
lt = SABLabelingTool()

im1_path = 'dog.jpg'
im2_path = 'cat.jpg'
lbs_path = 'tst_lbl001.txt'

# Creates toy list of paths
im_paths = [im1_path,im2_path,im1_path,im2_path]
lb_paths = [lbs_path,lbs_path,lbs_path,lbs_path]

lt.run(im_paths,lb_paths)
```

Note that ```im_paths``` and ```lb_paths``` must match in size.

## Things that can be done

- If you click the bbox in the image, it will be selected in the bboxes.
- Remove bounding boxes.

## Thing that cannot be done or need to be implemented

- Allow to change the bbox size from the image.
- Remove dependency of ```OBJECT_LABELS```.
- Allow more label files formats.
- Add a method that allows personalized funtions to load label files.
- Fix scrollbar in the labeling frame.
- Allow drawing rectangles in the image frame.
- Implement the add button to save the rectangles drew.
- Implement the modify/rename label button.