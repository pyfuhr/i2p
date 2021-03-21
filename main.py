import rsa
import socket
from threading import Thread
import sys, os
from PyQt5 import uic
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings


def UI():
    app = QApplication(sys.argv)
    global ex
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())


def potok(sc):
    ex.list.addItem(str(sc))
    sc.send(str(sc).encode())
    sc.close()


def settexth(box, text, color, new=False):
    if new:
        box.clear()
    box.appendHtml('<font color=\"' + color + '\">' + text + '</font>')


class MB(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('messagebox.ui', self)
        self.hide()


class Web(QWebEngineView):
    def __init__(self):
        super().__init__()

    def setAttr(self, type, state):
        settings = QWebEngineSettings.globalSettings()
        if type == 'js':
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, state())


class MyWidget(QMainWindow):

    def __init__(self):
        super().__init__()
        self.MB = MB()

        uic.loadUi('ui.ui', self)

        self.webEngineView = Web()
        self.gridLayout.addWidget(self.webEngineView)
        self.bGo.clicked.connect(lambda: self.loadPage(self.eBroURL.text()))
        self.bSendCommand.clicked.connect(self.i2cmp)
        self.bSendMessage.clicked.connect(self.sendMes)
        self.leMessage.returnPressed.connect(self.sendMes)
        self.leCommand.returnPressed.connect(self.i2cmp)
        self.eBroURL.returnPressed.connect(lambda: self.loadPage(self.eBroURL.text()))
        self.stateJS.stateChanged.connect(lambda:
                                self.webEngineView.setAttr('js', lambda: self.stateJS.checkState() == Qt.Checked))

        self.loadPage('main.html')
        self.abort.clicked.connect(self.webEngineView.stop)

    def viewmessage(self, title, text, yes):
        self.MB.setWindowTitle(title)
        self.MB.byes.text = yes
        self.MB.text.setText(text)
        self.MB.show()

    def loadPage(self, url: str):
        if url.startswith('eth:'):
            url = url[4:]
            self.webEngineView.load(QUrl('http://' + url))
        else:
            if os.path.isfile('browser/' + url):
                self.webEngineView.load(QUrl('file:///' + os.path.abspath(os.path.curdir).replace('\\', '/') + \
                                             '/browser/' + url))
            else:
                self.webEngineView.setHtml('<h1>404</h1>')

    def i2cmp(self):
        settexth(self.chatRoom, 'I2CMP: ' + self.leCommand.text(), '#00FF00')

    def sendMes(self):
        settexth(self.chatRoom, socket.gethostname() + ': ' + self.leMessage.text(), '#00AAFF')
        self.leMessage.setSelection(0, len(self.leMessage.text()))
        self.leMessage.backspace()


if __name__ == '__main__':

    ex = 0

    Thread(target=UI).start()

    print('Next')

    sock = socket.socket()
    sock.bind(('localhost', 5000))
    sock.listen(10)

    while True:
        so, addr= sock.accept()
        Thread(target=lambda: potok(so)).start()

