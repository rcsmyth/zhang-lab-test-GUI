import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# create empty arrays for time and strain data
time_data = np.array([])
strain_data = np.array([])
strain_rate_data = np.array([])

# create subplots for strain and strain rate
plt.subplot(2, 1, 1)
plt.xlabel('Time [units]')
plt.ylabel('Strain [units]')
plt.title('Strain vs Time')
strain_line, = plt.plot(time_data, strain_data, '.-')

plt.subplot(2, 1, 2)
plt.xlabel('Time [units]')
plt.ylabel('Strain Rate [units]')
plt.title('Strain Rate vs Time')
strain_rate_line, = plt.plot(time_data[1:], strain_rate_data, '.-')


# update plot with new data
def update_plot(frame):
    global time_data, strain_data, strain_rate_data
    
    # using sqrt x as fake data
    new_x = len(time_data)  
    new_strain = np.sqrt(new_x) 
    
    # new data pt
    time_data = np.append(time_data, new_x)
    strain_data = np.append(strain_data, new_strain)
    
    # update strain plot with new data
    strain_line.set_data(time_data, strain_data)
    
    #### STRAIN RATE CALCULATION #####
    if len(time_data) > 1:
        strain_diff = strain_data[-1] - strain_data[-2] 
        time_diff = time_data[-1] - time_data[-2]  
        new_strain_rate = strain_diff / time_diff  
        strain_rate_data = np.append(strain_rate_data, new_strain_rate) 
    
    strain_rate_line.set_data(time_data[1:], strain_rate_data) 
    
    # Update plot limits
    plt.subplot(2, 1, 1)
    plt.xlim(0, len(time_data))
    plt.ylim(0, max(strain_data) + 0.1)
    
    plt.subplot(2, 1, 2)
    plt.xlim(0, len(time_data))
    if len(strain_rate_data) > 0: 
        plt.ylim(0, max(strain_rate_data) + 0.1)  

ani = FuncAnimation(plt.gcf(), update_plot, frames=None, interval=100)  
plt.show()
