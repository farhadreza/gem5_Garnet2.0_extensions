#!/usr/bin/python2
#
# Plot latency numbers for simulation stats in outdir to latency_file

import os, sys, re
from ConfigParser import ConfigParser

## Parse stats.txt for the specified key and return the associated value as float
def getStatsForString(stats_file, key):
    with open(stats_file, "rt") as f:
        for line in f:
            if key in line:

                # Remove comments
                comment_pos = line.find("#")
                if comment_pos > -1:
                    line = line[0:comment_pos]

                # Return last column as float
                split = line.split()
                return float(split[-1])
    return 0.0

if len(sys.argv) < 2:
    print("Usage: %s <directory containing simulation directories> " % sys.argv[0])
    sys.exit(0)

rootdir = sys.argv[1]

for subdir, dirs, files in os.walk(rootdir):
    dirs = sorted(dirs)
    for outdir in dirs:
        stats_file = os.path.join(rootdir, outdir, "stats.txt")
        config_file = os.path.join(rootdir, outdir, "config.ini")
        if os.path.exists(stats_file):

            # Initialize ConfigParser
            config = ConfigParser()
            if not config.read(config_file):
                continue

            # Count number of CPUs
            num_cpus = 0
            children = config.get("system", "children")
            num_cpus = len(re.findall("cpu[0-9]+[0-9]*", children))

            if num_cpus == 0:
                continue

            # Get injection rate
            inj_rate = 0.0
            if config.has_option("system.cpu0", "inj_rate"):
                inj_rate = config.getfloat("system.cpu0", "inj_rate")
            elif config.has_option("system.cpu00", "inj_rate"):
                inj_rate = config.getfloat("system.cpu00", "inj_rate")
            elif config.has_option("system.cpu000", "inj_rate"):
                inj_rate = config.getfloat("system.cpu000", "inj_rate")
            elif config.has_option("system.cpu0000", "inj_rate"):
                inj_rate = config.getfloat("system.cpu0000", "inj_rate")
            else:
                continue

            # Get number of cycles for SE/FE simulation
            num_cycles = getStatsForString(stats_file, "system.cpu0.numCycles")
            if num_cycles == 0.0:
                num_cycles = getStatsForString(stats_file, "system.cpu00.numCycles")
            if num_cycles == 0.0:
                num_cycles = getStatsForString(stats_file, "system.cpu000.numCycles")
            if num_cycles == 0.0:
                num_cycles = getStatsForString(stats_file, "system.cpu000.numCycles")

            # Get number of cycles for Garnet_standalone simulation
            if num_cycles == 0.0:
                num_cycles = getStatsForString(stats_file, "sim_ticks")
            if num_cycles == 0.0:
                continue

            latency = getStatsForString(stats_file, "system.ruby.network.average_packet_latency")
            recep_rate = getStatsForString(stats_file, "system.ruby.network.packets_injected::total")\
                            / float(num_cpus) / num_cycles

            # Create file name for results

            print outdir
            print inj_rate, recep_rate, latency, "\n"
            
            

#stats_file = os.path.join(outdir, "stats.txt")

#

#with open(latency_file, "a") as f:
#    f.write("{0:f}   {1:f}\n".format(injrate, latency))

