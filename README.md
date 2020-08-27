# MicroAutoScale
Automatically adds scale bars to a batch of images.

The purpose of this program is to take a bunch of images taken with a microscope and add scales. It can save a lot of time when compared to manually editing each image to make sure it has the correct scale.

## Instructions

The program should be simple to use. Open with the Python 3.x interpreter and follow the GUI.

The input folder is where the images will be pulled from. It defaults to the folder that the program is found in. The user can change this folder either by manually writing the name of the desired folder, or by using the file browser (by pressing the Browse... button). By default, subfolders are not checked for images; this can be changed by checking the "Also edit files in subfolders" checkbox.

The files are saved with the same name as the input file, but with \_with_scale added to the end of the file. As a convenience to the user, files with \_with_scale in the filename will not be altered. By default, the files are saved in the same folder as the input files, but this can be changed in the Output Folder field. An option was also added to rename all files to only use lowercase characters for some internal usage; this setting changes all uppercase characters to lowercase. Numbers and special characters are not affected.

Once the input folder is set, the detected files will be present in the list below the folder settings. If no files are visible, double check the input folder and make sure that the "Also edit files in subfolders" is checked, if appropriate. For each file, there are a number of settings that can be changed. These are:
  * Do: Convert file. If the checkbox is unchecked, the file will be skipped during conversion.
  * File: The file name; not editable.
  * Zoom: Can choose either 10x, 50x, 100x or Custom. The first three are only really appropriate to the camera of our specific laboratory. These will automatically change the Pixel Per Unit value to a preset value. Custom allows the user to define the Pixels Per Unit manually.
  * Pixel Per Unit: How many pixels are in each unit of length. Typically this is found through a calibration image.
  * Bar size: How many units the scale bar will have. Defaults to 50 units.
  * Unit: The unit of measurement to be used. Defaults to micrometer. As a convenience to the user, "um" is automatically replaced by the micrometer sign.
  
At the bottom of the screen, there are a few buttons. The "Copy Settings to Other Files" button takes the settings of the selected file (files can be selected by clicking on them in the list) and applies them to all the other images. The "Select All" button enables the "Do" field on all images, while "Select None" disables the "Do" field on all images (to more easily add scale to a single image in a large list, for instance).

The "Refresh" button at the right of the image list refreshes the file view (in case there were changes to the files). When manually writing the input directory, the user must press this button to update the image list.

Finally, the "Add Scales" button adds scales to all selected images according to the chosen settings.

## Scalability

Some very questionable design decisions are explained by attempts to make the program as simple to use and specific as possible. That is, the original purpose was not to design a program that would do this for every possible image format with every possible setting being editable by the user; instead, the purpose was to allow the members of a specific laboratory to add scales to their images as quickly as possible, with the least amount of steps between opening the program and adding scales. This means that other groups will need to tweak the default values in order to get an easy to use program.

The code is presented as a single .py file, as we want to reduce the program's apparent complexity to users, which may not be tech literate, while retaining inter-platform compatibility.

The default amplification values (pixel per unit) are for the specific microscope available at my lab (which I am not allowed to reveal), which will be different for different setups. These default values are present at the top of the code, as ZOOM_10X, ZOOM_50X and ZOOM_100X. Since the setup we use had 3 different objectives (10x, 50x and 100x respectively), it is common for members of this lab to label their images accordingly; e.g. sample_x10.jpg or sample_50x.jpg. Therefore, when reading the file list the program will automatically check for the strings 'x10', 'x50', 'x100', '10x', '50x' and '100x' and will automatically set the scale of the image to the appropriate value. The user is then free to change the scales manually before performing edits on the images.


## Requirements

Python 3.x is required. Tested with Python 3.7.3.

Requirements.txt file available.

Requires PyQt 5 (>= 5.13.2) and Pillow (>= 6.2.1).
