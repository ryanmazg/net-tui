from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Footer, Header

from .wifi import scan_wifi_networks


class NetTuiApp(App):
    """A Textual app to manage network connections."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_wifi", "Refresh Wi-Fi List"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container(id="main-container"):
            yield DataTable(id="wifi-table")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        table = self.query_one(DataTable)

        table.add_columns("IN-USE", "SSID", "BSSID", "SIGNAL", "SECURITY")

        self.action_refresh_wifi()

    def action_refresh_wifi(self) -> None:
        """An action to refresh the Wi-Fi network list."""
        table = self.query_one(DataTable)

        table.clear()

        networks = scan_wifi_networks()

        if networks:
            # Sort networks by signal strength (strongest first)
            networks.sort(key=lambda net: net.signal, reverse=True)

            for net in networks:
                # Use a star character for the network in use
                in_use_char = "[green] ✔" if net.in_use else ""

                table.add_row(
                    in_use_char, net.ssid, net.bssid, f"{net.signal}%", net.security
                )


if __name__ == "__main__":
    app = NetTuiApp()
    app.run()
