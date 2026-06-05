# -*- coding: utf-8 -*-

import glob

def parse_file_list(param_value):
    '''
    Parses a parameter value that could be a single string, a list of strings, 
    or a comma-separated string, and returns a flat list of file paths.
    Also handles glob patterns.
    '''
    if isinstance(param_value, str):
        if ',' in param_value:
            items = [item.strip() for item in param_value.split(',')]
        else:
            items = [param_value.strip()]
    elif isinstance(param_value, list):
        items = [str(item).strip() for item in param_value]
    else:
        return []
        
    resolved_files = []
    for item in items:
        matches = glob.glob(item)
        if matches:
            resolved_files.extend(sorted(matches))
        else:
            resolved_files.append(item)
            
    return resolved_files
