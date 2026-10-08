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

OVERALL_STARTTIME=`date +%s.%N`

STARTTIME=`date +%s.%N`
echo running app dijkstra
rm -rf ${Sim_DIR}/dijkstra
mkdir -p ${Sim_DIR}/dijkstra
${Sniper_Home}/run-sniper  ${Config} -d ${Sim_DIR}/dijkstra -- ${APP_Home}/dijkstra/dijkstra_small ${APP_Home}/dijkstra/input.dat > ${Sim_DIR}/dijkstra/stdout_dijkstra.txt 
ENDTIME=`date +%s.%N`
RUNTIME=$(echo "$ENDTIME - $STARTTIME" | bc)
echo -e "${COLOR_GREEN}dijkstra Simulation finished. Runtime: ${RUNTIME} seconds${COLOR_CLEAR}"
