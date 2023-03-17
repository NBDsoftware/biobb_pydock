from biobb_pydock.pydock.setup import setup

input_receptor_path = '/path/to/biobb_pydock/biobb_pydock/test/data/setup/receptor.pdb'
input_lig_path = '/path/to/biobb_pydock/biobb_pydock/test/data/setup/ligand.pdb'

container_path = 'singularity'
container_generic_command = 'exec'
container_image = '/path/to/nbd_pydock.sif' 

prop = { 
    'container_path': container_path,
    'container_generic_command': container_generic_command,
    'container_image': container_image,
    'docking_name': 'docking_name',
    'receptor':               
        {'mol': 'A',
        'newmol': 'A'},
    'ligand': 
        {'mol': 'A',
        'newmol': 'B'}}

setup(input_receptor_path=input_receptor_path,
    input_lig_path=input_lig_path,
    output_receptor_path='new_receptor.pdb', # Any name/path
    output_ligand_path='new_ligand.pdb',     # Any name/path
    properties=prop)
