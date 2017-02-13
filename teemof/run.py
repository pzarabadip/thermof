# Run simulations for thermal conductivity measurements
# Date: Februay 2017
# Author: Kutay B. Sezginel
import os
import subprocess
from teemof.initialize import change_seed, lammps_qsub, export_lines


def initialize_trial(trial_dir, num_of_runs, input_lines, data_lines, qsub_lines, seed=None, verbose=True):
    """ Create directories and input files for a trial with multiple runs """
    trial_name = os.path.split(trial_dir)[1]
    print('Initializing %s...' % trial_name) if verbose else None

    if seed is None:
        default_seed = 123456
        last_seed = default_seed + num_of_runs
        seed = list(range(default_seed, last_seed))
        print('Generating seed numbers between %i and %i' % (default_seed, last_seed)) if verbose else None

    for i in range(1, num_of_runs + 1):
        print('Run %i / %i' % (i, num_of_runs)) if verbose else None
        # Create run directory
        run_dir = os.path.join(trial_dir, 'Run%i' % i)
        if not os.path.exists(run_dir):
            os.mkdir(run_dir)
        # Change seed number
        input_lines = change_seed(input_lines, seed=seed[i - 1])
        # Change job name
        job_name = '%s-Run%i' % (trial_name, i)
        qsub_lines = lammps_qsub(qsub_lines, name=job_name)
        # Determine file paths
        inp_dest = os.path.join(run_dir, 'in.cond')
        qs_dest = os.path.join(run_dir, 'lammps_qsub.sh')
        dt_dest = os.path.join(run_dir, 'lammps.data')
        # Export files
        export_lines(input_lines, inp_dest)
        export_lines(data_lines, dt_dest)
        export_lines(qsub_lines, qs_dest)


def submit_job(qsub_path, verbose=True):
    qsub = subprocess.run(['qsub', run_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    qsub_out = qsub.stdout.decode()
    print(qsub_out) if verbose else None


def submit_runs(runs_dir, verbose=True):
    """ Submit multiple runs for a single trial """
    for i, run in enumerate(os.listdir(runs_dir)):
        print('%i - %s' % (i, run)) if verbose else None
        qsub_path = os.path.join(runs_dir, run, 'lammps_qsub.sh')
        submit_job(qsub_path)


def submit_trials(trials_dir, verbose=True):
    """ Submit multiple trials with multiple runs """
    for i, trial in enumerate(os.listdir(trials_dir)):
        print('\n%i - %s' % (i, trial)) if verbose else None
        runs_dir = os.path.join(trials_dir, trial)
        submit_runs(runs_dir)
