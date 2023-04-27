import numpy as np        
from matplotlib import pyplot as plt        
        
bandstruc_ref = np.loadtxt('./ref/Si_diamond_ref.dat')        
bandstruc_model = np.loadtxt('./model_calc/bs/bands_tot.dat')        
shift_ref = np.min(bandstruc_ref[:, 5]) #shift valence band edge to zero so comparison with other bandstructures is easier        
shift_model = np.min(bandstruc_model[:,5])        
#plt.plot(bandstruc_ref[:,0], bandstruc_ref[:,1:10] - shift_ref, color='r')        
#plt.plot(bandstruc_model[:,0], bandstruc_model[:,1:10] - shift_model, 'b--')        
        
fig, (ax1, ax2) = plt.subplots(1, 2)        
ax1.plot(bandstruc_ref[:,0], bandstruc_ref[:,1:10] - shift_ref, color='r')        
ax1.plot(bandstruc_model[:,0], bandstruc_model[:,1:10] - shift_model, 'b--')        
ax1.plot([],[], 'r', label = 'reference')        
ax1.plot([],[], 'b--', label = 'xTB-model')        
ax1.legend()        
ax1.set_xticks([0, 30, 60], ['L', r'$\Gamma$', 'X'])        
        
bandgap_ref = np.min(bandstruc_ref[:, 5]) - np.max(bandstruc_ref[:, 4])
bandgap_model = np.min(bandstruc_model[:, 5]) - np.max(bandstruc_model[:, 4])

ax2.plot(bandstruc_ref[:,0], bandstruc_ref[:,4:6] - shift_ref, color='r')        
ax2.plot(bandstruc_model[:,0], bandstruc_model[:,4:6] - shift_model, 'b--')        
ax2.plot([], [], 'r', label = 'bandgap: ' + str(bandgap_ref))
ax2.plot([], [], 'b--', label = 'bandgap: ' + str(bandgap_model))
ax2.legend()
ax2.set_xticks([0, 30, 60], ['L', r'$\Gamma$', 'X'])        


plt.savefig('plot.png')
plt.show()
