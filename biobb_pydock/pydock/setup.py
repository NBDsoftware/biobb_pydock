#!/usr/bin/env python3

"""Module containing the Setup class and the command line interface."""
import argparse
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools.file_utils import launchlogger
from biobb_pydock.pydock.common import create_ini, rename_files


# 1. Rename class as required
class Setup(BiobbObject):
    """
    | biobb_pydock Setup
    | Wrapper class for the `pyDock setup <https://life.bsc.es/pid/pydock/doc/tutorial.html#setup-process>`_ module.
    | The pyDock setup module is used to prepare the input files for the docking process.

    Args:
        input_rec_pdb_path (str): Receptor PDB file (the largest of the two proteins). Provide either the pdb file or AMBER coordinates and topology files. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        input_rec_coords_path (str) (Optional): Receptor AMBER coordinates file (the largest of the two proteins). Provide either AMBER coordinates and topology or the pdb file. File type: input. Accepted formats: inpcrd (edam:format_3878), restrt (edam:format_3886), rs7 (edam:format_3886), crd (edam:format_3878).
        input_rec_top_path (str) (Optional): Receptor AMBER topology file (the largest of the two proteins). Provide either AMBER coordinates and topology or the pdb file. File type: input. Accepted formats: prmtop (edam:format_3881), top (edam:format_3881), parm7 (edam:format_3881)
        input_lig_pdb_path (str): Ligand PDB file (will be rotated and translated). Provide either the pdb file or AMBER coordinates and topology files. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476). 
        input_lig_coords_path (str) (Optional): Ligand AMBER coordinates file (will be rotated and translated). Provide either AMBER coordinates and topology or the pdb file. File type: input. Accepted formats: inpcrd, restrt, rs7, crd.
        input_lig_top_path (str) (Optional): Ligand AMBER topology file (will be rotated and translated). Provide either AMBER coordinates and topology or the pdb file. File type: input. Accepted formats: prmtop (edam:format_3881), top (edam:format_3881), parm7 (edam:format_3881)
        input_ref_path (str) (Optional): Reference PDB file. File type: input. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_rec_path (str): Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_rec_H_path (str): Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_rec_amber_path (str): Receptor AMBER parameters for each atom in the pdb structure. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_lig_path (str): Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_lig_H_path (str): Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_lig_amber_path (str): Ligand AMBER parameters for each atom in the pdb structure. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        output_ref_path (str) (Optional): Reference PDB file with the correct chain name adapted for pyDock dockser. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).
        properties (dic):
            * **docking_name** (*str*) - ("docking_name") Name for the docking.
            * **receptor** (*dict*) - ("{}") Receptor dictionary with "mol" (chain name of receptor in input_rec_pdb_path) and "newmol" (new chain name of receptor in output_rec_path). Do not include "pdb" file here.
            * **ligand** (*dict*) - ("{}") Ligand dictionary with "mol" (chain name of ligand in input_ligand_path) and "newmol" (new chain name of ligand in output_lig_path, different from receptor "newmol"). Do not include "pdb" here.
            * **reference** (*dict*) - ("{}") Reference dictionary with "recmol" (chain name of receptor in reference pdb), "ligmol" (chain name of ligand in reference pdb). Do not include "pdb", "newrcmol" or "newligmol" here.
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

            from biobb_pydock.pydock.setup import setup

            prop = { 
                'docking_name': 'docking_name',
                'receptor': 
                    {'mol': 'A',
                     'newmol': 'A'},
                'ligand': 
                    {'mol': 'A',
                     'newmol': 'B'}}

            setup(input_rec_pdb_path='receptor.pdb',
                  input_lig_pdb_path='ligand.pdb',
                  input_ref_path='reference.pdb',
                  output_rec_path='prepared_receptor.pdb',
                  output_rec_H_path='prepared_receptor.pdb.H',
                  output_rec_amber_path='prepared_receptor.pdb.amber',
                  output_lig_path='prepared_ligand.pdb',
                  output_lig_H_path='prepared_ligand.pdb.H',
                  output_lig_amber_path='prepared_ligand.pdb.amber',
                  output_ref_path='prepared_reference.pdb',
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
    def __init__(self, output_rec_path: str, output_rec_H_path: str, output_rec_amber_path: str, output_lig_path: str, 
                 output_lig_H_path: str, output_lig_amber_path: str, input_rec_pdb_path: str = None, input_rec_coords_path: str = None, 
                 input_rec_top_path: str = None, input_lig_pdb_path: str = None, input_lig_coords_path: str = None, input_lig_top_path: str = None,
                 input_ref_path: str = None, output_ref_path: str = None, properties: dict = None, **kwargs) -> None:
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
        self.reference = properties.get('reference')
        self.ini_file_name = f'{self.docking_name}.ini'

        # Save EXTERNAL filenames (only those that need self.docking_name in their file name) - arbitrary names for input files are ok in setup module
        self.external_output_paths = {'output_rec_path': output_rec_path, 'output_rec_H_path': output_rec_H_path, 'output_rec_amber_path': output_rec_amber_path,
                                      'output_lig_path': output_lig_path, 'output_lig_H_path': output_lig_H_path, 'output_lig_amber_path': output_lig_amber_path,
                                      'output_ref_path': output_ref_path}

        # Input/Output files (INTERNAL filenames)
        self.io_dict = { 
            'in': { 'input_rec_pdb_path': input_rec_pdb_path, 'input_rec_coords_path': input_rec_coords_path, 'input_rec_top_path': input_rec_top_path,
                    'input_lig_pdb_path': input_lig_pdb_path, 'input_lig_coords_path': input_lig_coords_path, 'input_lig_top_path': input_lig_top_path, 
                    'input_ref_path': input_ref_path}, 
            'out': { 'output_rec_path': f'{self.docking_name}_rec.pdb','output_rec_H_path': f'{self.docking_name}_rec.pdb.H','output_rec_amber_path': f'{self.docking_name}_rec.pdb.amber', 
                     'output_lig_path': f'{self.docking_name}_lig.pdb','output_lig_H_path': f'{self.docking_name}_lig.pdb.H','output_lig_amber_path': f'{self.docking_name}_lig.pdb.amber',
                     'output_ref_path': f'{self.docking_name}_ref.pdb'} 
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

        # Create command path: /input/output/path + /docking_name
        if self.container_path:
            cmd_path = str(Path(self.container_volume_path).joinpath(self.docking_name))
        else:
            cmd_path = str(Path(self.stage_io_dict.get("unique_dir")).joinpath(self.docking_name))

        # Create INI file for pyDock 
        create_ini(output_path = str(Path(self.stage_io_dict.get("unique_dir")).joinpath(self.ini_file_name)),
                   receptor_prop = self.receptor, ligand_prop = self.ligand, reference_prop = self.reference,
                   input_paths = self.stage_io_dict["in"])

        # Create command line
        self.cmd = [self.binary_path, cmd_path, 'setup']

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Rename output files 
        rename_files(source_paths = self.io_dict["out"], destination_paths = self.external_output_paths)

        # Remove temporal files 
        self.tmp_files.append(self.stage_io_dict.get("unique_dir"))
        self.remove_tmp_files()

        # Check output arguments
        self.check_arguments(output_files_created=True, raise_exception=False)

        return self.return_code

def setup(output_rec_path: str, output_rec_H_path: str, output_rec_amber_path: str, output_lig_path: str, output_lig_H_path: str, 
          output_lig_amber_path: str, input_rec_pdb_path: str = None, input_rec_coords_path: str = None, input_rec_top_path: str = None, 
          input_lig_pdb_path: str = None, input_lig_coords_path: str = None, input_lig_top_path: str = None,
          input_ref_path: str = None, output_ref_path: str = None, properties: dict = None, **kwargs) -> int:
    """Create :class:`Setup <pydock.setup.Setup>` class and
    execute the :meth:`launch() <pydock.setup.Setup.launch>` method."""

    return Setup(input_rec_pdb_path = input_rec_pdb_path, input_rec_coords_path = input_rec_coords_path, input_rec_top_path = input_rec_top_path, 
                 input_lig_pdb_path = input_lig_pdb_path, input_lig_coords_path = input_lig_coords_path, input_lig_top_path = input_lig_top_path,
                 input_ref_path = input_ref_path, output_rec_path = output_rec_path, output_rec_H_path = output_rec_H_path, 
                 output_rec_amber_path = output_rec_amber_path, output_lig_path = output_lig_path, output_lig_H_path = output_lig_H_path, 
                 output_lig_amber_path = output_lig_amber_path, output_ref_path = output_ref_path, properties = properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Wrapper of the pyDock setup module.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--output_rec_path', required=True, help='Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock. Accepted formats: pdb.')
    required_args.add_argument('--output_rec_H_path', required=True, help='Receptor PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--output_rec_amber_path', required=True, help='Receptor AMBER parameters for each atom in the pdb structure. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--output_lig_path', required=True, help='Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock. Accepted formats: pdb.')
    required_args.add_argument('--output_lig_H_path', required=True, help='Ligand PDB file with the correct chain name adapted for pyDock ftdock or zdock and with hydrogens. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    required_args.add_argument('--output_lig_amber_path', required=True, help='Ligand AMBER parameters for each atom in the pdb structure. File type: output. `Sample file <>`_. Accepted formats: pdb (edam:format_1476).')
    parser.add_argument('--input_rec_pdb_path', required=False, help='Receptor PDB file (the largest of the two proteins). Accepted formats: pdb.')
    parser.add_argument('--input_rec_coords_path', required=False, help='Receptor AMBER coordinates file (the largest of the two proteins). Provide either AMBER coordinates and topology or the pdb file. File type: input. Accepted formats: inpcrd, restrt, rs7, crd.')
    parser.add_argument('--input_rec_top_path', required=False, help='Receptor AMBER topology file (the largest of the two proteins). Provide either AMBER coordinates and topology or the pdb file. File type: input. Accepted formats: prmtop, top, parm7')
    parser.add_argument('--input_lig_pdb_path', required=False, help='Ligand PDB file (will be rotated and translated). Accepted formats: pdb.')
    parser.add_argument('--input_lig_coords_path', required=False, help='Ligand AMBER coordinates file (will be rotated and translated). Provide either AMBER coordinates and topology or the pdb file. File type: input. Accepted formats: inpcrd, restrt, rs7, crd.')
    parser.add_argument('--input_lig_top_path', required=False, help='Ligand AMBER topology file (will be rotated and translated). Provide either AMBER coordinates and topology or the pdb file. File type: input. Accepted formats: prmtop, top, parm7')
    parser.add_argument('--input_ref_path', required=False, help='Reference PDB file. Accepted formats: pdb.')
    parser.add_argument('--output_ref_path', required=False, help='Reference PDB file with the correct chain name adapted for pyDock dockser. Accepted formats: pdb.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    setup(input_rec_pdb_path = args.input_rec_pdb_path
          ,input_rec_coords_path = args.input_rec_coords_path
          ,input_rec_top_path = args.input_rec_top_path
          ,input_lig_pdb_path = args.input_lig_pdb_path
          ,input_lig_coords_path = args.input_lig_coords_path
          ,input_lig_top_path = args.input_lig_top_path
          ,input_ref_path = args.input_ref_path
          ,output_rec_path = args.output_rec_path
          ,output_rec_H_path= args.output_rec_H_path
          ,output_rec_amber_path = args.output_rec_amber_path
          ,output_lig_path = args.output_lig_path
          ,output_lig_H_path = args.output_lig_H_path
          ,output_lig_amber_path = args.output_lig_amber_path
          ,output_ref_path = args.output_ref_path
          ,properties = properties)

if __name__ == '__main__':
    main()