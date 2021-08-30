import logging
import os

from flask import Flask, render_template, request
import google.cloud.logging
from google.cloud import firestore
from google.cloud import storage

client = google.cloud.logging.Client()
client.get_default_handler()
client.setup_logging()

app = Flask(__name__)


@app.route('/')
def root():
    return render_template('home.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    successful_upload = False
    if request.method == 'POST':
        uploaded_file = request.files.get('picture')

        if uploaded_file:
            gcs = storage.Client()
            bucket = gcs.get_bucket(os.environ.get('BUCKET', 'my-bmd-bucket'))
            blob = bucket.blob(uploaded_file.filename)

            blob.upload_from_string(
                uploaded_file.read(),
                content_type=uploaded_file.content_type
            )

            logging.info(blob.public_url)

            successful_upload = True

    return render_template('upload_photo.html', 
                           successful_upload=successful_upload)


@app.route('/search')
def search():
    query = request.args.get('q')
    results = []

    if query:
        db = firestore.Client()
        doc = db.collection(u'tags').document(query.lower()).get().to_dict()

        try:
            for url in doc['photo_urls']:
                results.append(url)
        except TypeError as e:
            pass

    return render_template('search.html', query=query, results=results)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return render_template('error.html'), 500


if __name__ == '__main__':
    app.run(debug=True,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))

