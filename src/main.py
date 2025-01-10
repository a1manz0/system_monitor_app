import tkinter as tk
from tkinter import messagebox
import psutil
import sqlite3
import time


class SystemMonitorApp(tk.Tk):
    """
    Основной класс приложения вывода информации о загруженности
    процессора, озу и пзу
    """

    def __init__(self, db_file="resource_usage.db"):
        """
        Конструктор класса SystemMonitorApp.

        Инициализирует окно приложения и создает бд, если ее нет.

        Параметры:
            db_file(str): Имя файла базы данных для хранения данных.
            По умолчанию "resource_usage.db".
        """
        super().__init__()

        self.title("Системный монитор")
        self.configure(bg="black")

        self.is_recording = False
        self.db_file = db_file
        self.setup_database()

        # Интервал обновления данных в миллисекундах
        self.update_interval = 1000

        # Создаем и настраиваем метки для отображения уровней загруженности
        self.title_label = tk.Label(
            self,
            text="Уровень загруженности",
            font=("Helvetica", 12, "italic"),
            fg="white",
            bg="black",
        )
        self.cpu_label = tk.Label(
            self, font=("Helvetica", 12, "italic"), fg="white", bg="black"
        )
        self.ram_label = tk.Label(
            self, font=("Helvetica", 12, "italic"), fg="white", bg="black"
        )
        self.disk_label = tk.Label(
            self, font=("Helvetica", 12, "italic"), fg="white", bg="black"
        )

        # Размещаем метки в окне
        self.title_label.pack(anchor="nw", padx=10, pady=10)
        self.cpu_label.pack(anchor="nw", padx=10, pady=10)
        self.ram_label.pack(anchor="nw", padx=10, pady=10)
        self.disk_label.pack(anchor="nw", padx=10, pady=10)

        # Создаем рамку для кнопки
        button_frame = tk.Frame(self, bg="black", bd=20)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        # Кнопка для начала записи данных
        self.record_button = tk.Button(
            button_frame,
            text="Начать запись",
            command=self.start_recording,
            bg="black",
            fg="white",
        )
        self.record_button.pack()

        # Создаем метку для установки интервала обновления
        tk.Label(
            self,
            font=("Helvetica", 12, "italic"),
            fg="white",
            bg="black",
            text="Интервал обновления (сек):",
        ).pack(anchor="nw", padx=10, pady=10)

        # Поле ввода для установки интервала обновления
        self.interval_entry = tk.Entry(
            self,
            textvariable=tk.StringVar(value=int(self.update_interval / 1000)),
            width=23,
        )
        self.interval_entry.pack(anchor="nw", padx=10, pady=10)

        # Кнопка для установки нового интервала обновления
        self.set_interval_button = tk.Button(
            self,
            text="Установить интервал",
            command=self.set_update_interval,
            bg="black",
            fg="white",
        )
        self.set_interval_button.pack(side=tk.TOP, anchor="nw", padx=10, pady=10)

        # Запускаем функцию обновления метрик
        self.update_metrics()

    def update_metrics(self):
        """
        Обновляет значения загрузки ЦП, ОЗУ и ПЗУ и записывает
        значения в базу данных если пользователь начал запись

        Запускается каждые self.update_interval миллисекунд.
        """
        # Получаем нагруженность ЦП, ОЗУ, ПЗУ за последний интервал времени
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage("/").percent

        # Если запись включена, записываем данные в базу данных
        if self.is_recording:
            self.record_to_db(cpu_usage, ram_usage, disk_usage)

        # Обновляем текст меток с текущими значениями загрузки
        self.cpu_label.config(text=f"ЦП: {cpu_usage}%")
        self.ram_label.config(text=f"ОЗУ: {ram_usage}%")
        self.disk_label.config(text=f"ПЗУ: {disk_usage}%")

        # Запланировать следующий вызов обновления метрик через установленный интервал
        self.after(self.update_interval, self.update_metrics)

    def set_update_interval(self):
        """
        Устанавливает интервал обновления в миллисекундах.

        Исключения:
            ValueError: Если пользователь вводит некорректное значение
            интервала обновления (не положительное число или строку),
            выводится сообщение об ошибке через messagebox.
        """
        try:
            # Получаем значение из поля ввода и преобразуем его в целое число
            new_update_interval = int(self.interval_entry.get())

            # Проверяем, что значение больше или равно 1
            if new_update_interval < 1:
                raise ValueError("Значение не может быть < 1")

            # Устанавливаем новый интервал в миллисекундах
            self.update_interval = new_update_interval * 1000

            # Выводим сообщение об успешной установке интервала
            messagebox.showinfo(
                "Информация",
                f"Интервал обновления установлен на {int(new_update_interval)} секунд.",
            )
        except ValueError:
            # Показываем окно с ошибкой, если введено некорректное значение
            messagebox.showerror(
                "Ошибка", "Пожалуйста, введите целое положительное число"
            )

    def start_recording(self):
        """
        Запускает запись данных в базу данных

        """
        self.is_recording = True
        # Изменяем текст на кнопке и задаем команду остановки записи
        self.record_button.config(text="Остановить", command=self.stop_recording)

    def stop_recording(self):
        """
        Останавливает запись данных в базу данных
        """
        self.is_recording = False
        # Изменяем текст на кнопке и задаем команду для начала записи
        self.record_button.config(text="Начать запись", command=self.start_recording)

    def record_to_db(self, cpu, ram, disk):
        """
        Записывает данные о загрузке системы в базу данных.

        Параметры:
            cpu (float): Уровень загрузки CPU в процентах.
            ram (float): Уровень загрузки RAM в процентах.
            disk (float): Уровень загрузки диска в процентах.

        Исключения:
            sqlite3.Error: Если возникает ошибка при работе с базой данных.
        """
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            # Вставка данных о нагруженности в таблицу
            cursor.execute(
                "INSERT INTO usage (timestamp, cpu, ram, disk) VALUES (?, ?, ?, ?)",
                (time.strftime("%Y-%m-%d %H:%M:%S"), cpu, ram, disk),
            )
            db.commit()
        except sqlite3.Error as e:
            # Если возникает ошибка, останавливаем запись и отображаем сообщение
            self.is_recording = False
            self.record_button.config(
                text="Начать запись", command=self.start_recording
            )
            self.record_button.pack()
            messagebox.showerror("Ошибка", e)
        finally:
            cursor.close()
            db.close()

    def setup_database(self):
        """
        Настраивает бд для хранения данных о загруженности системы.

        Создает таблицу 'usage', если она еще не существует.

        Исключения:
            sqlite3.Error: Если возникает ошибка при работе с бд.
        """
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            # Создание таблицы, если она не существует
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS usage (
                                timestamp TEXT,
                                cpu REAL,
                                ram REAL,
                                disk REAL)"""
            )
            db.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", e)
        finally:
            cursor.close()
            db.close()


if __name__ == "__main__":
    app = SystemMonitorApp()
    app.mainloop()
