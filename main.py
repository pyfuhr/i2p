import rsa
import socket, threading, signal
from threading import Thread, Event
import sys, os
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings, QWebEngineDownloadItem

threADs = []
running = os.getpid()

def xor(data, key):
    x = bytearray()
    for i in range(len(data) // len(key)):
        q = data[i*len(key):(i+1)*len(key)]
        x += bytearray(a^b for a, b in zip(*map(bytearray, [q, key])))
    if len(data) % len(key) != 0:
        q = data[-(len(data) % len(key)):]
        x += bytearray(a^b for a, b in zip(*map(bytearray, [q, key[0:len(data) % len(key)]])))

    return x

class MyThread(Thread):

    # Thread class with a _stop() method.
    # The thread itself has to check
    # regularly for the stopped() condition.

    def __init__(self, *args, **kwargs):
        super(MyThread, self).__init__(*args, **kwargs)
        self._stop = Event()

    # function using _stop function
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


def closeAPP():
    global running
    for i in threADs:
        i.stop()
    os.kill(running, 1)


def UI():
    global ex
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    app.exec_()
    closeAPP()



def potok(sc):
    settexth(ex.chatRoom, 'I2CMP:Sock.open at ' + str(sc.getpeername()), '#00FF00')
    pubkey, privkey = rsa.newkeys(512)
    sc.send((str(pubkey.n) + ' ' + str(pubkey.e)).encode())
    ex.keylist[str(sc)] = rsa.decrypt(sc.recv(1024), privkey)
    settexth(ex.chatRoom, 'I2CMP: connection protected ' + str(sc.getpeername()) + '', '#FF8800')
    ex.conlist.append(str(sc.getpeername()[0]))
    ex.list.clear()
    for i in ex.conlist:
        ex.list.addItem(str(sc.getpeername()[0]))
        ex.list.item(ex.list.count() - 1).setForeground(Qt.green)
    while True:
        try:
            message = xor(sc.recv(1024), ex.keylist[str(sc)]).decode()
        except ConnectionResetError:
            break
        if message:
            if message.endswith('EXIT'):
                break
            settexth(ex.chatRoom, message, '#0000FF')
            ex.chatRoom.update()
    settexth(ex.chatRoom, 'I2CMP:Sock.close at ' + str(sc.getpeername()), '#FF0000')
    ex.chatRoom.update()
    del ex.conlist[ex.conlist.index(str(sc.getpeername()[0]))]
    ex.list.clear()
    for i in ex.conlist:
        ex.list.addItem(str(sc.getpeername()[0]))
        ex.list.item(ex.list.count() - 1).setForeground(Qt.green)
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

        self.keylist = {}
        self.conlist = []

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
        self.reload.clicked.connect(self.webEngineView.reload)
        self.redo.clicked.connect(self.webEngineView.back)

        self.webEngineView.page().profile().downloadRequested.connect(self.on_downloadRequested)
        self.tools.currentIndexChanged.connect(self.toolStart)

    def on_downloadRequested(self, download):
        old_path = download.path()
        suffix = QtCore.QFileInfo(old_path).suffix()
        path, _ = QFileDialog.getSaveFileName(self.webEngineView.page().view(), "Save File", old_path, "*."+suffix)
        if path:
            download.setPath(path)
            download.accept()

    def update(self) -> None:
        self.repaint()

    def toolStart(self):
        if self.tools.currentIndex() == 1:
            path, _ = QFileDialog.getSaveFileName(self, "Save File", os.curdir, "*.pdf")
            self.webEngineView.page().printToPdf(path)
        self.tools.setCurrentIndex(0)

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
        global iptable
        settexth(self.chatRoom, socket.gethostname() + ': ' + self.leMessage.text(), '#00AAFF')
        #print(iptable)
        for i in iptable.keys():
            iptable[i].send(xor(self.leMessage.text().encode(), self.keylist[str(iptable[i])]))
        self.leMessage.setSelection(0, len(self.leMessage.text()))
        self.leMessage.backspace()


if __name__ == '__main__':

    ex = 0
    Thread(target=UI).start()

    print('Next')

    iptable = {}

    sock = socket.socket()
    sock.bind(('10.20.2.61', 5000))
    sock.listen(10)

    while True:
        so, addr = sock.accept()
        iptable[addr] = so
        threADs.append(MyThread(target=lambda: potok(so)))
        threADs[-1].start()
