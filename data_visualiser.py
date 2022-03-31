import matplotlib.pyplot as plt   
from csv import reader, writer
import numpy as np 

file_name = 'data/BL4N-STY1-00x12x80-0x2x5-220331-1304.csv'

if __name__ == '__main__':
    with open(file_name, 'r') as file:
        csv_reader = reader(file)
        header = next(csv_reader)

        xs = []
        zs = []
        mags = []

        for row in csv_reader:
            if len(row) == 6:
                print(row)
                x,y,z,r,d,g = row
                xs.append(x)
                zs.append(z)
                mags.append(d)

        xs = np.array(xs)
        zs = np.array(zs)
        mags = np.array(mags)
        
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(xs,zs,mags)
        plt.show()


