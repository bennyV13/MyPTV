import numpy as np

class PointManager:
    """
    Handles parsing, grouping, and subset selection of calibration points.
    """
    def __init__(self, data):
        """
        data: numpy array of shape (N, 5) with columns:
              x_cam, y_cam, X_lab, Y_lab, Z_lab
        """
        self.data = data
        self.groups = self._group_by_xz()

    def _group_by_xz(self):
        """
        Groups points by unique (X_lab, Z_lab) pairs (columns).
        """
        groups = {}
        for row in self.data:
            # key is (X_lab, Z_lab)
            key = (float(row[2]), float(row[4]))
            if key not in groups:
                groups[key] = []
            groups[key].append(row)
        
        # Convert lists to numpy arrays
        for key in groups:
            groups[key] = np.array(groups[key])
        return groups

    def get_groups(self):
        """
        Returns the dictionary of grouped points.
        """
        return self.groups
