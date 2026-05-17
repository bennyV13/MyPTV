import os
import pandas as pd

def reformat_csv(file_path):
    print(f"Reformatting {file_path}...")
    
    # Try reading as CSV first
    try:
        df = pd.read_csv(file_path)
        # If columns exist, select them
        if 'PixelX' in df.columns:
            new_df = df[['PixelX', 'PixelY', 'WorldX', 'WorldY', 'WorldZ']]
        else:
            # Maybe it's already tab separated but with headers?
            df = pd.read_csv(file_path, sep='\t')
            if 'PixelX' in df.columns:
                new_df = df[['PixelX', 'PixelY', 'WorldX', 'WorldY', 'WorldZ']]
            else:
                # If no headers, assume it's already in the 5-column format
                new_df = pd.read_csv(file_path, sep='\t', header=None)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # New file path without .csv extension
    new_file_path = file_path.replace('.csv', '')
    
    # Save as tab-separated without header or index
    new_df.to_csv(new_file_path, sep='\t', header=False, index=False)
    
    # Remove the original csv file
    os.remove(file_path)
    print(f"Saved to {new_file_path} and removed original.")

def main():
    target_dir = 'Data_Analysis/MyPTV_analysis/20260506_analysis/cal'
    for filename in os.listdir(target_dir):
        if filename.endswith('_indexed.csv'):
            file_path = os.path.join(target_dir, filename)
            reformat_csv(file_path)

if __name__ == "__main__":
    main()
