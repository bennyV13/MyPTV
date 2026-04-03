'''
Summary: This code implements point-snapping to detected blobs and a 
coordinate suggestion listbox for the MyPTV initial calibration GUI.
'''


def location_handler(self, event):
    '''Handles mouse clicks with automatic snapping to the nearest segmented blob centroid.'''
    
    # Translate click coordinates to canvas coordinates, accounting for zoom (self.z) and scrolling
    x = int(self.canvas.canvasx(event.x)/self.z) + int(self.hbar.get()[1])
    y = int(self.canvas.canvasy(event.y)/self.z) + int(self.vbar.get()[1])
    
    # Snapping logic: find the nearest segmented blob within a threshold
    if len(self.segmented) > 0:
        from numpy.linalg import norm
        from numpy import array
        
        p_click = array([x, y])     # Current click point
        d_min = 30.0                # Snapping radius (threshold) in pixels
        snapped_p = None            # Placeholder for nearest blob coordinates
        
        # Iterate through detected blobs to find the closest one
        for b in self.segmented:
            p_blob = array([b[0], b[1]])
            d = norm(p_click - p_blob)
            if d < d_min:
                d_min = d
                snapped_p = p_blob
        
        # If a blob is found within the threshold, snap the coordinates to its centroid
        if snapped_p is not None:
            x, y = snapped_p
    
    # Update the UI labels with the (potentially snapped) coordinates
    self.Xloc.configure(text = x) 
    self.Yloc.configure(text = y)
    self.xy_marked = (x, y)
    
    # Optional: Update the pixel value display for the clicked location
    try:
        val = self.image.getpixel((int(x), int(y)))
        self.Valloc.configure(text = "%.1f" % val)
    except Exception:
        self.Valloc.configure(text = "-")
    
    # Redraw the selection markers on the canvas
    self.mark_points()


def on_target_select(self, event):
    '''Update lab space input fields when a user selects a coordinate from the suggestion listbox.'''
    selection = self.target_listbox.curselection()
    if selection:
        list_idx = selection[0]
        
        # TRANSFORMATION: Map the listbox selection back to the global target index
        global_idx = self.available_indices[list_idx]
        
        # Retrieve the original 3D coordinates (X, Y, Z) from the targets array
        t = self.targets[global_idx]
        
        # Auto-populate the input fields with the suggested coordinates
        self.x_input.delete(0, 'end')
        self.x_input.insert(0, str(t[0]))
        self.y_input.delete(0, 'end')
        self.y_input.insert(0, str(t[1]))
        self.z_input.delete(0, 'end')
        self.z_input.insert(0, str(t[2]))


def addPoint(self):
    '''Saves the marked point and advances the suggestion listbox.'''
    x_im, y_im = self.xy_marked
    if x_im == -1: return
    
    # Read values from inputs
    x_lab = float(self.x_input.get())
    y_lab = float(self.y_input.get())
    z_lab = float(self.z_input.get())
    
    selection = self.target_listbox.curselection()
    if selection:
        list_idx = selection[0]
        global_idx = self.available_indices[list_idx]
        ix, iy, iz = self.target_indices[global_idx]
    else:
        ix, iy, iz, global_idx = 0, 0, 0, -1
        
    # Append the point and metadata to the list of calibration points
    self.point_list.append([x_im, y_im, x_lab, y_lab, z_lab, ix, iy, iz, global_idx])
    
    # Reset marking state
    self.xy_marked = (-1, -1)
    
    # Advance the listbox: remove used point and highlight the next one
    if selection:
        del self.available_indices[list_idx]
        self.target_listbox.delete(list_idx)
        
        if self.target_listbox.size() > 0:
            next_idx = min(list_idx, self.target_listbox.size() - 1)
            self.target_listbox.selection_set(next_idx)
            self.target_listbox.see(next_idx)
    
    self.mark_points()


def refresh_listbox(self):
    '''
    Refreshes the suggestion listbox to show 3D coordinates instead of grid indices.
    Note: This is where the transformation from internal indices to user-facing 3D labels occurs.
    '''
    self.target_listbox.delete(0, 'end')
    for idx in self.available_indices:
        # Retrieve original 3D coordinates
        t = self.targets[idx]
        
        # Format the label to show (X, Y, Z) instead of [ix, iy]
        label = "(%.1f, %.1f, %.1f)" % (t[0], t[1], t[2])
        self.target_listbox.insert('end', label)

# -----------------------------------------------------------------------------
# TRANSFORMATION NOTE:
# The transformation between "Grid Indices" [ix, iy] and "3D Coordinates" (X, Y, Z)
# happens via the self.targets and self.available_indices structures.
# 
# To show 3D coordinates in the listbox, we map:
# global_idx -> self.targets[global_idx] 
# (instead of mapping to self.target_indices[global_idx])
# -----------------------------------------------------------------------------
