""" Common functions for package biobb_pydock.pydock """

import shutil
from pathlib import Path
from typing import Mapping

def create_ini(output_path: str, receptor_prop: Mapping[str, str], ligand_prop: Mapping[str, str], reference_prop: Mapping[str, str] = None, 
               ligand_path: str = None, receptor_path: str = None, reference_path: str = None) -> None:
    """Creates INI file for PyDock setup."""

    ini_lines  = []

    # Receptor
    ini_lines.append('[receptor]')

    # Receptor pdb path
    if receptor_path is None:
        receptor_path = '-'
    ini_lines.append(f'pdb = {receptor_path}')

    # Receptor items
    for key, value in receptor_prop.items():
        ini_lines.append(f'{key} = {value}')

    # Ligand
    ini_lines.append('[ligand]')

    # Ligand pdb path
    if ligand_path is None:
        ligand_path = '-'
    ini_lines.append(f'pdb = {ligand_path}')


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