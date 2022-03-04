import numpy as np
import csv

cylinder = True
radius = 50
xy_spacing = 5
depth = 100
z_spacing = 10

# number of columns (= num of rows) under the given radius and spacing
num_cols_half = int(radius/xy_spacing)
num_cols = 2 * num_cols_half + 1

# possible positions of each column
pos_xy = np.arange(-xy_spacing * num_cols_half, xy_spacing * (num_cols_half + 1), xy_spacing)

# Fill all possible x, y values
points_xy = np.zeros([num_cols * num_cols, 2])
index = 0
# Constants for order
order_inc = True
order_dec = False
order = order_inc
for i in range(num_cols):
    if order == order_inc:
        for j in range(0, num_cols, 1):
            x = pos_xy[i]
            y = pos_xy[j]
            # make sure points are within circle
            if (x * x + y * y < radius * radius):
                points_xy[index][0] = x
                points_xy[index][1] = y
                index += 1
    if order == order_dec:
        for j in range(num_cols-1, -1, -1):
            x = pos_xy[i]
            y = pos_xy[j]
            if (x * x + y * y < radius * radius):
                points_xy[index][0]= x
                points_xy[index][1] = y
                index += 1
    # switch increasing/decreasing order for every pass
    order = not(order)

# trim all zeros and get valid point length
points_xy_1D_trim = np.trim_zeros(points_xy.flatten(), trim = 'b')
points_xy = np.reshape(points_xy_1D_trim, (-1, 2))
num_points_xy = len(points_xy)


# possible positions in z direction (going into magnet)
num_z = int(depth/z_spacing) + 1
pos_z = np.arange(0, z_spacing * num_z, z_spacing)

# z direction points
points = np.zeros([num_points_xy * num_z, 3])
index = 0
order = order_inc
for i in range(num_points_xy):
    if order == order_inc:
        for j in range(0, num_z, 1):
            points[index][0] = points_xy[i][0]
            points[index][1] = points_xy[i][1]
            points[index][2] = pos_z[j]
            index += 1
    if order == order_dec:
        for j in range(num_z-1, -1, -1):
            points[index][0] = points_xy[i][0]
            points[index][1] = points_xy[i][1]
            points[index][2] = pos_z[j]
            index += 1
    order = not(order)

header = ['X', 'Y', 'Z', 'Rotation']

with open('path.csv', 'w', encoding='UTF8', newline='') as f:
    f.truncate()
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(points)
    f.close()

