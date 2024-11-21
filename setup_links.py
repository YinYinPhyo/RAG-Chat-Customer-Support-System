#!/usr/bin/env python
# coding: utf-8

import os
import shutil
import sys

def setup_project_links():
    """Setup symbolic links to Step 2 components"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    step2_dir = os.path.join(os.path.dirname(current_dir), 'Step 2')
    
    # Add Step 2 to Python path
    if step2_dir not in sys.path:
        sys.path.append(step2_dir)
    
    # Directories to link
    dirs_to_link = ['config', 'loaders', 'vectorstore', 'utils']
    
    for dir_name in dirs_to_link:
        src = os.path.join(step2_dir, dir_name)
        dst = os.path.join(current_dir, dir_name)
        
        if not os.path.exists(src):
            print(f"Warning: Source directory not found: {src}")
            continue
            
        # Remove existing directory/link if it exists
        if os.path.exists(dst):
            if os.path.islink(dst):
                os.unlink(dst)
            elif os.path.isdir(dst):
                shutil.rmtree(dst)
                
        # Create symbolic link
        os.symlink(src, dst, target_is_directory=True)
        print(f"Created symlink: {dst} -> {src}") 