"""
Analyze bond/angle spring constant search simulation results.
Run with directory to the data.
Read parameter search data
Plot average thermal conductivity (both over runs and directions)
Plot 2D histogram.
"""
import os, csv, sys
import numpy as np
from scipy import stats
import yaml
from thermof_tools import read_volume, read_thermal_flux, calculate_k, estimate_k
from thermof_plot import plot_kest


TERMS = ['', '_bond', '_angle']  # thermal conductivity contribution terms
P = 100000                       # correlation length
S = 5                            # sample interval
DT = 1                           # timestep (fs)
V_IDEAL = 80 * 80 * 80           # mof ideal volume
T0, T1 = int(P * 0.7), P         # thermal conductivity read interval
HIST_DATA = {}
PLT_DIR = 'par_plt'
main = os.path.abspath(sys.argv[1])
for sim in os.listdir(main):
    sim_dir = os.path.join(main, sim)
    sim_data = {'v': [], 'k': [], 'k_bond': [], 'k_angle': [],
                'j': [], 'j_angle': [], 'j_bond': []}
    for run in os.listdir(sim_dir):
        run_dir = os.path.join(sim_dir, run)

        ## READ VOLUME -------------------------------------
        vol_file = os.path.join(run_dir, 'vol_angles.csv')
        vol_data = read_volume(vol_file)
        v_avg = sum(vol_data['v']) / len(vol_data['v'])
        v_ratio = v_avg / V_IDEAL * 100
        sim_data['v'].append(v_ratio)

        ## READ THERMAL FLUX -------------------------------
        for trm in TERMS:
            for drx in ['x', 'y', 'z']:
                flux_file = os.path.join(run_dir, 'J0Jt_t%s%s.dat' % (drx, trm))
                flux, time = read_thermal_flux(flux_file, p=P, s=S, dt=DT)
                k = calculate_k(flux, v_avg, s=S, dt=DT)
                sim_data['k%s' % trm].append(k)
   
    # sim_data['v'] = sum(sim_data['v']) / len(sim_data['v'])
    HIST_DATA[sim] = {'v': sum(sim_data['v']) / len(sim_data['v'])}
    # Average multiple runs and directions for each term
    for trm in TERMS:
        sim_data['k%s' % trm] = np.average(sim_data['k%s' % trm], axis=0)
        sim_data['kest%s' % trm] = sum(sim_data['k%s' % trm][T0:T1]) / len(sim_data['k%s' % trm][T0:T1])
        slope, intercept, r_value, p_value, std_err = stats.linregress(time[T0:T1], sim_data['k%s' % trm][T0:T1])
        sim_data['slope%s' % trm] = slope
        HIST_DATA[sim]['k%s' % trm] = sim_data['kest%s' % trm]
        HIST_DATA[sim]['slope%s' % trm] = sim_data['slope%s' % trm]

    # Plot thermal conductivity and HCACF
    kest = {'t': time[T0:T1], 'k': sim_data['k'][T0:T1], 'kest': sim_data['kest']}
    plot_kest([sim_data['k%s' % trm] for trm in TERMS], time, kest=kest,
              title=sim, legend=['k%s' % trm for trm in TERMS],
              save=os.path.join(PLT_DIR, '%s.png' % sim))

    # Histogram data
    print('%8s | k: %5.2f (b: %4.2f a: %4.2f) | V: %.1f | m: %.5f' % (sim, HIST_DATA[sim]['k'], 
                                                                      HIST_DATA[sim]['k_bond'],
                                                                      HIST_DATA[sim]['k_angle'],
                                                                      HIST_DATA[sim]['v'],
                                                                      HIST_DATA[sim]['slope']))


with open('parameter_search_data.yaml', 'w') as f:
    yaml.dump(HIST_DATA, f)