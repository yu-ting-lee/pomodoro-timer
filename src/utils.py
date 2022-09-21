from PyQt5.QtCore import pyqtSignal, QTime, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QMenu,
    QSystemTrayIcon,
    QWidget,
)


class Timer(QTimer):
    work = pyqtSignal()
    rest = pyqtSignal()
    tick = pyqtSignal()
    ring = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.timeout.connect(self._timeout)
        self.duration = {
            'W': QTime(0, 25, 0),
            'S': QTime(0, 5, 0),
            'L': QTime(0, 15, 0)
        }
        self.alarm = QTime(0, 1, 0)
        self.reset()

    def reset(self, counter: bool = True) -> None:
        """reset timer to initial state"""
        self.state = 'W'
        self.time = self.duration[self.state]
        self.counter = 0 if counter else self.counter
        self.tick.emit()

    def toString(self) -> str:
        """return time in mm:ss format"""
        return self.time.toString('mm:ss')

    def _timeout(self) -> None:
        """update time and state"""
        if self.time != QTime(0, 0, 0):
            self.time = self.time.addSecs(-1)

        elif self.state == 'W':
            self.counter = (self.counter + 1) % 4
            self.state = 'S' if self.counter else 'L'
            self.time = self.duration[self.state]
            self.rest.emit()
        else:
            self.state = 'W'
            self.time = self.duration[self.state]
            self.work.emit()

        if self.state == 'W' and self.time == self.alarm:
            self.ring.emit()
        self.tick.emit()

    def start(self, msec: int) -> None:
        """start timer and check alarm time"""
        super().start(msec)
        if self.time == self.alarm:
            self.ring.emit()


class Icon(QSystemTrayIcon):

    def __init__(self, app: QApplication, widget: QWidget,
                 timer: Timer) -> None:
        super().__init__(QIcon("figure/timer.png"))

        self.activated.connect(self.trig)
        self.widget = widget
        self.app = app
        self.timer = timer
        timer.ring.connect(self.ring)

        menu = QMenu()
        ctrl = QAction("Start / Pause Timer", menu)
        ctrl.triggered.connect(self.ctrl)
        menu.addAction(ctrl)

        quit = QAction("Quit Pomodoro", menu)
        quit.triggered.connect(self.quit)
        menu.addAction(quit)
        self.setContextMenu(menu)

    def ring(self) -> None:
        """show notification at alarm time"""
        m, s = self.timer.alarm.minute(), self.timer.alarm.second()
        msg = f'\uD83D\uDD14 {m} minute(s) and {s} second(s) left!'
        self.showMessage('', msg)

    def ctrl(self) -> None:
        """toggle timer state"""
        if self.timer.state == 'W':
            self.widget.ctrl()

    def quit(self) -> None:
        """quit application"""
        if self.timer.state == 'W':
            self.app.quit()

    def trig(self, ar: QSystemTrayIcon.ActivationReason) -> None:
        """toggle widget visibility"""
        if ar != QSystemTrayIcon.Trigger:
            return
        if self.widget.isVisible():
            self.app.closeAllWindows()
        else:
            self.widget.show()