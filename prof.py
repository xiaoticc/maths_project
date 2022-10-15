import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        # подгружаем дизайн
        self.btn_ent.clicked.connect(self.open_pos)

    def open_pos(self):
        # открытие следующего окна
        self.pos_window = Possibilities()
        self.pos_window.show()
        self.pos_window.move(self.pos())
        self.hide()


class Possibilities(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('possibilities.ui', self)
        # подгружаем дизайн
        self.btn_test.clicked.connect(self.open_test)
        self.btn_prof.clicked.connect(self.open_profs)

    def open_test(self):
        # открытие теста
        self.test_window = Test()
        self.test_window.show()
        self.test_window.move(self.pos())
        self.hide()

    def open_profs(self):
        # открытие списка профессий
        self.profs_window = Profs()
        self.profs_window.show()
        self.profs_window.move(self.pos())
        self.hide()


class Test(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('test.ui', self)
        # подгружаем дизайн
        self.btn_endt.clicked.connect(self.open_res)

    def open_res(self):
        # открытие результатов теста
        self.res_window = Results()
        self.res_window.show()
        self.res_window.move(self.pos())
        self.hide()


class Profs(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('profs.ui', self)
        # подгружаем дизайн
        self.btn_mainp.clicked.connect(self.back_to_main)
        for button in self.prof_buttons.buttons():
            button.clicked.connect(self.open_journals)

    def open_journals(self):
        # открытие статей
        self.journ_window = Journals()
        self.journ_window.show()
        self.journ_window.move(self.pos())
        self.hide()

    def back_to_main(self):
        # вернуться в главное меню
        self.pos_wnd = Possibilities()
        self.pos_wnd.show()
        self.pos_wnd.move(self.pos())
        self.close()


class Results(Profs):
    # наследуется от класса Profs, тк у них действует один и тот же метод возвращения в главное меню
    def __init__(self, pos_wnd=None):
        super().__init__()
        uic.loadUi('results.ui', self)
        # подгружаем дизайн
        self.pos_wnd = pos_wnd
        self.btn_mainr.clicked.connect(self.back_to_main)


class Journals(QMainWindow):
    def __init__(self):
        super(Journals, self).__init__()
        uic.loadUi('journals.ui', self)
        # подгружаем дизайн
        self.btn_return.clicked.connect(self.back_to_profs)

    def back_to_profs(self):
        # возвращает обратно к списку профессий
        self.profs_wnd = Profs()
        self.profs_wnd.show()
        self.profs_wnd.move(self.pos())
        self.close()


# нужная вещь для отображения ошибок не кодами возврата
def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


if __name__ == "__main__":
    sys.excepthook = except_hook
    # создается экземпляр класса QApplication, то есть app - это наше приложение
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())