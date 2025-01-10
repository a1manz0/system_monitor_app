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

        self.update_interval = 1000

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

        self.title_label.pack(anchor="nw", padx=10, pady=10)
        self.cpu_label.pack(anchor="nw", padx=10, pady=10)
        self.ram_label.pack(anchor="nw", padx=10, pady=10)
        self.disk_label.pack(anchor="nw", padx=10, pady=10)

        button_frame = tk.Frame(self, bg="black", bd=20)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.record_button = tk.Button(
            button_frame,
            text="Начать запись",
            command=self.start_recording,
            bg="black",
            fg="white",
        )
        self.record_button.pack()

        tk.Label(
            self,
            font=("Helvetica", 12, "italic"),
            fg="white",
            bg="black",
            text="Интервал обновления (сек):",
        ).pack(anchor="nw", padx=10, pady=10)
        self.interval_entry = tk.Entry(
            self,
            textvariable=tk.StringVar(value=int(self.update_interval / 1000)),
            width=23,
        )
        self.interval_entry.pack(anchor="nw", padx=10, pady=10)

        self.set_interval_button = tk.Button(
            self,
            text="Установить интервал",
            command=self.set_update_interval,
            bg="black",
            fg="white",
        )
        self.set_interval_button.pack(side=tk.TOP, anchor="nw", padx=10, pady=10)

        self.update_metrics()

    def update_metrics(self):
        """
        Обновляет значения загрузки ЦП, ОЗУ и диска и записывает
        значения в базу данных если пользователь начал запись

        Запускается каждые self.update_interval миллисекунд.
        """
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage("/").percent

        if self.is_recording:
            self.record_to_db(cpu_usage, ram_usage, disk_usage)

        self.cpu_label.config(text=f"ЦП: {cpu_usage}%")
        self.ram_label.config(text=f"ОЗУ: {ram_usage}%")
        self.disk_label.config(text=f"ПЗУ: {disk_usage}%")
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
            new_update_interval = int(self.interval_entry.get())
            if new_update_interval < 1:
                raise ValueError("Значение не может быть < 1")
            self.update_interval = new_update_interval * 1000
            messagebox.showinfo(
                "Информация",
                f"Интервал обновления установлен на {int(new_update_interval)} секунд.",
            )
        except ValueError:
            messagebox.showerror(
                "Ошибка", "Пожалуйста, введите целое положительное число"
            )

    def start_recording(self):
        """
        Запускает запись данных в базу данных

        """
        self.is_recording = True
        self.record_button.config(text="Остановить", command=self.stop_recording)

    def stop_recording(self):
        """
        Останавливает запись данных в базу данных
        """
        self.is_recording = False
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
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usage (timestamp, cpu, ram, disk) VALUES (?, ?, ?, ?)",
                (time.strftime("%Y-%m-%d %H:%M:%S"), cpu, ram, disk),
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.is_recording = False
            self.record_button.config(
                text="Начать запись", command=self.start_recording
            )
            self.record_button.pack()
            messagebox.showerror("Ошибка", e)

    def setup_database(self):
        """
        Настраивает бд для хранения данных о загруженности системы.

        Создает таблицу 'usage', если она еще не существует.

        Исключения:
            sqlite3.Error: Если возникает ошибка при работе с бд.
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS usage (
                                timestamp TEXT,
                                cpu REAL,
                                ram REAL,
                                disk REAL)"""
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", e)


if __name__ == "__main__":
    app = SystemMonitorApp()
    app.mainloop()
