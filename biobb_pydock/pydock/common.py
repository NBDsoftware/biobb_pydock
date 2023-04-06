""" Common functions for package biobb_pydock.pydock """

import shutil
from pathlib import Path
from typing import Mapping

def create_ini(output_path: str, receptor_prop: Mapping[str, str], ligand_prop: Mapping[str, str], 
               reference_prop: Mapping[str, str] = None, input_paths: str = None) -> None:
    """Creates INI file for PyDock setup."""

    if input_paths:
        # Ligand input files: either pdb or coords and top
        ligand_pdb_path = input_paths.get("input_lig_pdb_path")
        ligand_coords_path = input_paths.get("input_lig_coords_path")
        ligand_top_path = input_paths.get("input_lig_top_path")

        # Receptor input files: either pdb or coords and top
        receptor_pdb_path = input_paths.get("input_rec_pdb_path")
        receptor_coords_path = input_paths.get("input_rec_coords_path")
        receptor_top_path = input_paths.get("input_rec_top_path")

        # Reference input file path
        reference_path = input_paths.get("input_ref_path")
    else:
        # Ligand input files: either pdb or coords and top
        ligand_pdb_path = "-"
        ligand_coords_path = None
        ligand_top_path = None

        # Receptor input files: either pdb or coords and top
        receptor_pdb_path = "-"
        receptor_coords_path = None
        receptor_top_path = None

        # Reference input file path
        reference_path = None

    ini_lines  = []

    # Receptor
    ini_lines.append('[receptor]')

    # Receptor pdb path
    if receptor_coords_path and receptor_top_path:
        ini_lines.append(f'pdb = {receptor_coords_path},{receptor_top_path}')
    else:
        ini_lines.append(f'pdb = {receptor_pdb_path}')
    
    # Receptor items
    for key, value in receptor_prop.items():
        ini_lines.append(f'{key} = {value}')

    # Ligand
    ini_lines.append('[ligand]')

    # Ligand pdb path
    if ligand_coords_path and ligand_top_path:
        ini_lines.append(f'pdb = {ligand_coords_path},{ligand_top_path}')
    else: 
        ini_lines.append(f'pdb = {ligand_pdb_path}')
    
    # Ligand items
    for key, value in ligand_prop.items():
        ini_lines.append(f'{key} = {value}')

    # Reference
    if None not in (reference_prop, reference_path):

        ini_lines.append('[reference]')

        # Reference pdb path
        ini_lines.append(f'pdb = {reference_path}')

        # Reference items
        for key, value in reference_prop.items():
            ini_lines.append(f'{key} = {value}')
        
        # Additional items
        ini_lines.append(f'newrecmol = {receptor_prop["newmol"]}')
        ini_lines.append(f'newligmol = {ligand_prop["newmol"]}')
        
    return write_ini(output_path, ini_lines)

def write_ini(output_path: str, ini_lines: list) -> None:
    """Writes INI file for PyDock setup """

    # Write INI file
    with open(output_path, 'w') as ini_file:
        for line in ini_lines:
            ini_file.write(line + '\n')

def rename_files(source_paths: Mapping[str, str] , destination_paths: Mapping[str, str]):
    """Rename files in source_paths using the destination_paths."""

    for file_ref, destination_path in destination_paths.items():
        if Path(source_paths[file_ref]).exists():
            shutil.move(source_paths[file_ref], destination_path)
    
def copy_files(source_paths: Mapping[str, str] , destination_paths: Mapping[str, str]):
    """Copy files in source_paths to the destination_paths."""

    for file_ref, destination_path in destination_paths.items():
        if Path(source_paths[file_ref]).exists():
            shutil.copy(source_paths[file_ref], destination_path)