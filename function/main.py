import os

from google.cloud import firestore
from google.cloud import vision


def photo_analysis_service(event, context):
    bucket = os.environ.get('BUCKET', 'my-bmd-bucket')
    file_name = event['name']

    objects = _analyze_photo(bucket, file_name)
    _store_results(bucket, file_name, objects)


def _analyze_photo(bucket, file_name):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(source=vision.ImageSource(image_uri=f'gs://{bucket}/{file_name}'))
    objects = client.object_localization(image=image).localized_object_annotations

    return objects


def _store_results(bucket, file_name, objects):
    db = firestore.Client()

    for object_ in objects:

        db.collection(u'tags').document(object_.name.lower()).set(
            {u'photo_urls': firestore.ArrayUnion(
                    [u'https://storage.googleapis.com/{}/{}'.format(bucket, file_name)]
                )
            },
            merge=True)

        print('\n{} (confidence: {})'.format(object_.name, object_.score))

