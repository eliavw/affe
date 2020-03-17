#!/bin/bash

echo === === === ALPHA RUN REMOTE === === ===
#   ----    ----    ----    ----    #
#           0. Inspect env          #
#   ----    ----    ----    ----    #

# I need to add one because we count from zero.
nb_processes_to_execute=$((nb_procs + 1))

echo "nb processses      $nb_processes_to_execute"
echo "commands fname     $commands_fname"
echo "exe atom fname     $exe_atom_fname"
echo "nodefile_fname     $nodefile_fname"
echo "remote conda       $remote_conda"

#   ----    ----    ----    ----    #
#           2. Script               #
#   ----    ----    ----    ----    #

seq 0 $nb_procs | parallel --gnu --progress --sshloginfile $nodefile_fname "export PATH="$remote_conda:$PATH";\
                  OMP_NUM_THREADS=1 python $exe_atom_fname $commands_fname $1"

echo === === === OMEGA RUN REMOTE === === ===
