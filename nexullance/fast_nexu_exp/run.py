import topoResearch.global_helpers as gl
import numpy as np
import csv
from topoResearch.nexullance.ultility import nexullance_exp_container
from diff_nexu.sampled_demand_analyzer import sampled_demand_analyzer
from paths import REPO_ROOT

Cap_core = 10 #GBps
Cap_access = 10 #GBps

csv_cols = [
    'V', 'D', 'M_id', 
    'phi_ECMP_ASP', 'phi_IT', 'phi_IT_fast', 'phi_IT_fast_diff',
    'time_IT', 'time_IT_fast', 'time_IT_fast_diff',
    'attempts_IT', 'attempts_IT_fast', 'attempts_IT_fast_diff'
]

_num_samples_sweep = [64]
# _num_samples_sweep = [1, 2, 4, 8, 16, 32, 64, 128, 256]
_repetitions = 3  # number of repetitions for each experiment

benchmarks = [
    ("FFT3D", 256, lambda size: f" nx={size} ny={size} nz={size} npRow=12"),
    # ("Alltoall", 64, lambda size: f" bytes={size}"),
    # ("Allreduce", 2048, lambda size: f" iterations=10 count={size}")
]

def main():
    config = gl.ddf_configs[0]
    V = config[0]
    D = config[1]
    EPR = (D+1)//2
    topo_name="DDF"
    for sampling_method in ["sent"]:
    # for sampling_method in ["sent", "enroute"]:

        for bench, problem_size, args_func in benchmarks:
            args_str = args_func(problem_size)
            pickle_file = f"{REPO_ROOT}/diff_nexu/data/{bench}{args_str}_({V},{D})RRG_ECMP_ASP_{sampling_method}.pickle.gz"
            demand_analyzer = sampled_demand_analyzer(pickle_file)
            
            for _num_samples in _num_samples_sweep:
                print(f"Running experiments for {_num_samples} samples...")
                
                M_EPs_s = demand_analyzer.get_inter_EP_demand_matrices(num_samples=_num_samples)[0]

                exp_container = nexullance_exp_container(topo_name, V, D, EPR)

                ECMP_ASP_phis = []
                IT_results = []
                # now apply Nexullance_MP_APST4 on each individual traffic demand matrices:
                for i, M_EPs in enumerate(M_EPs_s):
                    IT_result = exp_container.run_and_profile_nexullance_IT(M_EPs, f"sample{i}", repetitions=_repetitions)
                    IT_results.append(IT_result)
                    ECMP_ASP_phis.append(exp_container.run_ECMP_SP(M_EPs))
                # =================================================================

                # IT_fast_result = exp_container.run_nexullance_IT_fast_batch_mode(M_EPs_s, auto_scaling=True)
                IT_fast_result = exp_container.run_and_profile_nexullance_IT_fast_batch_mode(M_EPs_s, repetitions=_repetitions, 
                                            auto_scaling=True, from_initial_RT=True)

                # IT_fast_result = exp_container.run_nexullance_IT_fast_batch_mode(M_EPs_s, auto_scaling=True)
                IT_fast_diff_result = exp_container.run_and_profile_nexullance_IT_fast_batch_mode(M_EPs_s, repetitions=_repetitions, 
                                            auto_scaling=True, from_initial_RT=False)

                filename = f'{topo_name}_{V}_{D}_{_num_samples}_{sampling_method}_samples_{bench}_debug.csv'
                # save data to csv file
                with open(filename, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(csv_cols)
                    csvfile.flush()
                    for i in range(len(M_EPs_s)):
                        csvwriter.writerow([V, D, i, ECMP_ASP_phis[i], IT_results[i]["ave_phi"], IT_fast_result["ave_phi"][i], IT_fast_diff_result["ave_phi"][i],
                                            IT_results[i]["ave_time[s]"], IT_fast_result["ave_time[s]"][i], IT_fast_diff_result["ave_time[s]"][i],
                                            IT_results[i]["ave_num_attempts"], IT_fast_result["ave_num_attempts"][i], IT_fast_diff_result["ave_num_attempts"][i]]
                                            )
                        csvfile.flush()
                
                print(f"Completed experiments for {_num_samples} samples, saved to {filename}")


if __name__ == '__main__':
    main()