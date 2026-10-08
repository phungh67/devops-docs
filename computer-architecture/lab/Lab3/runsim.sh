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


# chmod +x apps/dijkstra/dijkstra_small
chmod +x apps/gsm-untoast/untoast
chmod +x apps/qsort/qsort_small
chmod +x apps/jpeg-cjpeg/cjpeg
# chmod +x apps/stringsearch/search_small 

OVERALL_STARTTIME=`date +%s.%N`

# STARTTIME=`date +%s.%N`
# echo running app dijkstra
# rm -rf ${Sim_DIR}/dijkstra
# mkdir -p ${Sim_DIR}/dijkstra
# ${Sniper_Home}/run-sniper  ${Config} -d ${Sim_DIR}/dijkstra -- ${APP_Home}/dijkstra/dijkstra_small ${APP_Home}/dijkstra/input.dat > ${Sim_DIR}/dijkstra/#stdout_dijkstra.txt 
# ENDTIME=`date +%s.%N`
# RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
# echo -e "${COLOR_GREEN}dijkstra Simulation finished. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"


# STARTTIME=`date +%s.%N`
# echo running app search_small
# mkdir -p ${Sim_DIR}/string_search
# ${Sniper_Home}/run-sniper  ${Config} -d ${Sim_DIR}/string_search -- ${APP_Home}/stringsearch/search_small > ${Sim_DIR}/string_search/stdout_search.txt 
# ENDTIME=`date +%s.%N`
# RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
# echo -e "${COLOR_GREEN}search_small Simulation finished. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"


STARTTIME=`date +%s.%N` 
echo running app qsort
rm -rf ${Sim_DIR}/qsort
mkdir -p ${Sim_DIR}/qsort
${Sniper_Home}/run-sniper  ${Config} -d ${Sim_DIR}/qsort -- ${APP_Home}/qsort/qsort_small ${APP_Home}/qsort/input_small.dat > ${Sim_DIR}/qsort/stdout_qsort.txt 
ENDTIME=`date +%s.%N`
RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
echo -e "${COLOR_GREEN}qsort Simulation finished. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"


STARTTIME=`date +%s.%N` 
echo running app gsm
rm -rf ${Sim_DIR}/gsm
mkdir -p ${Sim_DIR}/gsm 
${Sniper_Home}/run-sniper  ${Config} -d ${Sim_DIR}/gsm -- ${APP_Home}/gsm-untoast/untoast -fps -c ${APP_Home}/gsm-untoast/small.au.run.gsm > ${Sim_DIR}/gsm/stdout_gsm.txt 
ENDTIME=`date +%s.%N`
RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
echo -e "${COLOR_GREEN} gsmSimulation finished. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"


STARTTIME=`date +%s.%N`
echo running app jpeg 
rm -rf ${Sim_DIR}/jpeg
mkdir -p ${Sim_DIR}/jpeg
${Sniper_Home}/run-sniper  ${Config} -d ${Sim_DIR}/jpeg -- ${APP_Home}/jpeg-cjpeg/cjpeg -dct int -progressive -opt -outfile ${Sim_DIR}/jpeg/jpeg-cjpeg_output_small_encode.jpeg ${APP_Home}/jpeg-cjpeg/input_small.ppm > ${Sim_DIR}/jpeg/stdout_jpeg.txt 
ENDTIME=`date +%s.%N`
RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
echo -e "${COLOR_GREEN}jpeg Simulation finished. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"


OVERALL_ENDTIME=`date +%s.%N`
OVERALL_RUNTIME=$(echo "$OVERALL_ENDTIME - $OVERALL_STARTTIME" | bc)
echo -e "${COLOR_GREEN}All Simulations finished. Runtime: ${OVERALL_RUNTIME} seconds${COLOR_CLEAR}"



