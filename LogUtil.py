import logging


def create_logger(logger_name=None, level=logging.INFO, mode='a'):
    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    if logger_name is not None:
        log_setup = logging.getLogger(logger_name)
        file_handler = logging.FileHandler("log/"+logger_name+".log", mode=mode)
        file_handler.setFormatter(formatter)
        log_setup.addHandler(file_handler)
    else:
        log_setup = logging.getLogger("stdout")

    log_setup.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log_setup.addHandler(stream_handler)

    return log_setup
