import matplotlib.pyplot as plt   
import matplotlib
from csv import reader, writer
import numpy as np 
from scipy.interpolate import griddata

file_name = 'data/BL4N-STY1-00x12x80-0x2x5-220331-1304.csv'

if __name__ == '__main__':
    with open(file_name, 'r') as file:
        csv_reader = reader(file)
        header = next(csv_reader)

        points = []
        mags = []

        for row in csv_reader:
            if len(row) == 6:
                print(row)
                x,y,z,r,d,g = row
                points.append([float(x),float(z)])
                mags.append(float(d))

        points = np.array(points)
        xs = points[:,0]
        zs = points[:,1]

        min_x = np.amin(xs)
        max_x = np.amax(xs)
        min_z = np.amin(zs)
        max_z = np.amax(zs)

        mags = np.array(mags)
        print(points.size)
        print(mags.size)

        print(np.amax(mags))
        grid_x, grid_y = np.mgrid[min_x:max_x:40j, min_z:max_z:6j]

        grid = griddata(points, mags, (grid_x,grid_y), method='cubic')[10:-10,:].T

        font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}
        matplotlib.rc('font', **font)
        
        plt.title("Magnetic Field Mapping")
        plt.xlabel("Distance (cm)")
        plt.ylabel("Distance (cm)")
        im = plt.imshow(grid)
        im_ratio = grid.shape[0]/grid.shape[1]
        cbar = plt.colorbar(im,fraction=0.046*im_ratio, pad=0.04)
        cbar.ax.set_ylabel("Magnetic Field Strength (Gauss)")
        plt.show()
        # plt.tricontour(xs,zs,mags, levels=14)
        # plt.show()
        # fig = plt.figure()
        # ax = fig.add_subplot(projection='3d')
        # ax.scatter(xs,zs,mags)
        # plt.show()


