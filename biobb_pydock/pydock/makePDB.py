#!/usr/bin/env python3

"""Module containing the MakePDB class and the command line interface."""
import argparse
import pandas as pd
from pathlib import Path
from typing import List, Dict
from biobb_common.tools import file_utils as fu
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools.file_utils import launchlogger
from biobb_pydock.pydock.common import rename_files, copy_files

# 1. Rename class as required
class MakePDB(BiobbObject):
    """
    | biobb_pydock makePDB
    | Wrapper class for the `pyDock makePDB module.
    | The pyDock makePDB module is used to generate pdb structure files from docking poses.

    Args:
        input_rec_path (str): Prepared receptor PDB file with pydock setup (the largest of the two proteins). File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_rec_H_path (str): Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_rec_amber_path (str): Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_lig_path (str): Prepared ligand PDB file with pydock setup (will be rotated and translated). File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_lig_H_path (str): Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_lig_amber_path (str): Ligand AMBER parameters for each atom in the pdb structure. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_rot_path (str): File containing the transformation matrix for all the docking poses. File type: input. `Sample file <>`_. Accepted formats:  (edam:).
        input_ene_path (str): File containing the energy of each docking pose. File type: input. `Sample file <>`_. Accepted formats:  (edam:).
        output_zip_path (str): Output zip file with all the pdb structure files. File type: output. `Sample file <>`_. Accepted formats: zip (edam:format_3987).
        properties (dic):
            * **docking_name** (*str*) - ("docking_name") Name for the docking.
            * **rank1** (*str*) - ("1") First rank of the energy ranking file (input_ene_path) to generate the pdb structures from.
            * **rank2** (*str*) - ("10") Last rank of the energy ranking file (input_ene_path) to generate the pdb structures from (set equal to rank1 to generate a single structure).
            * **binary_path** (*str*) - ("pyDock3") Path to the pyDock executable binary.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **container_path** (*str*) - (None)  Path to the binary executable of your container.
            * **container_image** (*str*) - (None) Container Image identifier.
            * **container_volume_path** (*str*) - ("/data") Path to an internal directory in the container.
            * **container_working_dir** (*str*) - (None) Path to the internal CWD in the container.
            * **container_user_id** (*str*) - (None) User number id to be mapped inside the container.
            * **container_shell_path** (*str*) - ("/bin/bash") Path to the binary executable of the container shell.

    Examples:
        This is a use example of how to use the building block from Python:

            from biobb_pydock.pydock.makePDB import makePDB

            prop = { 
                'docking_name': 'docking_name',
                'rank1': '1',
                'rank2': '10'}

            makePDB(input_rec_path='prepared_receptor.pdb',
                    input_rec_H_path='prepared_receptor.pdb.H',
                    input_rec_amber_path='prepared_receptor.pdb.amber',
                    input_lig_path='prepared_ligand.pdb',
                    input_lig_H_path='prepared_ligand.pdb.H',
                    input_lig_amber_path='prepared_ligand.pdb.amber',
                    input_rot_path='poses_matrix.rot',
                    input_ene_path='energies.ene',
                    output_zip_path='docking_conformations.zip',
                    properties=prop)

    Info:
        * wrapped_software:
            * name: pyDock makePDB
            * version: >=3.6.1
            * license: 
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    # Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, input_rec_path: str, input_rec_H_path: str, input_rec_amber_path: str, 
                input_lig_path: str, input_lig_H_path: str, input_lig_amber_path: str, 
                input_rot_path: str, input_ene_path: str, output_zip_path: str,
                properties: dict = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Properties common to all PyDock BB - NOTE: docking name should be an internal property - it is not adding value to the user
        self.docking_name = properties.get('docking_name', 'docking_name')
        self.binary_path = properties.get('binary_path', 'pydock3')

        # Fix the working directory and the volume path inside the container
        # PyDock expects the volume path with input and output files to be in the working directory:
        #   - makePDB tries to find output in relative path "data/docking_name" to the working directory 
        self.container_volume_path = '/data'
        self.container_working_dir = '/'

        # Properties specific for BB
        self.rank1 = properties.get('rank1', '1')
        self.rank2 = properties.get('rank2', '100')

        # Save EXTERNAL filenames (only those that need self.docking_name in their file name)
        self.external_input_paths = {'input_rec_path': input_rec_path, 'input_rec_H_path': input_rec_H_path, 'input_rec_amber_path': input_rec_amber_path, 
                                     'input_lig_path': input_lig_path, 'input_lig_H_path': input_lig_H_path, 'input_lig_amber_path': input_lig_amber_path,
                                     'input_rot_path': input_rot_path, 'input_ene_path': input_ene_path}
        self.external_output_paths = {'output_zip_path': output_zip_path}

        # Input/Output files (INTERNAL filenames) - NOTE: here we are breaking restart = True option, as 'out' files have the INTERNAL filenames, different from the EXTERNAL ones with which they are saved
        # We need io_dict to contain the INTERNAL filenames, so that the input files are staged with the INTERNAL names (so pyDock can find them) and the output files are found and copied back to the host (pyDock creates them with the INTERNAL names)
        self.io_dict = { 
            'in': { 'input_rec_path': f'{self.docking_name}_rec.pdb', 'input_rec_H_path': f'{self.docking_name}_rec.pdb.H', 'input_rec_amber_path': f'{self.docking_name}_rec.pdb.amber',
                    'input_lig_path': f'{self.docking_name}_lig.pdb', 'input_lig_H_path': f'{self.docking_name}_lig.pdb.H', 'input_lig_amber_path': f'{self.docking_name}_lig.pdb.amber',
                    'input_rot_path': f'{self.docking_name}.rot', 'input_ene_path': f'{self.docking_name}.ene'}, 
            'out': self.get_conformations_dict()
        }
        
        # Check the properties
        self.check_properties(properties)
        # Check the arguments
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`MakePDB <pydock.makePDB.MakePDB>` object."""
        
        # MakePDB Biobb
        if self.check_restart(): return 0

        # Rename input files, EXTERNAL -> INTERNAL
        renaming_dir = self.renaming_stage()
        # Stage files with correct names 
        self.stage_files()

        # Create makePDB command path: /relative/path/to/inputs/from/working/dir + /docking_name
        if self.container_path:
            cmd_path = str(Path(self.container_volume_path).joinpath(self.docking_name)) 
        else:
            cmd_path = str(Path(self.stage_io_dict.get("unique_dir")).joinpath(self.docking_name)) 

        # Create command line
        self.cmd = [self.binary_path, cmd_path, 'makePDB', str(self.rank1), str(self.rank2)]

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Zip output files 
        fu.zip_list(zip_file = self.external_output_paths['output_zip_path'], file_list = list(self.io_dict['out'].values()))

        # Remove temporal files
        self.tmp_files.append(self.stage_io_dict.get("unique_dir"))
        self.tmp_files.append(renaming_dir)                           # Add duplicated input files
        self.tmp_files.extend(list(self.io_dict['out'].values()))     # Add duplicated output files

        self.remove_tmp_files()

        # Check output arguments
        self.check_arguments(output_files_created=True, raise_exception=False)

        return self.return_code

    def renaming_stage(self) -> str: 
        """Initial stage to rename files and respect pyDock convention regarding filenames."""

        renaming_dir = str(Path(fu.create_unique_dir()).resolve())

        # IN files, add renaming_dir to correct file names in io_dict["in"]
        for file_ref, file_path in self.io_dict["in"].items():
            if file_path:
                self.io_dict["in"][file_ref] = str(Path(renaming_dir).joinpath(Path(file_path).name))
        
        # Copy external input files to unique dir with correct names
        copy_files(source_paths = self.external_input_paths, destination_paths = self.io_dict["in"])

        return renaming_dir
    
    def get_conformations_dict(self) -> Dict[str, str]:
        """Return the output dictionary containing the pdb structure file names of the conformations in the rank1-rank2 range."""
        
        # NOTE: this is needed because pyDock will create the output files as: DockingName_ConformationNumber.pdb for each pose in the rank1-rank2 range - we need to know the conformation numbers to find the output file names

        # Get the conformations (to use as keys in the output dictionary)
        conformations = get_conformations(self.external_input_paths["input_ene_path"], self.rank1, self.rank2)

        # Get the output file names (to use as values in the output dictionary)
        output_files = get_conformation_filenames(self.docking_name, self.external_input_paths["input_ene_path"], self.rank1, self.rank2)

        # Create the output dictionary
        output_dict = {}

        # Add the output files to the output dictionary
        for conf, file in zip(conformations, output_files):
            output_dict[str(conf)] = file

        return output_dict

def get_conformations(input_ene_path: str, rank1: int, rank2: int) -> List[int]:
    """
    Find the conformations in the input_ene_path file that are in the rank1-rank2 range.
    Left outside the class to be able to use from the workflow.
    """

    # Read the input_ene_path file
    df = pd.read_csv(input_ene_path, delimiter='\s+')

    # Find the conformations in the rank1-rank2 range
    df = df[(df['RANK'] >= int(rank1)) & (df['RANK'] <= int(rank2))]

    # Return the conformations
    return df['Conf'].to_list()

def get_conformation_filenames(docking_name: str, input_ene_path: str, rank1: int, rank2: int) -> List[str]:
    """
    Find the output pdb structure files corresponding to the conformations in the input_ene_path file that are in the rank1-rank2 range.
    Left outside the class to be able to use from the workflow.
    """

    # Get the conformations
    conformations = get_conformations(input_ene_path, rank1, rank2)

    # Create the output files
    output_files = [f'{docking_name}_{conf}.pdb' for conf in conformations]

    return output_files

def makePDB(input_rec_path: str, input_rec_H_path: str, input_rec_amber_path: str,
            input_lig_path: str, input_lig_H_path: str, input_lig_amber_path: str,
            input_rot_path: str, input_ene_path: str, output_zip_path: str, 
            properties: dict = None, **kwargs) -> int:
    """Create :class:`MakePDB <pydock.makePDB.MakePDB>` class and
    execute the :meth:`launch() <pydock.makePDB.MakePDB.launch>` method."""

    return MakePDB(input_rec_path = input_rec_path, input_rec_H_path = input_rec_H_path, input_lig_amber_path = input_lig_amber_path,
                   input_lig_path = input_lig_path, input_lig_H_path = input_lig_H_path, input_rec_amber_path = input_rec_amber_path, 
                   input_rot_path = input_rot_path, input_ene_path = input_ene_path, output_zip_path = output_zip_path, 
                   properties = properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Wrapper of the pyDock makePDB', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_rec_path', required=True, help='Receptor PDB file. Accepted formats: pdb.')
    required_args.add_argument('--input_rec_H_path', required=True, help='Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--input_rec_amber_path', required=True, help='Receptor AMBER parameters for each atom in the pdb structure. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--input_lig_path', required=True, help='Ligand PDB file. Accepted formats: pdb.')
    required_args.add_argument('--input_lig_H_path', required=True, help='Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--input_lig_amber_path', required=True, help='Ligand AMBER parameters for each atom in the pdb structure. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--input_rot_path', required=True, help='Input rotftdock file. Accepted formats: rot.')
    required_args.add_argument('--input_ene_path', required=True, help='Output of makePDB, ranked docking poses. Accepted formats: ene.')
    required_args.add_argument('--output_zip_path', required=True, help='Output zip file with the pdb structures of the docking poses. Accepted formats: zip.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    makePDB(input_rec_path = args.input_rec_path
            ,input_rec_H_path = args.input_rec_H_path
            ,input_rec_amber_path = args.input_rec_amber_path
            ,input_lig_path = args.input_lig_path
            ,input_lig_H_path = args.input_lig_H_path
            ,input_lig_amber_path = args.input_lig_amber_path
            ,input_rot_path = args.input_rot_path
            ,input_ene_path = args.input_ene_path
            ,output_zip_path = args.output_zip_path
            ,properties = properties)

if __name__ == '__main__':
    main()