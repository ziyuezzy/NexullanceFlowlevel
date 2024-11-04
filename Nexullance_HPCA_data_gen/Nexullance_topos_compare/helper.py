import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def plot_bench_bars(_data: dict, methods_name: list, title: str, x_label: str, y_label: str, y_log: bool = False, normalized: bool = False, errors: dict = None):

    ## Example usage:
    # plot_data = {
    #     'Benchmark 1': [0.8, 0.7, 0.9],  
    #     'Benchmark 2': [0.6, 0.5, 0.7],  
    #     'Benchmark 3': [0.9, 0.8, 0.7],   
    #     'Benchmark 4': [0.9, 0.8, 0.7]
    # }

    # errors_data = {
    #     'Benchmark 1': [(0.05, 0.1), (0.06, 0.12), (0.03, 0.08)],  
    #     'Benchmark 2': [(0.03, 0.08), (0.04, 0.1), (0.02, 0.06)],  
    #     'Benchmark 3': [(0.04, 0.09), (0.05, 0.11), (0.03, 0.07)],   
    #     'Benchmark 4': [(0.03, 0.08), (0.04, 0.1), (0.02, 0.06)]
    # }

    # methods = ['Method 1', 'Method 2', 'Method 3']
    # plot_bench_bars(plot_data, errors_data, methods, "Performance Comparison", "Benchmark", "Performance", y_log=False, normalized=False)

    # Calculate bar width dynamically based on the number of methods
    num_methods = len(methods_name)
    bar_width = 0.7 / num_methods  # Adjust this scaling factor as needed

    # Generating x positions for each group of bars
    x_positions = np.arange(len(_data))  

    # Generate colors using a predefined colormap
    colors = cm.tab10(np.linspace(0, 1, num_methods))

    # Plotting
    plt.figure(figsize=(15, 2))  # Adjust size if necessary
    for i, method in enumerate(methods_name):
        # Extracting performance metrics for each method
        performance = [_data[bench][i] for bench in _data]
        if errors:
            error_min_max = np.array([errors[bench][i] for bench in errors])
        # Adjusting x positions for each group of bars
        x_positions_adjusted = x_positions + (i - num_methods//2) * bar_width
        # Plotting bars for each method
        plt.bar(x_positions_adjusted, performance, width=bar_width, align='center', label=method, color = colors[i])

        # Adding error bars
        if errors:
            error_bars = error_min_max.swapaxes(0, 1)
            plt.errorbar(x_positions_adjusted[:len(errors)], performance[:len(errors)], 
                        error_bars, fmt='none', ecolor='k', capsize=5)

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
    plt.ylim(0, 11)

    # Show plot
    plt.show()
