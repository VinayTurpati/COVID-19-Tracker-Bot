from flask import Flask, request, send_from_directory, send_file
import os
from flask_cors import CORS, cross_origin

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
CORS(app)
app.config["CORS_HEADERS"]= 'Content-Type'


@app.route('/img/<path:path>')
@cross_origin(origin='*',headers=['Access-Control-Allow-Origin','Content-Type'])
def send_img(path):
    print(path)
    print(os.listdir("static/img"))
    #return send_file(f'static/img/{path}',attachment_filename=path, mimetype='image/jpeg') #as_attachment=True)
    return send_from_directory('static/img', path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020)
