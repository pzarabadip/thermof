"""
Add runs with different seed numbers.
>>> python add_runs.py simdir
Would create run directories in simdir starting from 2 using 1 as reference.
"""
import os, sys
import shutil
from lammps_tools import change_job_name


simdir = os.path.abspath(sys.argv[1])
refdir = os.path.join(simdir, '1')
data_file_name = 'data.breathing_mof'
in_file_name = 'in.breathing_mof'
job_file_name = 'job.lammps'
nruns = int(input('Enter number of total runs: '))
job_name = input('Enter job name: ')


def change_seed(source_input, dest_input, seed=999999):
    """ Change seed number of Lammps input """
    with open(source_input, 'r') as inp_src:
        input_lines = inp_src.readlines()
    for i, line in enumerate(input_lines):
        if 'seed equal' in line:
            input_lines[i] = 'variable        seed equal %i\n' % seed
    with open(dest_input, 'w') as inp_dest:
        for line in input_lines:
            inp_dest.write(line)
    return None


for run in range(2, nruns + 1):
    rundir = os.path.join(simdir, str(run))
    print('Adding -> %s' % rundir)
    os.makedirs(rundir, exist_ok=True)
    shutil.copy(os.path.join(refdir, data_file_name), os.path.join(rundir, data_file_name))
    # Change seed number
    change_seed(os.path.join(refdir, in_file_name), os.path.join(rundir, in_file_name), seed=123456 + run)
    # Change job name
    change_job_name(os.path.join(refdir, job_file_name), os.path.join(rundir, job_file_name), job_name='%s-%i' % (job_name, run))
