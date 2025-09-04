from sense_hat import SenseHat
from signal import pause
import numpy as np
from datetime import date, datetime, timedelta
import time

sense = SenseHat()


init_habit_names = ["sleep", "exercise", "read"]
save_file = "/home/thomas/habit_app/weeks.npy"
state_to_colour = {
    "day_complete": (159, 43, 104),
    "day_part_complete": (128,128,0),
    "day_incomplete": (255 ,0,0),
    "day_upcoming": (128,128,128),
    "habit_complete": (0, 128, 0),
    "habit_incomplete": (128,0,0),
    "habit_upcoming": (0,0,0),
    "week_streak_good": (159, 43, 104),
    "week_streak_bad": (0,0,0),
    "history_good": (159, 43, 104),
    "history_bad": (128,0,0),
    0: (255,0,0),
    1: (159, 43, 104),
    2: (128,128,0)
}

class Week():
    def __init__(self, begin_date, habit_names):
        self.habit_names = habit_names
        self.begin_date = begin_date
        self.days = []
        for day in range(0,7):
            self.days.append(Day(begin_date + timedelta(days=1*day), habit_names))
            

class Day():
    # Value of 0 for incomplete, value of 1 for complete, handle other cases dynamically
    def __init__(self, date, habit_names):
        self.date = date
        self.habits = {habit_name: 0 for habit_name in habit_names}

    def is_complete(self):
        values = [self.habits[k] for k in sorted(self.habits)]
        # print(values)
        if sum(values) == len(values):
            return 1
        elif sum(values)>0:
            return 2
        else:
            return 0

    def make_illum_column(self):
        column = []
        today = date.today()
        if self.date > today:
            upcoming = True
        else:
            upcoming = False
            
        if self.is_complete()==1:
            column.append("day_complete")
        elif self.is_complete()==2:
            column.append("day_part_complete")
        else:
            if upcoming:
                column.append("day_upcoming")
            else:
                column.append("day_incomplete")

        values = [self.habits[k] for k in self.habits]
        for value in values:
            if value == 0:
                if upcoming:
                    column.append("habit_upcoming")
                else:
                    column.append("habit_incomplete")
            if value == 1:
                column.append("habit_complete")

        print(column)
        
        colour_column = [state_to_colour[item] for item in column]
        print(colour_column)
        return colour_column
                
        
        
        

class LightGrid():
    def __init__(self, weeks):
        self.current_pos = np.array([0,0])
        self.shape = [8,8]
        sense.set_pixel(*self.current_pos, (0,0,255))
        sense.stick.direction_any = self.any_interaction
        self.weeks = weeks
        self.build_display()
        self.save_state()
        self.on = True

    def any_interaction(self, e):
        if e.action == "pressed":
            if e.direction == "up":
                index_edit = [0,-1]
            if e.direction == "down":
                index_edit = [0,1]
            if e.direction == "left":
                index_edit = [-1,0]
            if e.direction == "right":
                index_edit = [1,0]
            if e.direction == "middle":
                index_edit = [0,0]
                toggle = True
                print("do other stuff")
            else:
                toggle = False

            trial_pos = self.current_pos + np.array(index_edit)
            if trial_pos[0] >= 0 and trial_pos[0] < self.shape[0] and trial_pos[1] >= 0 and trial_pos[1] < self.shape[1]:
                old_pos = self.current_pos
                new_pos = self.current_pos + np.array(index_edit)
                self.update_display(old_pos, new_pos, toggle)
                self.current_pos += np.array(index_edit)
                # time.sleep(0.1)
                # sense.set_pixel(*self.current_pos, (0,0,255))
            print(self.current_pos)
            
            
            # print(e.direction)

    def check_week_streak(self):
        today = date.today()
        current_weekday = (today.weekday() - 0) % 7
        current_week = self.weeks[-1]
        num_week_habits = len(current_week.habit_names)
        week_habit_counts = np.zeros(num_week_habits)
        for day in current_week.days:
            values = [day.habits[k] for k in day.habits]
            week_habit_counts += np.array(values)
        streaking = []
        for week_habit_count in week_habit_counts:
            if week_habit_count >= current_weekday+1:
                streaking.append("week_streak_good")
            else:
                streaking.append("week_streak_bad")

        colour_column = [state_to_colour[streak_item] for streak_item in streaking]
        return colour_column

    def get_history(self):
        num_weeks_to_show = max(0, 8-1-len(self.weeks[-1].habit_names))
        start_row = 1+len(self.weeks[-1].habit_names) #0-indexed
        if num_weeks_to_show > 0:
            for week in range(1, num_weeks_to_show+1):
                try:
                    week_output = []
                    current_week = self.weeks[-1-week]
                    for day in current_week.days:
                        week_output.append(day.is_complete())
                    week_output_colours = [state_to_colour[day_output] for day_output in week_output]
                    for i, output_colour in enumerate(week_output_colours):
                        sense.set_pixel(i+1,start_row + week-1, output_colour)
                except:
                    print("didn't work")
                    
    def save_state(self):
        np.save(save_file, weeks)

    def week_check(self):
        today = date.today()
        offset = (today.weekday() - 0) % 7   # days since Monday
        this_monday = today - timedelta(days=offset)
        
        if len(weeks) == 0 or weeks[-1].begin_date != this_monday:
            this_week = Week(this_monday, init_habit_names)
            self.weeks.append(this_week)
                
    def build_display(self):
        #Check whether a new week started
        self.week_check()
        # sense.clear()
        current_week = weeks[-1]
        for i, day in enumerate(current_week.days):
            day_column = day.make_illum_column()
            for j, colour in enumerate(day_column):
                sense.set_pixel(i+1, j, colour)
        #streaks section
        streaks_column = self.check_week_streak()
        for j, colour in enumerate(streaks_column):
            sense.set_pixel(0, j+1, colour)
        #history section
        self.get_history()

        #saving
        self.save_state()
        
        

    def update_display(self, old_pos, new_pos, toggle):
        print(old_pos, new_pos)
        if old_pos.tolist() == new_pos.tolist() == [0,0]:
            if self.on == True:
                sense.clear()
                self.on  = False
                return
            else:
                self.on = True
                self.build_display()
                
        if old_pos[1] < len(self.weeks[-1].days[0].habits)+1:
            # In the recent week section
            if old_pos[0] > 0:
                day_num = old_pos[0]-1
                current_week = weeks[-1]
                selected_day = current_week.days[day_num]
                day_column = selected_day.make_illum_column()
                habit_value = day_column[old_pos[1]]
                if not toggle:
                    sense.set_pixel(*old_pos, habit_value)
                    # sense.set_pixel(*new_pos, (0,0,255))
                else:
                    selected_day_habit_keys = [k for k in selected_day.habits]
                    if new_pos[1]>0: #A habit was clicked indicating the habit was togled
                        current_habit_value = selected_day.habits[selected_day_habit_keys[new_pos[1]-1]]
                        if current_habit_value == 0:
                            selected_day.habits[selected_day_habit_keys[new_pos[1]-1]] = 1
                        elif current_habit_value == 1:
                            selected_day.habits[selected_day_habit_keys[new_pos[1]-1]] = 0
                    else: #The day indicator was clicked indicating the day was successful
                        for key in selected_day_habit_keys:
                            selected_day.habits[key] = 1
                    self.build_display()
                        
            else: #Week streaks section
                if old_pos [1] > 0:
                    streak_column = self.check_week_streak()
                    sense.set_pixel(*old_pos, streak_column[old_pos[1]-1])                    
                else: #Left (0,0)
                    sense.set_pixel(*old_pos, (0,0,0))
        else:
            start_row = 1+len(self.weeks[-1].habit_names)
            if old_pos[0] > 0: #In history section
                week_index = 2+(old_pos[1]-start_row)
                try:
                    week_of_interest = self.weeks[-week_index]
                    day = week_of_interest.days[old_pos[0]-1]
                    if toggle:
                        selected_day_habit_keys = [k for k in day.habits]
                        for key in selected_day_habit_keys:
                            day.habits[key] = 1
                        self.build_display()
                    sense.set_pixel(*old_pos, state_to_colour[day.is_complete()])
                except:
                    print("No corresponding day")
                    sense.set_pixel(*old_pos, (0,0,0))
            else:
                sense.set_pixel(*old_pos, (0,0,0))
                        
            # 
        sense.set_pixel(*new_pos, (0,0,255))
                
            
            
        
     
try:
    weeks = np.load(save_file, allow_pickle=True) 
except:
    print("No saved data")
    weeks = []
    

today = date.today()
offset = (today.weekday() - 0) % 7   # days since Monday
this_monday = today - timedelta(days=offset)

if len(weeks) == 0 or weeks[-1].begin_date != this_monday:
    this_week = Week(this_monday, init_habit_names)
    weeks.append(this_week)

# def make_prior_test_weeks(current_monday, habit_names, n=3, seed=42,
#                           p_complete_by_day=(0.6, 0.65, 0.7, 0.6, 0.75, 0.8, 0.7)):
#     """
#     Generate n full weeks immediately before current_monday.
#     Each habit for each past day is a Bernoulli draw with weekday-dependent p.
#     Returns a list of Week objects in chronological order (oldest → newest).
#     """
#     rng = np.random.default_rng(seed)
#     prior_weeks = []
#     for k in range(n, 0, -1):  # n weeks ago ... 1 week ago
#         w = Week(current_monday - timedelta(days=7*k), habit_names)
#         for d, day in enumerate(w.days):  # d = 0..6 (Mon..Sun)
#             p = p_complete_by_day[d]
#             for h in day.habits:
#                 day.habits[h] = int(rng.random() < p)
#         prior_weeks.append(w)
#     return prior_weeks


# weeks = make_prior_test_weeks(this_monday, init_habit_names, n=4, seed=1) + weeks
sense.clear()
lg = LightGrid(weeks)

print("Listening. Ctrl+C to exit.")
try:
    pause()
except KeyboardInterrupt:
    pass