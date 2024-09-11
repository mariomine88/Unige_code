#!/bin/bash

set -e

#arr protocols
declare -a protocols=("tcp" "udp")

# Loop over the two protocols
for prot in "${protocols[@]}"
do

gnuplot <<-eNDgNUPLOTcOMMAND
	set term png size 900, 700
	set output "../data/${prot}graph.png"
	set logscale x 2
	set logscale y 10
	set xlabel "msg size (B)"
	set ylabel "throughput (KB/s)"
	plot "../data/${prot}_throughput.dat" using 1:2 title "${prot} median Throughput" \
			with linespoints, \
		"../data/${prot}_throughput.dat" using 1:3 title "${prot} average Throughput" \
		with linespoints
	clear
eNDgNUPLOTcOMMAND

done