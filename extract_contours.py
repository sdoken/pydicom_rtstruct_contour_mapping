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


# Extracting the Pixels that Fall Within
temp_list = []
for a, b in zip(x_pixel_nos, y_pixel_nos):
   temp_list.append([a, b])

polygon = np.array(temp_list)
left = np.min(polygon, axis=0)
right = np.max(polygon, axis=0)
x = np.arange(math.ceil(left[0]), math.floor(right[0]) + 1) 
y = np.arange(math.ceil(left[1]), math.floor(right[1]) + 1)

xv, yv = np.meshgrid(x, y, indexing='xy')
points = np.hstack((xv.reshape((-1,1)), yv.reshape((-1,1))))

path = matplotlib.path.Path(polygon)
mask = path.contains_points(points)

x_coords_of_points_within_contours = points[mask, 0]
y_coords_of_points_within_contours = points[mask, 1]


plt.figure()
plt.imshow(pixel_array, cmap='bone')
#plt.plot(x_pixel_nos, y_pixel_nos, color='r')
plt.plot(x_coords_of_points_within_contours, 
         y_coords_of_points_within_contours, color='g')
#plt.plot(y_coords_of_points_within_contours, 
plt.figure()
plt.show()

#find average pixel brightness inside contours
#create a matrix so that when you multiply element by element it shows
pixel_list = []
for x_coord, y_coord in zip(x_coords_of_points_within_contours,
                            y_coords_of_points_within_contours):
    pixel_list.append([x_coord, y_coord])

mask_array = np.zeros([512,512])

for element in pixel_list:
    mask_array[element[0], element[1]] = 1

print(mask_array.sum().sum())


pixel_list = np.array(pixel_list)

just_the_roi_array = np.multiply(mask_array, pixel_array)

print(just_the_roi_array.sum().sum()/mask_array.sum().sum())

plt.figure()
plt.imshow(pixel_array, cmap='bone')
plt.plot(x_pixel_nos, y_pixel_nos, color='r')
plt.figure()
plt.show()


