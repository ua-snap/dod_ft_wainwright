# HOW TO RUN IT IN A CLI-way...
def run_model( fn, command ):
	import os, subprocess
	head = '#!/bin/sh\n' + \
			'#SBATCH --ntasks=32\n' + \
			'#SBATCH --nodes=1\n' + \
			'#SBATCH --ntasks-per-node=32\n' + \
			'#SBATCH --account=snap\n' + \
			'#SBATCH --mail-type=FAIL\n' + \
			'#SBATCH --mail-user=malindgren@alaska.edu\n' + \
			'#SBATCH -p main\n'
	
	with open( fn, 'w' ) as f:
		f.writelines( head + '\n' + command + '\n' )
	subprocess.call([ 'sbatch', fn ])
	return 1

if __name__ == '__main__':
	import subprocess, os, itertools

	models = [ 'NCAR-CCSM4','GFDL-CM3', 'IPSL-CM5A-LR', 'MRI-CGCM3', 'GISS-E2-R' ]
	scenarios = [ 'rcp45', 'rcp60', 'rcp85']

	pyfile = '/workspace/Shared/Users/malindgren/TEST_NANCY_DOD/code/run_alfpp_militarylands.py'
	for model, scenario in itertools.product( models, scenarios ):
		command = 'python {} -m {} -s {}'.format( pyfile, model, scenario )  
		slurm_dir = '/workspace/Shared/Users/malindgren/TEST_NANCY_DOD/alfresco/slurm'
		os.chdir(slurm_dir)
		if not os.path.exists( slurm_dir ):
			_ = os.makedirs( slurm_dir )
		slurm_fn = os.path.join( slurm_dir, 'slurm_alf_pp_{}_{}.sbatch'.format(model, scenario) )
		run_model( slurm_fn, command )