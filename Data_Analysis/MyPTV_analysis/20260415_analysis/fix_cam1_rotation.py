
import os
import shutil
from myptv.extendedZolof.camera import camera_extendedZolof
from myptv.extendedZolof.calibrate import calibrate_extendedZolof

def rotate_points():
    W = 1728
    H = 1700
    base_dir = '/Users/user/Desktop/Research/Data_Analysis/MyPTV_analysis/20260415_analysis'
    
    files_to_rotate = [
        ('cam1_CalBlobs', 'xy'),       # col0=x, col1=y
        ('cam1_cal_points', 'yx'),     # col0=y, col1=x
        ('cam1_manualPoints', 'yx')    # col0=y, col1=x
    ]
    
    for fname, fmt in files_to_rotate:
        fpath = os.path.join(base_dir, fname)
        backup_path = fpath + '.bak'
        if not os.path.exists(backup_path):
            shutil.copy(fpath, backup_path)
            print(f'Backed up {fname} to {fname}.bak')
        
        with open(fpath, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            parts = line.split()
            if not parts: continue
            
            if fmt == 'xy':
                x = float(parts[0])
                y = float(parts[1])
                new_x = W - x
                new_y = H - y
                parts[0] = f'{new_x:.2f}'
                parts[1] = f'{new_y:.2f}'
            else: # yx
                y = float(parts[0])
                x = float(parts[1])
                new_y = H - y
                new_x = W - x
                parts[0] = f'{new_y:.2f}'
                parts[1] = f'{new_x:.2f}'
            
            new_lines.append('\t'.join(parts) + '\n')
            
        with open(fpath, 'w') as f:
            f.writelines(new_lines)
        print(f'Rotated {fname} 180 degrees.')

def run_calibration():
    base_dir = '/Users/user/Desktop/Research/Data_Analysis/MyPTV_analysis/20260415_analysis'
    os.chdir(base_dir)
    
    cam_name = 'cam1'
    cpf = 'cam1_manualPoints'
    
    print(f'Loading camera {cam_name}...')
    cam = camera_extendedZolof(cam_name, cal_points_fname=cpf)
    cam.load('.')
    
    print('Solving initial calibration...')
    cal = calibrate_extendedZolof(cam, cam.image_points, cam.lab_points, quadratic=True)
    cal.calibrate()
    
    err = cal.mean_squared_err()
    cam.save('.')
    print(f'Calibration finished! Mean squared error: {err:.3f} pixels')

if __name__ == '__main__':
    rotate_points()
    run_calibration()
