import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# plot_bench_bars(plot_data, methods, "a title", "x", "y")
def plot_bench_bars(_data: dict, methods_name: list, title: str, x_label: str, y_label: str, y_log: bool = False, normalized: bool = False):
    # example input: ==============
    # # Sample data: dictionary where keys are benchmarks and values are lists of performance metrics for each method
    # plot_data = {
    #     'Benchmark 1': [0.8, 0.7, 0.9],  # Performance metrics for Method 1, Method 2, Method 3 for Benchmark 1
    #     'Benchmark 2': [0.6, 0.5, 0.7],  # Performance metrics for Method 1, Method 2, Method 3 for Benchmark 2
    #     'Benchmark 3': [0.9, 0.8, 0.7],   # Performance metrics for Method 1, Method 2, Method 3 for Benchmark 3
    #     'Benchmark 34': [0.9, 0.8, 0.7]   # Performance metrics for Method 1, Method 2, Method 3 for Benchmark 3
    # }
    # # Method labels
    # methods = ['Method 1', 'Method 2', 'Method 3']
    # =============================

    # Calculate bar width dynamically based on the number of methods
    num_methods = len(methods_name)
    bar_width = 0.7 / num_methods  # Adjust this scaling factor as needed

    # Generating x positions for each group of bars
    x_positions = np.arange(len(_data))  

    # Generate colors using a predefined colormap
    colors = cm.tab10(np.linspace(0, 1, num_methods))

    # Plotting
    plt.figure(figsize=(10, 3))  # Adjust size if necessary
    for i, method in enumerate(methods_name):
        # Extracting performance metrics for each method
        performance = [_data[bench][i] for bench in _data]
        # Adjusting x positions for each group of bars
        x_positions_adjusted = x_positions + (i - num_methods//2) * bar_width
        # Plotting bars for each method
        plt.bar(x_positions_adjusted, performance, width=bar_width, align='center', label=method, color = colors[i])

    # Adding labels and title
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    # if normalized:
    #     plt.ylim(0, 1)
    if y_log:
        plt.yscale("log")  
    plt.title(title)
    plt.xticks(x_positions, _data.keys())
    # Moving the legend outside the figure to the right
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))


    # Show plot
    plt.show()

# example usage:

# # Sample data: dictionary where keys are benchmarks and values are lists of performance metrics for each method
# plot_data = {
#     'Benchmark 1': [0.8, 0.7, 0.9],  # Performance metrics for Method 1, Method 2, Method 3 for Benchmark 1
#     'Benchmark 2': [0.6, 0.5, 0.7],  # Performance metrics for Method 1, Method 2, Method 3 for Benchmark 2
#     'Benchmark 3': [0.9, 0.8, 0.7],   # Performance metrics for Method 1, Method 2, Method 3 for Benchmark 3
#     'Benchmark 34': [0.9, 0.8, 0.7]   # Performance metrics for Method 1, Method 2, Method 3 for Benchmark 3
# }
# # Method labels
# methods = ['Method 1', 'Method 2', 'Method 3']
# plot_bench_bars(plot_data, methods, "a title", "x", "y")




def plot_scaling_lines(_V: list, _data: dict, title: str, x_label: str, y_label: str, 
                       y_log: bool = False, _power_x: int = 1, y_max: int = 0, legends: list = None, legend_cols: int = 1, markers: list = None):
    # example input: ==============
    # # _V: list of x-axis data points
    # x axis values should be _V^_power_x
    # # _data: dictionary where keys are methods_name and values are lists of metrics (e.g., execution time) for each method
    # _data = {
    #     'Method 1': [0.8, 0.7, 0.9],  # metrics for _V[0], _V[1], _V[2] for Method 1
    #     'Method 2': [0.6, 0.5, 0.7],  # metrics for _V[0], _V[1], _V[2] for Method 2
    #     'Method 3': [0.9, 0.8, 0.7],   # metrics for _V[0], _V[1], _V[2] for Method 3
    #     'Method 4': [0.9, 0.8, 0.7]   # metrics for _V[0], _V[1], _V[2] for Method 3
    # }
    # =============================

    methods_name = list(_data.keys())
    num_methods = len(methods_name)

    # Generate colors using a predefined colormap
    colors = cm.tab10(np.linspace(0, 1, num_methods))

    # Plotting
    plt.figure(figsize=(4, 3))  # Adjust size if necessary
    for i, method in enumerate(methods_name):
        # Extracting performance metrics for each method, and plot
        metrics = _data[method]
        x_values = [_v ** _power_x for _v in _V]
        if len(metrics) < len (x_values):
            # truncate x_values if there are more metrics than x_values
            x_values = x_values[:len(metrics)]
        elif len(metrics) > len (x_values):
            raise ValueError("The length of metrics should be less than or equal to the length of x_values")

        if legends is not None:
            plt.plot(x_values, metrics, marker=markers[i], linestyle='-', color=colors[i], label=legends[i])
        else:
            plt.plot(x_values, metrics, marker=markers[i], linestyle='-', color=colors[i])


    # Adding labels and title
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if y_log:
        plt.yscale("log")
    plt.title(title)
    # Moving the legend outside the figure to the right
    if legends is not None:
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=legend_cols)
    # plt.legend()
    if y_max > 0:
        plt.ylim(0, y_max)

    # Show plot
    plt.show()
