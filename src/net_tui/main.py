from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, TabbedContent, TabPane
from textual.containers import Container

from .wifi import scan_wifi_networks, WiFiNetwork
from .bluetooth import scan_bluetooth_devices, BluetoothDevice


class NetTuiApp(App):
    """A Textual app to manage network connections."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_data", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with TabbedContent(id="tabs"):
            with TabPane("Wi-Fi", id="wifi-pane"):
                yield DataTable(id="wifi-table")
            with TabPane("Bluetooth", id="bluetooth-pane"):
                yield DataTable(id="bluetooth-table")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is first mounted to set up tables."""
        wifi_table = self.query_one("#wifi-table", DataTable)
        wifi_table.add_columns("IN-USE", "SSID", "BSSID", "SIGNAL", "SECURITY")

        bluetooth_table = self.query_one("#bluetooth-table", DataTable)
        bluetooth_table.add_columns("CONNECTED", "NAME", "MAC ADDRESS")

        self.populate_wifi_table()
        self.populate_bluetooth_table()

    def populate_wifi_table(self) -> None:
        """Populates the Wi-Fi table with scanned networks."""
        table = self.query_one("#wifi-table", DataTable)
        table.clear()
        networks = scan_wifi_networks()
        if networks:
            networks.sort(key=lambda net: net.signal, reverse=True)
            for net in networks:
                in_use_char = "[green] ✔" if net.in_use else ""
                table.add_row(
                    in_use_char, net.ssid, net.bssid, f"{net.signal}%", net.security
                )

    def populate_bluetooth_table(self) -> None:
        """Populates the Bluetooth table with scanned devices."""
        table = self.query_one("#bluetooth-table", DataTable)
        table.clear()
        devices = scan_bluetooth_devices()
        if devices:
            devices.sort(key=lambda dev: dev.name)
            for dev in devices:
                connected_char = "[green] ✔" if dev.connected else ""
                table.add_row(connected_char, dev.name, dev.mac_address)

    def action_refresh_data(self) -> None:
        """An action to refresh data for the currently active tab."""
        active_tab_id = self.query_one(TabbedContent).active
        if active_tab_id == "wifi-pane":
            self.populate_wifi_table()
        elif active_tab_id == "bluetooth-pane":
            self.populate_bluetooth_table()


if __name__ == "__main__":
    app = NetTuiApp()
    app.run()
