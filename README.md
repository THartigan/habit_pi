# HabitPi

A simple script for habit tracking using the raspberry pi sense hat.
- Blue pixel is your cursor.
 - Hover at the top left (0,0) and select by clicking the control stick down to turn on and off.
- Pixels starting from one to the right of the left edge on the top row denote days this week (red = no progress, orange = some progress, purple = complete, white=upcoming day)
 - Pixels on the rows immediately beneath the days row denote progress on habits for each day (red=incomplete, green=complete).
 - Pixels to the left of these habit rows show whether the habit has been successfully completed every day so far this week (off=incomplete, purple=streak alive!)
- Pixels starting from beneath these habit tracking rows (number of habit tracking rows = number of habits you want to track) show the completion in previous weeks if data exists for them. This should start to populate as you use the script more.
