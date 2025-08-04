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
    'phi_ECMP_ASP', 'phi_IT', 'phi_IT_fast', # TODO: IT_fast_diff
    'time_IT', 'time_IT_fast',
    'attempts_IT', 'attempts_IT_fast'
]

_num_samples_sweep = [2]
# _num_samples_sweep = [1, 2, 4, 8, 16, 32, 64, 128, 256]
_repetitions = 1  # number of repetitions for each experiment

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
                
                M_EPs_s = demand_analyzer.get_inter_EP_demand_matrices(num_samples=_num_samples)[0][0:]  # skip the first matrix

                exp_container = nexullance_exp_container(topo_name, V, D, EPR)

                # ECMP_ASP_phis = []
                # IT_results = []
                # # now apply Nexullance_MP_APST4 on each individual traffic demand matrices:
                # for i, M_EPs in enumerate(M_EPs_s):
                #     IT_result = exp_container.run_and_profile_nexullance_IT(M_EPs, f"sample{i}", repetitions=_repetitions)
                #     IT_results.append(IT_result)
                #     ECMP_ASP_phis.append(exp_container.run_ECMP_SP(M_EPs))
                # # =================================================================

                IT_fast_result = exp_container.run_nexullance_IT_fast_batch_mode(M_EPs_s, auto_scaling=True, _debug=False, from_initial_RT=True)
                # print out the results
                for i in range(len(M_EPs_s)):
                    print(f"IT_result for matrix {i}: ")
                    print(f"phi:{IT_fast_result[i].get_phi()} ")
                    print(f"time:{IT_fast_result[i].get_elapsed_time()} ")
                    print(f"attempts:{IT_fast_result[i].get_num_attempts()} ")



if __name__ == '__main__':
    main()