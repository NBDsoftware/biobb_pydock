#!/usr/bin/env python3

"""Module containing the Setup class and the command line interface."""
import argparse
import shutil
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_pydock.pydock.common import create_ini


# 1. Rename class as required
class Setup(BiobbObject):
    """
    | biobb_pydock Setup
    | Wrapper class for the `pyDock setup <https://life.bsc.es/pid/pydock/doc/tutorial.html#setup-process>`_ module.
    | The pyDock setup module is used to prepare the input files for the docking process.

    Args:
        input_receptor_path (str): Receptor PDB file (the largest of the two proteins). File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_lig_path (str): Ligand PDB file (will be rotated and translated). File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_receptor_path (str) (Optional): Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock. docking_name_rec.pdb by default. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_ligand_path (str) (Optional): Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock. 'docking_name'_lig.pdb by default. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        properties (dic):
            * **docking_name** (*str*) - ("docking_name") Name for the docking.
            * **receptor** (*dict*) - ("{}") Original and new chain names for receptor protein.
            * **ligand** (*dict*) - ("{}") Original and new chain names for ligand protein.
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

            from biobb_pydock.pydock.setup import setup

            prop = { 
                'docking_name': 'docking_name',
                'receptor': 
                    {'mol': 'A',
                     'newmol': 'A'},
                'ligand': 
                    {'mol': 'A',
                     'newmol': 'B'}}

            setup(input_receptor_path='/path/to/my/Receptor/receptor.pdb',
                  input_lig_path='/path/to/my/Ligand/ligand.pdb',
                  output_receptor_path='/path/to/new/Receptor/docking_name_rec.pdb',
                  output_ligand_path='/path/to/new/Ligand/docking_name_lig.pdb',
                  properties=prop)

    Info:
        * wrapped_software:
            * name: pyDock setup
            * version: >=3.6.1
            * license: 
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    # Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, input_receptor_path: str, input_lig_path: str, output_receptor_path: str = None, output_ligand_path: str = None,
                 properties: dict = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Properties common to all PyDock BB
        self.docking_name = properties.get('docking_name', 'docking_name')
        self.binary_path = properties.get('binary_path', 'pydock3')

        # Properties specific for BB
        self.receptor = properties.get('receptor', {'mol': 'A','newmol': 'A'})
        self.ligand = properties.get('ligand', {'mol': 'A','newmol': 'B'})
        self.output_ini_path = properties.get('output_ini_path', f'{self.docking_name}.ini')

        # Save external user-defined paths in properties (only the ones that will be modified)
        self.original_output_paths = {'output_receptor_path': output_receptor_path, 'output_ligand_path': output_ligand_path }

        # Input/Output files with correct output paths (pyDock makes assumptions about the file names)
        self.io_dict = { 
            'in': { 'input_receptor_path': input_receptor_path, 'input_lig_path': input_lig_path }, 
            'out': { 'output_receptor_path': f'{self.docking_name}_rec.pdb', 'output_ligand_path': f'{self.docking_name}_lig.pdb' } 
        }

        # Check the properties
        self.check_properties(properties)
        # Check the arguments
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Setup <pydock.setup.Setup>` object."""
        
        # Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()

        # Create INI file
        self.output_ini_path = create_ini(output_ini_path = str(Path(self.stage_io_dict.get("unique_dir")).joinpath(self.output_ini_path)),
                                          receptor = self.receptor, receptor_pdb=Path(self.stage_io_dict.get("input_receptor_path")).name,
                                          ligand = self.ligand, ligand_pdb=Path(self.stage_io_dict.get("input_lig_path")).name)

        # Copy INI file to container
        if self.container_path:
            self.output_ini_path = str(Path(self.container_volume_path).joinpath(Path(self.output_ini_path).name))

        # Create command line
        self.cmd = [self.binary_path, self.properties['docking_name'], 'setup']

        # 8. Uncomment to check the command line 
        print(' '.join(self.cmd))

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Rename output files using the user-defined external paths
        for file_ref, original_file_path in self.original_output_paths.items():
            if Path(self.io_dict["out"][file_ref]).exists():
                shutil.copy2(self.io_dict["out"][file_ref], original_file_path)

        # Remove temporal files
        self.tmp_files.append(self.stage_io_dict.get("unique_dir"))
        self.remove_tmp_files()

        # Check output arguments
        self.check_arguments(output_files_created=True, raise_exception=False)

        return self.return_code

def setup(input_receptor_path: str, input_lig_path: str, output_receptor_path: str = None, output_ligand_path: str = None, properties: dict = None, **kwargs) -> int:
    """Create :class:`Setup <pydock.setup.Setup>` class and
    execute the :meth:`launch() <pydock.setup.Setup.launch>` method."""

    return Setup(input_receptor_path = input_receptor_path, input_lig_path = input_lig_path, output_receptor_path = output_receptor_path, output_ligand_path = output_ligand_path,
                 properties = properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Wrapper of the pyDock pyDock3 setup module.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
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
    setup(input_receptor_path = args.input_receptor_path
          ,input_lig_path = args.input_lig_path
          ,output_receptor_path = args.output_receptor_path
          ,output_ligand_path = args.output_ligand_path
          ,properties = properties)

if __name__ == '__main__':
    main()