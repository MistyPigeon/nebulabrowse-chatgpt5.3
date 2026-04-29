import sys
from PyQt5 import QtWidgets, QtCore
from cefpython3 import cefpython as cef

# Fix for high DPI displays
cef.DpiAware.EnableHighDpiSupport()


class BrowserWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NebulaBrowse")
        self.setGeometry(100, 100, 1200, 800)

        self.browser = None

        # Central widget
        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QtWidgets.QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Navigation bar
        nav_bar = QtWidgets.QHBoxLayout()

        self.back_btn = QtWidgets.QPushButton("←")
        self.forward_btn = QtWidgets.QPushButton("→")
        self.reload_btn = QtWidgets.QPushButton("⟳")

        self.url_bar = QtWidgets.QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL...")

        self.go_btn = QtWidgets.QPushButton("Go")

        nav_bar.addWidget(self.back_btn)
        nav_bar.addWidget(self.forward_btn)
        nav_bar.addWidget(self.reload_btn)
        nav_bar.addWidget(self.url_bar)
        nav_bar.addWidget(self.go_btn)

        self.layout.addLayout(nav_bar)

        # Browser widget container
        self.browser_frame = QtWidgets.QFrame()
        self.layout.addWidget(self.browser_frame)

        # Connect buttons
        self.back_btn.clicked.connect(self.go_back)
        self.forward_btn.clicked.connect(self.go_forward)
        self.reload_btn.clicked.connect(self.reload_page)
        self.go_btn.clicked.connect(self.load_url)
        self.url_bar.returnPressed.connect(self.load_url)

        # Timer for CEF message loop
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.cef_loop)
        self.timer.start(10)

        self.show()

    def cef_loop(self):
        cef.MessageLoopWork()

    def embed_browser(self):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.browser_frame.width(), self.browser_frame.height()]
        window_info.SetAsChild(int(self.browser_frame.winId()), rect)

        self.browser = cef.CreateBrowserSync(
            window_info,
            url="https://www.google.com"
        )

    def resizeEvent(self, event):
        if self.browser:
            self.browser.SetBounds(0, 0, self.browser_frame.width(), self.browser_frame.height())
        super().resizeEvent(event)

    def showEvent(self, event):
        if not self.browser:
            self.embed_browser()
        super().showEvent(event)

    def load_url(self):
        url = self.url_bar.text().strip()

        if not url.startswith("http"):
            url = "https://" + url

        if self.browser:
            self.browser.LoadUrl(url)

    def go_back(self):
        if self.browser and self.browser.CanGoBack():
            self.browser.GoBack()

    def go_forward(self):
        if self.browser and self.browser.CanGoForward():
            self.browser.GoForward()

    def reload_page(self):
        if self.browser:
            self.browser.Reload()

    def closeEvent(self, event):
        self.timer.stop()
        cef.Shutdown()
        event.accept()


def main():
    cef.Initialize()

    app = QtWidgets.QApplication(sys.argv)
    window = BrowserWindow()

    app.exec_()


if __name__ == "__main__":
    main()
