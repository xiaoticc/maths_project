import sys
import sqlite3
from PyQt5.QtCore import Qt, QSize
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QGroupBox, QLabel, QLineEdit, QVBoxLayout, \
    QPushButton, QMessageBox

con = sqlite3.connect("maths_db.sqlite")


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
        self.btn_prof.clicked.connect(self.open_tasks)

    def open_test(self):
        # открытие теста
        self.test_window = Test()
        self.test_window.show()
        self.test_window.move(self.pos())
        self.hide()

    def open_tasks(self):
        # открытие списка профессий
        self.tasks_window = Tasks()
        self.tasks_window.show()
        self.tasks_window.move(self.pos())
        self.hide()


class Test(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('test.ui', self)
        # подгружаем дизайн
        self.btn_endt.clicked.connect(self.open_res)
        self.set_temp_task()

    def set_temp_task(self):
        cur = con.cursor()
        self.data = cur.execute("""SELECT * FROM task_answer, tasks_theme
                                    WHERE theme_id = task_id AND
                                    temp_answer = 1""").fetchall()
        # print(self.data)
        self.layout = QVBoxLayout()

        for i, el in enumerate(self.data):
            self.layout.addWidget(self.create_ui_answer(i + 1, el[2]))
            print(el)
        self.scrollArea.setWidgetResizable(True)
        # self.scrollArea.setLayout(layout)
        self.scrollAreaWidgetContents_2.setLayout(self.layout)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def create_ui_answer(self, num, name):
        layout = QVBoxLayout()
        groupBox = QGroupBox(f"Вопрос {num}")
        groupBox.setMinimumHeight(200)
        groupBox.setMinimumWidth(300)
        label = QLabel(name, self)
        label.setWordWrap(True)
        line_edit = QLineEdit(self)
        layout.addWidget(label)
        layout.addWidget(line_edit)
        groupBox.setLayout(layout)
        return groupBox

    def open_res(self):
        # открытие результатов теста
        self.res_window = Results(*self.results())
        self.res_window.show()
        self.res_window.move(self.pos())
        self.hide()

    def results(self):
        cur = con.cursor()
        counter_right = 0
        wrong_theme = [0, 0, 0]
        for i, el in enumerate(self.data):
            box = self.layout.itemAt(i).widget()
            line = box.findChildren(QLineEdit)[0]
            user_answer = line.text()
            right_answer = str(el[3])
            if user_answer == right_answer:
                counter_right += 1
            else:
                wrong_theme[int(el[1]) - 1] += 1
        return counter_right, wrong_theme
        # print(self.layout.itemAt(0).widget().findChildren(QLineEdit)[0].text())


# Profs - Tasks

class Tasks(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('profs.ui', self)
        # подгружаем дизайн
        self.btn_mainp.clicked.connect(self.back_to_main)
        for button in self.prof_buttons.buttons():
            button.clicked.connect(self.open_journals)

    def open_journals(self):
        # открытие статей
        text = self.sender().text()
        self.journ_window = Journals(text)
        self.journ_window.show()
        self.journ_window.move(self.pos())
        self.hide()

    def back_to_main(self):
        # вернуться в главное меню
        self.pos_wnd = Possibilities()
        self.pos_wnd.show()
        self.pos_wnd.move(self.pos())
        self.close()


class Results(Tasks):
    # наследуется от класса Tasks, тк у них действует один и тот же метод возвращения в главное меню
    def __init__(self, right, wrong_theme, pos_wnd=None):
        super().__init__()
        uic.loadUi('results.ui', self)
        # подгружаем дизайн
        self.right = right
        self.wrong_theme = wrong_theme
        self.pos_wnd = pos_wnd
        self.btn_mainr.clicked.connect(self.back_to_main)
        self.create_answer()

    def create_answer(self):
        cur = con.cursor()
        themes = cur.execute("""SELECT task_var FROM tasks_theme""").fetchall()
        themes = [el[0] for el in themes]
        a = '\n'.join([themes[el] for el in range(len(self.wrong_theme)) if self.wrong_theme[el] != 0])
        self.label_2.setText(f"""количество правильных ответов: {self.right} 
количество неправильных ответов: {sum(self.wrong_theme)}
у вас проблемы с темой(-ами): {a}""")


class Journals(QMainWindow):
    def __init__(self, name):
        super(Journals, self).__init__()
        uic.loadUi('journals.ui', self)
        # подгружаем дизайн
        self.name = name
        self.btn_return.clicked.connect(self.back_to_tasks)
        self.set_task()
        # for el in self.layout.itemAt(0).widget().findChildren(QLineEdit):
        #     print(1)

    def set_task(self):
        cur = con.cursor()
        # task = self.name
        command = f"""SELECT * FROM task_answer, tasks_theme
                                    WHERE theme_id = task_id AND
                                    temp_answer = 0 AND
                                    task_var = '{self.name}'"""
        # self.data = cur.execute("""SELECT * FROM task_answer, tasks_theme
        #                             WHERE theme_id = task_id AND
        #                             temp_answer = 0 AND
        #                             task_var =:task""", {"task": task}).fetchall()
        self.data = cur.execute(command).fetchall()
        self.layout = QVBoxLayout()

        for i, el in enumerate(self.data):
            self.layout.addWidget(self.create_ui_answer(i + 1, el[2]))
        self.scrollArea.setWidgetResizable(True)
        # self.scrollArea.setLayout(layout)
        self.scrollAreaWidgetContents.setLayout(self.layout)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def create_ui_answer(self, num, name):
        layout = QVBoxLayout()
        groupBox = QGroupBox(f"Вопрос {num}")
        # print(num)
        self.label.setText(f'Тренажер на тему: {self.name}')
        groupBox.setMinimumHeight(200)
        groupBox.setMinimumWidth(300)
        label = QLabel(name, self)
        label.setWordWrap(True)
        self.line_edit = QLineEdit(self)
        # сделать QPushButton и по нажатию на кнопку переходить на doSomething
        # или!! оставить изменение цвета, при вводе правильного или неправильного ответа,а на кнопку сделать показ решения
        # событие на изменение line_edit
        self.btn_answ = QPushButton("Правильный ответ", self)
        self.line_edit.textChanged.connect(lambda x: self.doSomething(num - 1))
        self.btn_answ.clicked.connect(lambda x: self.show_solution(num - 1))
        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.btn_answ)
        groupBox.setLayout(layout)
        return groupBox

    def back_to_tasks(self):
        # возвращает обратно к списку тем задач
        self.profs_wnd = Tasks()
        self.profs_wnd.show()
        self.profs_wnd.move(self.pos())
        self.close()

    def doSomething(self, num_question):
        # ПОМЕНЯТЬ!! может быть сделать MessageBox, для создания всплывающего окна,
        # которое будет показывать правильный ответ после нажатия на кнопку проверить ответ
        # кстати, можно в messagebox поместить кнопку, которая будет показывать решение задачи
        # (если в модулях будет решение, написанное словами, а не картинками)
        user_answer = self.sender().text()
        right_answer = str(self.data[num_question][3])
        print(right_answer, user_answer, self.data[num_question][3])
        if user_answer == right_answer:
            self.sender().setStyleSheet("color: rgb(0, 255, 0);")
        else:
            self.sender().setStyleSheet("color: rgb(255, 0, 0);")

    def show_solution(self, num_question):
        solution = QMessageBox()
        solution.setWindowTitle("решение")
        solution.setText("Здесь могло быть ваше решение")
        solution.setStandardButtons(QMessageBox.Ok)
        solution.setInformativeText('нужно подключить к базе данных решения, но пока что это сделано не было')
        solution.setDetailedText('детали детали')

        solution.exec_()


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
