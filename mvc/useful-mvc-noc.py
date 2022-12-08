# Experiment on a useful MVC architecture for TKinter.
# Pascal Hurni, december 2022
# Based on concepts described in https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller

# This version has no Controllers! Models are linked directly to Widgets and vice-versa.
#
# (Mvc) Models have no reference to anything. They may have subscribers that want to be notified when they change
#       but they have no direct knowing that Widgets or Controllers exist.
# (mVc) Widgets have references on the models to display their data and to mutate their state.

import tkinter as tk
from tkinter import ttk

class Observable:
    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer(self, *args, **kwargs)

    def unsubscribe(self, observer):
        self._observers.remove(observer)


class Score(Observable):
    def __init__(self, value):
        Observable.__init__(self)
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value
        print(f"Score#value=: {value}")

        self.notify_observers()


class User(Observable):
    def __init__(self):
        Observable.__init__(self)

    @property
    def firstname(self):
        return self.__firstname

    @firstname.setter
    def firstname(self, value):
        self.__firstname = value

    @property
    def lastname(self):
        return self.__lastname

    @lastname.setter
    def lastname(self, value):
        self.__lastname = value

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        self.__email = value
        
    def save(self):
        # Do whatever should be done to persist this user
        print(f"User#save(): {self.firstname} {self.lastname} {self.email}")

        self.notify_observers()


class ScoreEditWidget(ttk.Frame):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        
        # bind
        self.model.subscribe(self.on_model_changed)

        # create widgets
        label = ttk.Label(self, text='Score:')
        label.grid(row=1, column=0, sticky=tk.W)

        self.score_value = tk.StringVar(value=str(self.model.value))
        self.score_entry = ttk.Entry(self, textvariable=self.score_value, width=10, validate="focusout", validatecommand=self.on_score_entry_changed)
        self.score_entry.grid(row=1, column=1, sticky=tk.W)

    def on_model_changed(self, model):
        self.score_value.set(str(model.value))

    def on_score_entry_changed(self):
        try:
            self.model.value = int(self.score_value.get())

        except ValueError as error:
            pass
        
        return True


class ScoreUpdateWidget(ttk.Frame):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        
        # bind
        self.model.subscribe(self.on_model_changed)

        # create widgets
        label = ttk.Label(self, text='Score:')
        label.grid(row=0, column=0, sticky=tk.W)

        self.score_label = ttk.Label(self, text=str(self.model.value))
        self.score_label.grid(row=0, column=1, sticky=tk.W)

        self.increment_button = ttk.Button(self, text="+", command=self.increment)
        self.increment_button.grid(row=0, column=2, sticky=tk.W)
        self.decrement_button = ttk.Button(self, text="-", command=self.decrement)
        self.decrement_button.grid(row=0, column=3, sticky=tk.W)

    def on_model_changed(self, model):
        self.score_label.config(text=str(model.value))

    def increment(self):
        self.model.value += 1

    def decrement(self):
        self.model.value -= 1


class UserViewWidget(ttk.Frame):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        
        # bind
        self.model.subscribe(self.on_model_changed)

        # create widgets
        label = ttk.Label(self, text='User:')
        label.grid(row=0, column=0, sticky=tk.W)

        self.user_label = ttk.Label(self)
        self.user_label.grid(row=0, column=1, sticky=tk.W)

    def on_model_changed(self, model):
        self.user_label.config(text=self.format_user(model))
        
    def format_user(self, model):
        return f"{model.firstname} {model.lastname.upper()} ({model.email})"


class UserEditWidget(ttk.Frame):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        
        # create widgets
        label = ttk.Label(self, text='Firstname:')
        label.grid(row=0, column=0, sticky=tk.W)
        self.firstname_entry = ttk.Entry(self)
        self.firstname_entry.grid(row=0, column=1, sticky=tk.W)

        label = ttk.Label(self, text='Lastname:')
        label.grid(row=1, column=0, sticky=tk.W)
        self.lastname_entry = ttk.Entry(self)
        self.lastname_entry.grid(row=1, column=1, sticky=tk.W)

        label = ttk.Label(self, text='Email:')
        label.grid(row=2, column=0, sticky=tk.W)
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=2, column=1, sticky=tk.W)

        self.save_button = ttk.Button(self, text="Save", command=self.on_save_button_clicked)
        self.save_button.grid(row=3, column=1, sticky=tk.E)

    def on_save_button_clicked(self):
        self.model.firstname = self.firstname_entry.get()
        self.model.lastname = self.lastname_entry.get()
        self.model.email = self.email_entry.get()
        self.model.save()

        self.firstname_entry.delete(0, tk.END)
        self.lastname_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Tkinter UsefullMVC Demo')

        # create the models
        score = Score(3)
        user = User()

        # create all score related widgets using the same model
        widget = ScoreEditWidget(self, score)
        widget.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        widget = ScoreUpdateWidget(self, score)
        widget.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        # create user widgets
        widget = UserViewWidget(self, user)
        widget.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
        widget = UserEditWidget(self, user)
        widget.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)


if __name__ == '__main__':
    app = App()
    app.mainloop()
