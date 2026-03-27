from scripts.lagrangian_analysis import LagrangianAnalysis
import os
import matplotlib.pyplot as plt

def main():
    data_path = "Data_and_analysis/20260315_frames/smoothed_trajectories"
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}")
        return
        
    analysis = LagrangianAnalysis()
    analysis.load_data(data_path)
    
    # Calculate all statistics
    # Setting max_lag to a reasonable value for this dataset
    analysis.calculate_all(max_lag=100)
    
    # Save results
    output_dir = "Data_and_analysis/Analysis/lagrangian_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    analysis.save_results(os.path.join(output_dir, "analysis_results.pkl"))
    
    # Plot results
    print("Generating plots...")
    analysis.plot_msd(save_path=os.path.join(output_dir, "msd_plot.png"))
    plt.close()
    
    analysis.plot_lvacf(kind='vx', save_path=os.path.join(output_dir, "lvacf_vx_plot.png"))
    plt.close()
    
    analysis.plot_pdf(kind='vx', save_path=os.path.join(output_dir, "pdf_vx_plot.png"))
    plt.close()
    
    analysis.plot_pdf(kind='ax', save_path=os.path.join(output_dir, "pdf_ax_plot.png"))
    plt.close()
    
    print(f"Full analysis complete. Results and plots saved in {output_dir}")

if __name__ == "__main__":
    main()
