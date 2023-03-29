#!/usr/bin/env python3

"""Module containing the Ftdock class and the command line interface."""
import argparse
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools.file_utils import launchlogger
from biobb_pydock.pydock.common import rename_files, copy_files

# 1. Rename class as required
class Ftdock(BiobbObject):
    """
    | biobb_pydock FtDock
    | Wrapper class for the `pyDock ftdock <https://life.bsc.es/pid/pydock/doc/tutorial.html#sampling-using-fast-fourier-transform-fft-methods>`_ module
    | and the `pyDock rotftdock <https://life.bsc.es/pid/pydock/doc/tutorial.html#sampling-using-fast-fourier-transform-fft-methods>`_ module.
    | The pyDock ftdock module is used to generate docking positions using a Fast Fourier Transform algorithm (FFT).
    | The pyDock rotftdock module is used to generate the transformation matrix for all the docking poses.

    Args:
        input_receptor_path (str): Prepared receptor PDB file with pydock setup (the largest of the two proteins). File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_lig_path (str): Prepared ligand PDB file with pydock setup (will be rotated and translated). File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_ftdock_path (str): File with docking poses expressed as a translation vector and 3 rotation angles. File type: output. `Sample file <>`_. Accepted formats:  (edam:).
        output_rot_path (str): File containing the transformation matrix for all the docking poses. File type: output. `Sample file <>`_. Accepted formats:  (edam:).
        properties (dic):
            * **docking_name** (*str*) - ("docking_name") Name for the docking.
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

            from biobb_pydock.pydock.ftdock import ftdock

            prop = { 
                'docking_name': 'docking_name'}

            ftdock(input_receptor_path='/path/to/my/Receptor/prepared_receptor.pdb',
                  input_lig_path='/path/to/my/Ligand/prepared_ligand.pdb',
                  output_ftdock_path='/path/to/new/docking/positions/dock_poses.ftdock',
                  output_rot_path='/path/to/poses_matrix.rot',
                  properties=prop)

    Info:
        * wrapped_software:
            * name: pyDock ftdock and pyDock rotftdock
            * version: >=3.6.1
            * license: 
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    # Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, input_receptor_path: str, input_lig_path: str, output_ftdock_path: str,
                 output_rot_path: str, properties: dict = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Properties common to all PyDock BB
        self.docking_name = properties.get('docking_name', 'docking_name')
        self.binary_path = properties.get('binary_path', 'pydock3') 

        # Save external user-defined paths in properties (only those that need "docking_name" in their file name)
        self.external_input_paths = {'input_receptor_path': input_receptor_path, 'input_lig_path': input_lig_path}
        self.external_output_paths = {'output_ftdock_path': output_ftdock_path, 'output_rot_path': output_rot_path}

        # Input/Output files 
        self.io_dict = { 
            'in': { 'input_receptor_path': f'{self.docking_name}_rec.pdb', 'input_lig_path': f'{self.docking_name}_lig.pdb' }, 
            'out': { 'output_ftdock_path': f'{self.docking_name}.ftdock', 'output_rot_path': f'{self.docking_name}.rot'} 
        }

        # Copy input files to stage them with correct names
        copy_files(source_paths = self.external_input_paths, destination_paths = self.io_dict["in"])
        
        # Check the properties
        self.check_properties(properties)
        # Check the arguments
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Ftdock <pydock.ftdock.Ftdock>` object."""
        
        # Ftdock Biobb
        if self.check_restart(): return 0
        self.stage_files()

        # Create ftdock command path: /path/to/inputs + /docking_name
        if self.container_path:
            ftdock_path = str(Path(self.container_volume_path).joinpath(self.docking_name)) 
        else:
            ftdock_path = str(Path(self.stage_io_dict.get("unique_dir")).joinpath(self.docking_name)) 

        # Create rotftdock command path: /working_dir + /docking_name
        rotftdock_path = self.docking_name

        # Create command line
        self.cmd = [self.binary_path, ftdock_path, 'ftdock', '&&', self.binary_path, rotftdock_path, 'rotftdock']

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Rename output files 
        rename_files(source_paths = self.io_dict["out"], destination_paths = self.external_output_paths)

        # Remove temporal files
        self.tmp_files.append(self.stage_io_dict.get("unique_dir"))
        self.tmp_files.extend(list(self.io_dict['in'].values()))     # Add duplicated input files
        self.remove_tmp_files()

        # Check output arguments
        self.check_arguments(output_files_created=True, raise_exception=False)

        return self.return_code

def ftdock(input_receptor_path: str, input_lig_path: str, output_ftdock_path: str, output_rot_path: str, properties: dict = None, **kwargs) -> int:
    """Create :class:`Ftdock <pydock.ftdock.Ftdock>` class and
    execute the :meth:`launch() <pydock.ftdock.Ftdock.launch>` method."""

    return Ftdock(input_receptor_path = input_receptor_path, input_lig_path = input_lig_path, output_ftdock_path = output_ftdock_path,
                  output_rot_path = output_rot_path, properties = properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Wrapper of the pyDock ftdock and rotftdock modules.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_receptor_path', required=True, help='Receptor PDB file (the largest of the two proteins). Accepted formats: pdb.')
    required_args.add_argument('--input_lig_path', required=True, help='Ligand PDB file (will be rotated and translated). Accepted formats: pdb.')
    required_args.add_argument('--output_ftdock_path', required=True, help='Output ftdock file. Accepted formats: ftdock')
    required_args.add_argument('--output_rot_path', required=True, help='Output rotftdock file. Accepted formats: rot')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    ftdock(input_receptor_path = args.input_receptor_path
          ,input_lig_path = args.input_lig_path
          ,output_ftdock_path = args.output_ftdock_path
          ,output_rot_path = args.output_rot_path
          ,properties = properties)

if __name__ == '__main__':
    main()