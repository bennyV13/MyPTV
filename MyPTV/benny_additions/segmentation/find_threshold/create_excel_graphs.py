import pandas as pd
import plotly.graph_objects as go
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import os
from datetime import datetime
import tempfile
import plotly.io as pio
from openpyxl.styles import numbers

def create_excel_graphs(csv_path):
    """
    Create Excel graphs for each recording showing blob count vs threshold for all cameras.
    
    Args:
        csv_path (str): Path to the CSV file containing the segmentation results
    """
    # Verify the CSV file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
    
    # print(f"\nReading CSV file: {csv_path}")
    # print(f"File exists: {os.path.exists(csv_path)}")
    # print(f"File size: {os.path.getsize(csv_path)} bytes")
    
    # Read the CSV file and convert columns to appropriate types
    df = pd.read_csv(csv_path)
    # print("\nInitial data shape:", df.shape)
    # print("\nColumns in CSV:", df.columns.tolist())
    # print("\nFirst few rows of raw data:")
    # print(df.head())
    # print("\nData types before conversion:")
    # print(df.dtypes)
    
    # Convert columns to numeric and handle any conversion issues
    # print("\nConverting BlobCount to numeric...")
    # Remove commas from numbers and convert to numeric
    df['BlobCount'] = df['BlobCount'].astype(str).str.replace(',', '').astype(float)
    # print("\nConverting Threshold to numeric...")
    df['Threshold'] = pd.to_numeric(df['Threshold'], errors='coerce')
    
    # Format numbers with commas for display
    df['BlobCount'] = df['BlobCount'].apply(lambda x: f"{x:,.0f}")
    df['Threshold'] = df['Threshold'].apply(lambda x: f"{x:,.0f}")
    
    # print("\nData types after conversion:")
    # print(df.dtypes)
    
    # Check for any NaN values
    nan_counts = df.isna().sum()
    # print("\nNaN values in each column:")
    # print(nan_counts)
    
    # Get unique recordings
    recordings = df['Recording'].unique()
    # print("\nUnique recordings found:", recordings)
    
    # Create timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get the directory of the CSV file
    output_dir = os.path.dirname(csv_path)
    # print(f"\nOutput directory: {output_dir}")
    
    # Create paths for output files
    excel_path = os.path.join(output_dir, f'segmentation_graphs_{timestamp}.xlsx')
    
    # Create a directory for plot files in the same location as the CSV
    plots_dir = os.path.join(output_dir, f'plots_{timestamp}')
    os.makedirs(plots_dir, exist_ok=True)
    
    try:
        # Create Excel writer
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # For each recording
            for recording in recordings:
                # print(f"\nProcessing recording: {recording}")
                # Filter data for this recording
                rec_data = df[df['Recording'] == recording]
                # print(f"Data points for this recording: {len(rec_data)}")
                
                # Create a new worksheet for this recording
                sheet_name = f'Rec_{recording}'
                worksheet = writer.book.create_sheet(sheet_name)
                
                # Create the interactive plot using Plotly
                fig = go.Figure()
                
                # Convert back to numeric for plotting
                plot_data = rec_data.copy()
                plot_data['BlobCount'] = plot_data['BlobCount'].str.replace(',', '').astype(float)
                plot_data['Threshold'] = plot_data['Threshold'].str.replace(',', '').astype(float)
                
                # Calculate y-axis range for this recording
                y_min = plot_data['BlobCount'].min()
                y_max = plot_data['BlobCount'].max()
                # print(f"Y-axis range for {recording}: {y_min} to {y_max}")
                
                y_range = y_max - y_min
                y_min = max(0, y_min - y_range * 0.1)  # Add 10% padding below, but not below 0
                y_max = y_max + y_range * 0.1  # Add 10% padding above
                
                # Plot each camera's data
                for camera in plot_data['Camera'].unique():
                    # print(f"Plotting camera: {camera}")
                    cam_data = plot_data[plot_data['Camera'] == camera]
                    # print(f"Data points for {camera}: {len(cam_data)}")
                    # print(f"Sample data for {camera}:")
                    # print(cam_data[['Threshold', 'BlobCount']].head())
                    
                    # Check for NaN values in this camera's data
                    nan_count = cam_data['BlobCount'].isna().sum()
                    if nan_count > 0:
                        print(f"Warning: {nan_count} NaN values found in {camera}'s data")
                    
                    fig.add_trace(go.Scatter(
                        x=cam_data['Threshold'],
                        y=cam_data['BlobCount'],
                        mode='lines+markers',
                        name=camera,
                        hovertemplate='Camera: %{customdata[0]}<br>' +
                                    'Threshold: %{x}<br>' +
                                    'Blob Count: %{y:,.0f}<br>' +  # Format with thousand separator
                                    '<extra></extra>',
                        customdata=[[camera] for _ in range(len(cam_data))]
                    ))
                
                # Customize the plot
                fig.update_layout(
                    title=f'Blob Count vs Threshold - Recording {recording}',
                    xaxis_title='Threshold',
                    yaxis_title='Blob Count',
                    hovermode='x unified',
                    showlegend=True,
                    template='plotly_white',
                    width=1000,
                    height=600,
                    yaxis=dict(
                        range=[y_min, y_max],
                        zeroline=True,
                        zerolinewidth=2,
                        zerolinecolor='black',
                        tickformat=',.0f'  # Format y-axis ticks with thousand separator
                    )
                )
                
                # Add grid lines
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                
                # Save the plot to an HTML file in the plots directory
                plot_filename = f'plot_Rec_{recording}.html'
                plot_path = os.path.join(plots_dir, plot_filename)
                # print(f"Saving plot to: {plot_path}")
                pio.write_html(fig, file=plot_path, auto_open=False)
                
                # Add a note in Excel about the interactive plot
                worksheet['A1'] = f'Interactive plot for Recording {recording}'
                worksheet['A2'] = f'Please open the HTML file to view the interactive plot: {plot_filename}'
                
                # Add the raw data below the note
                data_start_row = 5  # Leave space for the note
                rec_data.to_excel(writer, sheet_name=sheet_name, 
                                startrow=data_start_row, index=False)
                
                # Adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        # print(f"\nFiles created successfully in {output_dir}:")
        # print(f"1. Excel file: {os.path.basename(excel_path)}")
        # print(f"2. Interactive plots directory: {os.path.basename(plots_dir)}")
        # print("\nInteractive plots have been saved as HTML files. You can open them in a web browser to:")
        # print("- Hover over data points to see exact values")
        # print("- Zoom in/out")
        # print("- Pan around")
        # print("- Download the plot as PNG")
        # print("- Use other interactive features")
    
    except Exception as e:
        print(f"Error occurred: {e}")
        # Clean up the plots directory if there was an error
        if os.path.exists(plots_dir):
            import shutil
            shutil.rmtree(plots_dir)
        raise

if __name__ == "__main__":
    # Get the CSV path from the master config
    import yaml
    
    # Load the master config to get the CSV path
    with open('master_config.yml', 'r') as f:
        master_config = yaml.safe_load(f)
    
    csv_path = master_config['results_csv']
    # print(f"Using CSV path from config: {csv_path}")
    
    # Create the Excel graphs
    create_excel_graphs(csv_path) 