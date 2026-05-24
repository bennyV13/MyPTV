# -*- coding: utf-8 -*-
"""
Created on Sun 20 March 2022


This script contains a class designed to make using MyPTV a bit easier
for users. 

1) We use a single text file to hold all the parameters used in MyPTV.

2) We have a class that reads the text file and performs the given task:
    segmentation, matching, tracking, smoothing and stitching.

"""


from pandas import DataFrame as df
from yaml import safe_load
from myptv.utils import print_histogram_from_blobs






class workflow(object):
    '''
    A class used to run specific MyPTV operations with parameters given 
    in a dedicated text file.
    '''
    
    def __init__(self, param_file, action, comment=""):
        '''
        input -
        
        param_file - string; the path to a text file with the specified 
                     parameters to be used.
        
        action - string; the name of the PTV action to be performed. Accepted
                 values are: 'segmentation', 'matching', 'tracking',
                 'smoothing', and 'stitching'.
        
        comment - string; a comment to be added to the log entry.
        '''
        
        # read the parameter file:
        self.param_file_path = param_file
        self.params = self.read_params_file()
        self.comment = comment
        
        
        self.allowed_actions = ['help', 'initial_calibration', 
                                'final_calibration',
                                'analyze_calibration_error',
                                'calibration_with_particles', 
                                'matching', 'analyze_disparity',
                                'segmentation',
                                'calculate_BG_image',
                                'calculate_BG_image_batch',
                                'calculate_equilization_map',
                                'smoothing', 'stitching', 'tracking', 
                                'calibration', 'calibration_point_gui', 
                                'match_target_file', '2D_tracking', 
                                'manual_matching',
                                'fiber_orientations',
                                'plot_trajectories',
                                'animate_trajectories',
                                'run_extention',
                                'web_gui',
                                'create_blob_mask',
                                'batch_segmentation']
        
        
        # perform the wanted action:
        if action is None:
            print('Started workflow with no particular action.')
            
        elif action != None:
            
            msg1 = 'The given action is unknown.'
            msg2 = 'allowed actions are:'+str(self.allowed_actions)
            if action not in self.allowed_actions:
                raise ValueError(msg1+'\n'+msg2)
            
            from myptv.logging_utils import ActionLogger
            action_params = self.get_action_params(action)
            
            with ActionLogger(action, action_params, self.param_file_path, comment=self.comment):
                if action == 'initial_calibration':
                    self.initial_calibration()
                
                elif action == 'web_gui':
                    self.do_web_gui()
                    
                elif action == 'final_calibration':
                    self.final_calibration()
                    
                elif action == 'analyze_calibration_error':
                    self.calibration_error_estimation()
                    
                elif action == 'calibration_with_particles':
                    self.calibration_with_particles()
                    
                elif action == 'segmentation':
                    self.do_segmentation()
                    
                elif action == 'matching':
                    self.do_matching()
                    
                elif action == 'analyze_disparity':
                    self.do_analyze_disparity()
                    
                elif action == 'tracking':
                    self.do_tracking()
                    
                elif action == '2D_tracking':
                    self.do_2d_tracking()
                    
                elif action == 'smoothing':
                    self.do_smoothing()
                
                elif action == 'stitching':
                    self.do_stitching()
                
                elif action == 'manual_matching':
                    self.do_manual_matching()
                    
                elif action == 'fiber_orientations':
                    self.do_orientations()
                    
                elif action == 'plot_trajectories':
                    self.do_plot_trajectories()
                    
                elif action == 'animate_trajectories':
                    self.do_animate_trajectories()
                
                elif action == 'run_extention':
                    self.do_run_extention()    
                
                elif action == 'calculate_BG_image':
                    self.do_calculate_BG_image()
                
                elif action == 'calculate_BG_image_batch':
                    self.do_calculate_BG_image_batch()
                    
                elif action == 'calculate_equilization_map':
                    self.do_calculate_equilization_map()

                elif action == 'create_blob_mask':
                    self.do_create_blob_mask()
                
                elif action == 'batch_segmentation':
                    self.do_batch_segmentation()
                
                elif action == 'help':
                    self.help_me()
                    
                    
                # legacy functions:
                elif action == 'calibration':
                    print('Note: you are running an outdated action!')
                    print('consider using the initial_calibration and')
                    print('final_calibration actions instead.')
                    self.calibration_sequence()
                
                elif action == 'calibration_point_gui':
                    print('Note: you are running an outdated action!')
                    print('consider using the initial_calibration and')
                    print('final_calibration actions instead.')
                    self.calibration_point_gui()
                
                elif action == 'match_target_file':
                    print('Note: you are running an outdated action!')
                    print('consider using the initial_calibration and')
                    print('final_calibration actions instead.')
                    self.match_target_file()
            
            
    
    def help_me(self):
        '''
        Prints a message that might help users with the allowable commands.
        '''
        print('\nThe workflow script is intended to help users utilize MyPTVs')
        print('capabilities in their 3D particle tracking experiments. \n')
        
        print('To use the workflow script, run it with Python, usin one of')
        print('the following actions that you would like to perform:\n')
        
        for e, act in enumerate(self.allowed_actions):
            print('%d) "%s"'%(e, act))
            
        print('\nThe script will now close, so the wanted action could be run.')
        
        print('\nGood luck!')
        
        print('\nP.S. - try using the user manual that is found on the main')
        print('Github repository.')
            
    
            
    
    
    def read_params_file(self):
        '''
        Reads the yaml file and formats it as a DataFrame.
        '''
        
        with open(self.param_file_path, 'r') as f:
            params = {}
            
            try:
                sl = safe_load(f)
            except:
                raise ValueError('Error in loading the parameters file.')
                
            for i in range(len(sl)):
                params.update(sl[i])
                    
        as_dict = {'operation':[], 'param': [], 'value': [] }
        for k in params.keys():
            for kk in params[k].keys():
                as_dict['operation'].append(k)
                as_dict['param'].append(kk)
                as_dict['value'].append(params[k][kk])
        
        for i in range(len(as_dict['value'])):
            if as_dict['value'][i] == 'None': 
                as_dict['value'][i] = None
        
        return df(as_dict)
    
    
    
    
    def get_param(self, act, param):
        '''
        Fetches a parameter value from the self.params DataFrame.
        '''
        if act not in set(self.params['operation']):
            raise ValueError('Cant find action %s in the parameter file.'%act)
        
        par_seg = self.params[self.params['operation']==act]
        
        if param not in set(par_seg['param']):
            msg = 'Cant find the %s -> %s in the parameters file.'%(act,param)
            raise ValueError(msg)
        
        return par_seg[par_seg['param']==param]['value'].iloc[0]
    
    
    
    def get_action_params(self, action):
        '''
        Extract the parameters from the self.params DataFrame for the given action.
        Returns a dictionary of key-value pairs (param and value).
        '''
        if action not in set(self.params['operation']):
            return {}
        
        par_seg = self.params[self.params['operation'] == action]
        return dict(zip(par_seg['param'], par_seg['value']))
    
    
    
    def initial_calibration(self):
        '''
        Starts the initial calibration GUI
        '''
        from matplotlib.pyplot import imread
        
        # fetch parameters from the file
        model_name = self.get_param('calibration', '3D_model')
        cam_name = self.get_param('calibration', 'camera_name')
        cal_image = self.get_param('calibration', 'calibration_image')
        target_file = self.get_param('calibration', 'target_file')
        res = self.get_param('calibration', 'resolution').split(',')
        res = (float(res[0]), float(res[1]))
        
        
        if model_name == 'Tsai':
            from myptv.TsaiModel.gui_initial_cal import initial_cal_gui
            image = imread(cal_image)
            if image.shape[1] != res[0] or image.shape[0] != res[1]:
                msg = 'The given resolution doesnt match the image size'
                raise ValueError(msg)
        
            gui = initial_cal_gui(cam_name, cal_image, target_file)
        
        
        elif model_name == 'extendedZolof':
            from myptv.extendedZolof.gui_initial_cal import initial_cal_gui
            image = imread(cal_image)
            gui = initial_cal_gui(cam_name, cal_image, target_file)
            
        
        else:
            models = str(['Tsai', 'extendedZolof'])[1:-1]
            msg = 'Unknown 3D model; permisible model names are: '
            raise ValueError(msg + models)
        
        
        
    def final_calibration(self):
        '''
        Starts the initial calibration GUI
        '''
        import os
        
        # fetch parameters from the file
        model_name = self.get_param('calibration', '3D_model')
        cam_name = self.get_param('calibration', 'camera_name')
        cal_image = self.get_param('calibration', 'calibration_image')
        res = self.get_param('calibration', 'resolution').split(',')
        res = (float(res[0]), float(res[1]))
        
        
        # checking that a camera file in the working directory
        ls = os.listdir('.')                
        
        # make sure camera file exists
        if cam_name not in ls:
            msg = 'No camera file was found. Start with initial calibration.'
            raise ValueError(msg)
            
        # detect the calibration folder
        cal_folder = '.'
        for fname in ls:
            if fname in ['calibration', 'Calibration', 'cal', 'Cal']:
                if os.path.isdir(os.path.join('.', fname)):
                    cal_folder = os.path.join('.', fname)
                    break
        
        # get the blob file and setup the camera instance
        blob_file = os.path.join(cal_folder, cam_name+'_cal_points')
        
        if model_name == 'Tsai':
            from myptv.TsaiModel.gui_final_cal import cal_gui
            from myptv.TsaiModel.camera import camera_Tsai
            from myptv.TsaiModel.calibrate import calibrate_Tsai
            
            try:
                cam = camera_Tsai(cam_name, cal_points_fname = blob_file)
            except:
                msg = 'Calibration point file (%s) is not right!'%blob_file
                msg2 = 'check that the file exists and that it has no errors.'
                raise ValueError(msg+msg2)
                
            
            # load the camera
            cam.load('.')
            print('camera data loaded successfully.')
            cal = calibrate_Tsai(cam, cam.lab_points, cam.image_points)
            print('initial error: %.3f pixels\n'%(cal.mean_squared_err()))
            
            # run the final calibration gui
            print('starting calibration GIU\n')
            gui = cal_gui(cal, cal_image)   

        
        elif model_name == 'extendedZolof':
            from myptv.extendedZolof.camera import camera_extendedZolof
            from myptv.extendedZolof.calibrate import calibrate_extendedZolof
            from myptv.extendedZolof.gui_final_cal import cal_gui
            
            try:
                cam = camera_extendedZolof(cam_name, cal_points_fname = blob_file)
            except:
                msg = 'Calibration point file (%s) is not right!'%blob_file
                msg2 = 'check that the file exists and that it has no errors.'
                raise ValueError(msg+msg2)
            
            cam.load('.')
            print('camera data loaded successfully.')
            cal = calibrate_extendedZolof(cam, 
                                          cam.image_points, 
                                          cam.lab_points)
            print('Starting calibration gui')
            gui = cal_gui(calibrate_obj=cal)
            #cal.calibrate()
            err = cal.mean_squared_err()
            print('Calibration finished. The calibration error is: %.3e'%err)
            #cam.save('.')
            
        
        else:
            models = str(['Tsai', 'extendedZolof'])[1:-1]
            msg = 'Unknown 3D model; permisible model names are: '
            raise ValueError(msg + models)                                
            
    
    
    
    
    def calibration_error_estimation(self):
        '''
        Performs stereo matching of the calibration points and compares
        then with the ground truth. 
        '''
        from numpy import loadtxt, array, mean, median, savez
        from myptv.imaging_mod import camera_wrapper, img_system
        from pandas import DataFrame
        
        cam_names = self.get_param('analyze_calibration_error', 'camera_names')
        cam_names = [val.strip() for val in cam_names.split(',')]
        plot = self.get_param('analyze_calibration_error', 'plot_histogram')
        
        # Get point file suffix option if specified, default to '_cal_points'
        action_params = self.get_action_params('analyze_calibration_error')
        point_file_suffix = action_params.get('point_file_suffix', '_cal_points')
        
        # setting up the img_system 
        cams = [camera_wrapper(cn,'./') for cn in cam_names]
        for cam in cams:
            try:
                cam.load()
            except:
                raise ValueError('camera file %s not found'%cam.name)
        imsys = img_system(cams)
        
        
        # read calibration point files and organize in a dictionary
        point_dic = {}
        for e, cn in enumerate(cam_names):
            filename = './Calibration/%s%s'%(cn, point_file_suffix)
            data = loadtxt(filename)
            for i in range(len(data)):
                try:
                    point_dic[tuple(data[i][2:])][e] = data[i][:2]
                except:
                    point_dic[tuple(data[i][2:])] = {e: data[i][:2]}
        
        
        # for each point in the dictionary, get the calibration error
        errors = []
        errsX, errsY, errsZ = [], [] ,[]
        x, y, z = [], [], []
        for k in point_dic.keys():
            if len(point_dic[k])!=len(cam_names): continue
            ground_truth = array(k)
            triangulation = imsys.stereo_match(point_dic[k], 1e20)[0]
            diff = triangulation - ground_truth
            err = sum((diff)**2)**0.5
            
            errors.append(err)
            errsX.append(diff[0])
            errsY.append(diff[1])
            errsZ.append(diff[2])
            x.append(ground_truth[0])
            y.append(ground_truth[1])
            z.append(ground_truth[2])
            
        
        print('Calibration error in in lab-space units:')
        print('RMS of full error: %.3e'%(mean(errors)))
        print('median of full error: %.3e'%(median(errors)))
        print('x error: %.3e'%(mean(abs(array(errsX)))))
        print('y error: %.3e'%(mean(abs(array(errsY)))))
        print('z error: %.3e'%(mean(abs(array(errsZ)))))
        print('')
        
        if plot == True:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(1,4)
            
            fig.suptitle('Errors in lab-space unites')
            titles = ['total error', 'x error', 'y error', 'z error']
            for e, lst in enumerate([errors, errsX, errsY, errsZ]):
                h = ax[e].hist(lst, bins='auto')
                ax[e].set_title(titles[e])
            plt.show()
        
        
        errs_df = DataFrame({'x':x, 'y':y, 'z':z,
                             'x_err':errsX, 'y_err':errsY, 'z_err':errsZ})
        
        errs_df.to_csv('calibration_errors_data', 
                       sep='\t', 
                       index=False,
                       float_format='%.4e')
        
        print('Calibration errors data saved as "calibration_errors_data" \n')
            
            
        
    
    
    def calibration_with_particles(self):
        '''
        This starts the calibrate with particles sequence
        '''
        from  matplotlib.pyplot import subplots, show
        
        # fetch parameters from the file
        camera_name_0 =  self.get_param('calibration_with_particles',
                                      'camera_name')
        #resolution = self.get_param('calibration_with_particles',
        #                     'resolution').split(',')
        #resolution = (float(resolution[0]), float(resolution[1]))
        traj_filename = self.get_param('calibration_with_particles',
                                      'traj_filename')
        cam_number_0 = self.get_param('calibration_with_particles',
                                      'cam_number') 
        blobs_fname_0 = self.get_param('calibration_with_particles',
                                      'blobs_fname')
        min_traj_len = self.get_param('calibration_with_particles',
                                      'min_traj_len')
        max_point_number = self.get_param('calibration_with_particles',
                                      'max_point_number')
        
        try:
            calibrate_all = self.get_param('calibration_with_particles', 
                                           'calibrate_all')
        except:
            calibrate_all = True

        print('\n', 'starting calibration with particles')
        
        # Identify all cameras in the project to allow looping
        if calibrate_all:
            try:
                all_cam_names = self.get_param('matching', 'camera_names')
                all_cam_names = [val.strip() for val in all_cam_names.split(',')]
                all_blob_files = self.get_param('matching', 'blob_files')
                all_blob_files = [val.strip() for val in all_blob_files.split(',')]
            except:
                try:
                    all_cam_names = self.get_param('analyze_disparity', 'camera_names')
                    all_cam_names = [val.strip() for val in all_cam_names.split(',')]
                    all_blob_files = self.get_param('analyze_disparity', 'blob_files')
                    all_blob_files = [val.strip() for val in all_blob_files.split(',')]
                except:
                    all_cam_names = [camera_name_0]
                    all_blob_files = [blobs_fname_0]
        else:
            all_cam_names = [camera_name_0]
            all_blob_files = [blobs_fname_0]

        # Prepare the list of cameras to process, starting with the primary one
        to_process = []
        primary_added = False
        if camera_name_0 in all_cam_names:
            idx = all_cam_names.index(camera_name_0)
            to_process.append((camera_name_0, idx + 1, all_blob_files[idx]))
            primary_added = True
        else:
            to_process.append((camera_name_0, cam_number_0, blobs_fname_0))
            
        for i, name in enumerate(all_cam_names):
            if name != camera_name_0:
                to_process.append((name, i + 1, all_blob_files[i]))

        # Loop through the cameras
        for i, (camera_name, cam_number, blobs_fname) in enumerate(to_process):
            
            if i > 0:
                print('')
                cont = input('do you want to continue to calibrate with particles %s? (y/n)'%camera_name)
                if cont.lower() != 'y':
                    continue

            print('\n' + '-'*20)
            print('Calibrating %s (camera %d)'%(camera_name, cam_number))
            
            cam_file = open('./'+camera_name, 'r')
            model = cam_file.readline().split()[0]
            cam_file.close()
            
            print('Camera model: %s'%model)
            
            if model == 'Tsai':
                from myptv.TsaiModel.gui_final_cal import cal_gui
                from myptv.TsaiModel.camera import camera_Tsai
                from myptv.TsaiModel.calibrate import calibrate_with_particles_Tsai
                from numpy import zeros
                
                # setting up a camera instance            
                cam = camera_Tsai(camera_name)
                cam.load('./')
                
                # set up the calibration object
                cal_with_p = calibrate_with_particles_Tsai(traj_filename, cam, 
                                                           cam_number, 
                                                           blobs_fname, 
                                                           min_traj_len=min_traj_len,
                                                           max_point_number=max_point_number)
                
                cal = cal_with_p.get_calibrate_instance()
                
                # run the final calibration gui
                print('starting calibration GIU using calibration with particles\n')
                cal_image = zeros(100,100,dtype='int8')
                gui = cal_gui(cal, cal_image) 
                
            if model == 'extendedZolof':
                from myptv.extendedZolof.gui_final_cal import cal_gui
                from myptv.extendedZolof.camera import camera_extendedZolof
                from myptv.extendedZolof.calibrate import calibrate_with_particles_EZ
                from myptv.imaging_mod import camera_wrapper
                from numpy import mean
                
                # setting up a camera instance            
                cam = camera_wrapper(camera_name, './')
                cam.load()
                
                # set up the calibration object
                cwp = calibrate_with_particles_EZ(traj_filename, cam, 
                                                    cam_number, 
                                                    blobs_fname, 
                                                    min_traj_len=min_traj_len,
                                                    max_point_number=max_point_number)
                
                cal = cwp.get_calibrate_instance()
                
                p = cwp.get_particle_disparity()
                err = [sum(pi**2)**0.5 for pi in p]
                print('')
                print('mean disparity before: %.4f px'%(mean(err)))
                print('max disparity before: %.4f px\n'%(max(err)))
                
                # run the final calibration gui
                print('calibrating...\n')
                cal.calibrate()
                
                p = cwp.get_particle_disparity()
                err = [sum(pi**2)**0.5 for pi in p]
                print('mean disparity after: %.4f px'%(mean(err)))
                print('max disparity after: %.4f px\n'%(max(err)))
                
                usr_input = input('save results? (1=yes, other=no)')
                if usr_input=='1':
                    cam.camera.save()
                    print('saved')
            
            
        
    def do_calculate_BG_image(self):
        '''
        Calculates and save static BG image, defined as the mean of images
        '''
        from myptv.segmentation_mod import calculate_BG_image
        import os
        
        dirname = self.get_param('calculate_BG_image', 'images_folder')
        ext = self.get_param('calculate_BG_image', 'image_extension')
        raw_format = self.get_param('calculate_BG_image', 'raw_format')
        N_img = self.get_param('calculate_BG_image', 'N_img')
        savename = self.get_param('calculate_BG_image', 'save_name')
        
        # New parameter
        try:
            iterations = self.get_param('calculate_BG_image', 'iterations')
            if iterations is None: iterations = 1
        except:
            iterations = 1
        
        if savename is not None:
            cwd_ls = os.listdir(os.getcwd())
            if savename in cwd_ls or os.path.exists(savename):
                print('\n The file name "%s" already exists in'%savename)
                print(' the working directory. Should I save anyways?')
                usr = input('(1=yes, else=no)')
                if usr != '1':
                    print('\nskipped calculation and saving')
                    return
        
        calculate_BG_image(dirname, ext, savename, N_img=N_img,
                       raw_format=raw_format, iterations=iterations)


    def do_calculate_BG_image_batch(self):
        '''
        Calculates and save static BG images for multiple folders
        '''
        from myptv.segmentation_mod import calculate_BG_image_batch
        
        recordings_dir = self.get_param('calculate_BG_image_batch', 'recordings_dir')
        output_dir = self.get_param('calculate_BG_image_batch', 'output_dir')
        ext = self.get_param('calculate_BG_image_batch', 'image_extension')
        raw_format = self.get_param('calculate_BG_image_batch', 'raw_format')
        N_img = self.get_param('calculate_BG_image_batch', 'N_img')
        
        try:
            iterations = self.get_param('calculate_BG_image_batch', 'iterations')
            if iterations is None: iterations = 1
        except:
            iterations = 1

        calculate_BG_image_batch(recordings_dir, output_dir, ext, N_img=N_img,
                                 raw_format=raw_format, iterations=iterations)
        
        
    
    def do_calculate_equilization_map(self):
        '''
        Calculates and saves an image equilization map
        '''
        from myptv.segmentation_mod import calculate_equilization_map
        import os
        
        dirname = self.get_param('calculate_equilization_map', 'images_folder')
        ext = self.get_param('calculate_equilization_map', 'image_extension')
        raw_format = self.get_param('calculate_equilization_map', 'raw_format')
        N_img = self.get_param('calculate_equilization_map', 'N_img')
        sigma = self.get_param('calculate_equilization_map', 'sigma')
        BG_image = self.get_param('calculate_equilization_map', 'BG_image')
        savename = self.get_param('calculate_equilization_map', 'save_name')
        
        if savename is not None:
            cwd_ls = os.listdir(os.getcwd())
            if savename in cwd_ls or os.path.exists(savename):
                print('\n The file name "%s" already exists in'%savename)
                print(' the working directory. Should I save anyways?')
                usr = input('(1=yes, else=no)')
                if usr != '1':
                    print('\nskipped calculation and saving')
                    return

        calculate_equilization_map(dirname, ext, sigma, savename, N_img=N_img,
                               BG_image=BG_image, raw_format=raw_format)
    
    
    
    def do_segmentation(self):
        '''
        Will perform segmentation on the images given in the parameters file
        and save the results on the given location.
        '''
        
        from numpy import zeros, amax
        from skimage.io import imread
        import os
        from os.path import exists as pathExists, dirname as path_dirname
        
        # fetching parameters
        dirname = self.get_param('segmentation', 'images_folder')
        ext = self.get_param('segmentation', 'image_extension')
        N_img = self.get_param('segmentation', 'Number_of_images')
        image_start = self.get_param('segmentation', 'image_start')
        sigma = self.get_param('segmentation', 'blur_sigma')
        threshold = self.get_param('segmentation', 'threshold')
        median = self.get_param('segmentation', 'median')
        local_filter = self.get_param('segmentation', 'local_filter')
        max_xsize = self.get_param('segmentation', 'max_xsize')
        max_ysize = self.get_param('segmentation', 'max_ysize')
        max_mass = self.get_param('segmentation', 'max_mass')
        min_xsize = self.get_param('segmentation', 'min_xsize')
        min_ysize = self.get_param('segmentation', 'min_ysize')
        min_mass = self.get_param('segmentation', 'min_mass')
        mask = self.get_param('segmentation', 'mask')
        plot_res = self.get_param('segmentation', 'plot_result')
        save_name = self.get_param('segmentation', 'save_name')
        ROI = self.get_param('segmentation', 'ROI')
        single_img_name = self.get_param('segmentation', 'single_image_name')
        method = self.get_param('segmentation', 'method')
        p_size = self.get_param('segmentation', 'particle_size')
        shape = self.get_param('segmentation', 'shape')
        remove_BG = self.get_param('segmentation', 'remove_background')
        eq_map = self.get_param('segmentation', 'equilization_map')
        raw_format = self.get_param('segmentation', 'raw_format')
        DoG_sigmas = self.get_param('segmentation', 'DoG_sigmas')
        multiprocessing = self.get_param('segmentation', 'multiprocessing')
        try:
            sub_type = self.get_param('segmentation', 'subtract_type')
        except:
            sub_type = 'absolute'
        try:
            pca_limit = self.get_param('segmentation', 'pca_limit')
        except:
            pca_limit = 1.0

        try:
            bg_iterations = self.get_param('segmentation', 'bg_iterations')
            if bg_iterations is None: bg_iterations = 1
        except:
            bg_iterations = 1
            
        try:
            draw_fiber_features = self.get_param('segmentation', 'draw_fiber_features')
            if draw_fiber_features is None: draw_fiber_features = True
        except:
            draw_fiber_features = True
            
        try:
            arrow_scale = self.get_param('segmentation', 'arrow_scale')
            if arrow_scale is None: arrow_scale = 100.0
        except:
            arrow_scale = 100.0
        
        # Pre-check the save directory
        if save_name is not None:
            saveDir = path_dirname(save_name)
            if saveDir != '' and not pathExists(saveDir):
                try:
                    from os import makedirs
                    makedirs(saveDir)
                    print(f"Created directory: {saveDir}")
                except Exception as e:
                    print(f"Warning: Could not create directory {saveDir} before starting. Error: {e}")
                    print("The calculation will continue, but data might be saved to 'saved_data' if the primary path remains unreachable.")

        # reading preprepared mask
        if type(mask)==str:
            mask = imread(mask)
        
        if method not in ['dilation', 'labeling']:
            raise ValueError('Method can be only "dilation" or "labeling"')
        
        if method=='dilation' and type(p_size) != int:
            raise ValueError('In dilation, particle_size can only be integer')
        
        if shape not in ['particles', 'fibers']:
            raise ValueError('Shape can be only "particles" or "fibers"')
        
        if raw_format==False:
            imread_func = lambda x: imread(x)
        else:
            import rawpy
            imread_func = lambda x: rawpy.imread(x).raw_image
        
        
        # get the shape of the images
        allfiles = os.listdir(dirname)
        n_ext = len(ext)
        image_files = sorted(list(filter(lambda s: (s[-n_ext:]==ext) and (not s.startswith('._')), allfiles)))
        if single_img_name in image_files:
            image0 = imread_func(os.path.join(dirname,single_img_name))
        else:
            image0 = imread_func(os.path.join(dirname,image_files[0]))
        
        # preparing a mask using the given ROI
        if ROI is not None:
            ROI = [int(val) for val in ROI.split(',')]
            mask_ROI = zeros(image0.shape)
            mask_ROI[ROI[2]:ROI[3]+1, ROI[0]:ROI[1]+1] = 1
            mask = mask * mask_ROI
            mask = (mask / amax(mask)).astype('uint')
            
            
        # getting equilization map
        if eq_map is None:
            print('\n','Not equilyzing')
            
        elif type(eq_map)==str:
            if shape=='particles':
                print('\n','using given equilization map')
                eq_map = imread(eq_map)
            
            elif shape=='fibers':
                raise TypeError('equilization not implemented yet for fibers')
        
        else:
            raise TypeError('equilization map not None nor path to an eqmap')
        
        
        if DoG_sigmas is not None and shape=='fibers':
                raise TypeError('DoG not implemented yet for fibers; use None')
            
            
        def calculate_BG_image(dirname, extension, iterations=1):
            '''
            Calculates the background of images, defined as the iterative median
            over a subsample of 200 images from the image folder.
            '''
            import os
            import numpy as np
            from skimage import io
            
            print('\ncalculating background...')
            
            allfiles = os.listdir(dirname)
            n_ext = len(extension)
            fltr = lambda s: (s[-n_ext:]==extension) and (not s.startswith('._'))
            image_files = sorted(list(filter(fltr, allfiles)))
            image_files = [os.path.join(dirname, fn) for fn in image_files]
            
            if len(image_files)<=200:
                im_paths = image_files
            else:
                im_paths = image_files[::int(len(image_files)/400+1)][:200]
            
            # Load images into memory as float32
            images = []
            for path in im_paths:
                images.append(io.imread(path).astype('float32'))
            images = np.array(images)
            
            # Initial background calculation (Iteration 1)
            BG_total = np.median(images, axis=0)
            
            # Iterative refinement (Iteration 2+)
            for i in range(iterations - 1):
                desc = f'Refining BG (iteration {i+2}/{iterations})'
                print(desc)
                residuals = images - BG_total
                BG_i = np.median(residuals, axis=0)
                BG_total += BG_i
            
            return BG_total
            
        
        if shape=='particles':
            
            from myptv.segmentation_mod import loop_segmentation
            from myptv.segmentation_mod import particle_segmentation
        
            # segmenting the image if there are more than 1 frames
            if N_img is None or N_img>1:
                
                if type(remove_BG)==str:
                    print('\n','using given background image')
                    BG = imread(remove_BG)*1.0
                elif remove_BG==True:
                    print('\n','calculating background image')
                    BG = calculate_BG_image(dirname, ext, iterations=bg_iterations)
                else:
                    BG=False
                
                loopSegment = loop_segmentation(dirname, 
                                                particle_size=p_size,
                                                extension=ext,
                                                image_start=image_start,
                                                N_img=N_img,
                                                remove_ststic_BG=BG,
                                                equalize_image=eq_map,
                                                DoG_sigma=DoG_sigmas,
                                                sigma=sigma, 
                                                median=median,
                                                threshold=threshold, 
                                                local_filter=local_filter, 
                                                max_xsize=max_xsize, 
                                                max_ysize=max_ysize,
                                                max_mass=max_mass,
                                                min_xsize=min_xsize, 
                                                min_ysize=min_ysize,
                                                min_mass=min_mass,
                                                mask=mask,
                                                method=method,
                                                subtract_type=sub_type,
                                                raw_format=raw_format,
                                                multiprocessing=multiprocessing)
            
                loopSegment.segment_folder_images()
                
                print('\n','blobs found:', len(loopSegment.blobs))
                
                # --- Added histogram plot ---
                try:
                    print_histogram_from_blobs(loopSegment.blobs, title=save_name)
                except Exception as e:
                    print(f" (Histogram skipped: {e})")
                # -----------------------------
                
                # saving the semented blobs:
                if save_name is not None and type(save_name)==str:
                    cwd_ls = os.listdir(os.getcwd())
                    if save_name in cwd_ls or os.path.exists(save_name):
                        print('\n The file name "%s" already exists in'%save_name)
                        print(' the working directory. Should I save anyways?')
                        usr = input('(1=yes, else=no)')
                        if usr == '1':
                            loopSegment.save_results(save_name)
                            print('\nfile saved.')
                        else:
                            print('\nskipped saving')
                        
                    else:
                        loopSegment.save_results(save_name)
                        print('\nfile saved.')    
                print('\nDone.\n')
                
            
            
            # segmenting the image if there is only 1 frames
            if N_img == 1:
                print('\n','starting segmentation on a single image.')
                if single_img_name not in image_files:
                    in_ = os.path.join(dirname,single_img_name)
                    msg = 'Image %s not found in the directory.'%in_
                    raise ValueError(msg)
                
                if type(remove_BG)==str:
                    print('\n','using given background image')
                    BG = imread(remove_BG)*1.0
                elif remove_BG==True:
                    print('\n','calculating background image')
                    BG = calculate_BG_image(dirname, ext, iterations=bg_iterations)
                else:
                    BG=None
                    
                print('\n','segmenting image: %s'%single_img_name)
                particleSegment = particle_segmentation(image0, 
                                                        particle_size=p_size,
                                                        sigma=sigma, 
                                                        median=median,
                                                        BG_image=BG,
                                                        EQ_map=eq_map,
                                                        DoG_sigma=DoG_sigmas,
                                                        threshold=threshold, 
                                                        local_filter=local_filter, 
                                                        max_xsize=max_xsize, 
                                                        max_ysize=max_ysize,
                                                        max_mass=max_mass,
                                                        min_xsize=min_xsize, 
                                                        min_ysize=min_ysize,
                                                        min_mass=min_mass,
                                                        mask=mask,
                                                        method=method,
                                                        subtract_type=sub_type)
                particleSegment.get_blobs()
                particleSegment.apply_blobs_size_filter()
                
                print('blobs found:', len(particleSegment.blobs))
                
                if plot_res:
                    from matplotlib.pyplot import show
                    particleSegment.plot_blobs()
                    show()
                    
                    
                # Saving the segmented blobs:
                if save_name is not None and type(save_name)==str:
                    cwd_ls = os.listdir(os.getcwd())
                    if save_name in cwd_ls or os.path.exists(save_name):
                        print('\n The file name "%s" already exists in'%save_name)
                        print(' the working directory. Should I save anyways?')
                        usr = input('(1=yes, else=no)')
                        if usr == '1':
                            particleSegment.save_results(save_name)
                            print('\nfile saved.')
                        else:
                            print('\nskipped saving')
                    else:
                        particleSegment.save_results(save_name)
                        print('\nfile saved.')
                    
                print('\nDone.\n')
                
            
        elif shape=='fibers':
            
            from myptv.fibers.fiber_segmentation_mod import fiber_segmentation
            from myptv.fibers.fiber_segmentation_mod import loop_fiber_segmentation
            
            # segmenting the image if there are more than 1 frames
            if N_img is None or N_img>1:
                
                if type(remove_BG)==str:
                    print('\n','using given background image')
                    BG = imread(remove_BG)*1.0
                elif remove_BG==True:
                    print('\n','calculating background image')
                    BG = calculate_BG_image(dirname, ext, iterations=bg_iterations)
                else:
                    BG=False
                    
                loopSegment = loop_fiber_segmentation(dirname, 
                                                particle_size=p_size,
                                                extension=ext,
                                                image_start=image_start,
                                                N_img=N_img, 
                                                sigma=sigma,
                                                remove_ststic_BG=BG,
                                                median=median,
                                                threshold=threshold, 
                                                local_filter=local_filter, 
                                                max_xsize=max_xsize, 
                                                max_ysize=max_ysize,
                                                max_mass=max_mass,
                                                min_xsize=min_xsize, 
                                                min_ysize=min_ysize,
                                                min_mass=min_mass,
                                                mask=mask,
                                                method=method,
                                                raw_format=raw_format,
                                                pca_limit=pca_limit)
                
                loopSegment.segment_folder_images()
                
                print('\n','blobs found:', len(loopSegment.blobs))
                
                # --- Added histogram plot ---
                try:
                    print_histogram_from_blobs(loopSegment.blobs, title=save_name)
                except Exception as e:
                    print(f" (Histogram skipped: {e})")
                # -----------------------------
                
                # saving the semented blobs:
                if save_name is not None and type(save_name)==str:
                    cwd_ls = os.listdir(os.getcwd())
                    if save_name in cwd_ls or os.path.exists(save_name):
                        print('\n The file name "%s" already exists in'%save_name)
                        print(' the working directory. Should I save anyways?')
                        usr = input('(1=yes, else=no)')
                        if usr == '1':
                            loopSegment.save_results(save_name)
                            loopSegment.save_results_direction(save_name+'_directions')
                            print('\nfile saved.')
                        else:
                            print('\nskipped saving')
                        
                    else:
                        loopSegment.save_results(save_name)
                        loopSegment.save_results_direction(save_name+'_directions')
                        print('\nfile saved.')    
                print('\nDone.\n')
                
            
            
            # segmenting the image if there is only 1 frames
            if N_img == 1:
                print('\n','starting segmentation on a single image.')
                if single_img_name not in image_files:
                    in_ = os.path.join(dirname,single_img_name)
                    msg = 'Image %s not found in the directory.'%in_
                    raise ValueError(msg)
                
                if type(remove_BG)==str:
                    print('\n','using given background image')
                    BG = imread(remove_BG)*1.0
                elif remove_BG==True:
                    print('\n','calculating background image')
                    BG = calculate_BG_image(dirname, ext, iterations=bg_iterations)
                else:
                    BG=None
                
                print('\n','segmenting image: %s'%single_img_name)
                particleSegment = fiber_segmentation(image0, 
                                                        particle_size=p_size,
                                                        sigma=sigma, 
                                                        median=median,
                                                        BG_image=BG,
                                                        threshold=threshold, 
                                                        local_filter=local_filter, 
                                                        max_xsize=max_xsize, 
                                                        max_ysize=max_ysize,
                                                        max_mass=max_mass,
                                                        min_xsize=min_xsize, 
                                                        min_ysize=min_ysize,
                                                        min_mass=min_mass,
                                                        mask=mask,
                                                        method=method,
                                                        pca_limit=pca_limit)
                
                particleSegment.get_blobs()
                particleSegment.apply_blobs_size_filter()
                
                print('blobs found:', len(particleSegment.blobs))
                
                if plot_res:
                    from matplotlib.pyplot import show
                    particleSegment.plot_blobs(draw_fiber_features=draw_fiber_features, scale=arrow_scale)
                    show()
                    
                    
                # Saving the segmented blobs:
                if save_name is not None and type(save_name)==str:
                    cwd_ls = os.listdir(os.getcwd())
                    if save_name in cwd_ls or os.path.exists(save_name):
                        print('\n The file name "%s" already exists in'%save_name)
                        print(' the working directory. Should I save anyways?')
                        usr = input('(1=yes, else=no)')
                        if usr == '1':
                            particleSegment.save_results(save_name)
                            particleSegment.save_results_direction(save_name+'_directions')
                            print('\nfile saved.')
                        else:
                            print('\nskipped saving')
                    else:
                        particleSegment.save_results(save_name)
                        particleSegment.save_results_direction(save_name+'_directions')
                        print('\nfile saved.')
                    
                print('\nDone.\n')
            
            
            
            
    def do_matching(self):
        '''
        Will perform the stereo matching with the file given parameters
        '''
        from myptv.particle_matching_mod import matching_with_marching_particles_algorithm
        from myptv.imaging_mod import camera_wrapper, img_system
        from os import getcwd, listdir
        from os.path import exists as pathExists, dirname as path_dirname
        from time import localtime, strftime
        
        
        # fetching the parameters
        blob_fn = self.get_param('matching', 'blob_files')
        blob_fn = [val.strip() for val in blob_fn.split(',')]
        cam_names = self.get_param('matching', 'camera_names')
        cam_names = [val.strip() for val in cam_names.split(',')]
        # res = self.get_param('matching', 'cam_resolution')
        # res = tuple([float(val) for val in res.split(',')])
        ROI = self.get_param('matching', 'ROI').split(',')
        ROI = [float(ROI[i]) for i in range(6)]
        voxel_size = self.get_param('matching', 'voxel_size')
        N0 = self.get_param('matching', 'N0')
        max_err = self.get_param('matching', 'max_err')
        min_cam_match = self.get_param('matching', 'min_cam_match')
        frame_start = self.get_param('matching', 'frame_start')
        N_frames = self.get_param('matching', 'N_frames')
        march_forwards = self.get_param('matching', 'march_forwards')
        march_backwards = self.get_param('matching', 'march_backwards')
        save_name = self.get_param('matching', 'save_name')
        
        
        if N0==0 and voxel_size==None:
            raise ValueError('No initial guess method given (N0=0, voxel_size=None)')
        
        if min_cam_match<2:
            raise ValueError('min_cam_match needs to be at least 2.')
        
        # setting up the img_system 
        cams = [camera_wrapper(cn,'./') for cn in cam_names]
        for cam in cams:
            try:
                cam.load()
            except:
                raise ValueError('camera file %s not found'%cam.name)
        imsys = img_system(cams)
        
        
        mps = matching_with_marching_particles_algorithm(imsys, 
                                               blob_fn, 
                                               max_err, 
                                               ROI,
                                               N0,
                                               voxel_size,
                                               min_cam_match=min_cam_match,
                                               reverse_eta_zeta=True)

        
        
        # setting the frame range to match
        ts = int(mps.frames[0])
        te = int(mps.frames[-1])
        print('segmented particles time range: %d -> %d'%(ts,te),'\n')
        
        if frame_start is not None:
            if frame_start>=ts and frame_start <=te:
                ts = frame_start
            else: 
                raise ValueError('frame_start outside the available frame range')
        
        if N_frames is None:
            frames = range(ts, te+1)
        else:
            try:
                frames = range(ts, ts+N_frames)
            except:
                tp = type(frames)
                msg = 'N_frames must be an integer or None (given %s).'%tp
                raise TypeError(msg)
                
        # Pre-check the save directory
        if save_name is not None:
            saveDir = path_dirname(save_name)
            if saveDir != '' and not pathExists(saveDir):
                try:
                    from os import makedirs
                    makedirs(saveDir)
                    print(f"Created directory: {saveDir}")
                except Exception as e:
                    print(f"Warning: Could not create directory {saveDir} before starting. Error: {e}")
                    print("The calculation will continue, but data might be saved to 'saved_data' if the primary path remains unreachable.")

        # mathing
        print('Starting stereo-matching at: ', strftime("%H:%M:%S", localtime()))
        
        if march_forwards==True:
            print('Matching forwards. Frames: %d -> %d'%(frames[0], frames[-1]))
            for f in frames:
                mps.match_frame(f)
                
        if march_backwards==True:
            print('\n','Matching backwards. Frames: %d -> %d'%(frames[-1], frames[0]))
            for f in frames[::-1]:
                mps.match_frame(f)
        
        
        
        # print matching statistics
        print('')
        print('Finished! \n')
        print('particles matched: %d \n'%(len(mps.matches)))
        
        Nframes = len(frames)
        c4 = sum([1 for p in mps.matches if len(p[1])==4]) / Nframes
        print('quadruplets: %.1f per frame'%c4)
        c3 = sum([1 for p in mps.matches if len(p[1])==3]) / Nframes
        print('triplets: %.1f per frame'%c3)
        c2 = sum([1 for p in mps.matches if len(p[1])==2]) / Nframes
        print('pairs: %.1f per frame \n'%c2)
        
        
        # save the results
        if save_name is not None:
            cwd_ls = listdir(getcwd())
            if save_name in cwd_ls or pathExists(save_name):
                print('\n The file name "%s" already exists in'%save_name)
                print(' the working directory. Should I save anyways?')
                usr = input('(1=yes, else=no)')
                if usr == '1':
                    print('\n','saving file.')
                    mps.save_particles(save_name)
                else:
                    print('\n','skiped saving.')
                
            else:
                print('\n','saving file.')
                mps.save_particles(save_name)
        
        print('\n', 'Finished Matching.\n')
            
        
        
    def do_analyze_disparity(self):
        '''
        Will run the matching_quality_GUI from 
        myptv -> makePlots -> quality_estimators.
        '''
        from myptv.makePlots.quality_estimators import matching_quality_GUI
        from myptv.imaging_mod import camera_wrapper, img_system
        
        # fetching parameters
        blob_files = self.get_param('analyze_disparity', 'blob_files')
        blob_files = [val.strip() for val in blob_files.split(',')]
        particle_filename = self.get_param('analyze_disparity', 'particle_filename')
        camera_names = self.get_param('analyze_disparity', 'camera_names')
        camera_names = [val.strip() for val in camera_names.split(',')]
        max_err = self.get_param('analyze_disparity', 'max_err')
        min_cam_match = self.get_param('analyze_disparity', 'min_cam_match')
        
        
        cams = [camera_wrapper(cn, './') for cn in camera_names]
        for c in cams: c.load()
        imsys = img_system(cams)
        dmax = max_err
        min_cam_match = min_cam_match
    
        G = matching_quality_GUI(imsys, blob_files, particle_filename, dmax, 
                                 min_cam_match=min_cam_match)
        
        
        
    def do_tracking(self):
        '''
        Will perform the tracking using the file given parameters.
        '''
        from myptv.tracking_mod import tracker_four_frames, tracker_multiframe
        from myptv.tracking_mod import traj_NSR, fill_in_trajectory
        from numpy import array
        from os import getcwd, listdir
        from os.path import exists as pathExists, dirname as path_dirname
        
        # fetching parameters
        particles_fm = self.get_param('tracking', 'particles_file_name')
        frame_start = self.get_param('tracking', 'frame_start')
        N_frames = self.get_param('tracking', 'N_frames')
        d_max = self.get_param('tracking', 'd_max')
        dv_max = self.get_param('tracking', 'dv_max')
        mean_flow = self.get_param('tracking', 'mean_flow')
        candidate_graph = self.get_param('tracking', 'plot_candidate_graph')
        save_name = self.get_param('tracking', 'save_name')
        
        method = self.get_param('tracking', 'method')
        max_dt = self.get_param('tracking', 'max_dt')
        Ns = self.get_param('tracking', 'Ns')
        NSR_th = self.get_param('tracking', 'NSR_threshold')
        
        # Pre-check the save directory
        if save_name is not None:
            saveDir = path_dirname(save_name)
            if saveDir != '' and not pathExists(saveDir):
                try:
                    from os import makedirs
                    makedirs(saveDir)
                    print(f"Created directory: {saveDir}")
                except Exception as e:
                    print(f"Warning: Could not create directory {saveDir} before starting. Error: {e}")
                    print("The calculation will continue, but data might be saved to 'saved_data' if the primary path remains unreachable.")

        if method not in ['multiframe', 'fourframe']:
            raise ValueError("method can only be 'multiframe' or 'four_frame'.")
        
        
        if method=='fourframe':
            
            # initiate the tracker
            t4f = tracker_four_frames(particles_fm, 
                                      d_max=d_max, 
                                      dv_max=dv_max,
                                      mean_flow=array(mean_flow),
                                      store_candidates = candidate_graph)
            
            #setting up the frame range
            ts = int(t4f.times[0])
            te = int(t4f.times[-1])
            
            print('available particles time range: %d -> %d'%(ts,te),'\n')
            
            if candidate_graph and (te-ts)>100:
                print('Warning: you are about to plot a candidate graph with')
                print('more than 100 frames.')
                ans = input('Do you wish to proceed (1 = Yes , else = No)?  ')
                
                if ans=='1':
                    pass
                
                else:
                    print('quitting ')
                    return None
                
            
            if frame_start is not None:
                if frame_start>=ts and frame_start <=te:
                    ts = frame_start
                else: 
                    print('Warning: frame_start outside the available frame range')
                    #raise ValueError('frame_start outside the available frame range')
            
            if N_frames is None:
                frames = range(ts, te)
            else:
                try:
                    frames = range(ts, ts+N_frames)
                except:
                    tp = type(frames)
                    msg = 'N_frames must be an integer or None (given %s).'%tp
                    raise TypeError(msg)
            
            # do the tracking
            t4f.track_all_frames(frames=frames)
            
            # print some statistics
            tr = array(t4f.return_connected_particles())
            untracked = len(tr[tr[:,0]==-1])
            tot = len(tr)
            print('untracked fraction:', untracked/tot)
            print('tracked per frame:', (tot-untracked)/len(set(tr[:,-1])))
            
            if candidate_graph:
                t4f.plot_candidate_graph()
        
        
        
        
        
        
        elif method=='multiframe':
            
            tmf = tracker_multiframe(particles_fm, max_dt, Ns, 
                                     d_max=d_max, dv_max=dv_max, 
                                     NSR_th=NSR_th, 
                                     mean_flow=array(mean_flow))
            
            #setting up the frame range
            ts = int(tmf.times[0])
            te = int(tmf.times[-1])
            print('available particles time range: %d -> %d'%(ts,te),'\n')
            
            if candidate_graph:
                print('\nNote, candidate graph can only be plotted with')
                print('fourframe tracker, so it is skipped.')
            
            
            if frame_start is not None:
                if frame_start>=ts and frame_start <=te:
                    ts = frame_start
                else: 
                    print('Warning: frame_start outside the available frame range')
                    #raise ValueError('frame_start outside the available frame range')
            
            if N_frames is None:
                frames = range(ts, te)
            else:
                try:
                    frames = range(ts, ts+N_frames)
                except:
                    tp = type(frames)
                    msg = 'N_frames must be an integer or None (given %s).'%tp
                    raise TypeError(msg)
            
            
            # doing the tracking
            if type(Ns)==list: 
                frame_skips = max([int(min(Ns)/3), 1])
                if any([ns%2==0 for ns in Ns]):
                    raise ValueError('Ns needs to have only odd integers')
                
            else: frame_skips = max([int(Ns/3), 1])
            tmf.track_frames(f0=ts, fe=te, frame_skips=frame_skips, Ns=Ns)
            
            # interpolating missing points
            tmf.interpolate_trajs()
            

        
        # save the results
        if save_name is not None:
            cwd_ls = listdir(getcwd())
            if save_name in cwd_ls or pathExists(save_name):
                print('\n The file name "%s" already exists in'%save_name)
                print(' the working directory. Should I save anyways?')
                usr = input('(1=yes, else=no)')
                if usr == '1':
                    print('\n','saving file.')
                    if method=='fourframe': t4f.save_results(save_name)
                    elif method=='multiframe': tmf.save_results(save_name)
                
                else:
                    print('\n', 'skipped saving.')
            
            else:
                print('\n','saving file.')
                if method=='fourframe': t4f.save_results(save_name)
                elif method=='multiframe': tmf.save_results(save_name)
        
        print('\n', 'Finished tracking.')
        
        
        
        
        
        
    def do_smoothing(self):
        '''
        Will smooth the trajectories using the specified file given paramters.
        '''
        from numpy import loadtxt
        from myptv.traj_smoothing_mod import smooth_trajectories
        from os import getcwd, listdir
        from os.path import exists as pathExists
        
        # fetching the smoothing parameters
        trajectory_file = self.get_param('smoothing', 'trajectory_file')
        window = self.get_param('smoothing', 'window_size')
        polyorder = self.get_param('smoothing', 'polynom_order')
        min_traj_length = self.get_param('smoothing', 'min_traj_length')
        repetitions = self.get_param('smoothing', 'repetitions')
        save_name = self.get_param('smoothing', 'save_name')
        
        if min_traj_length <= polyorder:
            raise ValueError('min_traj_length must be larger than polyorder')

        traj_list = loadtxt(trajectory_file)
        
        
        # smoothing the trajectories     
        print('Starting to smooth trajectories.')
        sm = smooth_trajectories(traj_list, 
                                 window, 
                                 polyorder,
                                 repetitions=repetitions,
                                 min_traj_length=min_traj_length)
        sm.smooth()
        
        # saving the data
        if save_name is not None:
            cwd_ls = listdir(getcwd())
            if save_name in cwd_ls or pathExists(save_name):
                print('\n The file name "%s" already exists in'%save_name)
                print(' the working directory. Should I save anyways?')
                usr = input('(1=yes, else=no)')
                if usr == '1':
                    print('\n', 'Saving the smoothed data (%s).'%save_name)
                    sm.save_results(save_name)
                else:
                    print('\n', 'Skipped saving file.')
            
            else:
                print('\n', 'Saving the smoothed data (%s).'%save_name)
                sm.save_results(save_name)
        
        print('\n', 'Done.')
        
        
    
    
    def do_stitching(self):
        '''
        Will perfrom trajectory stitching using the file given parameters.
        '''
        from numpy import loadtxt
        from myptv.traj_stitching_mod import traj_stitching
        from os import getcwd, listdir
        from os.path import exists as pathExists
        
        # fetchhing the stitching parameters
        trajectory_file = self.get_param('stitching', 'trajectory_file')
        Ts = self.get_param('stitching', 'max_time_separation')
        dm = self.get_param('stitching', 'max_distance')
        save_name = self.get_param('stitching', 'save_name')
        
        traj_list = loadtxt(trajectory_file)
        
        # stitch the trajectories
        ts = traj_stitching(traj_list, Ts, dm)
        ts.stitch_trajectories()
        
        # saving the data
        if save_name is not None:
            cwd_ls = listdir(getcwd())
            if save_name in cwd_ls or pathExists(save_name):
                print('\n The file name "%s" already exists in'%save_name)
                print(' the working directory. Should I save anyways?')
                usr = input('(1=yes, else=no)')
                if usr == '1':
                    print('\n', 'Saveing the data.')    
                    ts.save_results(save_name)
                else:
                    print('\n', 'Skipped saving file.')
            
            else:
                print('\n', 'Saveing the data.')    
                ts.save_results(save_name)
        
        print('\n', 'Done.')
        
        
        
    def do_2d_tracking(self):
        '''
        Will perform 2D tracking of segmented blobs using give data.
        '''
            
        from myptv.imaging_mod import camera_wrapper
        from myptv.tracking_2D_mod import track_2D
        
        # fetchhing the stitching parameters
        fname = self.get_param('2D_tracking', 'blob_file')
        frame_start = self.get_param('2D_tracking', 'frame_start')
        N_frames = self.get_param('2D_tracking', 'N_frames')
        cam_name = self.get_param('2D_tracking', 'camera_name')
        res = self.get_param('2D_tracking', 'camera_resolution')
        res = tuple([float(val) for val in res.split(',')])
        z_particles = self.get_param('2D_tracking', 'z_particles')
        d_max = self.get_param('2D_tracking', 'd_max')
        dv_max = self.get_param('2D_tracking', 'dv_max')
        save_name = self.get_param('2D_tracking', 'save_name')

        print('\ninitiating 2D tracking...')

        if cam_name==None:
            cam = None
        
        else:
            cam = camera_wrapper(cam_name, '')
            cam.load()
        
        print('\nloading blobs and transforming to lab-space coordinates')
        t2d = track_2D(cam, fname, z_particles, d_max=d_max, dv_max = dv_max, 
                       reverse_eta_zeta=True)
        
        t2d.blobs_to_particles()
        
        
        #setting up the frame range
        ts = int(t2d.times[0])
        te = int(t2d.times[-1])
        
        print('\navailable particles time range: %d -> %d'%(ts,te),'\n')
        
        if frame_start is not None:
            if frame_start>=ts and frame_start <=te:
                ts = frame_start
            else: 
                print('Warning: frame_start outside the available frame range')
                #raise ValueError('frame_start outside the available frame range')
        
        if N_frames is None:
            frames = range(ts, te)
        else:
            try:
                frames = range(ts, ts+N_frames)
            except:
                tp = type(frames)
                msg = 'N_frames must be an integer or None (given %s).'%tp
                raise TypeError(msg)
        
        
        print('\ntrackin particles...')
        
        t2d.track_all_frames(frames=frames)
        
        print('\nsaving results...')
        
        t2d.save_results(save_name)
        
        print('\nDone!')
        
        
    
    def do_manual_matching(self):
        '''
        Runs a GUI that helps performing manual stereo-matching of
        points from images. You simply click on the images from different
        cameras and the GUI gives back the 3D coordinates of this point. 
        '''
        from myptv.gui_manual_matching import man_match_gui
        
        # fetchhing the stitching parameters
        camera_names = self.get_param('manual_matching_GUI', 'cameras')
        im_fname = self.get_param('manual_matching_GUI', 'images')
        
        print(camera_names)
        print(im_fname)
        
        gui = man_match_gui(camera_names, im_fname, cameras_folder='.')
    
        
    
    
    
    
    def do_web_gui(self):
        '''
        Launches the web-based Initial Calibration GUI.
        '''
        import subprocess
        import os
        import sys
        import myptv

        print('\nStarting web-based Initial Calibration GUI...')

        # Find the package directory
        pkg_path = os.path.dirname(myptv.__file__)
        launch_script = os.path.join(pkg_path, "web_gui", "launch_gui.py")

        if not os.path.exists(launch_script):
            print(f"Error: Launch script not found at {launch_script}")
            return

        # Run the launch script as a separate process
        # We pass the param_file path as an environment variable or argument
        env = os.environ.copy()
        env["MYPTV_PARAMS"] = os.path.abspath(self.param_file_path)

        try:
            subprocess.run([sys.executable, launch_script], env=env)
        except KeyboardInterrupt:
            print("\nWeb GUI stopped.")


    def do_orientations(self):

        '''
        A part of Eric Aschari's Fiber tracking extension (MyFTV):
            
        Will perform a fiber orientation analysis
        '''
        from numpy import loadtxt, empty, array, zeros, pi, sign, savetxt, shape
        from os.path import exists as pathExists, dirname as path_dirname
        from os import makedirs
        
        # fetching the parameters
        cam_names = self.get_param('fiber_orientations', 'camera_names')
        cam_names = [val.strip() for val in cam_names.split(',')]
        blob_fn = self.get_param('fiber_orientations', 'blob_files')
        blob_fn = [val.strip() for val in blob_fn.split(',')]
        ori_lim = self.get_param('fiber_orientations', 'ori_lim')
        trajectory_file = self.get_param('fiber_orientations','trajectory_file')
        save_name = self.get_param('fiber_orientations', 'save_name')
        method = self.get_param('fiber_orientations','method')

        # Pre-check the save directory
        if save_name is not None:
            saveDir = path_dirname(save_name)
            if saveDir != '' and not pathExists(saveDir):
                try:
                    makedirs(saveDir)
                    print(f"Created directory: {saveDir}")
                except Exception as e:
                    print(f"Warning: Could not create directory {saveDir} before starting. Error: {e}")
        
        allowed_methods = ['MinProjection', 'PlaneIntersect']
        if method not in allowed_methods:
            raise ValueError('Method should be one of ' + str(allowed_methods))
        
        print('Running fiber orientations with the %s method'%allowed_methods)
        
        
        # The original Aschari Gambino and Brizzolara method
        # ==================================================
        if method == 'PlaneIntersect':  
            #run orientation code
            camn = shape(cam_names)[0]
            print('Running MyFTV on', camn, 'cameras...')
            if camn == 2:
                run_2cams_orientation(cam_names,blob_fn,trajectory_file,save_name)
            elif camn == 3:
                run_3cams_orientation(ori_lim,cam_names,blob_fn,trajectory_file,save_name)
            else:
                print('Currently the PlaneIntersect is limited to a maximum of 3 cameras.')
                print('Please either continue with the post-processing by matching and tracking') 
                print('fiber centroids with either 2 or 3 cameras, or use the MinProjection method')
        
        
        # The projection method, based on Verhille's 
        # work (10.1103/PhysRevLett.121.124502)
        # ==========================================
        if method=='MinProjection':
            from myptv.fibers.fiber_orientation_mod import fiber_ori_projection_method
            from myptv.fibers.fiber_orientation_mod import fiber_traj_orientation
            from myptv.imaging_mod import camera_wrapper
            
            cams = [camera_wrapper(cn, '.') for cn in cam_names]
            for c in cams:
                c.load()

            fto = fiber_traj_orientation(trajectory_file, blob_fn, cams)
            fto.get_ori_lst()
            fto.save_orientations(save_name)
    
    
    
    
    
    def do_plot_trajectories(self):
        '''
        This function is used to generate a 3D plot of the trajectories in 
        a given file.
        '''
        from myptv.makePlots.plot_trajectories import plot_trajectories
        
        # fetching the parameters
        file_name = self.get_param('plot_trajectories', 'file_name')
        min_length = self.get_param('plot_trajectories', 'min_length')
        write_trajID = self.get_param('plot_trajectories', 'write_trajID')
        t0 = self.get_param('plot_trajectories', 't0')
        te = self.get_param('plot_trajectories', 'te')
        
        plot_trajectories(file_name, 
                          min_length, 
                          write_trajID=write_trajID, 
                          t0=t0, 
                          te=te)
    
    
    
    def do_animate_trajectories(self):
        '''
        This function is used to generate a 3D animation of the trajectories
        in a given file.
        '''
        from myptv.makePlots.plot_trajectories import animate_trajectories
        
        # fetching the parameters
        fname = self.get_param('animate_trajectories', 'file_name')
        min_length = self.get_param('animate_trajectories', 'min_length')
        f0 = self.get_param('animate_trajectories', 'f_start')
        fe = self.get_param('animate_trajectories', 'f_end')
        fps = self.get_param('animate_trajectories', 'fps')
        tail_length = self.get_param('animate_trajectories', 'tail_length')
        elevation = self.get_param('animate_trajectories', 'elevation')
        azimoth = self.get_param('animate_trajectories', 'azimoth')
        rotation_rate= self.get_param('animate_trajectories', 'rotation_rate')
                 
        
        at = animate_trajectories(fname, min_length, fps=fps, 
                                  tail_length=tail_length, 
                                  f0=f0, fe=fe,
                                  view_angles = (elevation, azimoth), 
                                  rotation_rate = rotation_rate)
        at.animate()
        
        print('')
        print('animation saved. Done!')
    
    
    
    
        
    def do_run_extention(self):
        '''
        This is an option to load extrenal extentions to MyPTV. Get it done
        by setting the propper parameters in the params_file.
        '''
        
        # fetchhing the stitching parameters
        path_to_extention = self.get_param('run_extention', 'path_to_extention')
        action_name = self.get_param('run_extention', 'action_name')
        extention_params_file = self.get_param('run_extention', 'extention_params_file')
        
        # 1) import the script  "path_to_extention"
        
        # 2) load the extensions' parameter from extention_params_file
        
        # 3) run the class given as action_name, with the parameter given
        
        

        return None
        
    
    
    def do_create_blob_mask(self):
        '''
        This is used to create a polygon mask around a blob file.
        '''
        p = self.get_action_params('create_blob_mask')
        from myptv.masking_mod import generate_blob_polygon_mask
        
        # Check for optional parameters
        max_sides = p.get('max_sides', None)
        alpha = p.get('alpha', None)
        
        try:
            generate_blob_polygon_mask(
                p['blob_file'],
                p['reference_image'],
                p['padding'],
                p['output_bit_depth'],
                p['save_name'],
                max_sides=max_sides,
                alpha=alpha
            )
        except Exception as e:
            print(f"\nError creating blob mask: {e}")
            return
            
    
    
    
    # ========================================================================
    # /\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    #  Legacy functions that are no longer needed due to the cal_gui
    # /\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    # ========================================================================
    
    def match_target_file(self):
        '''
        This function is used to match calibration points to a target file.
        '''
        from myptv.imaging_mod import camera
        from myptv.utils import match_calibration_blobs_and_points
        from matplotlib.pyplot import show
        
        # fetch parameters from the file
        cam_name = self.get_param('calibration', 'camera_name')
        points_file = self.get_param('calibration', 'calibration_points_file')
        target_file = self.get_param('calibration', 'target_file')
        segmented_file = self.get_param('calibration', 'segmented_points_file')
        res = self.get_param('calibration', 'resolution').split(',')
        res = (float(res[0]), float(res[1]))
        
        print('Matching target file and segmental calibration points')
        print('for camera: %s'%cam_name)
        # initiate the camera
        cam = camera(cam_name, res)
        cam.load('.')
        
        # match the points
        mtf = match_calibration_blobs_and_points(cam,
                                                 segmented_file,
                                                 target_file)
        mtf.pair_points()
    
        # plot the pairs
        mtf.plot_projections()
        show()
        
        print('Please confirm that the points were pairs correctly')
        print("in the figure, by making sure that the blue points")
        print("and the red x's are close to each other." ,'\n')
        
        print("To confirm and save the calibration point file, enter '1'")
        print("If there are errors, enter '2' and improve the initial calibration.")
        user = input()
        
        if user == '1':
            mtf.save_results(points_file)
            print('\n', 'file saved', '\n')
        
        elif user == '2':
            print('\n', 'file not saved', '\n')
        
        else:
            print('\n','unrecognized command. Leaving the workflow.', '\n')
            
        print('Done.')
        
        
    
    
    
    def calibration_sequence(self):
        '''
        Starts a sequence to guide users through the calibration process.
        '''
        from myptv.imaging_mod import camera
        from myptv.calibrate_mod import calibrate
        from os import listdir
        from os.path import isfile
        #from matplotlib.pyplot import subplots, show, imread
        
        # fetch parameters from the file
        cam_name = self.get_param('calibration', 'camera_name')
        blob_file = self.get_param('calibration', 'calibration_points_file')
        cal_image = self.get_param('calibration', 'calibration_image')
        res = self.get_param('calibration', 'resolution').split(',')
        res = (float(res[0]), float(res[1]))
        
        
        # checking that a camera file in the working directory
        ls = listdir('.')                
        
        # if the file is found, start calibration sequence
        if cam_name in ls:
            print('Starting calibration sequence.')
            
            try:
                cam = camera(cam_name, res, cal_points_fname = blob_file)
            except:
                print('\n','Calibration point file (%s) not found!'%blob_file)
                print('\n','Would you like to start the calibration point gui?')
                user = input('1=yes,  else=no : ')
                if user == '1':
                    self.calibration_point_gui()  
                else:
                    print('quitting...')
                return 
            
            cam.load('.')
            print('camera data loaded successfully.')
            cal = calibrate(cam, cam.lab_points, cam.image_points)
            print('initial error: %.3f pixels\n'%(cal.mean_squared_err()))
            
            
            print('starting calibratino GIU\n')
            from myptv.gui_final_cal import cal_gui
            gui = cal_gui(cal, cal_image)
                    
            
        # if not, generate an empty file camera file
        else:
            print('')
            print('camera files not detected in the working directory.')
            print('Generating a new empty file and leaving calib. sequence.')
            print('To continue calibration, fill in an initial guess in the')
            print('empty file, and then run again the calibration sequence.')
            cam = camera(cam_name, res)
            cam.save('.')
            print('\n', 'Done.')
    
    
    
    
    def calibration_point_gui(self):
        '''
        This will start the calibration segmentation point gui.
        '''
        from myptv.cal_point_gui import cal_point_gui
        
        # fetch parameters from the file
        blob_file = self.get_param('calibration', 'calibration_points_file')
        cal_image = self.get_param('calibration', 'calibration_image')
        res = self.get_param('calibration', 'resolution').split(',')
        res = (float(res[0]), float(res[1]))
        
        print('\n', 'Starting calibration point segmentation GUI', '\n')
        gui = cal_point_gui(cal_image, blob_file)
        
        
    # ========================================================================
    # /\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    #                         End of legacy functions
    # /\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    # ========================================================================
    def do_batch_segmentation(self):
        '''
        Runs MyPTV segmentation for every (Recording, Camera) pair under recordings_dir
        and logs the final summary and statistics to a CSV file.
        '''
        import sys
        import os
        import copy
        import subprocess
        import re
        import csv
        from datetime import datetime
        from yaml import safe_dump, safe_load

        # 1. Fetch batch_segmentation parameters from the params file
        recordings_dir = self.get_param('batch_segmentation', 'recordings_dir')
        ptv_results_dir = self.get_param('batch_segmentation', 'ptv_results_dir')
        results_csv_path = self.get_param('batch_segmentation', 'results_csv')
        sub_dir = self.get_param('batch_segmentation', 'sub_dir')
        
        # Check dry run
        cli_dry_run = '--dry-run' in sys.argv or '-d' in sys.argv
        try: file_dry_run = self.get_param('batch_segmentation', 'dry_run')
        except: file_dry_run = False
        dry_run = cli_dry_run or file_dry_run

        try: run_if_exists = self.get_param('batch_segmentation', 'run_if_exists')
        except: run_if_exists = True
            
        try: save_blobs = self.get_param('batch_segmentation', 'save_blobs')
        except: save_blobs = True

        try: cams = self.get_param('batch_segmentation', 'cams')
        except: cams = None
        if isinstance(cams, str):
            cams = [c.strip() for c in cams.split(',')]

        try: masks_dir = self.get_param('batch_segmentation', 'masks_dir')
        except: masks_dir = None

        try: bg_dir = self.get_param('batch_segmentation', 'bg_dir')
        except: bg_dir = None

        try: global_blur_sigma = self.get_param('batch_segmentation', 'blur_sigma')
        except: global_blur_sigma = None

        try: global_min_mass = self.get_param('batch_segmentation', 'min_mass')
        except: global_min_mass = None

        try: camera_thresholds = self.get_param('batch_segmentation', 'camera_thresholds')
        except: camera_thresholds = None

        try: camera_blur_sigmas = self.get_param('batch_segmentation', 'camera_blur_sigmas')
        except: camera_blur_sigmas = None

        try: camera_min_masses = self.get_param('batch_segmentation', 'camera_min_masses')
        except: camera_min_masses = None

        if not os.path.exists(recordings_dir):
            print(f"ERROR: recordings_dir does not exist: {recordings_dir}")
            return

        planned = []
        for rec in sorted(os.listdir(recordings_dir)):
            rec_path = os.path.join(recordings_dir, rec)
            if not (os.path.isdir(rec_path) and rec.lower().startswith("rec")):
                continue
            for cam in sorted(os.listdir(rec_path)):
                cam_img_dir = os.path.join(rec_path, cam)
                if not (os.path.isdir(cam_img_dir) and cam.lower().startswith("cam")):
                    continue
                if cams and cam not in cams:
                    continue
                planned.append((rec, cam, cam_img_dir))

        if not planned:
            print("No (Rec, Cam) pairs found.")
            return

        workflow_path = os.path.abspath(__file__)

        if dry_run:
            print(f"--- DRY RUN: Planned (Rec, Cam) pairs to process ---")
            print(f"Recordings Dir: {recordings_dir}")
            print(f"Results CSV Destination: {results_csv_path}")
            print(f"Save Blobs: {save_blobs} | Run If Exists: {run_if_exists}")
            if masks_dir: print(f"Masks Dir: {masks_dir}")
            if bg_dir: print(f"BG Dir: {bg_dir}")
            
            for rec, cam, cam_img_dir in planned:
                out_dir = os.path.join(ptv_results_dir, f"{rec}_data", sub_dir)
                target_name = f"blobs_{cam}"
                existing_path = None
                if os.path.exists(out_dir):
                    for f in os.listdir(out_dir):
                        if f.lower() == target_name.lower():
                            existing_path = os.path.join(out_dir, f)
                            break
                
                status_str = "Will process"
                if existing_path:
                    status_str = "Will SKIP (exists)" if not run_if_exists else "Will SAVE TO TMP (exists)"
                elif not save_blobs:
                    status_str = "Will run but NOT SAVE blobs"

                bg_info = "None"
                if bg_dir:
                    rec_bg_subfolder = None
                    if os.path.exists(bg_dir):
                        for d in os.listdir(bg_dir):
                            if d.lower() == rec.lower() and os.path.isdir(os.path.join(bg_dir, d)):
                                rec_bg_subfolder = os.path.join(bg_dir, d)
                                break
                    bg_file = None
                    if rec_bg_subfolder:
                        for f in os.listdir(rec_bg_subfolder):
                            if f.lower().startswith("bg") and cam.lower() in f.lower() and f.lower().endswith(".tif"):
                                bg_file = os.path.join(rec_bg_subfolder, f)
                                break
                    if bg_file:
                        bg_info = f"Recording-specific: {bg_file}"
                    else:
                        if os.path.exists(bg_dir):
                            for f in os.listdir(bg_dir):
                                if f.lower().startswith("bg") and cam.lower() in f.lower() and f.lower().endswith(".tif") and os.path.isfile(os.path.join(bg_dir, f)):
                                    bg_file = os.path.join(bg_dir, f)
                                    break
                        if bg_file:
                            bg_info = f"Global fallback: {bg_file}"
                        else:
                            bg_info = "None found (Warning)"

                mask_info = "None"
                if masks_dir:
                    mask_filename = f"mask_{cam}.tif"
                    mask_path = None
                    if os.path.exists(masks_dir):
                        for f in os.listdir(masks_dir):
                            if f.lower() == mask_filename.lower():
                                mask_path = os.path.join(masks_dir, f)
                                break
                    mask_info = mask_path if mask_path else f"MISSING ({mask_filename})"

                thr = camera_thresholds.get(cam, "Default") if camera_thresholds else "Default"
                bs = camera_blur_sigmas.get(cam, global_blur_sigma if global_blur_sigma is not None else "Default") if camera_blur_sigmas else (global_blur_sigma if global_blur_sigma is not None else "Default")
                mm = camera_min_masses.get(cam, global_min_mass if global_min_mass is not None else "Default") if camera_min_masses else (global_min_mass if global_min_mass is not None else "Default")

                print(f" - Rec={rec} | Cam={cam} | threshold={thr} | blur_sigma={bs} | min_mass={mm} | Mask={mask_info} | BG={bg_info} | Status={status_str}")
            print(f"--- Dry run complete. No files written. ---")
            return

        # Actual run
        os.makedirs(os.path.dirname(os.path.abspath(results_csv_path)) or ".", exist_ok=True)

        with open(results_csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Recording", "Camera", "Threshold", "BlurSigma", "MinMass", "BlobCount"])
            csvfile.flush()

            for rec, cam, cam_img_dir in planned:
                out_dir = os.path.join(ptv_results_dir, f"{rec}_data", sub_dir)
                os.makedirs(out_dir, exist_ok=True)
                target_name = f"blobs_{cam}"
                save_name = os.path.join(out_dir, target_name)

                existing_path = None
                if os.path.exists(out_dir):
                    for f in os.listdir(out_dir):
                        if f.lower() == target_name.lower():
                            existing_path = os.path.join(out_dir, f)
                            break

                is_backup = False
                if existing_path:
                    if not run_if_exists:
                        print(f"SKIP: {existing_path} already exists and run_if_exists=False.")
                        continue
                    
                    tmp_dir = os.path.join(out_dir, "tmp")
                    os.makedirs(tmp_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_name = os.path.join(tmp_dir, f"blobs_{cam}_{timestamp}")
                    print(f"INFO: {existing_path} already exists. Saving to tmp: {save_name}")
                    is_backup = True

                actual_save_name = save_name
                delete_after = False
                if not save_blobs:
                    delete_after = True
                    if not is_backup:
                        actual_save_name = os.path.join(out_dir, f"temp_blobs_{cam}_{datetime.now().strftime('%H%M%S')}")
                    print(f"INFO: save_blobs=False. {actual_save_name} will be deleted after counting.")

                with open(self.param_file_path, "r", encoding="utf-8") as f:
                    base_params = safe_load(f)

                seg_block = None
                for d in base_params:
                    if "segmentation" in d:
                        seg_block = d["segmentation"]
                        break
                if seg_block is None:
                    seg_block = {}
                    base_params.append({"segmentation": seg_block})

                seg_block["images_folder"] = cam_img_dir.replace("\\", "/")
                seg_block["save_name"] = actual_save_name.replace("\\", "/")

                if masks_dir:
                    mask_filename = f"mask_{cam}.tif"
                    mask_path = None
                    if os.path.exists(masks_dir):
                        for f in os.listdir(masks_dir):
                            if f.lower() == mask_filename.lower():
                                mask_path = os.path.join(masks_dir, f)
                                break
                    if mask_path:
                        seg_block["mask"] = os.path.abspath(mask_path).replace("\\", "/")
                    else:
                        print(f"ERROR: Mask file not found for {cam} in {masks_dir} (expected {mask_filename})")
                        sys.exit(1)

                if camera_thresholds and cam in camera_thresholds:
                    seg_block["threshold"] = camera_thresholds[cam]

                if camera_blur_sigmas and cam in camera_blur_sigmas:
                    seg_block["blur_sigma"] = camera_blur_sigmas[cam]
                elif global_blur_sigma is not None:
                    seg_block["blur_sigma"] = global_blur_sigma

                if camera_min_masses and cam in camera_min_masses:
                    seg_block["min_mass"] = camera_min_masses[cam]
                elif global_min_mass is not None:
                    seg_block["min_mass"] = global_min_mass

                if bg_dir:
                    bg_file_rec = None
                    rec_bg_subfolder = None
                    if os.path.exists(bg_dir):
                        for d in os.listdir(bg_dir):
                            if d.lower() == rec.lower() and os.path.isdir(os.path.join(bg_dir, d)):
                                rec_bg_subfolder = os.path.join(bg_dir, d)
                                break
                    if rec_bg_subfolder:
                        for f in os.listdir(rec_bg_subfolder):
                            f_lower = f.lower()
                            if f_lower.startswith("bg") and cam.lower() in f_lower and f_lower.endswith(".tif"):
                                bg_file_rec = os.path.join(rec_bg_subfolder, f)
                                break
                    if bg_file_rec:
                        seg_block["remove_background"] = os.path.abspath(bg_file_rec).replace("\\", "/")
                        print(f"Applying recording-specific background: {seg_block['remove_background']}")
                    else:
                        bg_file_global = None
                        if os.path.exists(bg_dir):
                            for f in os.listdir(bg_dir):
                                f_lower = f.lower()
                                if f_lower.startswith("bg") and cam.lower() in f_lower and f_lower.endswith(".tif") and os.path.isfile(os.path.join(bg_dir, f)):
                                    bg_file_global = os.path.join(bg_dir, f)
                                    break
                        if bg_file_global:
                            seg_block["remove_background"] = os.path.abspath(bg_file_global).replace("\\", "/")
                            print(f"Applying global fallback background: {seg_block['remove_background']}")
                        else:
                            print(f"Warning: No background found for {cam} in {bg_dir}")
                            if "remove_background" in seg_block:
                                del seg_block["remove_background"]
                else:
                    if "remove_background" in seg_block:
                        del seg_block["remove_background"]

                threshold_used = seg_block.get("threshold", "N/A")
                blur_sigma_used = seg_block.get("blur_sigma", "N/A")
                min_mass_used = seg_block.get("min_mass", "N/A")

                params_dir = os.path.dirname(os.path.abspath(self.param_file_path))
                temp_params_file = os.path.join(params_dir, f"temp_params_batch_{cam}.yml")
                with open(temp_params_file, "w", encoding="utf-8") as tf:
                    safe_dump(base_params, tf, sort_keys=False)

                print(f"Running segmentation | Rec={rec} | Cam={cam} | threshold={threshold_used} | blur_sigma={blur_sigma_used} | min_mass={min_mass_used}")

                cmd = [sys.executable, workflow_path, os.path.abspath(temp_params_file), "segmentation"]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=params_dir)

                if result.returncode != 0:
                    print(f"ERROR: Workflow failed for {temp_params_file}")
                    print(result.stderr.strip())
                    count = 0
                else:
                    m = re.search(r"blobs found:\s*(\d+)", result.stdout)
                    count = int(m.group(1)) if m else 0

                writer.writerow([rec, cam, threshold_used, blur_sigma_used, min_mass_used, count])
                csvfile.flush()
                print(f"Done | Rec={rec} | Cam={cam} | blobs: {count}")

                if os.path.exists(temp_params_file):
                    os.remove(temp_params_file)
                if delete_after and os.path.exists(actual_save_name):
                    os.remove(actual_save_name)

        print(f"Batch segmentation completed. Results -> {results_csv_path}")


#%%
        
        
        


if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser(description='Run MyPTV workflow.')
    parser.add_argument('fname', help='Parameters file name')
    parser.add_argument('action', help='Action to perform')
    parser.add_argument('--comment', default='', help='Comment for the log entry')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Run in dry-run mode for batch action')
    args = parser.parse_args()

    print('\n','given inputs -')
    print('params file name:', args.fname)
    print('action:', args.action, '\n')
    wf = workflow(args.fname, args.action, comment=args.comment)
    
    
    
    
    

