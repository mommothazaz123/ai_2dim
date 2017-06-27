# ai_2dim
2d machine learning

# How to run
First, clone the repo into a folder of your choice and install the requirements with `pip install -r requirements.txt`.  
Then, simply plug in a gamepad (Xbox controller works best), and run `python run.py`.  

### Requirements  
- Python 3.4+  
- A gamepad (Xbox controller works best)  

## What the program's doing

First, a window labelled `2D Point ROBOT` will appear. This is the machine learning step of the program.  
Click once to begin, and the computer will run it's learning step. After one minute, it will complete, and a window labelled `2D Point HUMAN` will appear.  
Here's where you come in. Click once, and use your gamepad to move the green dot to the black dot. Your movements will be recorded.  
After one minute, the program will compare your data to the robot's, and score you. It will also generate a file in `/data` detailing exactly how you compared to the computer.
Send that file to me at `machinelearning@avrae.io`!

### Difficulty

There are 3 different difficulty options (1, 2, or 3).  
Difficulty 1: Controls act as expected. (Joystick up = move up, etc.)  
Difficulty 2: Controls are randomized, but stay consistent. (Joystick up = move left, etc.)  
Difficulty 3: Controls are randomized, and randomize again every time a target is reached.
