from biobb_pydock.pydock.oda import oda

input_structure_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/oda/receptor.pdb'

container_volume_path = '/data'
container_working_dir = '/'  # Avoid execution in $HOME, tmp files are created in the working dir
container_path = 'singularity'
container_generic_command = 'exec'
container_image = '/shared/work/NBD_Utilities/pyDock3/3.6.1/nbd_pydock.sif' 

prop = { 
    'subunit_name': 'subunit_name',
    'container_path': container_path,
    'container_image': container_image,
    'container_volume_path': container_volume_path,
    'container_working_dir': container_working_dir,
    'container_generic_command': container_generic_command}

oda(input_structure_path=input_structure_path,
    output_oda_path='receptor.pdb.oda',
    output_oda_H_path='receptor.pdb.oda.H',
    output_oda_tab_path='receptor.pdb.oda.ODAtab',
    output_oda_amber_path='receptor.oda.amber',
    properties=prop)
