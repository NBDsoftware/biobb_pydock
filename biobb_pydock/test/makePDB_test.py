from biobb_pydock.pydock.makePDB import makePDB

input_rec_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/makePDB/prepared_receptor.pdb'
input_rec_H_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/makePDB/prepared_receptor.pdb.H'
input_rec_amber_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/makePDB/prepared_receptor.pdb.amber'
input_lig_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/makePDB/prepared_ligand.pdb'
input_lig_H_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/makePDB/prepared_ligand.pdb.H'
input_lig_amber_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/makePDB/prepared_ligand.pdb.amber'
input_rot_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/makePDB/rotftdock_output.rot'
input_ene_path = '/shared/scratch/jobs/pnavarro/2023_EUCANSHARE/biobb_pydock/biobb_pydock/test/data/makePDB/dockser_output.ene' 

container_volume_path = '/data'
container_working_dir = '/'  # Avoid execution in $HOME, tmp files are created in the working dir
container_path = 'singularity'
container_generic_command = 'exec'
container_image = '/shared/work/NBD_Utilities/pyDock3/3.6.1/nbd_pydock.sif' 

prop = { 
    'docking_name': 'docking_name',
    'rank1': 1,
    'rank2': 3,
    'container_path': container_path,
    'container_image': container_image,
    'container_volume_path': container_volume_path,
    'container_working_dir': container_working_dir,
    'container_generic_command': container_generic_command}

makePDB(input_rec_path=input_rec_path,
        input_rec_H_path=input_rec_H_path,
        input_rec_amber_path=input_rec_amber_path,
        input_lig_path=input_lig_path,
        input_lig_H_path=input_lig_H_path,
        input_lig_amber_path=input_lig_amber_path,
        input_rot_path=input_rot_path,
        input_ene_path=input_ene_path,
        output_zip_path = 'docking_conformations.zip',
        properties=prop)
