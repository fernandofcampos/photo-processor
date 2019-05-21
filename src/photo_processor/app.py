#!/usr/bin/env python
import urllib.request
from PIL import Image
import logging
from db import DB
from consumer import Consumer
from config import Config


logger = logging.getLogger(__name__)
consumer = None
db = None


def process_image(ch, method_frame, header_frame, body):
    photo_uuid = body.decode()

    try:
        photo = db.get_photo(photo_uuid)
        # Check if uuid is valid and if photo has `pending` state
        # If not, abort
        if photo is None or photo['status'] != 'pending':
            logger.error('Invalid uuid %s', photo_uuid)
            db.commit()
            return

        # Update db `photos.status` to `processing`
        rows = db.update_photo_status(photo_uuid, 'processing')
        if rows == 0:
            raise Exception('Error updating photo status to processing.')

        # Download photo using `photos.url`
        photo = download(photo['url'])
        if photo is None:
            raise Exception('Error downloading image from url %s',
                            photo['url'])

        # Generate a thumbnail of max 320x320 dimensions,
        # maintaining the aspect ratio. Store thumbnail file on
        # mounted `/waldo-app-thumbs` directory
        thumbnail_file_path = getFilePath(photo['url'])
        _, width, height = create_thumbnail(photo, thumbnail_file_path)

        photo.close()

        # Store a new row on db table `photo_thumbnails`
        # with the thumbnail details. For the `photo_thumbnails.url`
        # just use the relative path to the file.
        rows = db.insert_photo_thumbnail(photo_uuid, width,
                                         height, thumbnail_file_path)
        if rows == 0:
            raise Exception('Error inserting thumbnail details into db.')

        # Update `photos.status` to `completed`.
        rows = db.update_photo_status(photo_uuid, 'completed')
        if rows == 0:
            raise Exception('Error updating photo status to completed.')

        db.commit()

    except Exception:
        logger.exception('Error')
        # Rolls back whatever change on DB
        db.rollback()
        # Update `photos.status` to `failed`.
        db.update_photo_status(photo_uuid, 'failed')
        db.commit()


def create_thumbnail(original_file, thumbnail_file_path):
    with Image.open(original_file) as im:
        size = (320, 320)
        im.thumbnail(size)
        im.save(thumbnail_file_path)
        width, height = im.width, im.height
        im.close()
        return thumbnail_file_path, width, height


def download(url):
    r = urllib.request.urlopen(url)
    return r


def getFilePath(url):
    return '/waldo-app-thumbs/' + getFileName(url)


def getFileName(url):
    if url.find('/'):
        return url.rsplit('/', 1)[1]
    else:
        raise Exception('Invalid file URL %s' + url)


def init_db():
    global db
    uri = Config.PG_CONNECTION_URI
    db = DB(uri)


def init_consumer():
    global consumer
    uri = Config.AMQP_URI
    consumer = Consumer(uri, 'photo-processor', process_image)


def main():
    try:
        init_db()
        init_consumer()
        consumer.start()

    except Exception:
        logger.exception('Error')

    finally:
        consumer.stop()
        consumer.close()
        db.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    main()
