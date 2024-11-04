import os
import sys
sys.path.append("/users/ziyzhang/topology-research")
from topologies import HPC_topo
import globals as gl
import numpy as np
import pickle
import csv
from nexullance import Nexullance_MP
from nexullance.ultility import nexullance_exp_container

Cap_core = 10 #GBps
Cap_access = 10 #GBps

csv_cols = ['V', 'D', 'M_name', 'M_weight', 'ave_time_MP_APST4', 'std_time_MP_APST4', 'ave_peakRAM_MP_APST4', 'std_peakRAM_MP_APST4', 
            'ave_time_IT', 'std_time_IT', 'ave_peakRAM_IT',' std_peakRAM_IT', 
            'ave_time_MD_MP_APST4', 'std_time_MD_MP_APST4', 'ave_peakRAM_MD_MP_APST4', 'std_peakRAM_MD_MP_APST4', 
            'ave_time_MD_IT', 'std_time_MD_IT', 'ave_peakRAM_MD_IT', 'std_peakRAM_MD_IT']


def main():

    # define a list for each col:
    ave_time_MP_APST4=[]
    std_time_MP_APST4=[]
    ave_peakRAM_MP_APST4=[]
    std_peakRAM_MP_APST4=[]
    ave_time_IT=[]
    std_time_IT=[]
    ave_peakRAM_IT=[]
    std_peakRAM_IT=[]
    ave_time_MD_MP_APST4=[]
    std_time_MD_MP_APST4=[]
    ave_peakRAM_MD_MP_APST4=[]
    std_peakRAM_MD_MP_APST4=[]
    ave_time_MD_IT=[]
    std_time_MD_IT=[]
    ave_peakRAM_MD_IT=[]
    std_peakRAM_MD_IT=[]
    
    
    config = gl.ddf_configs[0]
    V = config[0]
    D = config[1]
    EPR = (D+1)//2
    topo_name="DDF"
    _network = HPC_topo.HPC_topo.initialize_child_instance(topo_name+"topo", V, D)

    _network.pre_calculate_ECMP_ASP()
    _network.pre_calculate_APST_n(4)

    # ==============================================================
    M_EPs_names=[] 
    for i in range(1, V*EPR):
        M_EPs_names.append(f"shift_{i}")
    M_EPs_s = gl.gen_M_EPs_s(topo_name, V, D, EPR, M_EPs_names, 10.0)
    M_weights = [1/len(M_EPs_s) for _ in range(len(M_EPs_s))]

    MD_container = nexullance_exp_container(topo_name, V, D, EPR)

    # now apply Nexullance_MP_APST4 on each individual traffic demand matrices:
    for i, M_EPs in enumerate(M_EPs_s):
        _result = MD_container.run_and_profile_nexullance_MP(4, M_EPs, M_EPs_names[i], repetitions=5)
        ave_time_MP_APST4.append(_result["ave_time[s]"])
        std_time_MP_APST4.append(_result["std_time[s]"])
        ave_peakRAM_MP_APST4.append(_result["ave_PeakRAM[B]"])
        std_peakRAM_MP_APST4.append(_result["std_PeakRAM[B]"])

    # now apply Nexullance_IT on each individual traffic demand matrices:
    for i, M_EPs in enumerate(M_EPs_s):
        _result = MD_container.run_and_profile_nexullance_IT(M_EPs, M_EPs_names[i], repetitions=5)
        ave_time_IT.append(_result["ave_time[s]"])
        std_time_IT.append(_result["std_time[s]"])
        ave_peakRAM_IT.append(_result["ave_PeakRAM[B]"])
        std_peakRAM_IT.append(_result["std_PeakRAM[B]"])

    # now start with MD_Nexullance:
    _result= MD_container.run_and_profile_MD_nexullance_MP(M_EPs_s, M_weights, 4, repetitions=5)
    ave_time_MD_MP_APST4.append(_result["ave_time[s]"])
    std_time_MD_MP_APST4.append(_result["std_time[s]"])
    ave_peakRAM_MD_MP_APST4.append(_result["ave_PeakRAM[B]"])
    std_peakRAM_MD_MP_APST4.append(_result["std_PeakRAM[B]"])

    _result= MD_container.run_and_profile_MD_nexullance_IT(M_EPs_s, M_weights, repetitions=5)
    ave_time_MD_IT.append(_result["ave_time[s]"])
    std_time_MD_IT.append(_result["std_time[s]"])
    ave_peakRAM_MD_IT.append(_result["ave_PeakRAM[B]"])
    std_peakRAM_MD_IT.append(_result["std_PeakRAM[B]"])


    # =================================================================

    filename = f'{topo_name}_{V}_{D}_MD_IT_all_shifts_profiling.csv'
    # save data to csv file
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(csv_cols)
        csvfile.flush()
        for i in range(len(M_EPs_s)):
            csvwriter.writerow([V, D, M_EPs_names[i], M_weights[i], ave_time_MP_APST4[i], std_time_MP_APST4[i], 
                                ave_peakRAM_MP_APST4[i], std_peakRAM_MP_APST4[i], ave_time_IT[i], std_time_IT[i], 
                                ave_peakRAM_IT[i], std_peakRAM_IT[i], 0, 0, 
                                0, 0, 
                                0, 0, 0, 0
                                ])
            csvfile.flush()
        
        csvwriter.writerow([V, D, "MD", 0, 0, 0, 
                            0, 0, 0, 0, 
                            0, 0, ave_time_MD_MP_APST4[0], std_time_MD_MP_APST4[0],
                            ave_peakRAM_MD_MP_APST4[0],
                            std_peakRAM_MD_MP_APST4[0],
                            ave_time_MD_IT[0],
                            std_time_MD_IT[0],
                            ave_peakRAM_MD_IT[0],
                            std_peakRAM_MD_IT[0],
                            ])
        csvfile.flush()


if __name__ == '__main__':
    main()
