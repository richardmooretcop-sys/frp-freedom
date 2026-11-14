import logging
from pathlib import Path
import threading
from unittest.mock import Mock

from src.core.device_manager import DeviceInfo, DeviceManager
from src.gui.device_selection import DeviceSelectionFrame


def make_device(**overrides):
    values = {
        "serial": "serial-001",
        "model": "Test Phone",
        "manufacturer": "Example",
        "android_version": "14",
        "sdk_version": "34",
        "bootloader_version": "unknown",
        "frp_status": "unknown",
        "connection_type": "adb",
    }
    values.update(overrides)
    return DeviceInfo(**values)


def test_adb_poll_reuses_details_for_an_unchanged_device(monkeypatch):
    manager = DeviceManager.__new__(DeviceManager)
    manager.logger = logging.getLogger(__name__)
    manager.adb_path = Path("adb")
    existing_device = make_device()
    manager.connected_devices = [existing_device]
    manager._get_adb_device_info = Mock(
        side_effect=AssertionError("poll should reuse cached device details")
    )
    monkeypatch.setattr(
        "src.core.device_manager.subprocess.run",
        Mock(return_value=Mock(
            returncode=0,
            stdout="List of devices attached\nserial-001 device model:Test_Phone\n",
            stderr="",
        )),
    )

    devices = manager._scan_adb_devices(refresh_details=False)

    assert devices == [existing_device]
    manager._get_adb_device_info.assert_not_called()


def test_scan_rebuilds_modem_ports_on_local_records_before_publishing():
    device = make_device(modem_port="COM7")
    manager = DeviceManager.__new__(DeviceManager)
    manager.logger = logging.getLogger(__name__)
    manager._scan_lock = threading.Lock()
    manager.connected_devices = [device]
    manager._scan_adb_devices = Mock(return_value=[device])
    manager._scan_fastboot_devices = Mock(return_value=[])
    manager._scan_download_mode_devices = Mock(return_value=[])

    def scan_modems(scan_devices):
        assert device.modem_port == "COM7"
        assert scan_devices[0] is not device
        assert scan_devices[0].modem_port == ""
        scan_devices[0].modem_port = "COM8"
        return []

    manager.scan_samsung_modems = Mock(side_effect=scan_modems)

    manager.scan_devices(refresh_details=False)

    manager.scan_samsung_modems.assert_called_once()
    assert device.modem_port == "COM7"
    assert manager.connected_devices[0] is not device
    assert manager.connected_devices[0].modem_port == "COM8"


def test_device_list_poll_does_not_rebuild_unchanged_tree_rows():
    frame = DeviceSelectionFrame.__new__(DeviceSelectionFrame)
    frame.winfo_exists = Mock(return_value=True)
    frame.device_tree = Mock()
    frame.device_tree.winfo_exists.return_value = True
    frame.device_tree.item.return_value = (
        "serial-001",
        "Test Phone",
        "unknown",
        "14",
        "ADB",
        "unknown",
    )
    frame.status_label = Mock()
    frame.status_label.winfo_exists.return_value = True
    frame.device_items_by_key = {("adb", "serial-001"): "row-1"}
    old_device = make_device(model="Old Model")
    frame.device_map = {"row-1": old_device}
    frame.selected_device = old_device
    frame.device_tree.selection.side_effect = [("row-1",), ()]
    frame.update_device_details = Mock()

    refreshed_device = make_device()
    DeviceSelectionFrame.update_device_list(frame, [refreshed_device])

    frame.device_tree.insert.assert_not_called()
    frame.device_tree.delete.assert_not_called()
    assert frame.device_tree.item.call_count == 1
    assert frame.device_map["row-1"] is refreshed_device
    assert frame.selected_device is refreshed_device
    frame.update_device_details.assert_called_once_with(refreshed_device)


def test_removing_selected_device_clears_selection_state():
    frame = DeviceSelectionFrame.__new__(DeviceSelectionFrame)
    frame.winfo_exists = Mock(return_value=True)
    frame.device_tree = Mock()
    frame.device_tree.winfo_exists.return_value = True
    frame.device_tree.selection.side_effect = [("row-1",), ()]
    frame.status_label = Mock()
    frame.status_label.winfo_exists.return_value = True
    frame.device_items_by_key = {("adb", "serial-001"): "row-1"}
    frame.device_map = {"row-1": make_device()}
    frame.selected_device = frame.device_map["row-1"]
    frame.select_button = Mock()
    frame.info_button = Mock()
    frame.update_device_details = Mock()

    DeviceSelectionFrame.update_device_list(frame, [])

    assert frame.selected_device is None
    frame.device_tree.delete.assert_called_once_with("row-1")
    frame.select_button.configure.assert_called_once_with(state="disabled")
    frame.info_button.configure.assert_called_once_with(state="disabled")
    frame.update_device_details.assert_called_once_with(None)
