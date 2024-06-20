from celery import shared_task
import os
import logging

logger = logging.getLogger(__name__)

@shared_task(name='delete_student_detail_csv')
def delete_student_detail_csv(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
        else:
            logger.warning(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
