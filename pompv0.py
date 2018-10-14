import tkinter as tk
from functools import wraps
import datetime
import webbrowser
import time
from datetime import datetime
import math

master = tk.Tk( "170x200+30+30")
master.title("Pompodoro")
master.geometry()




current_bottom_frame_row = iter(x for x in range(10))
current_bottom_frame_column = iter(x for x in range(10))

info_labels = (" Set :", "Now : ")

user_number_buttons = (
                "pomodoro duration",
                "pomodoros per long break",
                "regular break duration",
                "long break duration",
                )

values = (
           45,
            2,
            15,
            30,
         )


value_types = (
               tk.IntVar(),
               tk.IntVar(),
               tk.IntVar(),
               tk.IntVar(),
               )


activity_list =["activity 1", "activity 2", "activity 3", "activity 4..............................."
                ]


Paused = False
duration_of_this_states_previous_pauses = 0
previous_state = ""
starting_time = datetime.now()
current_time = datetime.now()
state_place_holder = 0


top_frame = tk.Frame(master)
middle_frame = tk.Frame(master)
bottom_frame = tk.Frame(master)

class HintLabel(tk.Label):
    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self._parent_name = self.winfo_parent()
        self._parent = self._nametowidget(self._parent_name)

    def place_hint_label(self):
        self.grid(
            row=next(current_bottom_frame_row),
            column=0)


class NumberController(tk.Button):
    def __init__(self, *args, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self.configure(command=self.just_clicked)
        self._parent_name = self.winfo_parent()
        self._parent = self._nametowidget(self._parent_name)
        self.grid(
                  row=0,
                  column=1 + next(current_bottom_frame_column)
                  )

    def display_button_text(self, text):
        self.config(text=text)

    def init_associated_value(self, associated_value=0, value_type=tk.IntVar()):
        self._tk_associated_value = value_type
        self._tk_associated_value.set(associated_value)

    def display_associated_value(self, *args, **kwargs):
        ## need to check type later
        if hasattr(self, '_Entry_Box'):
            if self._Entry_Box.get().isdigit():
                self._tk_associated_value.set(self._Entry_Box.get())
            self._Entry_Box.grid_remove()
            self.config(fg='black')
            del self._Entry_Box

        self._display = tk.Message(self._parent,
                                   text=str(self._tk_associated_value.get()))
        self._display.grid(
                           row=1,
                           column=self.grid_info()['column']
                           )


    def update(self):
        if hasattr(self, '_display'):
            self._display.grid_remove()
        self._Entry_Box = tk.Entry(self._parent, justify='center')
        self._Entry_Box.grid(
                             row=1,
                             column=self.grid_info()['column']
                             )
        self._Entry_Box.focus()
        self._Entry_Box.bind('<Return>', self.display_associated_value)

    def just_clicked(self):
        self.config(fg='red')
        self.update()

    # for the activity Button later
    def reconfig_command(self, command):
        self.configure(command=command)


class ActivityController(NumberController):
    def __init__(self, *args, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self.configure(command=self.select_new_or_old_activity)
        self._parent_name = self.winfo_parent()
        self._parent = self._nametowidget(self._parent_name)
        self.grid(
            row=0,
            column=1 + next(current_bottom_frame_column)
        )

    def init_associated_value(self, associated_value=activity_list[0], value_type=tk.StringVar()):
        self._tk_associated_value = value_type
        self._tk_associated_value.set(associated_value)


    def display_associated_value(self, *args, **kwargs):
        ## need to check type later
        if hasattr(self, '_Entry_Box'):
            self._tk_associated_value.set(self._Entry_Box.get())
            self._Entry_Box.grid_remove()
            self.config(fg='black')
            del self._Entry_Box
            if self._tk_associated_value.get() in activity_list:
                activity_list.remove(self._tk_associated_value.get())
            activity_list.insert(0, self._tk_associated_value.get())
        # for after a recent activity is chosen
        if hasattr(self, '_activities'):
            self._tk_associated_value.set(activity_list[self._activities.curselection()[0]])
            self._activities.grid_remove()
            del self._activities
            activity_list.remove(self._tk_associated_value.get())
            activity_list.insert(0, self._tk_associated_value.get())

        self._display = tk.Message(self._parent,
                                       text=str(self._tk_associated_value.get()))
        self._display.grid(
                row=1,
                column=self.grid_info()['column']
            )


    def select_new_or_old_activity(self):
        self._frame_for_selection = tk.Frame(self._parent)
        self._new_box_var = tk.IntVar()
        self._recent_box_var = tk.IntVar()
        self._new_box = tk.Checkbutton(self._frame_for_selection, text="Create new activity.",
                                        variable=self._new_box_var
                                        ).grid(row=0, column=0, sticky='w')
        self._recent_box = tk.Checkbutton(self._frame_for_selection, text="Choose recent activity.",
                                            variable=self._recent_box_var
                                            ).grid(row=1, column=0, sticky='w')
        self._okay_button = tk.Button(self._frame_for_selection, text="Continue",
                                    command=self.check_activity_box_option
                                    ).grid(row=2, column=0, sticky='w')
        self._frame_for_selection.grid(row=self._display.grid_info()['row'], sticky='w',
                                      column=self._display.grid_info()['column'])
        # self.grid_remove()
        self._display.grid_remove()

    def check_activity_box_option(self):
        row = self._frame_for_selection.grid_info()['row']
        column = self._frame_for_selection.grid_info()['column']
        parent = self._frame_for_selection._nametowidget(self._frame_for_selection.winfo_parent())
        self._frame_for_selection.grid_remove()
        if self._new_box_var.get() == 1:
            self.just_clicked()
        elif self._recent_box_var.get() == 1:
            self._activities = tk.Listbox(parent)
            for activity in activity_list:
                self._activities.insert(tk.END, activity)
            self._activities.grid(row=row, column=column)
            self._activities.bind('<Return>', self.get_old_chosen_activity)
            self._activities.bind('<Double-Button-1>', self.get_old_chosen_activity)
        else:
            self.display_associated_value()

    def get_old_chosen_activity(self,  *args, **kwargs):
        self.display_associated_value()


def make_labels():
    for label in info_labels:
            _label = HintLabel(bottom_frame, text=label)
            _label.place_hint_label()


def make_activity_setter():
    global activity_setter
    activity_setter = ActivityController(bottom_frame)
    activity_setter.init_associated_value()
    activity_setter.display_associated_value()
    activity_setter.display_button_text(text="    activity    ")


def make_number_controllers():
    global number_controller_dict
    number_controller_dict={}
    for i in range(len(user_number_buttons)):
        number_controller = NumberController(bottom_frame)
        number_controller.init_associated_value(associated_value=values[i],
                                                value_type=value_types[i])
        number_controller.display_button_text(text=user_number_buttons[i])
        number_controller.display_associated_value()
        number_controller_dict[user_number_buttons[i]] = number_controller

def make_frames():
    for frame in [top_frame, middle_frame, bottom_frame]:
        frame.pack()


def add_options_menu():
    main_menu = tk.Menu(master)
    master.config(menu=main_menu)
    options_menu = tk.Menu(main_menu)
    main_menu.add_cascade(label="Options", menu=options_menu)
    options_menu.add_command(label="Hide Settings", command=bottom_frame.pack_forget)
    options_menu.add_command(label="Show Settings", command=bottom_frame.pack)


class StartButton(tk.Button):
    def __init__(self, *args, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self._parent_name = self.winfo_parent()
        self._parent = self._nametowidget(self._parent_name)
        self.config(fg='black', text="START")
        self.grid(column=round(next(current_bottom_frame_column)/2)+1 )
        self.config(command=self.start_sequence)

    def start_sequence(self):
        self.grid_remove()
        self.pause_button = tk.Button(self._parent)
        self.pause_button.config(fg='black', text="PAUSE", command=self.pause)
        self.pause_button.grid(column=round(next(current_bottom_frame_column) / 2)+0 , row=3)
        self.restart_button = tk.Button(self._parent)
        self.restart_button.config(fg='black', text="RESTART", command=self.start_and_restart_additional_configuration)
        self.restart_button.grid(column=self.pause_button.grid_info()['column'], row=self.pause_button.grid_info()['row']+1)
        self.start_and_restart_additional_configuration()

    def start_and_restart_additional_configuration(self):
        global Paused
        Paused = False
        global starting_time
        starting_time = datetime.now()
        global state_place_holder
        state_place_holder = 0
        global duration_of_this_states_previous_pauses
        duration_of_this_states_previous_pauses = 0
        show_time_and_state()

    def pause(self):
        global Paused
        Paused = True
        self.pause_button.config(fg='black', text="UNPAUSE", command=self.unpause)
        global this_pause_start
        this_pause_start = datetime.now()


    def unpause(self):
        global Paused
        Paused = False
        self.pause_button.config(fg='black', text="PAUSE", command=self.pause)

        this_pause_end = datetime.now()
        global this_pause_start
        seconds_paused = (this_pause_end - this_pause_start).total_seconds()
        min_paused = int(math.floor(seconds_paused / 60))
        global duration_of_this_states_previous_pauses
        duration_of_this_states_previous_pauses += min_paused
        pass


def get_states_and_durations():
    pomoduro_duration = number_controller_dict['pomodoro duration']._tk_associated_value.get()
    pomodoros_per_long_break = number_controller_dict["pomodoros per long break"]._tk_associated_value.get()
    regular_break_duration = number_controller_dict["regular break duration"]._tk_associated_value.get()
    long_break_duration = number_controller_dict["long break duration"]._tk_associated_value.get()
    current_job = activity_setter._tk_associated_value.get()

    states_and_durations = []
    if pomodoros_per_long_break > 0 :
        for x in range(pomodoros_per_long_break - 1):
            states_and_durations.append([current_job, pomoduro_duration])
            states_and_durations.append(["Break", regular_break_duration])
        states_and_durations.append([current_job, pomoduro_duration])
        states_and_durations.append(["Long Break", long_break_duration])
    else:
        states_and_durations.append(["Long Break", long_break_duration])
    return states_and_durations


def control_state():
    global starting_time
    global state_place_holder
    global current_time
    global duration_of_this_states_previous_pauses
    global previous_state

    states_and_durations = get_states_and_durations()
    this_state_and_duration = states_and_durations[state_place_holder]
    this_state = this_state_and_duration[0]
    this_duration = int(this_state_and_duration[1])
    current_time = datetime.now()

    if Paused == True:
        return previous_state


    seconds_passed = (current_time - starting_time).total_seconds()         # still need to factor in pauses after
    min_passed = int(math.floor(seconds_passed / 60)) - duration_of_this_states_previous_pauses  # pauses factored in
    if min_passed >= this_duration:
        state_place_holder += 1
        state_place_holder = state_place_holder % len(states_and_durations)

        duration_of_this_states_previous_pauses = 0 # set time paused back to 0 for the next state
        starting_time = datetime.now()


    if this_duration-min_passed > 1:
        previous_state = this_state+" for "+ str(math.floor(this_duration-min_passed)) + " more minutes"
        return this_state+" for "+ str(math.floor(this_duration-min_passed)) + " more minutes"
    else:
        previous_state = this_state + " for  1 more minute"
        return this_state+" for  1 more minute"


add_options_menu()
make_labels()
make_activity_setter()
make_number_controllers()
make_frames()
StartButton(bottom_frame)


time_left = tk.Message(middle_frame, text= control_state())
earlier_control_state = control_state()

def show_time_and_state(message=time_left):
    global earlier_control_state
    if earlier_control_state != control_state():
        message.grid_remove()
    message.config(text = control_state())
    message.grid(row=1, column=1)
    earlier_control_state = control_state()
    master.after(2500, show_time_and_state)  #update every 2.5 seconds


master.mainloop()
