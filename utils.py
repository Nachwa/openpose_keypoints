pose_names = ['nose', 'neck', 'shoulder R', 'elbow R', 'wrist R', 'shoulder L', 'elbow L', 'wrist L', 'pelvis', 'hip R', 'knee R', 'ankle R', 'hip L', 'knee L', 'ankle L', 'eye R', 'eye L', 'ear R', 'ear L', 'big_toe L', 'small_toe L', 'heel L', 'big_toe R', 'small_toe R', 'heel R']

Lhand_names = [f'Lhand_{i}' for i in range(21)]
Rhand_names = [f'Rhand_{i}' for i in range(21)]
face_names = [f'face_{i}' for i in range(70)]
keynames = [pose_names, face_names, Lhand_names, Rhand_names]

keypoint_categories = ['pose_keypoints_2d', 'face_keypoints_2d', 'hand_left_keypoints_2d', 'hand_right_keypoints_2d']
colors = ["#ffbf00", "#ff00af", "#5d8aa8", "#fe6f5e", "#8a2be2", "#006a4e", "#4b3621", "#0047ab", "#00ffff", "#734f96"]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'json'}
json_dict_keys = []

import json, os
from PIL import Image
import numpy as np 
from werkzeug.utils import secure_filename

def load_json(filename):
    with open(filename) as keypoints_file:
        keypoints_json = json.load(keypoints_file)
    
    if len(keypoints_json['people']) > 0:
        global json_dict_keys
        json_dict_keys = list(keypoints_json['people'][0].keys())
    return keypoints_json

def read_json(filename):
    keypoints_json = load_json(filename)    

    keypoints_dict = {}
    keypoint_names = []
    colors_names = []
    for p, person in enumerate(keypoints_json['people']):
        for cat, keypoints in enumerate(keypoint_categories):
            keypoints_arr = np.array(person[keypoints], 
                                    dtype=np.float).reshape(-1, 3)
            for i, (x, y, c) in enumerate(keypoints_arr):
                keypoints_dict[f'{p}_{cat}_{i}'] = [x, y, c] 
                keypoint_names.append(keynames[cat][i])
                colors_names.append(colors[p%len(colors)])
    return keypoints_dict, (keypoint_names, colors_names)

def add_person(keypoints_dict, keypoint_names, colors_names):
    num_keypoints = sum([len(k) for k in keynames])
    p_id = len(keypoints_dict.values())//num_keypoints
    
    for cat, keypoints in enumerate(keypoint_categories):
        keypoints_arr = np.zeros((len(keynames[cat]), 3), dtype=np.float)
        for i, (x, y, c) in enumerate(keypoints_arr):
            keypoints_dict[f'{p_id}_{cat}_{i}'] = [x, y, c] 
            keypoint_names.append(keynames[cat][i])
            colors_names.append(colors[p_id%len(colors)])

    return keypoints_dict, (keypoint_names, colors_names)

def get_new_person_dict():
    global json_dict_keys
    new_person_dict = {'person_id': [-1]}
    new_person_dict.update({k: [0]*(3*len(kn)) for k, kn in zip(keypoint_categories, keynames)})
    for k in json_dict_keys:
        if not k in new_person_dict:
            new_person_dict[k] = []
    return new_person_dict

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_metadate(filename):
    with Image.open(filename) as img:
        w, h = img.size
    return w, h