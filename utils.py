import numpy as np

def divide_patches(image, patch_size=(512, 512), return_coords=False):
    h, w = image.shape[:2]
    patches = []
    coords = []
    for y in range(0, h, patch_size[1]):
        for x in range(0, w, patch_size[0]):
            patch = image[y:y + patch_size[1], x:x + patch_size[0]]
            if patch.shape[0] >= 64 and patch.shape[1] >= 64:
                patches.append(patch)
                coords.append((x, y))
    if return_coords:
        return patches, coords
    return patches


def estimate_yield(wheat_heads, avg_grain_weight_g=1.4, area_m2=1):
    return (avg_grain_weight_g * wheat_heads * 15) / area_m2  # kg/ha
