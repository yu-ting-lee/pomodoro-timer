import sys

from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QCloseEvent, QFont, QIcon, QKeyEvent
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)
from utils import Icon, Timer

COUNTER = ['First', 'Second', 'Third', 'Fourth']

timer = Timer()


class GearWidget(QWidget):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.title = 'Setting'
        self.initUI()

    def initUI(self) -> None:
        """initialize user interface"""
        self.setWindowTitle(self.title)
        self.setWindowFlags(Qt.Window | self.windowFlags())
        self.setGeometry(0, 0, 500, 350)
        main = QVBoxLayout()

        main.addStretch()
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)
        label = QLabel('WORK', self)
        grid.addWidget(label, 0, 0, 1, 1)
        self.work = QTimeEdit(timer.duration['W'], self)
        self.work.setDisplayFormat('mm:ss')
        self.work.setMinimumTime(QTime(0, 0, 1))
        self.work.timeChanged.connect(self.change)
        grid.addWidget(self.work, 0, 1, 1, 1)

        label = QLabel('SHORT BREAK', self)
        grid.addWidget(label, 1, 0, 1, 1)
        self.short = QTimeEdit(timer.duration['S'], self)
        self.short.setDisplayFormat('mm:ss')
        self.short.setMinimumTime(QTime(0, 0, 1))
        grid.addWidget(self.short, 1, 1, 1, 1)

        label = QLabel('LONG BREAK', self)
        grid.addWidget(label, 2, 0, 1, 1)
        self.long = QTimeEdit(timer.duration['L'], self)
        self.long.setDisplayFormat('mm:ss')
        self.long.setMinimumTime(QTime(0, 0, 1))
        grid.addWidget(self.long, 2, 1, 1, 1)

        label = QLabel('ALARM', self)
        grid.addWidget(label, 3, 0, 1, 1)
        self.alarm = QTimeEdit(timer.alarm, self)
        self.alarm.setDisplayFormat('mm:ss')
        self.alarm.setTimeRange(QTime(0, 0, 1), self.work.time())
        grid.addWidget(self.alarm, 3, 1, 1, 1)
        main.addLayout(grid)
        main.addStretch()

        line = QHBoxLayout()
        self.backBtn = QPushButton(QIcon('figure/back.png'), ' Back', self)
        self.backBtn.clicked.connect(self.close)
        line.addWidget(self.backBtn)
        self.saveBtn = QPushButton(QIcon('figure/save.png'), ' Save', self)
        self.saveBtn.clicked.connect(self.save)
        line.addWidget(self.saveBtn)
        main.addLayout(line)

        self.setLayout(main)
        self.show()
        self.center()

    def change(self) -> None:
        """update alarm time limit"""
        self.alarm.setMaximumTime(self.work.time())

    def save(self) -> None:
        """save timer settings and reset"""
        self.close()
        self.parent().counter.setText('First Pomodoro')
        timer.duration = {
            'W': self.work.time(),
            'S': self.short.time(),
            'L': self.long.time(),
        }
        timer.alarm = self.alarm.time()
        timer.reset()

    def center(self) -> None:
        """move widget to the center of screen"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class RestWidget(QWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.title = 'Short Break' if timer.state == 'S' else 'Long Break'
        self.locked = True
        timer.tick.connect(self.tick)
        timer.work.connect(self.work)
        self.initUI()

    def initUI(self) -> None:
        """initialize user interface"""
        self.setWindowTitle(self.title)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint | self.windowFlags())
        self.setGeometry(0, 0, 0, 0)
        main = QVBoxLayout()

        main.addStretch()
        self.counter = QLabel(self.parent().counter.text(), self)
        self.counter.setStyleSheet('font-size: 18px;')
        main.addWidget(self.counter)

        self.time = QLabel(timer.toString(), self)
        self.time.setStyleSheet('font-size: 125px; font-weight: bold;')
        main.addWidget(self.time)
        main.addStretch()

        self.setLayout(main)
        self.showFullScreen()

    def tick(self) -> None:
        """update timer text"""
        self.time.setText(timer.toString())

    def work(self) -> None:
        """update parent counter and close the widget"""
        self.locked = False
        self.parent().counter.setText(COUNTER[timer.counter] + ' Pomodoro')
        self.close()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """hidden method to close the widget"""
        if event.key() != Qt.Key_Q:
            return
        timer.reset(reset_counter=False)
        self.work()
        timer.start(1000)

    def closeEvent(self, event: QCloseEvent) -> None:
        """ignore close event unless the timer timeout"""
        if self.locked:
            event.ignore()
        else:
            event.accept()


class Widget(QWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.title = 'Pomodoro Timer'
        timer.tick.connect(self.tick)
        timer.rest.connect(self.rest)
        self.initUI()

    def initUI(self) -> None:
        """initialize user interface"""
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, 500, 350)
        main = QVBoxLayout()

        main.addStretch()
        self.counter = QLabel('First Pomodoro', self)
        self.counter.setStyleSheet('font-size: 18px;')
        main.addWidget(self.counter)

        self.time = QLabel(timer.toString(), self)
        self.time.setStyleSheet('font-size: 125px; font-weight: bold;')
        main.addWidget(self.time)
        main.addStretch()

        line = QHBoxLayout()
        self.gearBtn = QPushButton(QIcon('figure/setting.png'), ' Setting',
                                   self)
        self.gearBtn.clicked.connect(self.gear)
        line.addWidget(self.gearBtn)
        self.ctrlBtn = QPushButton(QIcon('figure/toggle.png'), ' Start', self)
        self.ctrlBtn.clicked.connect(self.ctrl)
        line.addWidget(self.ctrlBtn)
        main.addLayout(line)

        self.setLayout(main)
        self.show()
        self.center()

    def ctrl(self) -> None:
        """toggle timer state"""
        if timer.isActive():
            self.ctrlBtn.setText(' Start')
            timer.stop()
        else:
            self.ctrlBtn.setText(' Pause')
            timer.start(1000)

    def gear(self) -> None:
        """show setting widget"""
        self.widget = GearWidget(self)
        self.widget.setStyleSheet("""
            QLabel { padding: 10px; }
            QPushButton { font-size: 20px; }
            QTimeEdit { font-size: 20px; }
            """)
        self.ctrlBtn.setText(' Start')
        timer.stop()

    def tick(self) -> None:
        """update timer text"""
        self.time.setText(timer.toString())

    def rest(self) -> None:
        """show rest widget"""
        self.widget = RestWidget(self)
        self.widget.setStyleSheet("""
            QLabel { qproperty-alignment: AlignCenter; }
            """)

    def center(self) -> None:
        """move widget to the center of screen"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event: QCloseEvent) -> None:
        """ignore close event and hide the widget"""
        event.ignore()
        self.hide()


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName('Pomodoro Timer')
    app.setQuitOnLastWindowClosed(False)

    font = QFont('Courier')
    font.setStyleHint(QFont.TypeWriter)
    app.setFont(font)

    widget = Widget()
    widget.setStyleSheet("""
        QLabel { qproperty-alignment: AlignCenter; } 
        QPushButton { font-size: 20px; }
        """)
    icon = Icon(timer, widget, app)
    icon.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()