#!/usr/bin/env python3

"""Module containing the Oda class and the command line interface."""
import argparse
from pathlib import Path
from biobb_common.tools import file_utils as fu
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools.file_utils import launchlogger
from biobb_pydock.pydock.common import rename_files, copy_files

# 1. Rename class as required
class Oda(BiobbObject):
    """
    | biobb_pydock Oda
    | Wrapper class for the `pyDock oda <https://life.bsc.es/pid/pydock/doc/tutorial.html#optimal-docking-area-oda-analysis-or-interface-prediction-from-protein-surface-desolvation-energy>`_ module.
    | The pyDock oda module is used analyze the optimal desolvation patch on a protein surface to predict potential binding interface sites

    Args:
        input_structure_path (str): Protein PDB file. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_oda_path (str): . File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_oda_H_path (str): . File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_oda_amber_path (str): . File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_oda_tab_path (str): . File type: output. `Sample file <>`_. Accepted formats:  ().
        properties (dic):
            * **subunit_name** (*str*) - ("subunit_name") Name for the protein subunit.
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

            from biobb_pydock.pydock.oda import oda

            prop = { 
                'subunit_name': 'receptor',
                }

            oda(input_structure_path='receptor.pdb',
                output_oda_path='receptor.pdb.oda',
                output_oda_H_path='receptor.pdb.oda.H',
                output_oda_tab_path='receptor.pdb.oda.ODAtab',
                output_oda_amber_path='receptor.oda.amber',
                properties=prop)

    Info:
        * wrapped_software:
            * name: pyDock oda
            * version: >=3.6.1
            * license: 
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    # Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, input_structure_path: str, output_oda_path: str, output_oda_H_path: str, output_oda_amber_path: str, 
                 output_oda_tab_path: str, properties: dict = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Properties common to all PyDock BB
        self.binary_path = properties.get('binary_path', 'pydock3') 

        # Properties specific for BB
        self.subunit_name = properties.get('subunit_name', 'subunit_name')

        # Save EXTERNAL filenames (only those that need self.subunit_name in their file name)
        self.external_input_paths = {'input_structure_path' : input_structure_path}
        self.external_output_paths = {'output_oda_path': output_oda_path, 'output_oda_H_path': output_oda_H_path, 
                                      'output_oda_amber_path': output_oda_amber_path, 'output_oda_tab_path': output_oda_tab_path}

        # Input/Output files (INTERNAL filenames)
        self.io_dict = { 
            'in':  { 'input_structure_path': f'{self.subunit_name}.pdb' }, 
            'out': { 'output_oda_path': f'{self.subunit_name}.pdb.oda','output_oda_H_path': f'{self.subunit_name}.pdb.oda.H', 
                     'output_oda_amber_path': f'{self.subunit_name}.oda.amber','output_oda_tab_path': f'{self.subunit_name}.pdb.oda.ODAtab'} 
        }

        # Check the properties
        self.check_properties(properties)
        # Check the arguments
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Oda <pydock.oda.Oda>` object."""
        
        # Oda Biobb
        if self.check_restart(): return 0

        # Rename input files, EXTERNAL -> INTERNAL
        renaming_dir = self.renaming_stage()
        # Stage files with correct names 
        self.stage_files()

        # Create oda command path: /relative/path/to/inputs/from/working/dir + /subunit_name.pdb
        if self.container_path:
            cmd_path = str(Path(self.container_volume_path).joinpath(f'{self.subunit_name}.pdb')) 
        else:
            cmd_path = str(Path(self.stage_io_dict.get("unique_dir")).joinpath(f'{self.subunit_name}.pdb')) 

        # Create command line
        self.cmd = [self.binary_path, cmd_path, 'oda']

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

def oda(input_structure_path: str, output_oda_path: str, output_oda_H_path: str, output_oda_amber_path: str, 
        output_oda_tab_path: str, properties: dict = None, **kwargs) -> int:
    """Create :class:`Oda <pydock.oda.Oda>` class and
    execute the :meth:`launch() <pydock.oda.Oda.launch>` method."""

    return Oda(input_structure_path = input_structure_path, output_oda_path = output_oda_path, output_oda_H_path = output_oda_H_path, 
               output_oda_amber_path = output_oda_amber_path, output_oda_tab_path = output_oda_tab_path,
               properties = properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Wrapper of the pyDock oda module.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_structure_path', required=True, help=' Protein PDB file. Accepted formats: pdb.')
    required_args.add_argument('--output_oda_path', required=True, help=' File type: output. Accepted formats: pdb.')
    required_args.add_argument('--output_oda_H_path', required=True, help=' File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--output_oda_amber_path', required=True, help=' File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--output_oda_tab_path', required=True, help=' File type: output. Accepted formats: pdb.')
   
    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    oda(input_structure_path = args.input_structure_path
        ,output_oda_path = args.output_oda_path
        ,output_oda_H_path = args.output_oda_H_path
        ,output_oda_amber_path= args.output_oda_amber_path
        ,output_oda_tab_path = args.output_oda_tab_path
        ,properties = properties)

if __name__ == '__main__':
    main()