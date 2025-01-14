import os
import sys


def check_finished(sim_dir, file_name='lammps_out.txt'):
    dir_list = os.listdir(sim_dir)
    if file_name in dir_list:
        with open(os.path.join(sim_dir, file_name), 'r') as lout:
            lammps_lines = lout.readlines()
        if len(lammps_lines) > 0:
            if 'Total wall time' in lammps_lines[-1]:
                walltime = lammps_lines[-1].split()[-1]
                print('%-20s -> finished in %s' % (os.path.basename(sim_dir), walltime))
            elif any(['log' in f for f in dir_list]):
                print('%-20s -> running' % os.path.basename(sim_dir))
            else:
                print('%-20s -> ERROR' % os.path.basename(sim_dir))
        else:
            print('%-20s -> NOT started' % os.path.basename(sim_dir))
    elif all([os.path.isdir(os.path.join(sim_dir, f)) for f in dir_list]):
        print('########## %s ##########' % sim_dir)
        for sdir in dir_list:
            check_finished(os.path.join(sim_dir, sdir))
    else:
        print('%-20s -> Lammps out file not found' % os.path.basename(sim_dir))


check_finished(sys.argv[-1])
