from traycortex.tray import borgmatic_checker
from traycortex.client import send_msg
from traycortex.defaults import MSG_JOB_STARTED, MSG_JOB_FINISHED, MSG_CLOSE
import threading
import time


def test_borgmatic_checker(populated_config_object, mock_icon):
    inner_func = borgmatic_checker(mock_icon, populated_config_object)
    checker = threading.Thread(target=inner_func)
    checker.start()
    # We need to wat for the thread to have initialized
    time.sleep(1)
    send_msg(MSG_JOB_STARTED, populated_config_object)
    send_msg(MSG_JOB_FINISHED, populated_config_object)
    send_msg(MSG_CLOSE, populated_config_object)
    assert mock_icon.notifications == ["Backup started", "Finished backup"]
