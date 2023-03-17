""" Common functions for package biobb_pydock.pydock """

from pathlib import Path
from biobb_common.tools import file_utils as fu
from typing import Dict, Mapping

def create_ini(output_ini_path: str, receptor: Mapping[str, str], receptor_pdb: str,
               ligand: Mapping[str, str], ligand_pdb: str) -> None:
    """Creates INI file for PyDock setup """

    ini_lines  = []

    # Receptor
    ini_lines.append('[receptor]')

    # Receptor pdb file
    ini_lines.append(f'pdb = {receptor_pdb}')

    # Receptor items
    for key, value in receptor.items():
        ini_lines.append(f'{key} = {value}')

    # Ligand
    ini_lines.append('[ligand]')

    # Ligand pdb file
    ini_lines.append(f'pdb = {ligand_pdb}')

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
    
    return