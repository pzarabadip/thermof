import os
import yaml


def read_yaml(yaml_file):
    """ Read given yaml file """
    with open(yaml_file, 'r') as f:
        var = yaml.safe_load(f)
    return var


par_dir = os.path.abspath(os.path.dirname(__file__))
k_parameters = read_yaml(os.path.join(par_dir, 'k_parameters.yaml'))
plot_parameters = read_yaml(os.path.join(par_dir, 'plot_parameters.yaml'))
lammps_parameters = read_yaml(os.path.join(par_dir, 'lammps_parameters.yaml'))
thermof_parameters = read_yaml(os.path.join(par_dir, 'thermof_parameters.yaml'))
job_parameters = read_yaml(os.path.join(par_dir, 'job_parameters.yaml'))
default_parameters = dict(k=k_parameters, lammps=lammps_parameters, job=job_parameters,
                          plot=plot_parameters, thermof=thermof_parameters)

# Thermo headers for thermo_style
thermo_headers = read_yaml(os.path.join(par_dir, 'thermo_headers.yaml'))
