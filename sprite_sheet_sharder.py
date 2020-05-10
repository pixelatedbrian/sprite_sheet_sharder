from PIL import Image

import numpy as np
import pandas as pd

def get_inputs():
    '''
    Gets inputs from users to figure out:
    * what file to load
    * remove green lines
    * sprite size (default 16px)
    * remove signature for files from: https://www.spriters-resource.com/fullview/119176/
    * output file name
    * integration validation test
    '''
    
    rules = {}
    
    go = True
    count = 0
    
    while go is True and count < 100:
    
        # get a file name
        result = input("path to file, ex map.png: ")
        
        if ".png" in result or ".jpg" in result:
            go = False
            rules["file"] = result
            
        else:
            print("    There was some kind of error in the input, did you specify a '.png' or '.jpg' file?")
            
    go = True
    count = 0
    
    while go is True and count < 100:
        
        # remove green lines?
        _input = input("remove green screen lines? (usually screen indicators): y/n/?   ")
        
        if _input == "?":
            print("some maps have line padding to indicate screens.\n For example: https://www.spriters-resource.com/fullview/119176/\n")
            
        elif _input.lower() == "y":
            rules["green_lines"] = True
            go = False
            
            print("    ok, will attempt to remove green lines")
            
        elif _input.lower() == "n":
            rules["green_lines"] = False
            go = False
            
            print("   ok, skipping removing green lines")
            
    go = True
    count = 0
    
    while go is True and count < 100:
        
        # what's the sprite size?
        _input = input("what is the pixel size of the sprites? Typically 16px:  ex: 16   ")
        
        # converted to int?
        converted = False
        
        try:
            fixed_input = int(_input)
            converted = True
            
            go = False
            rules["sprite_size"] = fixed_input
            print("    ok, sprite size is {:}px squared".format(fixed_input))
            
            
        except:
            print("Integer conversion failed on input: ", repr(_input))
            converted = False
            
            
    go = True
    count = 0
    
    while go is True and count < 100:
        
        # remove signature from lower right?
        _input = input("remove signature from the image? y/n/?    ")
        
        if _input == "?":
            print("some maps have a signature in the lower right and this will try to remove that.\nFor example: https://www.spriters-resource.com/fullview/119176/\n")
            
        elif _input.lower() == "y":
            rules["remove_signature"] = True
            go = False
            
            print("    ok, trying to remove the signature")
            
        elif _input.lower() == "n":
            rules["remove_signature"] = False
            go = False
            
            print("    ok, not removing the signature")
            
    go = True
    count = 0
    
    while go is True and count < 100:
        
        _input = input("there will be an output .png and .csv file. Enter name for the output files: ex: 'overworld'  ")
        
        go = False
        
        print("    ok, will try to write '{:}.png' and '{:}.csv'".format(_input, _input))
        
        rules["output_path"] = _input
        
    go = True
    count = 0
    
    while go is True and count < 100:
        
        _input = input("Validate that we can reconstruct the image from the output files? y/n:   ")
        
        if _input.lower() == "y":
            rules["validation_test"] = True
            go = False
            
            print("    ok, will perform a validation test at the end")
            
        elif _input.lower() == "n":
            rules["validation_test"] = False
            go = False
            
            print("    ok, skipping validation test")      
        
    
    return rules


def img_in_inventory(img, inventory):
    '''
    img = numpy array that is 16x16x3
    inventory: dictionary of unique img items where the key is a unique number that represents the sprite
    
    ex: 0: tree_sprite, 1: ground_sprite, 2: water_sprite, etc
    '''
    
    if len(inventory.keys()) > 0:
        max_key = np.max([int(key) for key in inventory.keys()])
        
    else:
        # save space by incrementing max_key when a new one is created
        # since we want to start at zero initialize at -1
        max_key = -1 
    
    for item in inventory.items():
        
        diff = np.sum(item[1] - img)
#         print("diff", diff)
        
        if diff == 0: # images match, use this key
            
#             print("matches item: {:}".format(item[0]))
            
            return (int(item[0]), inventory)
        
    # if we got this far then the item isn't in the inventory, so create a new item in the inventory and return new key
    new_key = max_key + 1
    inventory[new_key] = img
        
#     print("went through all items and no match, add this to the dictionary")
#     print("    there are now {:} unique sprites in the dictionary\n".format(new_key + 1))
    return (new_key, inventory)


def parse_sprites():
    '''
    * what file to load
    * remove green lines
    * sprite size (default 16px)
    * remove signature for files from: https://www.spriters-resource.com/fullview/119176/
    * output file name
    * integration validation test
    '''
    
    print("parse_sprites: get the inputs for how this script should run")
    
    rules = get_inputs()
    
    OUT_CSV = "{:}.csv".format(rules["output_path"])
    OUT_PIC = "{:}.png".format(rules["output_path"])
    
    print("parse_sprites: inputs gathered")
    print("parse_sprites: Loading image: {:}".format(rules["file"]))
        
    img = np.array(Image.open(rules["file"]))
    
    print("parse_sprites: Loaded image.")
    
    if rules["green_lines"] is True:
        
        print("parse_sprites: starting to process green lines")
        
        img = img[1:, 1:, :]
        
        # figure out how many screens there are wide and down
        horizontal_frames = img.shape[1] // 257
        vertical_frames = img.shape[0] // 177
        
        # create a placeholder for the clean image
        clean_img = np.zeros(shape=(vertical_frames * 176, horizontal_frames * 256, 3), dtype=np.uint8)
        
        print("parse_sprites: created a placeholder image in memory of size: ", clean_img.shape)
        
        for idx in range(horizontal_frames):  # walk through the screens left to the right
            for idy in range(vertical_frames):  # walk through the screens top to bottom
                col_start = idx * 256 + idx
                col_end = col_start + 256

                row_start = idy * 176 + idy
                row_end = row_start + 176

                snip = img[row_start:row_end, col_start:col_end, :3]

                clean_col_start = idx * 256
                clean_col_end = (idx + 1) * 256

                clean_row_start = idy * 176
                clean_row_end = (idy + 1) * 176

                clean_img[clean_row_start:clean_row_end, clean_col_start:clean_col_end, :] = snip
                
        img = clean_img
        
        print("parse_sprites: finished trying to remove the green lines")
                
    print("parse_sprites: working image shape: ", img.shape)    
        
    if rules["remove_signature"] is True:
        print("parse_sprites: attempting to remove the signature")
        
        img[1500:, 3500:, 0] = 0
        img[1500:, 3500:, 1] = 128
        img[1500:, 3500:, 2] = 0
        
        print("parse_sprites: attempt to remove signature complete")
        
    else:
        print("parse_sprites: skipping trying to remove the signature")
    
    # prepare to start walking the image using the sprite pixel size
    START_COL = 0
    START_ROW = 0

    SPRITE_SIZE = rules["sprite_size"]
    
    COL_STEPS = clean_img.shape[1] // SPRITE_SIZE
    ROW_STEPS = clean_img.shape[0] // SPRITE_SIZE

    END_COL = START_COL + COL_STEPS
    END_ROW = START_ROW + ROW_STEPS

    temp_img = img[START_ROW * SPRITE_SIZE:END_ROW * SPRITE_SIZE,
                   START_COL * SPRITE_SIZE:END_COL * SPRITE_SIZE, :]

    sprite_dict = {} # mapping of numbers and images
    
    results = np.zeros((ROW_STEPS, COL_STEPS), np.uint8)
    
    for id_c in range(COL_STEPS):
        for id_r in range(ROW_STEPS):
    #         print("starting x: {:} y: {:}".format(id_c, id_r))
            r_s = id_r * SPRITE_SIZE
            r_e = (id_r + 1) * SPRITE_SIZE

            c_s = id_c * SPRITE_SIZE
            c_e = (id_c + 1) * SPRITE_SIZE

            _img = temp_img[r_s:r_e, c_s:c_e, :]

            result, sprite_dict = img_in_inventory(_img, sprite_dict)

            results[id_r, id_c] = result

    #         print("\n\n")


    num_sprites = len(sprite_dict.keys())

    print("Found {:} sprites to work with.".format(num_sprites))
    
    print("example results:")
    
    print(results[5:10, 5:10])
    
    temp_results = pd.DataFrame(results)
    
    print("attempting to save {:}".format(OUT_CSV))
    
    temp_results.to_csv(OUT_CSV, header=None, index=None)
    
    # try to make the spritesheet
    num_sprites = len(sprite_dict.keys())

    sprite_img = np.zeros((SPRITE_SIZE, SPRITE_SIZE * num_sprites, 3), dtype=np.uint8)

    for key in sprite_dict.keys():
        start = int(key) * SPRITE_SIZE
        end = (int(key) + 1) * SPRITE_SIZE

        sprite_img[:, start:end, :] = sprite_dict[key]

    sprite_img = Image.fromarray(sprite_img)

    print("attempting to save {:}".format(OUT_PIC))
    
    sprite_img.save(OUT_PIC)
    
    print("tried to save the new spritesheet {:}".format(OUT_PIC))
    
    if rules["validation_test"] is True:
        
        print("try to load the new sprite sheet")
        load_sprite_img = np.array(Image.open(OUT_PIC))
        
        num_sprites = load_sprite_img.shape[1] // SPRITE_SIZE
        
        print("detected {:} sprites in the sprite sheet.".format(num_sprites))
        
        # store the mapping of keys and images
        sprite_map = {}

        for idx in range(num_sprites):
            sprite = load_sprite_img[:, idx * SPRITE_SIZE: (idx + 1) * SPRITE_SIZE, :]
            
            sprite_map[idx] = sprite
            
        print("loaded the sprite sheet into the dictionary.")
        
        print("now load the array of sprite numbers from the CSV")
        
        # originally a dataframe
        sprite_data = pd.read_csv(OUT_CSV, header=None)
        
        # convert to a numpy array
        sprite_data = np.array(sprite_data.values)
        
        print("loaded the csv and got an array with the shape: ", sprite_data.shape)
        print("examples from the array:")
        print(sprite_data[5:10, 5:10])
        print("\n")
        
        constructed_image = np.zeros(shape=(sprite_data.shape[0] * SPRITE_SIZE,
                                            sprite_data.shape[1] * SPRITE_SIZE,
                                            3), dtype=np.uint8)

        
        for row in range(sprite_data.shape[0]):
            for col in range(sprite_data.shape[1]):
                r_start = row * SPRITE_SIZE
                r_end = r_start + SPRITE_SIZE

                col_start = col * SPRITE_SIZE
                col_end = col_start + SPRITE_SIZE

                sprite_number = sprite_data[row, col]

                constructed_image[r_start:r_end, col_start:col_end, :] += sprite_map[sprite_number]
                
        print("finished trying to reconstruct the original image")
        
        print("now compare the pixel values of the original img (stripped of greenlines if applicable) and the reconstructed image")
        
        diffs = np.array(constructed_image, dtype=float) - np.array(clean_img, dtype=float)
        
        diffs = int(np.sum(diffs))
        
        if diffs == 0:
            
            print("\n\nIt appears that the reconstructed image is exactly the same as the input image.")
            print("Script is Complete.")
            
        else:
            print("The difference between the images was not zero so there was one or more issues with reconstructing the image. The sum of errors was {:}".format(diffs))
        
        
    else:
        print("skipping validation testing. Script complete!")
    
if __name__ == "__main__":
    
  parse_sprites()

