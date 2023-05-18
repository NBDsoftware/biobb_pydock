#!/usr/bin/env python3

"""Module containing the Dockrst class and the command line interface."""
import argparse
from pathlib import Path
from biobb_common.tools import file_utils as fu
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools.file_utils import launchlogger
from biobb_pydock.pydock.common import rename_files, copy_files, create_ini

# 1. Rename class as required
class Dockrst(BiobbObject):
    """
    | biobb_pydock Dockrst
    | Wrapper class for the `pyDock dockrst <https://life.bsc.es/pid/pydock/doc/tutorial.html#addition-of-experimental-data-restraints-to-guide-docking>`_ module.
    | The pyDock dockrst module is used to add experimental data restraints to the pyDock energy ranking.

    Args:
        input_rec_path (str): Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_rec_H_path (str): Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_rec_amber_path (str): Receptor AMBER parameters for each atom in the pdb structure. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_lig_path (str): Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_lig_H_path (str): Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_lig_amber_path (str): Ligand AMBER parameters for each atom in the pdb structure. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_rot_path (str): File containing the transformation matrix for all the docking poses. File type: input. `Sample file <>`_. Accepted formats:  (edam:).
        input_ene_path (str): File containing the energy ranking for all docking poses in input_rot_path. File type: input. `Sample file <>`_. Accepted formats:  (edam:).
        output_rst_path (str): File containing the scoring of each docking model based on the distance restraints. File type: output. `Sample file <>`_. Accepted formats:  (edam:).
        output_ene_rst_path (str): Combination of input_ene_path with output_rst_path. File type: output. `Sample file <>`_. Accepted formats:  (edam:).
        properties (dic):
            * **docking_name** (*str*) - ("docking_name") Name for the docking.
            * **receptor** (*dict*) - ("{}") Receptor dictionary with: "mol" (chain name of receptor in input_rec_path), "newmol" (new chain name of receptor in output_rec_path) and "restr" (restraint defined as a combination of three fields separated by dots: the first field corresponds to the new chain name “newmol”, the second field is the 3 letter amino-acid code with the first letter in uppercase and the last field is the amino acid number, as it appear in the original pdb file. Do not include "pdb" file here.
            * **ligand** (*dict*) - ("{}") Ligand dictionary with "mol" (chain name of ligand in input_ligand_path) and "newmol" (new chain name of ligand in output_lig_path, different from receptor "newmol"). Do not include "pdb" file here.
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

            from biobb_pydock.pydock.dockrst import dockrst

            prop = { 
                'docking_name': 'docking_name',
                'receptor': 
                    {'mol': 'A',
                     'newmol': 'A', 
                     'restr': 'A.Arg.45'},
                'ligand': 
                    {'mol': 'A',
                     'newmol': 'B',
                     'restr': 'B.Ala.88'}}

            dockrst(input_rec_path='prepared_receptor.pdb',
                    input_rec_H_path='prepared_receptor.pdb.H',
                    input_rec_amber_path='prepared_receptor.pdb.amber',
                    input_lig_path='prepared_ligand.pdb',
                    input_lig_H_path='prepared_ligand.pdb.H',
                    input_lig_amber_path='prepared_ligand.pdb.amber',
                    input_rot_path='matrix.rot',
                    input_ene_path='original_scoring.ene',
                    output_rst_path='restrains_scoring.rst',
                    output_ene_rst_path='combined_scoring.eneRST',
                    properties=prop)

    Info:
        * wrapped_software:
            * name: pyDock dockrst
            * version: >=3.6.1
            * license: 
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    # Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, input_rec_path: str, input_rec_H_path: str, input_rec_amber_path: str, 
                 input_lig_path: str, input_lig_H_path: str, input_lig_amber_path: str, 
                 input_rot_path: str, input_ene_path: str, output_rst_path: str, 
                 output_ene_rst_path: str, properties: dict = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Properties common to all PyDock BB - NOTE: docking name should be an internal property - it is not adding value to the user
        self.docking_name = properties.get('docking_name', 'docking_name')
        self.binary_path = properties.get('binary_path', 'pydock3') 

        # Properties specific for BB
        self.receptor_prop = properties.get('receptor', {'mol': 'A','newmol': 'A'})
        self.ligand_prop = properties.get('ligand', {'mol': 'A','newmol': 'B'})
        self.ini_file_name = f'{self.docking_name}.ini'

        # Save EXTERNAL filenames (only those that need self.docking_name in their file name)
        self.external_input_paths = {'input_rec_path': input_rec_path, 'input_rec_H_path': input_rec_H_path, 'input_rec_amber_path': input_rec_amber_path, 
                                     'input_lig_path': input_lig_path, 'input_lig_H_path': input_lig_H_path, 'input_lig_amber_path': input_lig_amber_path,
                                     'input_rot_path': input_rot_path, 'input_ene_path': input_ene_path}
        self.external_output_paths = {'output_rst_path': output_rst_path, 'output_ene_rst_path': output_ene_rst_path}

        # Input/Output files (INTERNAL filenames) - NOTE: here we are breaking restart = True option, as 'out' files have the INTERNAL filenames, different from the EXTERNAL ones with which they are saved
        # We need io_dict to contain the INTERNAL filenames, so that the input files are staged with the INTERNAL names (so pyDock can find them) and the output files are found and copied back to the host (pyDock creates them with the INTERNAL names)
        self.io_dict = { 
            'in': { 'input_rec_path': f'{self.docking_name}_rec.pdb', 'input_rec_H_path': f'{self.docking_name}_rec.pdb.H', 'input_rec_amber_path': f'{self.docking_name}_rec.pdb.amber',
                    'input_lig_path': f'{self.docking_name}_lig.pdb', 'input_lig_H_path': f'{self.docking_name}_lig.pdb.H', 'input_lig_amber_path': f'{self.docking_name}_lig.pdb.amber',
                    'input_rot_path': f'{self.docking_name}.rot', 'input_ene_path': f'{self.docking_name}.ene'}, 
            'out': { 'output_ene_rst_path': f'{self.docking_name}.eneRST', 'output_rst_path': f'{self.docking_name}.rst'} 
        }

        # Check the properties
        self.check_properties(properties)
        # Check the arguments
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Dockrst <pydock.dockrst.Dockrst>` object."""
        
        # Dockrst Biobb
        if self.check_restart(): return 0

        # Rename input files, EXTERNAL -> INTERNAL
        renaming_dir = self.renaming_stage()
        # Stage files with correct names 
        self.stage_files()

        # Find  /relative/path/to/inputs/from/working/dir
        if self.container_path:
            io_path = self.container_volume_path
        else:
            io_path = self.stage_io_dict.get("unique_dir")

        # Create command path: io_path + /docking_name
        cmd_path = str(Path(io_path).joinpath(self.docking_name))

        # Create INI file for pyDock
        create_ini(output_path = str(Path(self.stage_io_dict.get("unique_dir")).joinpath(self.ini_file_name)),
                   receptor_prop = self.receptor_prop, ligand_prop = self.ligand_prop)

        # Create command line
        self.cmd = [self.binary_path, cmd_path, 'dockrst']

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Rename output files 
        rename_files(source_paths = self.io_dict["out"], destination_paths = self.external_output_paths)

        # Remove temporal files 
        self.tmp_files.append(self.stage_io_dict.get("unique_dir"))
        self.tmp_files.append(renaming_dir) 
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

def dockrst(input_rec_path: str, input_rec_H_path: str, input_rec_amber_path: str, 
            input_lig_path: str, input_lig_H_path: str, input_lig_amber_path: str, 
            input_rot_path: str, input_ene_path: str, output_rst_path: str, 
            output_ene_rst_path: str, properties: dict = None, **kwargs) -> int:
    """Create :class:`Dockrst <pydock.dockrst.Dockrst>` class and
    execute the :meth:`launch() <pydock.dockrst.Dockrst.launch>` method."""

    return Dockrst(input_rec_path = input_rec_path, input_rec_H_path = input_rec_H_path, input_rec_amber_path = input_rec_amber_path, 
                   input_lig_path = input_lig_path, input_lig_H_path = input_lig_H_path, input_lig_amber_path = input_lig_amber_path,
                   input_rot_path = input_rot_path, input_ene_path = input_ene_path, output_ene_rst_path = output_ene_rst_path,
                   output_rst_path = output_rst_path, properties = properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Wrapper of the pyDock dockrst module.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_rec_path', required=True, help='Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock. Accepted formats: pdb.')
    required_args.add_argument('--input_rec_H_path', required=True, help='Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. Accepted formats: pdb.')
    required_args.add_argument('--input_rec_amber_path', required=True, help='Receptor AMBER parameters for each atom in the pdb structure. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--input_lig_path', required=True, help='Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock. Accepted formats: pdb.')
    required_args.add_argument('--input_lig_H_path', required=True, help='Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--input_lig_amber_path', required=True, help='Ligand AMBER parameters for each atom in the pdb structure. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--input_rot_path', required=True, help='File containing the transformation matrix for all the docking poses. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--input_ene_path', required=True, help='File containing the energy ranking for all docking poses in input_rot_path. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--output_rst_path', required=True, help='File containing the scoring of each docking model based on the distance restraints.  File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')   
    required_args.add_argument('--output_ene_rst_path', required=True, help='Combination of input_ene_path with output_rst_path. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    dockrst(input_rec_path = args.input_rec_path
          ,input_rec_H_path = args.input_rec_H_path
          ,input_rec_amber_path = args.input_rec_amber_path
          ,input_lig_path= args.input_lig_path
          ,input_lig_H_path = args.input_lig_H_path
          ,input_lig_amber_path = args.input_lig_amber_path
          ,input_rot_path = args.input_rot_path
          ,input_ene_path = args.input_ene_path
          ,output_rst_path = args.output_rst_path
          ,output_ene_rst_path = args.output_ene_rst_path
          ,properties = properties)

if __name__ == '__main__':
    main()