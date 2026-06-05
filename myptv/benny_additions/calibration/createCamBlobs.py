import numpy as np

# Load the original 2-column data (PixelX, PixelY)

txt = np.loadtxt('Cam4.txt')

# Create a new pre-allocated array with 6 columns
N = txt.shape[0]
new_txt = np.zeros((N, 6))

# Copy original PixelX and PixelY to columns 0 and 1
new_txt[:, :2] = txt

# Assign standard MyPTV blob parameters to the remaining columns
new_txt[:, 2] = 4        # Column 2
new_txt[:, 3] = 4        # Column 3
new_txt[:, 4] = 10000    # Column 4 (intensity)
new_txt[:, 5] = 0        # Column 5 (frame placeholder)

# Save the new 6-column array back
# Using standard MyPTV formatting: floats for pixels, ints for parameters
np.savetxt('Cam4_calBlobs', new_txt, fmt=['%.02f', '%.02f', '%d', '%d', '%d', '%d'], delimiter='\t')

print(f"Successfully converted Cam1.txt of shape {txt.shape} to Cam1_6cols.txt of shape {new_txt.shape}")
print("First row:", new_txt[0])