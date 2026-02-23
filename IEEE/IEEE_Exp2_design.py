## Copyrighted by ViiVAI Labs and Studio 2025

## __Milano_Exp2_design: 

# ''' HAPTIC CANVAS FOR SERIAL API

###################################################
### File generated: 02 October 2025             ########
''' 


'''
###################################################
''' 
Last update: 05 October 2025
reviewed: 12 December 2025
'''

###################################################
from types import SimpleNamespace

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkvideo import tkvideo 
from tkinter.filedialog import askopenfilename, asksaveasfilename
import cv2
from PIL import Image, ImageTk
import json, csv
import time, threading
import math, os, re
import serial
import serial.tools.list_ports
import numpy as np
import pandas as pd
from pythonosc import udp_client
import matplotlib.pyplot as plt

from IEEE_CRHapticDriver import CR_RP2040W
from IEEE_HapticHardware import setupHapticDictionary
from IEEE_HapticHardware import map_linearhaptics, barycentricLinear, barycentricEnergy
from IEEE_HapticHardware import bilinearLinear, bilinearEnergy
from IEEE_HapticHardware import sendUDPamplitude, sendUDPparameter


class ExpDrawingApp:
    def __init__(self, master, Haptics_is_ON=False):
        self.master = master
        self.Haptics_is_ON = Haptics_is_ON

        # study parameters
        self.user = "Please Enter your ID"
        
        # device dictionary
        self.deviceDict = ''
        self.framesize = SimpleNamespace(x=0, y=0, w=800, h=360)
        self.channels = 6
        self.act = np.zeros(self.channels)
        self.circle_positions = [] ## to store actuator center for animation in layout

        ## Define start and end points
        self.start_point = (50, 50)
        self.end_point = (150, 200)
        self.pps = 300

        # Drawing variables
        self.current_color = "#000000"  # Default to black
        self.current_thickness = 1
        self.circle_radius = 20

        # time variables
        self.start_time = time.time()

        ## ------------------------------------
        # # --- LEFT FRAME ---
        self.left_frame = tk.Frame(self.master)
        self.left_frame.pack(side='left')
        
        # -- check box to rendering schemes ---
        self.chbox_frame = tk.Frame(self.left_frame, bg="lightblue")
        self.chbox_frame.pack()

        self.checkbox1Var=tk.BooleanVar()
        self.checkbox1=tk.Checkbutton(self.chbox_frame, text="Barycentric", variable=self.checkbox1Var)
        self.checkbox1.pack(side='left')
        self.checkbox1Var.set(1)

        self.checkbox2Var=tk.BooleanVar()
        self.checkbox2=tk.Checkbutton(self.chbox_frame, text="Energy Rendering", variable=self.checkbox2Var)
        self.checkbox2.pack()
        self.checkbox2Var.set(1)

        ## -- Middle Frame ----
        self.middle_frame = tk.Frame(self.left_frame, bg="lightblue")
        self.middle_frame.pack()

        # -- Drawing Canvas ---
        self.canvas_frame = tk.Frame(self.middle_frame, bg="lightblue")
        self.canvas_frame.pack(side='left')

        self.canvas = tk.Canvas(self.canvas_frame, width=self.framesize.w, height=self.framesize.h, bg="white")
        self.canvas.pack(pady=10, side='left')
        self.canvas.bind("<Button-1>", self.start_drawing)  # Bind left-click to start drawing
        self.canvas.bind("<B1-Motion>", self.draw)  # Bind mouse drag with left button down
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)  # Bind left-click release

        ## -- text box ---
        self.user_text = tk.StringVar()
        self.user_text.set(self.user)
        self.textbox1  = tk.Entry(self.left_frame, textvariable=self.user_text)
        self.textbox1.pack()

        # --- RIGHT FRAME ---
        self.right_frame = tk.Frame(self.master)
        self.right_frame.pack(side='left')

        ## sliders and labels
        tk.Label(self.right_frame, text="pps").grid(row=0, column=0, pady=0)
        self.slider_pps=tk.Scale(self.right_frame, from_=100, to=1200, resolution=10, length=200, orient=tk.HORIZONTAL, command=self.on_pps)
        self.slider_pps.grid(row=0, column=1, columnspan=2, pady=0)#,
        self.slider_pps.set(self.pps)
        tk.Label(self.right_frame, text="size").grid(row=1, column=0, pady=0)
        self.slider_radius=tk.Scale(self.right_frame, from_=10, to=50, resolution=10, length=200, orient=tk.HORIZONTAL, command=self.on_radius)
        self.slider_radius.grid(row=1, column=1, columnspan=2, pady=0)#, length=200)
        self.slider_radius.set(self.circle_radius)
        
        tk.Label(self.right_frame, text="enter the starting and fininshing points").grid(row=2, column=0, columnspan=3, pady=0)
        tk.Label(self.right_frame, text="x").grid(row=3, column=1, pady=0)
        tk.Label(self.right_frame, text="y").grid(row=3, column=2, pady=0)
        tk.Label(self.right_frame, text="start point").grid(row=4, column=0, pady=0)
        self.slider_startx=tk.Scale(self.right_frame, from_=0, to=self.framesize.w, orient=tk.HORIZONTAL, command=self.on_startx)
        self.slider_startx.grid(row=4, column=1, pady=0)
        self.slider_startx.set(self.start_point[0])
        self.slider_starty=tk.Scale(self.right_frame, from_=0, to=self.framesize.h, orient=tk.HORIZONTAL, command=self.on_starty)
        self.slider_starty.grid(row=4, column=2, pady=0)
        self.slider_starty.set(self.start_point[1])

        tk.Label(self.right_frame, text="end point").grid(row=5, column=0, pady=5)
        self.slider_endx=tk.Scale(self.right_frame, from_=0, to=self.framesize.w, orient=tk.HORIZONTAL, command=self.on_endx)
        self.slider_endx.grid(row=5, column=1, pady=0)#
        self.slider_endx.set(self.end_point[0])
        self.slider_endy=tk.Scale(self.right_frame, from_=0, to=self.framesize.h, orient=tk.HORIZONTAL, command=self.on_endy)
        self.slider_endy.grid(row=5, column=2, pady=0)
        self.slider_endy.set(self.end_point[1])

        # Create play button
        self.play_button = tk.Button(self.right_frame, text='play', width=15, command=self.on_button_press)
        self.play_button.grid(row=8, column=0, columnspan=3, pady=10)
        
        ## ------------------------------------
        ## Create the circle at the starting point
        self.circle = self.canvas.create_oval(self.start_point[0] - self.circle_radius, self.start_point[1] - self.circle_radius,
                                self.start_point[0] + self.circle_radius, self.start_point[1] + self.circle_radius,
                                fill="blue", outline="darkblue")
        
        self.red_circle = self.canvas.create_oval(self.start_point[0] - 2, self.start_point[1] - 2,
                                self.start_point[0] + 2, self.start_point[1] + 2,
                                fill="red", outline="maroon")

        self.rectangle = self.canvas.create_rectangle(self.start_point[0], self.start_point[1], self.end_point[0], self.end_point[1], 
                                            outline="blue", dash=(5, 3), fill="")
    
    ## receive callback from Master App
    def update_callback(self, mtype=1):
        if mtype == 1:
            # print('#'*10)
            self.framesize = self.deviceDict['frame border']
            self.channels = self.deviceDict['channels']
            self.act = np.zeros(self.deviceDict['channels'])
            self.actuator_type = self.deviceDict['actuator_type']
            self.act_size = self.deviceDict['actuator_size']
            
            self.canvas.config(width=self.framesize.w, height=self.framesize.h)
            self.slider_startx.config(to=self.framesize.w)
            self.slider_starty.config(to=self.framesize.h)
            self.slider_endx.config(to=self.framesize.w)
            self.slider_endy.config(to=self.framesize.h)

            # print('#'*10)
            # print('Haptic Canvas Device Ready', self.deviceDict['device_type'])
            # print('Haptic Canvas: channels are: ', self.channels, ' and ', self.act)
            # print(f'Haptic Canvas frame: {self.framesize}')
            self.clear_canvas()

    # --- Canvas free hand drawing functions ---
    def start_drawing(self, event):
        self.clear_canvas()
        self.Haptics_is_ON = True

        x, y = event.x, event.y
        radius = 40

        ## draw mouse circle
        self.mouse_circle=self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill=self.current_color, outline='black')
        ## RENDER HAPTICS HERE
        player_pos = SimpleNamespace(x=x, y=y)
        act = self.set_actuators(player_pos=player_pos, line_thickness=self.current_thickness)
        self.update_act_size(act, reset=1)
        self.update_act_size(act, reset=0)

    def draw(self, event):
        timestamp = time.time() - self.start_time  # Time relative to starting draw
        x, y = event.x, event.y
        radius = 40
        
        ## draw mouse circle
        self.canvas.coords(self.mouse_circle, x-radius, y-radius, x+radius, y+radius)
        ## RENDER HAPTICS HERE
        player_pos = SimpleNamespace(x=x, y=y)
        act = self.set_actuators(player_pos=player_pos, line_thickness=self.current_thickness)
        self.update_act_size(act, reset=0)

    def stop_drawing(self, event):
        # store last value to capture hold time
        x, y = event.x, event.y
        timestamp = time.time() - self.start_time  # Time relative to starting draw
        self.Haptics_is_ON = False
        
        self.act = np.zeros(self.channels)
        
        # self.clear_canvas()
        self.update_act_size(self.act, reset=0)
        self.canvas.coords(self.mouse_circle, 0, 0, 0, 0)

    ## set actuator values (Barycentric rendering)
    def set_actuators(self, player_pos, line_thickness=1):
        act = np.zeros(self.channels) ## 
        amplitude = 1000

        if player_pos.x<0.001: player_pos.x=0.001
        if player_pos.x>self.framesize.w-0.001: player_pos.x=self.framesize.w-0.001

        if player_pos.y<0.001: player_pos.y=0.001
        if player_pos.y>self.framesize.h-0.001: player_pos.y=self.framesize.h-0.001
        
        if self.checkbox2Var.get(): ## enery mapping check
            if self.checkbox1Var.get(): ## barycenter check
                result, act = barycentricEnergy(act, self.deviceDict['act_layout'], self.deviceDict['tri_layout'], [player_pos.x, player_pos.y])
            else: ## bilinear
                result, act = bilinearEnergy(act, self.deviceDict['act_layout'], self.deviceDict['rect_layout'], [player_pos.x, player_pos.y])
        else: ## linear mapping
            if self.checkbox1Var.get(): ## barycenter check
                result, act = barycentricLinear(act, self.deviceDict['act_layout'], self.deviceDict['tri_layout'],[player_pos.x, player_pos.y])
            else: ## bilinear
                result, act = bilinearLinear(act, self.deviceDict['act_layout'], self.deviceDict['rect_layout'], [player_pos.x, player_pos.y])
        
        if result == "Outside": 
            print("Point is outside the grid", player_pos, result)
        else: # set act intensity levels
            match (line_thickness):
                case 1:  amplitude = 1000
                case 10:  amplitude = 600
                case 20:  amplitude = 700
                case 30:  amplitude = 800
                case 40:  amplitude = 900
                case 50:  amplitude = 1000
                case _:  amplitude = 0

            self.Haptics_is_ON = False
            for i in range(self.channels):
                act[i]=act[i]*amplitude
                if act[i]>999: act[i]=999
                self.act[i]=int(act[i])
            self.Haptics_is_ON = True
        
        return act

    ## Grid layout + visual animation 
    def draw_layout(self):
        # #canvas, framesize, act_layout, tri_layout, act_size=20):
        # # print(len(tri_layout.tolist()))
        tlayout = self.deviceDict['tri_layout'].tolist()

        for i in tlayout:#tri_layout:
            self.canvas.create_polygon(i, outline="lightgrey", fill="", width=0.5)

        off = self.act_size/2
        for i in self.deviceDict['act_layout']:
            self.canvas.create_oval(i[0]-off, i[1]-off, i[0]+off, i[1]+off, fill='lightblue', outline='black')

    def init_act_grid(self, act_size=10):
        self.circle_positions = []
        off = act_size/2
        for i in self.deviceDict['act_layout']:
            cid=self.canvas.create_oval(i[0]-off, i[1]-off, i[0]+off, i[1]+off, fill='red', outline='black')
            self.circle_positions.append((cid, (i[0],i[1])))   

    def update_act_size(self, act, act_min=10, act_max=100, reset=0):
        # new_diameter = float(val)
        if reset:
            off = 5
            for index, (circle_id, (x, y)) in enumerate(self.circle_positions):
                self.canvas.coords(circle_id, x-off, y-off, x+off, y+off)
        else:
            for index, (circle_id, (x, y)) in enumerate(self.circle_positions):
                # Calculate new coordinates for the oval based on the act amplitude
                x0 = x - act[index]/4 / 3
                y0 = y - act[index]/4 / 3
                x1 = x + act[index]/4 / 3
                y1 = y + act[index]/4 / 3
                self.canvas.coords(circle_id, x0, y0, x1, y1)

    ## moving circle
    def draw_circle(self):
        self.circle = self.canvas.create_oval(self.start_point[0] - self.circle_radius, self.start_point[1] - self.circle_radius,
                                self.start_point[0] + self.circle_radius, self.start_point[1] + self.circle_radius, fill="blue", outline="darkblue")

        self.red_circle = self.canvas.create_oval(self.start_point[0] - 2, self.start_point[1] - 2,
                                self.start_point[0] + 2, self.start_point[1] + 2,
                                fill="red", outline="maroon")
        
        self.rectangle = self.canvas.create_rectangle(self.start_point[0], self.start_point[1], self.end_point[0], self.end_point[1], 
                                            outline="blue", dash=(5, 3), fill="")
    
    def redraw_circle(self):
        self.canvas.coords(self.circle, self.start_point[0] - self.circle_radius, self.start_point[1] - self.circle_radius,
                                self.start_point[0] + self.circle_radius, self.start_point[1] + self.circle_radius)
        self.canvas.coords(self.red_circle, self.start_point[0] - 2, self.start_point[1] - 2,
                                self.start_point[0] + 2, self.start_point[1] + 2)
        self.canvas.coords(self.rectangle, self.start_point[0], self.start_point[1], self.end_point[0], self.end_point[1])
        
    def on_pps(self, value):
        self.pps = int(value)

    def on_radius(self, value):
        self.circle_radius = int(value)
        self.redraw_circle()
    
    def on_startx(self, value):
        self.start_point = (int(value),) + self.start_point[1:]
        self.redraw_circle()

    def on_starty(self, value):
        self.start_point = (self.start_point[0], int(value))
        self.redraw_circle()

    def on_endx(self, value):
        self.end_point = (int(value),) + self.end_point[1:]
        self.redraw_circle()
        pass

    def on_endy(self, value):
        self.end_point = (self.end_point[0], int(value))
        self.redraw_circle()
        pass

    def on_button_press(self):

        self.redraw_circle()
        self.move_circle_to_point(self.canvas, self.circle, self.start_point[0], self.start_point[1], self.end_point[0], self.end_point[1], self.pps)

    def move_circle_to_point(self, canvas, circle_id, start_x, start_y, end_x, end_y, speed_pps):
        """
        Moves a circle on a Tkinter canvas from a starting point to an ending point
        at a specified speed in pixels per second.
        """
        self.current_x, self.current_y = start_x, start_y
        # self.current_x, self.current_y, _, _ = canvas.coords(circle_id) # Get current coordinates of the circles
        # print(self.current_x, self.current_y)
        # turn haptics on 
        self.act = np.zeros(self.channels)
        self.Haptics_is_ON = True
        
        # Calculate displacement
        dx = end_x - start_x
        dy = end_y - start_y
        # Calculate distance
        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0: # Already at the destination
            return

        # Calculate time needed for the move
        time_needed_seconds = distance / speed_pps
        
        # Define update interval (e.g., 20 milliseconds for smooth animation)
        update_interval_ms = 20
        
        # Calculate number of steps
        num_steps = int(time_needed_seconds * (1000 / update_interval_ms))

        if num_steps == 0: # Handle cases where the distance is too small for multiple steps
            canvas.move(circle_id, dx, dy)
            return

        ## Calculate step size
        step_dx = dx / num_steps
        step_dy = dy / num_steps


        def animate_step(step_count):
            if step_count < num_steps:
                self.current_x += step_dx
                self.current_y += step_dy
                canvas.move(circle_id, step_dx, step_dy)
                canvas.coords(self.red_circle,self.current_x-2,self.current_y-2,self.current_x+2,self.current_y+2)

                player_pos = SimpleNamespace(x=self.current_x, y=self.current_y)
                act = self.set_actuators(player_pos=player_pos, line_thickness=self.circle_radius)
                self.update_act_size(act, reset=0)
                canvas.after(update_interval_ms, animate_step, step_count + 1)
            else:
                # Ensure the circle ends exactly at the target point
                final_dx = end_x - (canvas.coords(circle_id)[0] + (canvas.coords(circle_id)[2] - canvas.coords(circle_id)[0]) / 2)
                final_dy = end_y - (canvas.coords(circle_id)[1] + (canvas.coords(circle_id)[3] - canvas.coords(circle_id)[1]) / 2)
                self.Haptics_is_ON = False
                self.act = np.zeros(self.channels)
                self.update_act_size(self.act, reset=0)
                # canvas.move(circle_id, final_dx, final_dy)
                # canvas.move(circle_id, step_dx, step_dy)
        ## start animation
        animate_step(0)

    ## clear canvas and draw the layout
    def clear_canvas(self):
        self.canvas.delete("all")  # Deletes all items on the canvas
        self.draw_layout()
        self.init_act_grid()
        self.draw_circle()
        pass

# # Example usage:
# if __name__ == "__main__":
#     root = tk.Tk()
#     # root.geometry("660x800")
#     app = ExpDrawingApp(root)
#     root.mainloop()



###################################################
### Last update: 08 August 2025             ########
''' DEMO of MAIN TOOL (VIDEO PLAY, CANVAS, PATTERNS)
    1. plays video TkInter and cv2 in loop; pause, play and reset.
    2. Videoplayer tab as a class (commented)
    3. Haptic Canvas (color, thickness, save, replay)
    4. Shape Canvas (commented, for refernce only)
    5. Haptic Pattern Tool (libraries, editing, saving)
'''
###################################################

class TabbedApplication:
    def __init__(self, master):
        
        master.title("Haptic Playground")
        self.master = master
        # self.video_source = "video.mp4"
        self.master.protocol("WM_DELETE_WINDOW", self.destructor)
        self.Haptics_is_ON = False
        self.haptic_rate = 0.01
        self.framesize = SimpleNamespace(x=0, y=0, w=200, h=200)
        self.last_time=time.time()
        self.hchannels = 2
        self.act = np.zeros(self.hchannels)
        self.range = (0, 1)
        self.porttype = ''
        self.frequency, self.modulation = 200, 20

        ## Common frame for buttons, serial list for all table
        self.common_frame = tk.Frame(self.master)
        self.common_frame.pack(side="top", pady=20, padx=20)

        ## frame to set buttons on one end in a column
        self.button_frame = tk.Frame(self.common_frame)
        self.button_frame.pack(side="left", pady=5, padx=0)

        ## --- Haptic Toggle button ---
        self.toggle_button = tk.Button(self.button_frame, text="Haptic is OFF", relief="raised", command=self.toggle_hapticbutton_state)
        self.toggle_button.pack(side='top', pady=5)
        ## --- Export button ---
        self.export_button = tk.Button(self.button_frame, text="Export", relief="raised", command=self.export_hapticfile)
        self.export_button.pack(side='top', pady=5)
        ## --- ch box for baseline adjustment ---
        self.checkboxBaseVar=tk.BooleanVar()
        self.checkboxBase=tk.Checkbutton(self.button_frame, text="Baseline adjustment", variable=self.checkboxBaseVar)
        self.checkboxBase.pack()
        self.checkboxBaseVar.set(0)

        ## --- common frame for combo lists
        self.right_common_frame = tk.Frame(self.common_frame)
        self.right_common_frame.pack(side="left", pady=5, padx=0)
        ## --- refresh button
        tk.Button(self.right_common_frame, text="Refresh", command=self.refresh_ports).pack(side='top', pady=5)
        ## --- Combobox for port selection
        self.port_selector = ttk.Combobox(self.right_common_frame, state="readonly", width=25)
        self.port_selector.pack(side='top', pady=5, padx = 40)
        ## --- Combobox for device selection
        device_list = ['CR Milano Vibe','GrayPad','8ch_triangle','8ch_2x4rectangle','12ch_2x6rectangle','6ch_3x2rectangle','4ch_2x2rectangle','2ch_1x2rectangle']
        self.device_selector = ttk.Combobox(self.right_common_frame, width=25, state="readonly", values=device_list)
        self.device_selector.pack(side='top', pady=5, padx = 40)
        self.device_selector.bind("<<ComboboxSelected>>", self.select_device)
        self.device_selector.current(0)

        ## ----- Notebook with Tabs
        ## -------------------------
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=1, fill="both")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_selected)

        # Tab 3: Haptic Canvas for Tracing
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Haptic Canvas")
        self.create_canvas_tab()

        self.select_device(1) ## any event = 1 is entered
        self.refresh_ports()
        self.notebook.select(0)

        ## Haptic Thread --- Initial call to start the repeating task
        self.haptic_timer_object = threading.Timer(self.haptic_rate, self.haptic_engine)
        self.haptic_timer_object.start()
    
    ## ---- on haptic export
    def export_hapticfile(self):
        pass
    
    ## ---- on haptic on/off
    def toggle_hapticbutton_state(self):
        ''' toggle haptics driver. currently using serial protocol'''
        self.Haptics_is_ON = not self.Haptics_is_ON
        self.on_HapticFlagChange_callback() ## update haptic counters for all subclasses

        if self.Haptics_is_ON:
            self.toggle_button.config(text="Haptics is ON", relief="sunken")
            print("Hatics Loop", self.Haptics_is_ON, " (ON)")
 
            ## Connect Haptic Device
            match self.hDevice: 
                case 'CR Milano Vibe': self.connect_serialport()
                case 'GrayPad': self.connect_UDPport()
                case _: self.connect_UDPport()
            
        else:
            self.toggle_button.config(text="Haptics is OFF", relief="raised")
            print("Hatics Loop", self.Haptics_is_ON, " (OFF)")
            time.sleep(0.1) ## a bit delay to complete ongoing serial transactions
            ## close serial port if already opened 
            if hasattr(self, "HapticDevice"):
                self.HapticDevice.disconnect()
                # print(self.HapticDevice)
                delattr(self, "HapticDevice")

    ## for change in self.Haptics_is_ON flag
    def on_HapticFlagChange_callback(self):
        ## update only when haptics are stopped
        if not self.Haptics_is_ON:
            self.haptic_canvas.Haptics_is_ON = self.Haptics_is_ON

    ## select_haptic device
    def select_device(self, event):
        ''''''
        if self.Haptics_is_ON: # turn haptics OFF
            self.toggle_hapticbutton_state()

        self.hDevice = self.device_selector.get()
        print(self.hDevice)
        self.deviceDict = setupHapticDictionary(self.hDevice)#, self.framesize)
        self.hchannels = self.deviceDict['channels']
        self.act = np.zeros(self.hchannels)
        self.range = self.deviceDict['range']
        self.porttype = self.deviceDict['port']
        self.actuator_type = self.deviceDict['actuator_type']
        
        # print(self.act)
        # print("Border: ", self.deviceDict['frame border'], ' port type: ', self.porttype, 'range', self.range, 'actuator types: ',self.actuator_type)
        self.on_HapticDeviceUpdate_callback()
        
    ## haptic device update callback
    def on_HapticDeviceUpdate_callback(self):
        self.haptic_canvas.deviceDict = self.deviceDict
        self.haptic_canvas.update_callback(mtype=1) ## a callback funtion in class



    ## --- haptic engine (timer object used in Threading)
    def haptic_engine(self):

        # print(self.tab_index)
        # print(f"Task executed at: {time.time()-self.last_time} ms.")
        
        ## time elapsed
        elapsed_time=time.time()-self.last_time
        self.last_time=time.time()

        ## reset actuators (creates jitters in rendering)
        # self.act = np.zeros(self.hchannels)

        ## --- for Haptic Canvas application
        if self.haptic_canvas.Haptics_is_ON: # if canvas is drawing
            if self.hchannels != self.haptic_canvas.channels:
                print('actuator mismatch bt haptic engine and tab demo')
            else:
                self.act = self.haptic_canvas.act.copy()
                # print(f'{elapsed_time:0.5f}: {self.haptic_canvas.act}')
                for i in range(self.hchannels):
                    if self.act[i]>999: self.act[i]=999
                    if self.act[i]<0.01: self.act[i]=0.0
                    if self.checkboxBaseVar.get():
                        self.act[i] = map_linearhaptics(self.act[i], 300, self.range[1], 0, 999)
                    else:
                        self.act[i] = map_linearhaptics(self.act[i], self.range[0], self.range[1], 0, 999)
                    if self.act[i]<0.0001: self.act[i]=0.0

            # print(f'{elapsed_time:0.5f}: {self.act}')
        else:
            self.act = np.zeros(self.hchannels)

        
        ## --- Main Haptic rendering Loop
        if self.Haptics_is_ON:
            '''check serial connection and write act to serial port'''
            match self.hDevice:
                case 'CR Milano Vibe': # serial com
                    if hasattr(self, "HapticDevice"):
                        if self.HapticDevice.HapticDevice.is_open:
                            # print(f'AWESOME. ({elapsed_time:.4f} ms) - {self.act}')
                            self.HapticDevice.DirectHaptics(self.act, index=0)
                case 'GrayPad':  # UDP
                    if hasattr(self, "client1"):
                        sendUDPparameter(self.client1, self.frequency, self.modulation)
                    if hasattr(self, "client2"):
                        sendUDPamplitude(self.client2, self.act)
                    # print('Another device')
                    pass
                case _:
                    if hasattr(self, "client1"):
                        sendUDPparameter(self.client1, self.frequency, self.modulation)
                    if hasattr(self, "client2"):
                        sendUDPamplitude(self.client2, self.act)

        else:
            ## perhaps send out zeros
            pass

        self.haptic_timer_object = threading.Timer(self.haptic_rate, self.haptic_engine)
        self.haptic_timer_object.start()
    
    ## serial and UDP ports
    def refresh_ports(self):
        """Refresh the list of ports in the dropdown."""
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]#self.list_serial_ports()
        self.port_selector['values'] = port_list
        if port_list:
            self.port_selector.current(0)  # Select first port by default
        else:
            self.port_selector.set('')  # Clear if no ports found

    def connect_serialport(self):
        """Get selected port and print it."""
        self.com_port = self.port_selector.get()
        if self.com_port:
            if '.usbmodem' in self.com_port or 'PicoW' in self.com_port:  ## BLE Might have a different name
                print(f"Selected port: {self.com_port}")
                self.HapticDevice = CR_RP2040W(port=self.com_port)
                print(self.HapticDevice)
            else:
                print(f"Not a Pico controller {self.com_port}")
                self.toggle_hapticbutton_state()
        else:
            print("No port selected.")
            self.toggle_hapticbutton_state()
       
    def connect_UDPport(self):
        self.client1 = udp_client.UDPClient('127.0.0.1', 5000)
        self.client2 = udp_client.UDPClient('127.0.0.1', 5001)
        print("UDPs:", self.client1, self.client2)

    ## on tab change
    def on_tab_selected(self, event):
        selected_tab_id = event.widget.select()
        self.tab_index = event.widget.index(selected_tab_id)
        self.tab_text = event.widget.tab(selected_tab_id, "text")
        print(f"Tab changed to: {selected_tab_id} ({self.tab_index}) {self.tab_text}")
        
        if self.Haptics_is_ON: ## stop haptics
            self.toggle_hapticbutton_state()

    ## tabs
    def create_canvas_tab(self):
        self.haptic_canvas = ExpDrawingApp(self.tab3, self.Haptics_is_ON)

    def destructor(self):
        self.haptic_timer_object.cancel() # Stop the timer thread
        self.master.destroy()
        
if __name__ == "__main__":  
    root = tk.Tk()
    root.geometry("800x800")
    app = TabbedApplication(root)
    root.mainloop()



###################################################
### Last update: 29 July 2025             ########
''' 
''' 
###################################################
