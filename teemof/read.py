# Date: August 2017
# Author: Kutay B. Sezginel
"""
Read Lammps output files for thermal conductivity calculations
"""
import os
import math
import yaml
from teemof.reldist import reldist
from teemof.parameters import k_parameters


def read_thermal_flux(file_path, k_par=k_parameters, start=200014, j_index=3):
    """Read thermal flux autocorellation vs time data from Lammps simulation output file

    Args:
        - file_path (str): Thermal flux autocorellation file generated by Lammps
        - dt (int): Time step
        - start (int): Index of the line to start reading flux autocorrelation (corresponds to last function)
        - j_index (int): Index of thermal flux in file

    Returns:
        - list: thermal flux autocorrelation function
        - list: time
    """
    dt = k_par['dt']
    with open(file_path, 'r') as f:
        flux_lines = f.readlines()
    flux, time = [], []
    for line in flux_lines[start:]:
        ls = line.split()
        t = (float(ls[0]) - 1) * dt / 1000.0
        flux.append(float(ls[j_index]))
        time.append(t)
    return flux, time


def calculate_k(flux, k_par=k_parameters):
    """Calculate thermal conductivity (W/mK) from thermal flux autocorrelation function

    Args:
        - flux (list): Thermal flux autocorellation read by read_thermal_flux method
        - k_par (dict): Dictionary of calculation parameters

    Returns:
        - list: Thermal conductivity autocorrelation function
    """
    k = flux[0] / 2 * k_par['volume'] * k_par['dt'] / (k_par['kb'] * math.pow(k_par['temp'], 2)) * k_par['conv']
    k_data = [k]
    for J in flux[1:]:
        k = k + J * k_par['volume'] * k_par['dt'] / (k_par['kb'] * math.pow(k_par['temp'], 2)) * k_par['conv']
        k_data.append(k)
    return k_data


def estimate_k(k_data, time, t0=5, t1=10):
    """ Get approximate thermal conductivity value for a single simulation.
    The arithmetic average of k values are taken between given timesteps.

    Args:
        - k_data (list): Thermal conductivity autocorrelation function
        - time (list): Simulation timestep
        - t0: Timestep to start taking average of k values
        - t1: Timestep to end taking average of k values

    Returns:
        - float: Estimate thermal conductivity
    """
    start, end = time.index(t0), time.index(t1)
    return (sum(k_data[start:end]) / len(k_data[start:end]))


def average_k(k_runs):
    """Calculate average thermal conductivity for multiple runs

    Args:
        - k_runs (list): 2D list of thermal conductivity autocorrelation function for multiple runs

    Returns:
        - list: Arithmetic average of thermal conductivity per timestep for multiple runs
    """
    n_frames = len(k_runs[0])
    for run_index, k in enumerate(k_runs):
        run_frames = len(k)
        if run_frames != n_frames:
            raise TimestepsMismatchError('Number of timesteps for inital run not equal to run %i (%i != %i)'
                                         % (run_index, n_frames, run_frames))
    avg_k_data = []
    for timestep in range(n_frames):
        avg_k_data.append(sum([k[timestep] for k in k_runs]) / len(k_runs))
    return avg_k_data


def get_flux_directions(run_dir, k_par=k_parameters, verbose=True):
    """Return thermal flux data file and direction name for each direction as lists.
    Each file with the given prefix is selected as thermal flux file and direction is read as the
    character between prefix and file extension.

    Example: J0Jt_tx.dat -> prefix should be 'J0Jt_t' and direction would be read as 'x'.

    Args:
        - run_dir (str): Lammps simulation directory with thermal flux files

    Returns:
        - list: List of thermal flux files found with given prefix
        - list: List of thermal flux directions
    """
    flux_files, directions = [], []
    for f in os.listdir(run_dir):
        if k_par['prefix'] in f:
            flux_files.append(os.path.join(run_dir, f))
            directions.append(f.split('.')[0].split('J0Jt_t')[1])
    if len(directions) == 0:
        raise FluxFileNotFoundError('No flux file found with prefix: %s' % k_par['prefix'])
    else:
        print('%i directions found.' % (len(directions)))
    return flux_files, directions


def read_run(run_dir, k_par=k_parameters, t0=5, t1=10, verbose=True):
    """Read single Lammps simulation run
    Args:
        - run_dir (str): Lammps simulation directory for single run
        - k_par (dict): Dictionary of calculation parameters
        - t0 (int): Timestep to start taking average of k values
        - t1 (int): Timestep to end taking average of k values
        - verbose (bool): Print information about the run

    Returns:
        - dict: Run data containing thermal conductivity, estimate, timesteps, run name
    """
    run_data = dict(name=os.path.basename(run_dir), k={}, k_est={}, time=[], directions=[])
    trial_data = []
    runs_id = []
    if os.path.isdir(run_dir):
        flux_files, directions = get_flux_directions(run_dir, k_par=k_par)
        run_message = '%-9s ->' % run_data['name']
        for direction, flux_file in zip(directions, flux_files):
            flux, time = read_thermal_flux(flux_file, k_par=k_par)
            k = calculate_k(flux, k_par=k_par)
            run_data['k'][direction] = k
            run_data['k_est'][direction] = estimate_k(k, time, t0=t0, t1=t1)
            run_message += ' k: %.3f W/mK (%s) |' % (run_data['k_est'][direction], direction)
        if k_par['read_info']:
            run_data['info'] = read_run_info(run_dir, filename='run_info.yaml')
        if k_par['read_thermo']:
            run_data['thermo'] = read_thermo(read_log(os.path.join(run_dir, 'log.lammps')))
        run_data['time'] = time
        run_data['directions'] = directions
        print(run_message) if verbose else None
    else:
        raise RunDirectoryNotFoundError('Run directory not found: %s' % run_dir)
    if k_par['isotropic']:
        run_data['k']['iso'] = average_k([run_data['k'][d] for d in directions])
        run_data['k_est']['iso'] = estimate_k(run_data['k']['iso'], run_data['time'], t0=t0, t1=t1)
        print('Isotropic -> k: %.3f W/mK from %i directions' % (run_data['k_est']['iso'], len(directions))) if verbose else None

    return run_data


def read_trial(trial_dir, k_par=k_parameters, t0=5, t1=10, verbose=True):
    """Read Lammps simulation trial with any number of runs

    Args:
        - trial_dir (str): Lammps simulation directory including directories for multiple runs
        - k_par (dict): Dictionary of calculation parameters
        - t0 (int): Timestep to start taking average of k values
        - t1 (int): Timestep to end taking average of k values
        - verbose (bool): Print information about the run

    Returns:
        - dict: Trial data containing thermal conductivity, estimate, timesteps, run name for each run
    """
    trial = dict(runs=[], data={}, name=os.path.basename(trial_dir))
    print('\n------ %s ------' % trial['name']) if verbose else None
    run_list = [os.path.join(trial_dir, run) for run in os.listdir(trial_dir)
                if os.path.isdir(os.path.join(trial_dir, run))]
    for run in run_list:
        run_data = read_run(run, k_par=k_par, t0=t0, t1=t1)
        trial['data'][run_data['name']] = run_data
        trial['runs'].append(run_data['name'])
    if k_par['average']:
        trial['avg'] = average_trial(trial, isotropic=k_par['isotropic'])
    return trial


def average_trial(trial, isotropic=False):
    """Take average of thermal conductivities for multiple runs.
    Assumes all runs have the same number of directions.

    Args:
        - isotropic (bool): Isotropy of thermal flux, if True aveage is taken for each direction

    Returns:
        - dict: Trial data average for thermal conductivity and estimate
    """
    trial_avg = dict(k={}, k_est={})
    for direction in trial['data'][trial['runs'][0]]['directions']:
        # Take average of k for each direction
        trial_avg['k'][direction] = average_k([trial['data'][run]['k'][direction] for run in trial['runs']])
        k_est_runs = [trial['data'][run]['k_est'][direction] for run in trial['runs']]
        trial_avg['k_est'][direction] = sum(k_est_runs) / len(trial['runs'])
    if isotropic:
        # Take average of isotropic k and k_estimate
        trial_avg['k']['iso'] = average_k([trial['data'][run]['k']['iso'] for run in trial['runs']])
        k_est_iso_runs = [trial['data'][run]['k_est']['iso'] for run in trial['runs']]
        trial_avg['k_est']['iso'] = sum(k_est_iso_runs) / len(trial['runs'])
    return trial_avg


def read_trial_set(trial_set_dir, k_par=k_parameters, t0=5, t1=10, verbose=True):
    """Read multiple trials with multiple runs

    Args:
        - trial_set_dir (str): Lammps simulation directory including directories for multiple trials
        - k_par (dict): Dictionary of calculation parameters
        - t0 (int): Timestep to start taking average of k values
        - t1 (int): Timestep to end taking average of k values
        - verbose (bool): Print information about the run

    Returns:
        - dict: Trial set data containing thermal conductivity, estimate, timesteps, trial name for each trial
    """
    trial_set = dict(trials=[], data={}, name=os.path.basename(trial_set_dir))
    trial_list = [os.path.join(trial_set_dir, t) for t in os.listdir(trial_set_dir)
                  if os.path.isdir(os.path.join(trial_set_dir, t))]
    for trial_dir in trial_list:
        trial = read_trial(trial_dir, k_par=k_par, t0=5, t1=10, verbose=verbose)
        trial_set['trials'].append(os.path.basename(trial_dir))
        trial_set['data'][trial['name']] = trial
    return trial_set


def read_log(log_path, headers='Step Temp Press PotEng TotEng Volume'):
    """ Read log.lammps file and return lines for multiple thermo data """
    with open(log_path, 'r') as log:
        log_lines = log.readlines()

    thermo_start = []
    thermo_end = []
    for line_index, line in enumerate(log_lines):
        if headers in line:
            start = line_index + 1
            thermo_start.append(start)
        if 'Loop time' in line:
            end = line_index
            thermo_end.append(end)

    thermo_data = []
    for s, e in zip(thermo_start, thermo_end):
        thermo_data.append(log_lines[s:e])

    return thermo_data


def read_thermo(thermo_data, headers=['step', 'temp', 'press', 'tot_eng', 'volume']):
    """ Read thermo data from given thermo log lines """
    thermo = {key: [] for key in headers}
    for data in thermo_data:
        line = data.strip().split()
        for i, h in enumerate(headers):
            thermo[h].append(float(line[i]))

    return thermo


def read_run_info(run_dir, filename='run_info.yaml'):
    """ Read run info yaml file """
    run_info_path = os.path.join(run_dir, filename)
    run_info = yaml.load(open(run_info_path, 'r'))
    return run_info


def read_legend(trial_dir, key='name', run='Run1'):
    """ Read legend name from given trial """
    if run is not None:
        run_dir = os.path.join(trial_dir, run)
    else:
        run_dir = trial_dir
    run_info = read_run_info(run_dir)
    return run_info[key]


def read_distance_runs(trial_dir, start=0, end=300000):
    """ Read relative distance data for given trial with multiple runs """
    hist_data = []
    for run in os.listdir(trial_dir):
        traj_path = os.path.join(trial_dir, run, 'traj.xyz')
        x_coords, y_coords, z_coords = reldist(traj_path, end=end)
        x_coords.append(0)
        x_coords.append(1)
        y_coords.append(0)
        y_coords.append(1)

        title = '%s' % run
        sort_param = int(run.split('Run')[1])
        hist_data.append((x_coords[start:], y_coords[start:], z_coords[start:], title, sort_param))

    return sorted(hist_data, key=lambda x: x[4])


def read_distance_trials(trial_set_dir, run='Run1', start=0, end=300000, xkey='sigma'):
    """ Read relative distance data for given trial set """
    hist_data = []
    for i, trial in enumerate(os.listdir(trial_set_dir), start=1):
        trial_dir = os.path.join(trial_set_dir, trial)
        traj_path = os.path.join(trial_dir, run, 'traj.xyz')
        x_coords, y_coords, z_coords = reldist(traj_path, end=end)
        x_coords.append(0)
        x_coords.append(1)
        y_coords.append(0)
        y_coords.append(1)

        leg = read_legend(trial_dir, key='legend')
        sort_param = read_legend(trial_dir, key=xkey)
        title = '%s' % leg
        hist_data.append((x_coords[start:], y_coords[start:], z_coords[start:], title, sort_param))

    return sorted(hist_data, key=lambda x: x[4])


class FluxFileNotFoundError(Exception):
    pass


class TimestepsMismatchError(Exception):
    pass


class RunDirectoryNotFoundError(Exception):
    pass
