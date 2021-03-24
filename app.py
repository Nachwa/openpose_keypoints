import json, os
from flask import Flask, flash, request, redirect, url_for, render_template

from werkzeug.middleware.shared_data import SharedDataMiddleware

from utils import *

UPLOAD_FOLDER = './uploads'

app = Flask(__name__, template_folder='.')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'sds'

app.add_url_rule('/uploads/<filename>', 'uploads')
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
                    '/uploads':  app.config['UPLOAD_FOLDER']
                })

JSON_file, IMG_file = "", ""
IMG_SIZE = 0, 0
keypoints_dict = {}
keypoint_names, colors_names = [], []

def upload_file(file):
    secure_fname = secure_filename(file.filename)
    filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_fname)
    file.save(filename)
    return filename
    
@app.route('/', methods=['GET', 'POST'])
def load_data():
    global IMG_file, JSON_file, IMG_SIZE, keypoints_dict, keypoint_names, colors_names
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            if file.filename.rsplit('.', 1)[1].lower() == 'json':
                filename = upload_file(file)
                keypoints_dict, (keypoint_names, colors_names) = read_json(filename)
                JSON_file = filename
            else:
                filename = upload_file(file)
                IMG_SIZE = get_metadate(filename)
                IMG_file = filename
       
    return render_template('index.html',
                keyp_src=JSON_file,
                img_src=IMG_file,
                img_size=IMG_SIZE, 
                kpnts = keypoints_dict, 
                keyprop = (keypoint_names, colors_names))


@app.route("/add_person", methods=['POST'])
def add_new_person():
    global keypoints_dict, keypoint_names, colors_names
    keypoints_dict, (keypoint_names, colors_names) = add_person(keypoints_dict, keypoint_names, colors_names)
    return redirect(url_for('load_data'))

@app.route("/update_data", methods=["POST"])
def update_keypoints():
    global keypoints_dict
    keypoint_id = request.values.get('keypoint_id')
    x = float(request.values.get('x'))
    y = float(request.values.get('y'))
    conf = float(request.values.get('conf'))

    keypoints_dict[keypoint_id] = [x, y, conf]
    return {}


@app.route("/save_json", methods=["POST"])
def save_json():
    global keypoints_dict
    keypoints_json = load_json(JSON_file)
    for key_id in keypoints_dict:
        p, cat, k = key_id.split('_')
        p, cat, k = int(p), int(cat), int(k)
        if p >= len(keypoints_json['people']):
            keypoints_json['people'].append(get_new_person_dict())
        keypoints_json['people'][p]['person_id'] = [p]
        keypoints_json['people'][p][keypoint_categories[cat]][k*3:k*3+3] = keypoints_dict[key_id]

    fname = JSON_file.split('/')[-1].split('.json')[0]
    with open(f'./corrected_json/{fname}_corrected.json', 'w') as keypoints_file:
        json.dump(keypoints_json, keypoints_file)
    return {}


if __name__ == '__main__':
    app.run()
