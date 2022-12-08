# Experiment on a useful MVC architecture for TKinter.
# Pascal Hurni, december 2022
# Based on concepts described in https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller

# Widgets are of two kinds:
#  - View widgets: they only display data that comes from the model.
#    Their responsibility is to present the model in a user friendly way.
#    They need to be fed with the model object. They may subscribe to the model changes.
#  - Action widgets: they will receive user interactions to mutate data.
#    They do not display a representation of the data.
#    They need to be fed with the appropriate controller.
#
# (Mvc) Models have no reference to anything. They may have subscribers that want to be notified when they change
#       but they have no direct knowing that Widgets or Controllers exist.
# (mvC) Controllers only have references to models, they have no reference on widgets.
# (mVc) View widgets have references on the models to display their data.
# (mVc) Action widgets have references on the controllers to propagate user actions.

import tkinter as tk
from tkinter import ttk

class Observable:
    """
    Generic observable behaviour
    """
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


# This is a View kind widget
class ScoreViewWidget(ttk.Frame):
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

    def on_model_changed(self, model):
        self.score_label.config(text=str(model.value))


# This is an Action kind widget
class ScoreUpdaterWidget(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.increment_button = ttk.Button(self, text="+", command=self.increment)
        self.increment_button.grid(row=0, column=0)
        self.decrement_button = ttk.Button(self, text="-", command=self.decrement)
        self.decrement_button.grid(row=0, column=1)

    def increment(self):
        self.controller.increment()

    def decrement(self):
        self.controller.decrement()


# This is a View kind widget
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


# This is an Action kind widget
class UserEditWidget(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
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
        self.controller.save(self.firstname_entry.get(), self.lastname_entry.get(), self.email_entry.get())
        self.firstname_entry.delete(0, tk.END)
        self.lastname_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)


# This is a hybrid kind widget!!!
# It is a View kind widget because it displays the score in the Entry and it updates the Entry value when the score changes from the outside
# It is an Action widget because when the user enters a new value in the Entry and goes to another widget (focus-out) the score is updated with this value
class ScoreEditWidget(ttk.Frame):
    def __init__(self, parent, model, controller):
        super().__init__(parent)
        self.model = model
        self.controller = controller
        
        # bind
        self.model.subscribe(self.on_model_changed)

        # create widgets
        label = ttk.Label(self, text='Score:')
        label.grid(row=0, column=0, sticky=tk.W)

        self.score_value = tk.StringVar(value=str(self.model.value))
        self.score_entry = ttk.Entry(self, textvariable=self.score_value, width=10, validate="focusout", validatecommand=self.on_score_entry_changed)
        self.score_entry.grid(row=0, column=1, sticky=tk.W)

    def on_model_changed(self, model):
        self.score_value.set(str(model.value))

    def on_score_entry_changed(self):
        try:
            self.controller.try_change_value(int(self.score_value.get()))

        except ValueError as error:
            pass
        
        return True


class ScoreController:
    def __init__(self, model):
        self.model = model
        
    def increment(self):
        self.model.value += 1

    def decrement(self):
        self.model.value -= 1

    def try_change_value(self, new_value):
        self.model.value = new_value
    

class UserController:
    def __init__(self, model):
        self.model = model
        
    def save(self, firstname, lastname, email):
        self.model.firstname = firstname
        self.model.lastname = lastname
        self.model.email = email
        self.model.save()
    

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Tkinter UsefullMVC Demo')

        # create the models
        score = Score(3)
        user = User()

        # create a single score controller linked to the model
        score_controller = ScoreController(score)
        # create all score related widgets using the same controller
        widget = ScoreEditWidget(self, score, score_controller)
        widget.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
        widget = ScoreViewWidget(self, score)
        widget.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        widget = ScoreUpdaterWidget(self, score_controller)
        widget.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # create user controller and widgets
        user_controller = UserController(user)
        widget = UserViewWidget(self, user)
        widget.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
        widget = UserEditWidget(self, user_controller)
        widget.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)


if __name__ == '__main__':
    app = App()
    app.mainloop()
