import numpy as np
import matplotlib.pyplot as plt

x = np.linspace( -2000, -1500, 40 ) 
y = np.linspace( -500, 500, 40 )

ax = plt.axes()
ax.hist2d( x, y )

plt.show()
