from biobb_pydock.pydock.setup import setup

input_receptor_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/setup/receptor.pdb'
input_lig_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/setup/ligand.pdb'
input_ref_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/setup/reference.pdb'

container_volume_path = '/data'
container_working_dir = container_volume_path  # Avoid execution in $HOME, tmp files are created in the working dir
container_path = 'singularity'
container_generic_command = 'exec'
container_image = '/shared/work/NBD_Utilities/pyDock3/3.6.1/nbd_pydock.sif' 

prop_ref = { 
    'docking_name': 'docking_name',
    'receptor': 
        {'mol': 'A',
        'newmol': 'A'},
    'ligand': 
        {'mol': 'A',
        'newmol': 'B'},
    'reference':
        {'recmol': 'A',
         'ligmol': 'H',
         'newrecmol': 'A',
         'newligmol': 'B'},
    'container_path': container_path,
    'container_image': container_image,
    'container_volume_path': container_volume_path,
    'container_working_dir': container_working_dir,
    'container_generic_command': container_generic_command}

prop = { 
    'docking_name': 'docking_name',
    'receptor': 
        {'mol': 'A',
        'newmol': 'A'},
    'ligand': 
        {'mol': 'A',
        'newmol': 'B'},
    'container_path': container_path,
    'container_image': container_image,
    'container_volume_path': container_volume_path,
    'container_working_dir': container_working_dir,
    'container_generic_command': container_generic_command}

setup(input_rec_path=input_receptor_path,
      input_lig_path=input_lig_path,
      input_ref_path=input_ref_path,
      output_rec_path='prepared_receptor.pdb',
      output_rec_H_path='prepared_receptor.pdb.H',
      output_rec_amber_path='prepared_receptor.pdb.amber',
      output_lig_path='prepared_ligand.pdb',
      output_lig_H_path='prepared_ligand.pdb.H',
      output_lig_amber_path='prepared_ligand.pdb.amber',
      output_ref_path='prepared_reference.pdb',
      properties=prop_ref)
