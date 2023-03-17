from biobb_pydock.pydock.setup import setup

prop = { 
    'docking_name': 'docking_name',
    'receptor': 
        {'mol': 'A',
        'newmol': 'A'},
    'ligand': 
        {'mol': 'A',
        'newmol': 'B'}}

setup(input_receptor_path='.pdb',
    input_lig_path='.pdb',
    output_receptor_path='docking_name_rec.pdb',
    output_ligand_path='docking_name_lig.pdb',
    properties=prop)