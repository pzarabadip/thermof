# Date: August 2017
# Author: Kutay B. Sezginel
"""
Mean squared displacement calculation for Lammps trajectory.
"""
import numpy as np
import periodictable


def center_of_mass(atoms, coordinates):
    """ Calculate center of mass for given coordinates and atom names of a single frame

    Args:
        - atoms (list): List of element names
        - coordinates (list): List of coordinates (2D list)

    Returns:
        - list: Center of mass coordinate for list of atom coordinates
    """
    masses = np.array([periodictable.elements.symbol(atom).mass for atom in atoms])
    total_mass = masses.sum()
    x_cm = (masses * np.array([i[0] for i in coordinates])).sum() / total_mass
    y_cm = (masses * np.array([i[1] for i in coordinates])).sum() / total_mass
    z_cm = (masses * np.array([i[2] for i in coordinates])).sum() / total_mass
    return [x_cm, y_cm, z_cm]


def time_avg_displacement(coordinates, normalize=True, reference_frame=0):
    """
    Calculate time averaged (mean) displacement for a single atom in each direction using given trajectory coordinates.

    Args:
        - coordinates (list): 2D list of coordinates vs time
        - normalize (bool): Normalize displacement by subtracting coordinates from each frame for given reference frame
        - reference_frame (int): Index for reference frame

    Returns:
        - list: Average displacement for each direction
    """
    n_frames = len(coordinates)
    ref_frame = np.array(coordinates[reference_frame])
    if normalize:
        coor = np.array(coordinates) - ref_frame
    else:
        coor = np.array(coordinates)
    return np.sum(coor, axis=0) / len(coor)


def time_avg_squared_displacement(coordinates, normalize=True, reference_frame=0):
    """
    Calculate time averaged (mean) squared displacement for a single atom in each direction using given trajectory coordinates.

    Args:
        - coordinates (list): 2D list of coordinates vs time
        - normalize (bool): Normalize displacement by subtracting coordinates from each frame for given reference frame
        - reference_frame (int): Index for reference frame

    Returns:
        - list: Average squared displacement for each direction
    """
    n_frames = len(coordinates)
    ref_frame = np.array(coordinates[reference_frame])
    if normalize:
        coor = np.array(coordinates) - ref_frame
    else:
        coor = np.array(coordinates)
    return np.sum(coor ** 2, axis=0) / len(coor)


def calculate_distances(coordinates, unit_cell, reference_frame=0):
    """
    Calculate distance of each atom from it's reference position for each frame in the coordinates (3D list).
    ---------- ORTHORHOMBIC ONLY ----------

    Args:
        - coordinates (list): A list of frames containing coordinates for multiple/single atom(s)
        - unit_cell (list): Orthorhombic unit cell dimensions
        - reference_frame (int): Reference frame to calculate the distances from

    Returns:
        - list: Distance of each atom in each frame to it's position in the reference frame
    """
    if len(np.shape(coordinates)) != 3:
        raise CoordinatesDimensionError('Coordinates list must be 3 dimensional with shape: (n_frames, n_atoms, axis)')
    n_frames, n_atoms = np.shape(coordinates)[:2]
    ref_coordinates = coordinates[reference_frame]
    distances = np.zeros((n_frames, n_atoms))
    for frame_idx, frame in enumerate(coordinates):
        for atom_idx, (atom, ref_atom) in enumerate(zip(frame, ref_coordinates)):
            d = [0, 0, 0]
            for i in range(3):
                d[i] = atom[i] - ref_atom[i]
                if d[i] > unit_cell[i] * 0.5:
                    d[i] = d[i] - unit_cell[i]
                elif d[i] <= -unit_cell[i] * 0.5:
                    d[i] = d[i] + unit_cell[i]
            distances[frame_idx][atom_idx] = np.sqrt((d[0] ** 2 + d[1] ** 2 + d[2] ** 2))
    return distances


def subdivide_coordinates(coordinates, frames, atoms, dimensions):
    """
    Subdivide coordinates by selecting frames, atoms and dimensions.

    Args:
        - coordinates (list): Trajectory coordinates to be subdivided
        - atoms (list): List of atoms to be included in subdivision
        - frames (list): List of frames to be included in the subdivision
        - dimensions (list): List of dimensions to be included in the subdivision

    Returns:
        - list: 3D list of coordinates subdivision
    """
    traj_shape = np.shape(coordinates)
    if len(traj_shape) != 3:
        raise CoordinatesDimensionError('Coordinates list must be 3 dimensional with shape: (n_frames, n_atoms, axis)')

    if frames is None:
        frames = list(range(traj_shape[0]))
    if atoms is None:
        atoms = list(range(traj_shape[1]))
    if dimensions is None:
        dimensions = list(range(traj_shape[2]))

    div_coordinates = np.zeros((len(frames), len(atoms), len(dimensions)))
    for frame_idx, frame in enumerate(frames):
        for atom_idx, atom in enumerate(atoms):
            for dim_idx, dim in enumerate(dimensions):
                div_coordinates[frame_idx][atom_idx][dim_idx] = coordinates[frame][atom][dim]
    return div_coordinates


def subdivide_atoms(traj_atoms, frames, atoms):
    """
    Subdivide coordinates by selecting frames, atoms and dimensions.

    Args:
        - traj_atoms (list): Trajectory atoms to be subdivided
        - frames (list): List of frames to be included in the subdivision
        - atoms (list): List of atoms to be included in the subdivision

    Returns:
        - list: 2D list of atoms subdivision
    """
    traj_shape = np.shape(traj_atoms)
    if frames is None:
        frames = list(range(traj_shape[0]))
    if atoms is None:
        atoms = list(range(traj_shape[1]))

    div_atoms = []
    for frame_idx, frame in enumerate(frames):
        div_atoms.append([])
        for atom in atoms:
            div_atoms[frame_idx].append(traj_atoms[frame][atom])
    return div_atoms


class CoordinatesDimensionError(Exception):
    pass
