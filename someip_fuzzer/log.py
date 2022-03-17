import logging
import threading

logger = logging.getLogger("someip_fuzzer")
logger.setLevel(logging.DEBUG)

# formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%H:%M:%S")

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger.addHandler(ch)

lock = threading.Lock()

def log_debug(text):
    lock.acquire()
    logger.debug(text)
    lock.release()

def log_info(text):
    lock.acquire()
    logger.info(text)
    lock.release()

def log_warning(text):
    lock.acquire()
    logger.warning(text)
    lock.release()

def log_error(text):
    lock.acquire()
    logger.error(text)
    lock.release()
