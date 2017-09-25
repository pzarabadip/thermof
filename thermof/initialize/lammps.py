# Date: September 2017
# Author: Kutay B. Sezginel
"""
Initialize Lammps simulation using lammps_interface
"""
import os
from lammps_interface.lammps_main import LammpsSimulation
from lammps_interface.structure_data import from_CIF
from thermof.initialize import read_lines, write_lines
from thermof.sample import lammps_input


def write_lammps_files(parameters):
    """
    Write Lammps files using lammps_interface.

    Args:
        - parameters (Parameters): Lammps simulation parameters

    Returns:
        - None: Writes Lammps simulation files to simulation directory
    """
    sim = LammpsSimulation(parameters)
    cell, graph = from_CIF(parameters.cif_file)
    sim.set_cell(cell)
    sim.set_graph(graph)
    sim.split_graph()
    sim.assign_force_fields()
    sim.compute_simulation_size()
    sim.merge_graphs()
    sim.write_lammps_files(parameters.sim_dir)


def get_npt_lines(simpar, npt_file=lammps_input['npt']):
    """
    Get input lines for NPT simulation using thermof_parameters.
    """
    npt_lines = read_lines(npt_file)
    npt_lines[1] = 'variable        pdamp      equal %i*${dt}' % simpar['npt']['pdamp']
    npt_lines[2] = 'variable        tdamp      equal %i*${dt}' % simpar['npt']['tdamp']
    npt_lines[4] = 'run             %i' % simpar['npt']['steps']
    return npt_lines
