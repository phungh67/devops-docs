#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $SCRIPT_DIR/env.sh


COLOR_CLEAR='\e[0m'
COLOR_RED='\e[31m'
COLOR_GREEN='\e[32m'
COLOR_BLUE='\e[34m'
COLOR_YELLOW='\e[33m'
COLOR_PURPLE='\e[35m'
COLOR_CYAN='\e[36m'


if [ $# -lt 2 ]
then
	echo "Seems like you forgot some arguments..."
	echo "Usage: $0 <Simulation Directory> <Configuration file (withour .cfg)>"
	exit

fi

Sniper_Home='sniper'
APP_Home='./apps'  
Sim_DIR=$1    #The simulation directory 
Config_file=$2   #The name of the configuration file (without ".cfg")
Config="-n 1 -c gainestown -c ${Sim_DIR}/${Config_file}.cfg --power"


chmod +x apps/dijkstra/dijkstra_small
chmod +x apps/gsm-untoast/untoast
chmod +x apps/qsort/qsort_small
chmod +x apps/jpeg-cjpeg/cjpeg
chmod +x apps/stringsearch/search_small 

OVERALL_STARTTIME=`date +%s.%N`

STARTTIME=`date +%s.%N`
echo -e "${COLOR_GREEN}running app dijkstra until succeed."
Result=${Sim_DIR}/dijkstra/sim.out
#while [ ! -s Result ]
while :
do
	rm -rf ${Sim_DIR}/dijkstra
	mkdir -p ${Sim_DIR}/dijkstra
	./runsim_dijkstra.sh $1 $2
	if [ -s "$Result" ]
	then
		break
	else
		sleep 0.1s
	fi
done
ENDTIME=`date +%s.%N`
RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
echo -e "${COLOR_GREEN}dijkstra Simulation Succeed!. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"


STARTTIME=`date +%s.%N`
echo -e "${COLOR_GREEN}running app search_small until succeed."
Result=${Sim_DIR}/string_search/sim.out
echo ${Result}
while :
do
	rm -rf ${Sim_DIR}/string_search
	mkdir -p ${Sim_DIR}/string_search
	./runsim_stringsearch.sh $1 $2
	if [ -s "$Result" ]
	then
		break
	else
		sleep 0.1s
	fi
done
ENDTIME=`date +%s.%N`
RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
echo -e "${COLOR_GREEN}search_small Simulation Succeed!. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"


STARTTIME=`date +%s.%N` 
echo -e "${COLOR_GREEN}running app qsort until succeed."
Result=${Sim_DIR}/qsort/sim.out
echo ${Result}
while :
do
	rm -rf ${Sim_DIR}/qsort
	mkdir -p ${Sim_DIR}/qsort
	./runsim_qsort.sh $1 $2
	if [ -s "$Result" ]
	then
		break
	else
		sleep 0.1s
	fi
done
ENDTIME=`date +%s.%N`
RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
echo -e "${COLOR_GREEN}qsort Simulation Succeed!. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"


STARTTIME=`date +%s.%N` 
echo -e "${COLOR_GREEN}running app gsm until succeed."
Result=${Sim_DIR}/gsm/sim.out
echo ${Result}
while :
do
	rm -rf ${Sim_DIR}/gsm
	mkdir -p ${Sim_DIR}/gsm
	./runsim_gsm.sh $1 $2
	if [ -s "$Result" ]
	then
		break
	else
		sleep 0.1s
	fi
done
ENDTIME=`date +%s.%N`
RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
echo -e "${COLOR_GREEN} gsmSimulation Succeed!. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"


STARTTIME=`date +%s.%N`
echo -e "${COLOR_GREEN}running app jpeg until succeed."
Result=${Sim_DIR}/jpeg/sim.out
echo ${Result}
while :
do
	rm -rf ${Sim_DIR}/jpeg
	mkdir -p ${Sim_DIR}/jpeg
	./runsim_jpeg.sh $1 $2
	if [ -s "$Result" ]
	then
		break
	else
		sleep 0.1s
	fi
done
ENDTIME=`date +%s.%N`
RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
echo -e "${COLOR_GREEN}jpeg Simulation Succeed!. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"


OVERALL_ENDTIME=`date +%s.%N`
OVERALL_RUNTIME=$(echo "$OVERALL_ENDTIME - $OVERALL_STARTTIME" | bc)
echo -e "${COLOR_GREEN}All Simulations Succeed!. Runtime: ${OVERALL_RUNTIME} seconds${COLOR_CLEAR}"
