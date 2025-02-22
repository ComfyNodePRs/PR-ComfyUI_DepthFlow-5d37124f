from DepthFlow import DepthScene
from attr import Factory, define
from Broken.Externals.Depthmap import DepthAnythingV2, DepthEstimator
import random
import numpy as np
import torch
import os, shutil
from PIL import Image
import folder_paths
   
class DepthFlow:

    def __init__(self):
        self.glob_estimator = None

    def tensor2pil(self, image):
        return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))
    
    # PIL to Tensor
    def pil2tensor(self, image):
        return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)
    
    @classmethod
    def INPUT_TYPES(s):
        
        return {
      "required": {
        "images": ("IMAGE",),
        "fps": ("INT",{"default": 24, "min": 8, "max": 60, "step": 1}), 
        "width": ("INT",  {"default": 512, "min": 20, "max": 9999, "step": 1}), 
        "height": ("INT",  {"default": 512, "min": 20, "max": 9999, "step": 1}), 
        "filename_prefix": ("STRING", {"default": "depthflow"}),
      },    
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("filepath",)

    FUNCTION = "doit"

    CATEGORY = "DepthFlow"


    def doit(self, images, fps, width, height, filename_prefix):
        
        depthflow = DepthScene(backend='headless')
        
        if self.glob_estimator == None:   # trick 1 to avoid vram leak
            self.glob_estimator = depthflow.estimator
        else:
            depthflow.estimator = self.glob_estimator
        
        img = self.tensor2pil(images[0])
        frame = img.convert('RGB')

        random_number = random.randint(0, 1073741824)
        input_dir = folder_paths.get_input_directory()
        tmpfile_path = os.path.join(input_dir, 'depthin{}.png'.format(random_number))
        frame.save(tmpfile_path)
        depthflow.input(image=tmpfile_path)
        
        output_dir = folder_paths.get_output_directory()
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, output_dir, width, height)
        
        file =  f"{filename}_{counter:05}_.mp4"
        save_path = os.path.join(full_output_folder, file)

        depthflow.main(output=save_path, fps=fps, width=width, height=height)
        depthflow.window.destroy()  # trick 2 to avoid vram leak
        shutil.os.remove(tmpfile_path)
        #del depthflow

        return (save_path, )
