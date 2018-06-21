import math
import numpy as np
import pydicom
import matplotlib.pyplot as plt
import matplotlib.path

def find_correct_image(contoursequence):
    """
    Given an rtstruct.dicom files ROIContourSequence[9].ContourSequence[i],
    return the correct filename (using the UID)
    """
    return uid_to_filename_map[contoursequence.ContourImageSequence[0].ReferencedSOPInstanceUID]


def calculate_image_seq_on_dicompyler(image_no):
    return 136-image_no + 1


def display_scan(filename_text):
    plt.imshow(pydicom.dcmread(filename_text).pixel_array, cmap=plt.cm.bone)


integervalue = 3
'{0:03d}'.format(integervalue) # creates a string 001, 002 etc
image_uids = [] # sop_instance_ids_of_136_scans
uid_to_filename_map = dict()
uid_to_location_map = dict() # 'location' = height
filename = 'data/P1152/P1152_pCT_20140226_'

#Creating map from filename to UID
for i in range(1, 137):
    current_filename = filename + '{0:03d}'.format(i) + '.dcm'
    current_file = pydicom.dcmread(current_filename)
    current_uid = current_file.SOPInstanceUID #str vs int : think about cost
    image_uids.append(current_uid)
    uid_to_filename_map[current_uid] = current_filename
    
#Opening the Image and Corresponding Contour Files
cffas = pydicom.dcmread('data/P1152/P1152_RTStructure_1.dcm')
contour_sequence = cffas.ROIContourSequence[9].ContourSequence[6]
file_of_slice_with_contours = pydicom.dcmread(find_correct_image(contour_sequence))

# Image
pixel_array = file_of_slice_with_contours.pixel_array

# Some Metadata : For Converting Contours to Pixels
pixel_spacing = file_of_slice_with_contours.PixelSpacing
x_gap = pixel_spacing[0]
y_gap = pixel_spacing[1]

image_position_starting_point = file_of_slice_with_contours.\
                                    ImagePositionPatient
x_start = float(image_position_starting_point[0])
y_start = float(image_position_starting_point[0])

# Contours
contours = contour_sequence.ContourData
x_coords_of_contours = [ float(number) for number in contours[0::3] ]
y_coords_of_contours = [ float(number) for number in contours[1::3] ]
x_coords_of_contours = np.array(x_coords_of_contours)
y_coords_of_contours = np.array(y_coords_of_contours)

x_pixel_nos = (x_coords_of_contours-x_start)/x_gap
y_pixel_nos = (y_coords_of_contours-y_start)/y_gap


