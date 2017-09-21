"""
Parameters for reading and plotting thermal flux
"""


class Parameters:
    def __init__(self, par_dict=None):
        if par_dict is not None:
            self.set(par_dict)

    def __repr__(self):
        return "<Parameter set: %i parameters>" % (len(vars(self).keys()))

    def set(self, par_dict):
        """ Set parameters from given dictionary """
        for par in par_dict.keys():
            setattr(self, par, par_dict[par])

    def show(self):
        """ Show parameters and values """
        for v in sorted(vars(self)):
            print('%-25s: %s' % (v, getattr(self, v)))


k_parameters = dict(kb=0.001987,
                    conv=69443.84,
                    dt=5,
                    volume=80 * 80 * 80,
                    temp=300,
                    prefix='J0Jt_t',
                    isotropic=True,
                    average=True,
                    traj='traj.xyz',
                    read_info=False,
                    read_thermo=False)

plot_parameters = {
    'k': dict(limit=(0, 2000),
              size=(5, 3),
              fontsize=8,
              lw=1.5,
              dpi=200,
              avg=True,
              cmap='Spectral_r',
              save=None,
              legendloc=(1.02, 0),
              ncol=1,
              title=None,
              xlabel='Time',
              ylabel='k (W/mK)'),
    'thermo': dict(size=(20, 10),
                   dpi=200,
                   save=None,
                   title=None,
                   fontsize=8,
                   scilimits=(-4, 4),
                   subplots_adjust=(0.3, 0.25),
                   xlabel='Timesteps',
                   fix=['NVT', 'NVE1'],
                   colors=dict(NVT='r', NVE1='g', NVE2='b'),
                   variable=['temp', 'e_pair', 'tot_eng', 'e_mol', 'press'],
                   fig_height=3),
    'k_sub': dict(limit=(0, 10000),
                  size=(20, 6),
                  dpi=200,
                  subplot=(2, 5),
                  subplots_adjust=(.4, .3),
                  fontsize=9,
                  lw=2.5,
                  k_est=True,
                  k_est_color='r',
                  k_est_loc=(5, 0.1),
                  k_est_t0=5,
                  k_est_t1=10,
                  ylim=(0, 1.2),
                  save=None,
                  xlabel='Time',
                  ylabel='k (W/mK)'),
    'f_dist': dict(subplot=(2, 5),
                   size=(14, 6),
                   dpi=200,
                   space=(0.2, 0.1),
                   grid_size=10,
                   bin_size=1.5,
                   vmax=40,
                   vmin=1.1,
                   cmap='YlOrRd',
                   grid_limit=10,
                   ticks=False,
                   cbar=[0.92, 0.135, 0.02, 0.755],
                   save=None,
                   traj='traj.xyz',
                   traj_start=0,
                   traj_end=1e6)
}

lammps_parameters = dict(cif_file='',                    # File options
                         output_cif=False,
                         output_raspa=False,
                         force_field='UFF',              # Force field options
                         mol_ff=None,
                         h_bonding=False,
                         dreid_bond_type='harmonic',
                         fix_metal=False,
                         minimize=False,                 # Simulation options
                         bulk_moduli=False,
                         thermal_scaling=False,
                         npt=False,
                         nvt=False,
                         cutoff=12.5,
                         replication=None,
                         orthogonalize=False,
                         random_vel=False,
                         dump_dcd=0,
                         dump_xyz=0,
                         dump_lammpstrj=0,
                         restart=False,
                         tol=0.4,                        # Parameter options
                         neighbour_size=5,
                         iter_count=10,
                         max_dev=0.01,
                         temp=298.0,
                         pressure=1.0,
                         nprodstp=200000,
                         neqstp=200000,
                         insert_molecule="",             # Molecule insertion options
                         deposit=0,
                         thermal_conductivity=False,     # ----- Used by therMOF library -----)
                         timestep=0.5,                   # delta T
                         thermo=10000,                   # Thermo dump interval
                         seed=123456)                    # Seed number for velocity distribution

job_parameters = dict(scheduler="slurm",
                      name="therMOF",
                      nodes=2,
                      ppn=12,
                      walltime="12:00:00",
                      cluster="mpi",
                      queue="idist_big",
                      input="in.thermof",
                      output="lammps_out.txt")