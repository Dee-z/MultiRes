#!/usr/bin/env bash
#
#SBATCH --mem=10000
#SBATCH --job-name=no-variates-only-seq
#SBATCH --partition=1080ti-long
#SBATCH --gres=gpu:1
#SBATCH --output=cross_val_multi_task_autoencoder_no_covariates-%A.out
#SBATCH --error=cross_val_multi_task_autoencoder_no_covariates-%A.err
#SBATCH --mail-type=ALL
#SBATCH --ntasks-per-node=6
#SBATCH --nodes=1
#SBATCH --time=2-00:00:00
#SBATCH --mail-user=abhinavshaw@umass.edu

# Log the jobid.
echo $SLURM_JOBID - `hostname` >> ~/gypsum-jobs.txt

cd ~/projects/MultiRes/student_life
PYTHONPATH=../ python -m src.experiments.multitask_learning.multi_task_no_covariate
