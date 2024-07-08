from pathlib import Path
from traycortex.tray import borgmatic_checker, borgmatic_runner, create_menu, menu_click
from traycortex.client import TCMessage, send_msg
from traycortex.defaults import (
    DEFAULT_PORT,
    MSG_JOB_ERROR,
    MSG_JOB_STARTED,
    MSG_JOB_FINISHED,
    MSG_CLOSE,
    TITLE_ERROR,
    TITLE_IDLE,
    TITLE_PREFIX_RUNNING,
    MENU_PREFIX_ENGAGE,
    MENU_ENGAGE_ALL,
    MENU_DISCARD,
)
import threading
import time
import queue
import pytest


def test_borgmatic_checker(populated_config_object, mock_icon):
    # Make test not fail if another instance is already running
    populated_config_object.config.set("connection", "port", value=str(DEFAULT_PORT))
    inner_func = borgmatic_checker(mock_icon, populated_config_object)
    checker = threading.Thread(target=inner_func)
    checker.start()
    # We need to wait for the thread to have initialized
    time.sleep(0.1)
    send_msg(TCMessage(MSG_JOB_STARTED, ""), populated_config_object)
    send_msg(TCMessage(MSG_JOB_FINISHED, ""), populated_config_object)
    send_msg(TCMessage(MSG_CLOSE, ""), populated_config_object)
    assert mock_icon.notifications == ["Backup started", "Finished backup"]


def test_borgmatic_checker_with_args(populated_config_object, mock_icon):
    # Make test not fail if another instance is already running
    populated_config_object.config.set("connection", "port", value=str(DEFAULT_PORT))
    inner_func = borgmatic_checker(mock_icon, populated_config_object)
    checker = threading.Thread(target=inner_func)
    checker.start()
    # We need to wait for the thread to have initialized
    time.sleep(0.1)
    send_msg(TCMessage(MSG_JOB_STARTED, "someconfig.yml"), populated_config_object)
    time.sleep(0.1)
    assert mock_icon.title == f"{TITLE_PREFIX_RUNNING}someconfig.yml"
    send_msg(TCMessage(MSG_JOB_FINISHED, "someconfig.yml"), populated_config_object)
    time.sleep(0.1)
    assert mock_icon.title == TITLE_IDLE
    send_msg(TCMessage(MSG_JOB_ERROR, "some error"), populated_config_object)
    send_msg(TCMessage(MSG_CLOSE, ""), populated_config_object)
    time.sleep(0.1)
    assert mock_icon.notifications == [
        "Backup started",
        "Finished backup",
        "Backup error: some error",
    ]
    assert mock_icon.title == TITLE_ERROR


@pytest.mark.parametrize(
    "borgmatic_command, notifications",
    [
        ("/bin/true", ["Commencing backup...", "Finished backup"]),
        ("/bin/false", ["Commencing backup...", "Backup error (1)"]),
        ("exit 9", ["Commencing backup...", "Backup error (9)"]),
    ],
)
def test_borgmatic_runner_success(
    populated_config_object, mock_icon, borgmatic_command, notifications
):
    populated_config_object.config.set("connection", "port", value=str(DEFAULT_PORT))
    populated_config_object.config.add_section("borgmatic")
    populated_config_object.config.set("borgmatic", "command", value=borgmatic_command)
    runq = queue.Queue()
    inner_func = borgmatic_runner(mock_icon, populated_config_object, runq)
    runner = threading.Thread(target=inner_func)
    runner.start()
    runq.put(True)
    time.sleep(0.1)
    # End the thread
    runq.put(False)
    assert mock_icon.notifications == notifications


def test_create_menu(monkeypatch, populated_config_object):

    def mock_path_exists(_):
        return True

    def mock_find_all_borgmatic_yaml():
        return [
            Path("/etc/borgmatic/config.yaml"),
            Path("/test/test.yaml"),
            Path("/test/test2.yml"),
        ]

    monkeypatch.setattr("traycortex.borgmatic.Path.exists", mock_path_exists)
    monkeypatch.setattr(
        "traycortex.tray.find_all_borgmatic_yaml", mock_find_all_borgmatic_yaml
    )
    runq: "queue.Queue[str]" = queue.Queue()
    menu = create_menu(populated_config_object, runq)
    menu_items = [x.text for x in menu.items]
    assert menu_items == [
        f"{MENU_PREFIX_ENGAGE}{MENU_ENGAGE_ALL}",
        f"{MENU_PREFIX_ENGAGE}/etc/borgmatic/config.yaml",
        f"{MENU_PREFIX_ENGAGE}/test/test.yaml",
        f"{MENU_PREFIX_ENGAGE}/test/test2.yml",
        "- - - -",
        MENU_DISCARD,
    ]


def test_menu_click(populated_config_object, mock_icon):
    runq: "queue.Queue[str]" = queue.Queue()
    click_handler = menu_click(runq, populated_config_object)
    click_handler(mock_icon, f"{MENU_PREFIX_ENGAGE}Gookenprien")
    assert runq.get() == "Gookenprien"
