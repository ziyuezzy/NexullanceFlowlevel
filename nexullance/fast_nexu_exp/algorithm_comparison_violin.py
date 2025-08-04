#!/usr/bin/env python3
"""
Algorithm Comparison Visualization Script

This script compares three algorithms (IT, IT_fast, IT_fast_diff) using violin plots
for the following metrics:
1. Phi values achieved by each algorithm
2. Execution time
3. Number of attempts
4. Time per attempt

Author: Generated for algorithm comparison analysis
Date: July 8, 2025
"""

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
FONT_SIZE = 22

matplotlib.rcParams.update({'font.size': 22})

# # Set global font size for both matplotlib and seaborn
# plt.rcParams.update({
#     'font.size': 22,
#     'axes.titlesize': 22,
#     'axes.labelsize': 22,
#     'axes.ticksize': 22,
#     'xtick.labelsize': 22,
#     'ytick.labelsize': 22,
#     'ytick.ticksize': 22,
#     'legend.fontsize': 22,
#     'figure.titlesize': 24
# })
# sns.set_context("notebook", rc={"font.size": 22, "axes.titlesize": 22, "axes.labelsize": 22})

# Set global font size

def load_and_prepare_data(csv_file_path):
    """
    Load CSV data and prepare it for violin plot visualization
    
    Args:
        csv_file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: Prepared data for plotting
    """
    # Load the data
    df = pd.read_csv(csv_file_path)
    
    # Calculate time per attempt for each algorithm, set to zero if attempts is zero
    df['time_per_attempt_IT'] = np.where(df['attempts_IT'] == 0, 0, df['time_IT'] / df['attempts_IT'])
    df['time_per_attempt_IT_fast'] = np.where(df['attempts_IT_fast'] == 0, 0, df['time_IT_fast'] / df['attempts_IT_fast'])
    df['time_per_attempt_IT_fast_diff'] = np.where(df['attempts_IT_fast_diff'] == 0, 0, df['time_IT_fast_diff'] / df['attempts_IT_fast_diff'])
    
    return df

def create_violin_plots(df, output_dir=None, benchmark_name=None):
    """
    Create violin plots comparing the three algorithms
    
    Args:
        df (pandas.DataFrame): Data containing algorithm results
        output_dir (str, optional): Directory to save plots
    """
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('Algorithm Comparison: IT vs IT_fast vs IT_fast_diff', fontweight='bold')
    
    # 1. Phi values comparison
    ax1 = axes[0, 0]
    phi_data = [df['phi_IT'], df['phi_IT_fast'], df['phi_IT_fast_diff']]
    phi_labels = ['IT', 'IT_fast', 'IT_fast_diff']
    
    violin_parts = ax1.violinplot(phi_data, positions=[1, 2, 3], showmeans=True, showmedians=False, showextrema=True)
    ax1.set_xticks([1, 2, 3])
    ax1.set_xticklabels(phi_labels, fontsize=FONT_SIZE)
    ax1.set_title('Solution quality Comparison', fontweight='bold', fontsize=FONT_SIZE)
    ax1.set_ylabel('Phi [GBps]', fontsize=FONT_SIZE)
    ax1.grid(True, alpha=0.3)
    
    # Add mean values as text
    for i, data in enumerate(phi_data):
        mean_val = np.mean(data)
        ax1.text(i+1, mean_val, f'mean={mean_val:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Execution time comparison
    ax2 = axes[0, 1]
    time_data = [df['time_IT'], df['time_IT_fast'], df['time_IT_fast_diff']]
    time_labels = ['IT', 'IT_fast', 'IT_fast_diff']
    
    violin_parts = ax2.violinplot(time_data, positions=[1, 2, 3], showmeans=True, showmedians=False, showextrema=True)
    ax2.set_xticks([1, 2, 3])
    ax2.set_xticklabels(time_labels, fontsize=FONT_SIZE)
    ax2.set_title('Execution Time Comparison', fontweight='bold', fontsize=FONT_SIZE)
    ax2.set_ylabel('Execution Time for each input matrix [seconds]', fontsize=FONT_SIZE)
    ax2.grid(True, alpha=0.3)
    
    # Add mean values as text
    for i, data in enumerate(time_data):
        mean_val = np.mean(data)
        ax2.text(i+1, mean_val, f'mean={mean_val:.4f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Number of attempts comparison
    ax3 = axes[1, 0]
    attempts_data = [df['attempts_IT'], df['attempts_IT_fast'], df['attempts_IT_fast_diff']]
    attempts_labels = ['IT', 'IT_fast', 'IT_fast_diff']
    
    violin_parts = ax3.violinplot(attempts_data, positions=[1, 2, 3], showmeans=True, showmedians=False, showextrema=True)
    ax3.set_xticks([1, 2, 3])
    ax3.set_xticklabels(attempts_labels, fontsize=FONT_SIZE)
    ax3.set_title('Number of Iterations Comparison', fontweight='bold', fontsize=FONT_SIZE)
    ax3.set_ylabel('Number of Iterations', fontsize=FONT_SIZE)
    ax3.grid(True, alpha=0.3)
    
    # Add mean values as text
    for i, data in enumerate(attempts_data):
        mean_val = np.mean(data)
        ax3.text(i+1, mean_val, f'mean={mean_val:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Time per attempt comparison
    ax4 = axes[1, 1]
    time_per_attempt_data = [
        df['time_per_attempt_IT'], 
        df['time_per_attempt_IT_fast'], 
        df['time_per_attempt_IT_fast_diff']
    ]
    time_per_attempt_labels = ['IT', 'IT_fast', 'IT_fast_diff']
    
    violin_parts = ax4.violinplot(time_per_attempt_data, positions=[1, 2, 3], showmeans=True, showmedians=True, showextrema=True)
    ax4.set_xticks([1, 2, 3])
    ax4.set_xticklabels(time_per_attempt_labels, fontsize=FONT_SIZE)
    ax4.set_title('Time per iteration Comparison', fontweight='bold', fontsize=FONT_SIZE)
    ax4.set_ylabel('Time per iteration [seconds]', fontsize=FONT_SIZE)
    ax4.set_yscale('log')  # Use log scale for better visualization
    ax4.grid(True, alpha=0.3)
    
    # Add mean values as text
    for i, data in enumerate(time_per_attempt_data):
        mean_val = np.mean(data)
        median_val = np.median(data)
        ax4.text(i+1, mean_val, f'mean={mean_val:.0E}', ha='center', va='bottom', fontweight='bold', color='blue')
        ax4.text(i+1, median_val, f'median={median_val:.0E}', ha='center', va='top', fontweight='bold', color='red')
        # mean_val = np.mean(data)
        # ax4.text(i+1, mean_val, f'mean={mean_val:.6f}', ha='center', va='bottom', fontweight='bold')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save plot if output directory is specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        plt.savefig(output_path / f'algorithm_comparison_violin_{benchmark_name}.png', dpi=300, bbox_inches='tight')
        # plt.savefig(output_path / 'algorithm_comparison_violin.pdf', bbox_inches='tight')
        print(f"Plots saved to {output_path}")
    
    plt.show()

def print_summary_statistics(df):
    """
    Print summary statistics for all algorithms
    
    Args:
        df (pandas.DataFrame): Data containing algorithm results
    """
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    # Phi values
    print("\n1. PHI VALUES:")
    print("-" * 40)
    algorithms = ['IT', 'IT_fast', 'IT_fast_diff']
    phi_cols = ['phi_IT', 'phi_IT_fast', 'phi_IT_fast_diff']
    
    for alg, col in zip(algorithms, phi_cols):
        data = df[col]
        print(f"{alg:12}: Mean={data.mean():.4f}, Std={data.std():.4f}, Min={data.min():.4f}, Max={data.max():.4f}")
    
    # Execution time
    print("\n2. EXECUTION TIME (seconds):")
    print("-" * 40)
    time_cols = ['time_IT', 'time_IT_fast', 'time_IT_fast_diff']
    
    for alg, col in zip(algorithms, time_cols):
        data = df[col]
        print(f"{alg:12}: Mean={data.mean():.6f}, Std={data.std():.6f}, Min={data.min():.6f}, Max={data.max():.6f}")
    
    # Number of attempts
    print("\n3. NUMBER OF ATTEMPTS:")
    print("-" * 40)
    attempts_cols = ['attempts_IT', 'attempts_IT_fast', 'attempts_IT_fast_diff']
    
    for alg, col in zip(algorithms, attempts_cols):
        data = df[col]
        print(f"{alg:12}: Mean={data.mean():.1f}, Std={data.std():.1f}, Min={data.min():.1f}, Max={data.max():.1f}")
    
    # Time per attempt
    print("\n4. TIME PER ATTEMPT (seconds):")
    print("-" * 40)
    time_per_attempt_cols = ['time_per_attempt_IT', 'time_per_attempt_IT_fast', 'time_per_attempt_IT_fast_diff']
    
    for alg, col in zip(algorithms, time_per_attempt_cols):
        data = df[col]
        print(f"{alg:12}: Mean={data.mean():.8f}, Std={data.std():.8f}, Min={data.min():.8f}, Max={data.max():.8f}")

def create_comparative_box_plots(df, output_dir=None):
    """
    Create additional box plots for detailed comparison
    
    Args:
        df (pandas.DataFrame): Data containing algorithm results
        output_dir (str, optional): Directory to save plots
    """
    # Prepare data for seaborn plotting
    phi_melted = pd.melt(df, value_vars=['phi_IT', 'phi_IT_fast', 'phi_IT_fast_diff'],
                        var_name='Algorithm', value_name='Phi_Value')
    phi_melted['Algorithm'] = phi_melted['Algorithm'].str.replace('phi_', '')
    
    time_melted = pd.melt(df, value_vars=['time_IT', 'time_IT_fast', 'time_IT_fast_diff'],
                         var_name='Algorithm', value_name='Time')
    time_melted['Algorithm'] = time_melted['Algorithm'].str.replace('time_', '')
    
    attempts_melted = pd.melt(df, value_vars=['attempts_IT', 'attempts_IT_fast', 'attempts_IT_fast_diff'],
                             var_name='Algorithm', value_name='Attempts')
    attempts_melted['Algorithm'] = attempts_melted['Algorithm'].str.replace('attempts_', '')
    
    time_per_attempt_melted = pd.melt(df, value_vars=['time_per_attempt_IT', 'time_per_attempt_IT_fast', 'time_per_attempt_IT_fast_diff'],
                                     var_name='Algorithm', value_name='Time_Per_Attempt')
    time_per_attempt_melted['Algorithm'] = time_per_attempt_melted['Algorithm'].str.replace('time_per_attempt_', '')
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('Algorithm Comparison: Box Plots', fontweight='bold')
    
    # Box plots
    sns.boxplot(data=phi_melted, x='Algorithm', y='Phi_Value', ax=axes[0, 0])
    axes[0, 0].set_title('Phi Values Distribution', fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    
    sns.boxplot(data=time_melted, x='Algorithm', y='Time', ax=axes[0, 1])
    axes[0, 1].set_title('Execution Time Distribution', fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    
    sns.boxplot(data=attempts_melted, x='Algorithm', y='Attempts', ax=axes[1, 0])
    axes[1, 0].set_title('Number of Attempts Distribution', fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    sns.boxplot(data=time_per_attempt_melted, x='Algorithm', y='Time_Per_Attempt', ax=axes[1, 1])
    axes[1, 1].set_title('Time per Attempt Distribution', fontweight='bold')
    axes[1, 1].set_yscale('log')  # Use log scale for better visualization
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot if output directory is specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        plt.savefig(output_path / 'algorithm_comparison_boxplots.png', dpi=300, bbox_inches='tight')
        plt.savefig(output_path / 'algorithm_comparison_boxplots.pdf', bbox_inches='tight')
        print(f"Box plots saved to {output_path}")
    
    plt.show()

def main():
    """Main function to run the analysis"""
    # plt.rcParams.update({'font.size': 30})
    
    # Output directory for saving plots (optional)
    output_dir = "/groups/ilabt-imec-be/hpcnetworksimulation/ziyzhang/EFM_experiments/topoResearch/nexullance/fast_nexu_exp/plots"
    
    # Path to your CSV file
    # bench= "Alltoall"  # Example benchmark name
    # bench= "Allreduce"  # Example benchmark name
    bench= "FFT3D"  # Example benchmark name
    csv_file_path = f"/groups/ilabt-imec-be/hpcnetworksimulation/ziyzhang/EFM_experiments/topoResearch/nexullance/fast_nexu_exp/DDF_36_5_64_sent_samples_{bench}.csv"

    try:
        # Load and prepare data
        print("Loading data...")
        df = load_and_prepare_data(csv_file_path)
        print(f"Data loaded successfully. Shape: {df.shape}")
        
        # Print summary statistics
        print_summary_statistics(df)
        
        # Create violin plots
        print("\nCreating violin plots...")
        create_violin_plots(df, output_dir, bench)
        
        # # Create box plots for additional comparison
        # print("\nCreating box plots...")
        # create_comparative_box_plots(df, output_dir)
        
        print("\nAnalysis completed successfully!")
        
    except FileNotFoundError:
        print(f"Error: Could not find the CSV file at {csv_file_path}")
        print("Please check the file path and try again.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
