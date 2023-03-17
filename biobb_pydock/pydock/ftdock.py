#!/usr/bin/env python3

"""Module containing the Ftdock class and the command line interface."""
import argparse
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger


# 1. Rename class as required
class Ftdock(BiobbObject):
    """
    | biobb_pydock FtDock
    | Wrapper class for the `pyDock ftdock <https://life.bsc.es/pid/pydock/doc/tutorial.html#ftdock-process>`_ module.
    | The pyDock ftdock module is used to generate docking positions using a Fast Fourier Transform algorithm (FFT).

    Args:
        input_receptor_path (str): Prepared receptor PDB file with pydock setup (the largest of the two proteins). File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_lig_path (str): Prepared ligand PDB file with pydock setup (will be rotated and translated). File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_ftdock_path (str) (Optional): Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock. docking_name_rec.pdb by default. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
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
        This is a use example of how to use the building block from Python::

            from biobb_pydock.pydock.ftdock import ftdock

            prop = { 
                'docking_name': 'docking_name'}

            ftdock(input_receptor_path='/path/to/my/Receptor/docking_name_rec.pdb',
                  input_lig_path='/path/to/my/Ligand/docking_name_lig.pdb',
                  output_ftdock_path='/path/to/ ',
                  properties=prop)

    Info:
        * wrapped_software:
            * name: pyDock ftdock
            * version: >=3.6.1
            * license: 
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    # Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, input_receptor_path: str, input_lig_path: str, output_ftdock_path: str,
                 properties: dict = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = { 
            'in': { 'input_receptor_path': input_receptor_path, 'input_lig_path': input_lig_path }, 
            'out': { 'output_receptor_path': output_receptor_path, 'output_ligand_path': output_ligand_path } 
        }

        # Properties specific for BB
        self.docking_name = properties.get('docking_name', 'docking_name')
        self.receptor_mol = properties.get('receptor_mol', 'A')
        self.receptor_newmol = properties.get('receptor_newmol', 'A')
        self.ligand_mol = properties.get('ligand_mol', 'A')
        self.ligand_newmol = properties.get('ligand_newmol', 'B')
        self.binary_path = properties.get('binary_path', 'zip')
        self.properties = properties

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

        # Create command line
        self.cmd = [self.binary_path, self.properties['docking_name'], 'ftdock']
        fu.log('Creating command line with instructions and required arguments', self.out_log, self.global_log)

        # 8. Uncomment to check the command line 
        print(' '.join(self.cmd))

        # Run Biobb block
        self.run_biobb()

        # If output paths are provided, change the output file names?

        # Copy files to host
        self.copy_to_host()

        # Remove temporal files
        self.tmp_files.append(self.stage_io_dict.get("unique_dir"))
        self.remove_tmp_files()

        # Check output arguments
        self.check_arguments(output_files_created=True, raise_exception=False)

        return self.return_code

def ftdock(input_receptor_path: str, input_lig_path: str, output_receptor_path: str, output_ligand_path: str, properties: dict = None, **kwargs) -> int:
    """Create :class:`Ftdock <pydock.ftdock.Ftdock>` class and
    execute the :meth:`launch() <pydock.ftdock.Ftdock.launch>` method."""

    return Ftdock(input_receptor_path = input_receptor_path, input_lig_path = input_lig_path, output_receptor_path = output_receptor_path, output_ligand_path = output_ligand_path,
                 properties = properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Wrapper of the pyDock pyDock3 ftdock module.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_receptor_path', required=True, help='Receptor PDB file (the largest of the two proteins). Accepted formats: pdb.')
    required_args.add_argument('--input_lig_path', required=True, help='Ligand PDB file (will be rotated and translated). Accepted formats: pdb.')
    parser.add_argument('--output_receptor_path', required=False, help='Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock. docking_name_rec.pdb by default. (optional). Accepted formats: pdb.')
    parser.add_argument('--output_ligand_path', required=False, help='Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock. docking_name_lig.pdb by default. (optional). Accepted formats: pdb.')
    
    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    ftdock(input_receptor_path = args.input_receptor_path
          ,input_lig_path = args.input_lig_path
          ,output_receptor_path = args.output_receptor_path
          ,output_ligand_path = args.output_ligand_path
          ,properties = properties)

if __name__ == '__main__':
    main()