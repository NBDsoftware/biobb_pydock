""" Common functions for package biobb_pydock.pydock """

import shutil
from pathlib import Path
from typing import Mapping

def create_ini(output_ini_path: str, receptor: Mapping[str, str], receptor_pdb_name: str,
               ligand: Mapping[str, str], ligand_pdb_name: str, io_path: str) -> None:
    """Creates INI file for PyDock setup """

    ini_lines  = []

    # Receptor
    ini_lines.append('[receptor]')

    # Receptor pdb path
    receptor_pdb_path = str(Path(io_path).joinpath(receptor_pdb_name))
    ini_lines.append(f'pdb = {receptor_pdb_path}')

    # Receptor items
    for key, value in receptor.items():
        ini_lines.append(f'{key} = {value}')

    # Ligand
    ini_lines.append('[ligand]')

    # Ligand pdb path
    ligand_pdb_path = str(Path(io_path).joinpath(ligand_pdb_name))
    ini_lines.append(f'pdb = {ligand_pdb_path}')

    # Ligand items
    for key, value in ligand.items():
        ini_lines.append(f'{key} = {value}')

    return write_ini(output_ini_path, ini_lines)

def write_ini(output_ini_path: str, ini_lines: list) -> None:
    """Writes INI file for PyDock setup """

    # Write INI file
    with open(output_ini_path, 'w') as ini_file:
        for line in ini_lines:
            ini_file.write(line + '\n')

def rename_files(source_paths: Mapping[str, str] , destination_paths: Mapping[str, str]):
    """Rename files in source_paths using the destination_paths."""

    for file_ref, destination_path in destination_paths.items():
        if Path(source_paths[file_ref]).exists():
            shutil.move(source_paths[file_ref], destination_path)
    
def copy_files(source_paths: Mapping[str, str] , destination_paths: Mapping[str, str]):
    """Copy files in source_paths using the destination_paths."""

    for file_ref, destination_path in destination_paths.items():
        if Path(source_paths[file_ref]).exists():
            shutil.copy(source_paths[file_ref], destination_path)
