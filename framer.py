from PIL import Image, ImageOps
import face_recognition
import sys
import os
import numpy as np
from functools import reduce

crop = {
    "top": 0,
    "bottom": 50,
    "left": 15,
    "right":15
}

if len(sys.argv) <= 1:
    print("usage: framer.py <names of frames folder>")
for arg in sys.argv[1:]:
    base_name = arg
    if base_name[-1] == "/":
        base_name = base_name[:-1]
    warnings = []
    errors = []
    num = 0
    while True:
        num += 1
        image_name = base_name+"/"+str(num)+".jpg"
        face_image_name = "/".join(image_name.split("/")[:-1]) + "/auto_" + image_name.split("/")[-1]
        if os.path.exists(face_image_name):
            print(face_image_name+" already exists, skipping it")
            continue

        # Load the jpg file into a numpy array
        try:
            image = face_recognition.load_image_file(image_name)
            print("processing "+image_name)
        except:
            print("done")
            break

        size = (len(image), len(image[0]))
        if size[0] < size[1]:
            image = [[image[i][j] for i in range(crop["left"]*size[0]//100,(100-crop["right"])*size[0]//100)] for j in range(crop["top"]*size[1]//100,(100-crop["bottom"])*size[1]//100)]
        else: 
            image = [[image[i][j] for i in range(crop["top"]*size[1]//100,(100-crop["bottom"])*size[1]//100)] for j in range(crop["left"]*size[0]//100,(100-crop["right"])*size[0]//100)]

        image = np.array(image)
        cropped_size = (len(image), len(image[0]))

        pil_image = Image.fromarray(image.astype(np.uint8))
        cropped_image_name = "/".join(image_name.split("/")[:-1]) + "/auto_cropped_" + image_name.split("/")[-1]
        
        border_size = cropped_size[0]//3
        ImageOps.expand(pil_image,border=border_size,fill='black').save(cropped_image_name)

        # Load the jpg file into a numpy array
        image = face_recognition.load_image_file(cropped_image_name)

        # Find all facial features in all the faces in the image
        face_landmarks_list = face_recognition.face_landmarks(image)

        match_index = 0
        if len(face_landmarks_list) != 1:
            print("{} face(s) found".format(len(face_landmarks_list)))
            if len(face_landmarks_list) == 0:
                print("skip (no face found)")
                errors.append("Error in "+image_name+": No face found")
                continue
            else:
                warnings.append("Warning in "+image_name+": Multiple faces found")
                print("take the first match")

        face_landmarks = face_landmarks_list[0]
        chin = face_landmarks["chin"]
        left_eye = face_landmarks["left_eye"]
        right_eye = face_landmarks["right_eye"]

        if not (len(chin) > 0 and len(left_eye) > 0 and len(right_eye) > 0):
            print("skip (features not found)")
            errors.append("Error in "+image_name+": Missing some key properties")
            continue

        chin = [p[0] for p in chin]
        width = max(chin) - min(chin)
        ll_eye = reduce(lambda p1, p2: p1 if p1[0] < p2[0] else p2, left_eye) 
        rl_eye = reduce(lambda p1, p2: p1 if p1[0] > p2[0] else p2, left_eye) 
        lr_eye = reduce(lambda p1, p2: p1 if p1[0] < p2[0] else p2, right_eye) 
        rr_eye = reduce(lambda p1, p2: p1 if p1[0] > p2[0] else p2, right_eye)

        centerx = (ll_eye[0] + rl_eye[0] + lr_eye[0] + rr_eye[0])//4
        centery = (ll_eye[1] + rl_eye[1] + lr_eye[1] + rr_eye[1])//4
        size = (width, width)
        top = centery - size[1]
        bottom = centery + size[1]
        right = centerx + size[0]
        left = centerx - size[0]
        if top < 0 or left < 0 or bottom >= cropped_size[0] + border_size or right >= cropped_size[1] + border_size:
            print("skip (out of bounds)")
            print ("tblr", top, bottom, left, right)
            print ("size w c",  cropped_size, width, centerx, centery)
            errors.append("Error in "+image_name+": Face goes out of bounds")
            continue

        face_image = image[top:bottom, left:right]
        face_image = Image.fromarray(face_image)
        face_image = face_image.resize((1000,1000))
        face_image.save(face_image_name)

    for w in warnings:
        print(w)
    for e in errors:
        print(e)
    if len(warnings) == 0 and len(errors) == 0:
        print("successfully generated "+str(num-1)+" frames in "+base_name+"/")
