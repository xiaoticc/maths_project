import sys
import sqlite3
from PyQt5.QtCore import Qt, QSize
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QGroupBox, QLabel, QLineEdit, QVBoxLayout, \
    QPushButton, QMessageBox

con = sqlite3.connect("maths_db.sqlite")


class Main(QMainWindow):
    # основное окно
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        # подгружаем дизайн
        self.btn_ent.clicked.connect(self.open_pos)
        print('main')

    def open_pos(self):
        # открытие следующего окна
        self.pos_window = Possibilities()
        self.pos_window.show()
        self.pos_window.move(self.pos())
        self.hide()


class Possibilities(QMainWindow):
    # пройти тест - перейти к заданиям
    def __init__(self):
        super().__init__()
        uic.loadUi('possibilities.ui', self)
        # подгружаем дизайн
        self.btn_test.clicked.connect(self.open_test)
        self.btn_themes.clicked.connect(self.open_tasks)
        self.btn_theory.clicked.connect(self.open_theory)
        print('possib')

    def open_theory(self):
        self.theory_window = Choose_theory()
        self.theory_window.show()
        self.theory_window.move(self.pos())
        self.hide()

    def open_test(self):
        # открытие теста
        self.test_window = Test()
        self.test_window.show()
        self.test_window.move(self.pos())
        self.hide()

    def open_tasks(self):
        # открытие списка задач
        self.tasks_window = Tasks()
        self.tasks_window.show()
        self.tasks_window.move(self.pos())
        self.hide()


class Test(QMainWindow):
    # пробное тестирование по одной задачке из кажого модуля
    def __init__(self):
        super().__init__()
        uic.loadUi('test.ui', self)
        # подгружаем дизайн
        self.btn_endt.clicked.connect(self.open_res)
        self.set_temp_task()
        print('test')

    def set_temp_task(self):
        cur = con.cursor()
        self.data = cur.execute("""SELECT * FROM task_answer, tasks_theme
                                    WHERE theme_id = task_id AND
                                    temp_answer = 1""").fetchall()
        self.layout = QVBoxLayout()

        for i, el in enumerate(self.data):
            self.layout.addWidget(self.create_ui_answer(i + 1, el[2]))
            print(el)
            # i - номер задачи (но тк в циклах идет счет с нуля, то приходится в функции вызывать i + 1) el -
            # значения таблицы с задачами и с блоками задач(отобранные в нужном формате в self.data) с заданиями
            # ответами и решениями(т.е. в el хранятся значения: айди задания, айди блока заданий, само задание,
            # решение, ответ, а также внешний ключ по которому связан блок заданий и само задание и сортировка на
            # тестовые и общие задания(0 или 1))

        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2.setLayout(self.layout)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def create_ui_answer(self, num, condit):
        layout = QVBoxLayout()
        groupBox = QGroupBox(f"Вопрос {num}")
        groupBox.setMinimumHeight(200)
        groupBox.setMinimumWidth(300)
        label = QLabel(condit, self)
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
        counter_right = 0
        wrong_theme = [0 for i in range(len(self.data))]
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


class Tasks(QMainWindow):
    # темы тестов
    def __init__(self):
        super().__init__()
        uic.loadUi('profs.ui', self)
        # подгружаем дизайн
        self.btn_mainp.clicked.connect(self.back_to_main)
        self.set_button()
        print('tasks')

    def open_themed_tests(self, text):
        # открытие статей
        self.themed_tests_window = Themed_tests(text)
        self.themed_tests_window.show()
        self.themed_tests_window.move(self.pos())
        self.hide()

    def set_button(self):
        cur = con.cursor()
        command = f"""SELECT task_var FROM tasks_theme"""
        self.data = cur.execute(command).fetchall()
        self.layout = QVBoxLayout()

        for i, el in enumerate(self.data):
            print(el[0])
            self.layout.addWidget(self.create_ui_answer(el[0]))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents.setLayout(self.layout)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def create_ui_answer(self, name):
        layout = QVBoxLayout()
        button = QPushButton(name, self)
        button.setMinimumHeight(150)
        button.setMinimumWidth(200)
        button.setStyleSheet('background-color: rgb(145, 182, 182); border-width: 1px; border-radius: 15px;')
        button.clicked.connect(lambda x: self.open_themed_tests(name))
        button.setLayout(layout)
        return button

    def back_to_main(self):
        # вернуться в главное меню
        self.pos_wnd = Possibilities()
        self.pos_wnd.show()
        self.pos_wnd.move(self.pos())
        self.close()


class Results(Tasks):
    # наследуется от класса Tasks, тк у них действует один и тот же метод возвращения в главное меню
    # результат пробного тестирования
    def __init__(self, right, wrong_theme, pos_wnd=None):
        super().__init__()
        uic.loadUi('results.ui', self)
        # подгружаем дизайн
        self.right = right
        self.wrong_theme = wrong_theme
        self.pos_wnd = pos_wnd
        self.btn_mainr.clicked.connect(self.back_to_main)
        self.create_answer()
        print('res')

    def create_answer(self):
        cur = con.cursor()
        themes = cur.execute("""SELECT task_var FROM tasks_theme""").fetchall()
        themes = [el[0] for el in themes]
        a = '\n'.join([themes[el] for el in range(len(self.wrong_theme)) if self.wrong_theme[el] != 0])
        self.label_2.setText(f"""количество правильных ответов: {self.right} 
количество неправильных ответов: {sum(self.wrong_theme)}
у вас проблемы с темой(-ами): {a}""")


class Themed_tests(QMainWindow):
    # тестирование по теме
    def __init__(self, name):
        super(Themed_tests, self).__init__()
        uic.loadUi('themed_tests.ui', self)
        # подгружаем дизайн
        self.name = name
        self.btn_return.clicked.connect(self.back_to_tasks)
        self.btn_answ.clicked.connect(self.answers)
        self.set_task()

    def set_task(self):
        cur = con.cursor()
        command = f"""SELECT * FROM task_answer, tasks_theme
                                    WHERE theme_id = task_id AND
                                    temp_answer = 0 AND
                                    task_var = '{self.name}'"""
        self.data = cur.execute(command).fetchall()
        self.layout = QVBoxLayout()

        for i, el in enumerate(self.data):
            self.layout.addWidget(self.create_ui_answer(i + 1, el[2]))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents.setLayout(self.layout)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def create_ui_answer(self, num, name):
        layout = QVBoxLayout()
        groupBox = QGroupBox(f"Вопрос {num}")
        self.label.setText(f'Тренажер на тему: {self.name}')
        groupBox.setMinimumHeight(200)
        groupBox.setMinimumWidth(300)
        label = QLabel(name, self)
        label.setWordWrap(True)
        self.line_edit = QLineEdit(self)
        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        groupBox.setLayout(layout)
        return groupBox

    def back_to_tasks(self):
        # возвращает обратно к списку тем задач
        self.tasks_wnd = Tasks()
        self.tasks_wnd.show()
        self.tasks_wnd.move(self.pos())
        self.close()

    def results(self):
        answer = []
        for i, el in enumerate(self.data):
            box = self.layout.itemAt(i).widget()
            line = box.findChildren(QLineEdit)[0]
            answer.append(line.text())

        print(answer)
        return answer

    def answers(self, num_question):
        self.tasks_answ = Themed_test_answers(self.results(), self.name)
        self.tasks_answ.show()
        self.tasks_answ.move(self.pos())
        self.close()


class Themed_test_answers(QMainWindow):
    def __init__(self, answers, name):
        super(Themed_test_answers, self).__init__()
        uic.loadUi('themed_test_answers.ui', self)
        # подгружаем дизайн
        self.answers = answers
        self.name = name
        cur = con.cursor()
        command = f"""SELECT * FROM task_answer, tasks_theme
                                            WHERE theme_id = task_id AND
                                            temp_answer = 0 AND
                                            task_var = '{self.name}'"""

        self.data = cur.execute(command).fetchall()
        self.btn_return.clicked.connect(self.back_to_tasks)
        self.set_task()
        print(self.data)

    def set_task(self):
        self.layout = QVBoxLayout()

        for i, el in enumerate(self.data):
            self.layout.addWidget(self.create_ui_answer(i + 1, el[2]))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents.setLayout(self.layout)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def create_ui_answer(self, num, name):
        layout = QVBoxLayout()
        groupBox = QGroupBox(f"Вопрос {num}")
        self.label.setText(f'Ответы')
        groupBox.setMinimumHeight(200)
        groupBox.setMinimumWidth(300)

        label_task = QLabel(name, self)
        label_task.setWordWrap(True)
        layout.addWidget(label_task)

        label_sol = QLabel(self.data[num - 1][4])
        label_sol.setWordWrap(True)
        layout.addWidget(label_sol)

        label_res = QLabel(f'Правильный ответ: {self.data[num - 1][3]}')
        label_res.setWordWrap(True)
        layout.addWidget(label_res)
        if str(self.data[num - 1][3]) == self.answers[num - 1]:
            label_res = QLabel(f'Введенный ответ: {self.answers[num - 1]}')
            label_res.setStyleSheet("color: rgb(0, 255, 0);")
            label_res.setWordWrap(True)
            layout.addWidget(label_res)
        else:
            label_res = QLabel(f'Введенный ответ: {self.answers[num - 1]}')
            label_res.setStyleSheet("color: rgb(255, 0, 0);")
            label_res.setWordWrap(True)
            layout.addWidget(label_res)
        groupBox.setLayout(layout)
        return groupBox

    def back_to_tasks(self):
        # возвращает обратно к списку тем задач
        self.tasks_wnd = Tasks()
        self.tasks_wnd.show()
        self.tasks_wnd.move(self.pos())
        self.close()


class Theory(Tasks):
    def __init__(self, name):
        super(Theory, self).__init__()
        uic.loadUi('theory.ui', self)
        # подгружаем дизайн
        self.name = name
        print(self.name)
        self.btn_endt.clicked.connect(self.back_to_main)
        self.set_text()

    def set_text(self):
        cur = con.cursor()
        command = f"""SELECT theory FROM theory, tasks_theme
                                                    WHERE id_theme = theme_id AND
                                                    task_var = '{self.name}'"""

        self.data = cur.execute(command).fetchall()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.create_ui_theory(self.data[0][0]))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents.setLayout(self.layout)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def create_ui_theory(self, name):
        layout = QVBoxLayout()
        print(name)
        label = QLabel(name)
        label.setWordWrap(True)
        label.setLayout(layout)
        return label


class Choose_theory(QMainWindow):
    # темы тестов
    def __init__(self):
        super().__init__()
        uic.loadUi('profs.ui', self)
        # подгружаем дизайн
        self.btn_mainp.clicked.connect(self.back_to_main)
        self.set_button()
        print('tasks')

    def open_themed_theory(self, text):
        # открытие теории
        self.themed_theory_window = Theory(text)
        self.themed_theory_window.show()
        self.themed_theory_window.move(self.pos())
        self.hide()

    def set_button(self):
        cur = con.cursor()
        command = f"""SELECT task_var FROM tasks_theme"""
        self.data = cur.execute(command).fetchall()
        self.layout = QVBoxLayout()
        for i, el in enumerate(self.data):
            self.layout.addWidget(self.create_ui_answer(el[0]))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents.setLayout(self.layout)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def create_ui_answer(self, name):
        layout = QVBoxLayout()
        button = QPushButton(name, self)
        button.setMinimumHeight(150)
        button.setMinimumWidth(200)
        button.setStyleSheet('background-color: rgb(145, 182, 182); border-width: 1px; border-radius: 15px;')
        button.clicked.connect(lambda x: self.open_themed_theory(name))
        button.setLayout(layout)
        return button

    def back_to_main(self):
        # вернуться в главное меню
        self.pos_wnd = Possibilities()
        self.pos_wnd.show()
        self.pos_wnd.move(self.pos())
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
