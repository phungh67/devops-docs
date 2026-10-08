#!/bin/bash

COLOR_CLEAR='\e[0m'
COLOR_RED='\e[31m'
COLOR_GREEN='\e[32m'
COLOR_BLUE='\e[34m'
COLOR_YELLOW='\e[33m'
COLOR_PURPLE='\e[35m'
COLOR_CYAN='\e[36m'


if [ $# -lt 1 ]
then
	echo "Seems like you forgot some arguments..."
	echo "Usage: $0 <Simulation Directory> "
	exit

fi


rm -rf temp.txt 


Sim_DIR=$1    #The simulation directory 
benchmarks="dijkstra qsort string_search gsm jpeg"


################ Performance

statsfilename="sim.out"
stats="Instructions Cycles"

echo $benchmarks
for s in $stats
do
echo -n "$s,"
	for b in $benchmarks
	do
		if [ ! -f ${Sim_DIR}/${b}/$statsfilename ] 
		then
			echo -n "NaN,"
		else
			res=$(cat ${Sim_DIR}/${b}/$statsfilename | fgrep $s | awk '{print $3}')
			echo -n "$res,"
		fi
	done
	echo ""
done


#################### Power


statsfilename="power.txt"
stats=("Area =" "Peak Dynamic =" "Runtime Dynamic =" "Subthreshold Leakage =" )


for s in "${stats[@]}"
do
	echo -n "$s,"
	for b in $benchmarks
	do
		if [ ! -f ${Sim_DIR}/${b}/$statsfilename ] 
		then
			echo -n "NaN,"
		else
			cat ${Sim_DIR}/${b}/$statsfilename | fgrep -A6 "Core:" > temp.txt
			cat temp.txt | fgrep "$s" > temp1.txt
			res=$(cat temp1.txt | awk '{print  $(NF-1)}')
			echo -n "$res,"
		fi
	done
	echo ""
done

