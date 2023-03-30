from biobb_pydock.pydock.ftdock import ftdock

input_receptor_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/ftdock/prepared_receptor.pdb'
input_lig_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/ftdock/prepared_ligand.pdb'

container_volume_path = '/data'
container_working_dir = container_volume_path  # Avoid execution in $HOME, tmp files are created in the working dir
container_path = 'singularity'
container_generic_command = 'exec'
container_image = '/shared/work/NBD_Utilities/pyDock3/3.6.1/nbd_pydock.sif' 

prop = { 
    'docking_name': 'docking_name',
    'container_path': container_path,
    'container_image': container_image,
    'container_volume_path': container_volume_path,
    'container_working_dir': container_working_dir,
    'container_generic_command': container_generic_command}
   
ftdock(input_rec_path=input_receptor_path,
    input_lig_path=input_lig_path,
    output_ftdock_path='ftdock_output.ftdock',
    output_rot_path='rotftdock_output.rot',
    properties=prop)
