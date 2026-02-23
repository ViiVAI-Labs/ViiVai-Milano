## Copyrighted by ViiVAI Labs and Studio 2025

## IEEE_Demo1: 
###################################################
### Last update: 13 October 2025             ########
''' 
'''

from types import SimpleNamespace

import tkinter as tk
from tkinter import ttk
from tkvideo import tkvideo 
from tkinter.filedialog import askopenfilename, asksaveasfilename
import json, os
import time, threading
import serial
import serial.tools.list_ports
import numpy as np
from pythonosc import udp_client

from IEEE_CRHapticDriver import CR_RP2040W
from IEEE_HapticHardware import setupHapticDictionary
from IEEE_HapticHardware import map_linearhaptics, barycentricLinear, barycentricEnergy, barycentricSquare
from IEEE_HapticHardware import sendUDPamplitude, sendUDPparameter

class DrawingApp:
    def __init__(self, master, Haptics_is_ON):
        self.master = master
        self.Haptics_is_ON = Haptics_is_ON

        # device dictionary
        self.deviceDict = ''
        self.framesize = SimpleNamespace(x=0, y=0, w=800, h=360)
        self.channels = 2
        self.act = np.zeros(self.channels)
        self.frequency = 400 ## frequency of VCM signal
        self.modulation = 20 ## modulation of VCM signal
        self.circle_positions = [] ## to store actuator center for animation in layout
        
        # filename and path
        self.filename = 'drawing.json'
        self.path = os.getcwd()
        self.path = os.path.join(self.path,'patterns')
        # print(f"Current working directory (os.getcwd()): {self.path}")
        self.filepath = os.path.join(self.path,self.filename)
        # print(f"the full file path is: {self.filepath}")
        
        # --- Sliders for color control ---
        self.color_slider_frame = tk.Frame(master, bg="lightblue")
        self.color_slider_frame.pack()

        self.red_slider = tk.Scale(self.color_slider_frame, from_=0, to=255, orient=tk.HORIZONTAL, label="Red", command=self.update_color)
        self.red_slider.pack(side='left')#side=tk.LEFT)
        self.green_slider = tk.Scale(self.color_slider_frame, from_=0, to=255, orient=tk.HORIZONTAL, label="Green", command=self.update_color)
        self.green_slider.pack(side='left')#side=tk.LEFT)
        self.blue_slider = tk.Scale(self.color_slider_frame, from_=0, to=255, orient=tk.HORIZONTAL, label="Blue", command=self.update_color)
        self.blue_slider.pack(side='left')#side=tk.LEFT)

        # --- Sliders for thickness control ---
        self.thick_slider = tk.Scale(master, from_=1, to=6, orient=tk.HORIZONTAL, length=300, label="Thickness", command=self.update_thickness)
        self.thick_slider.set(4)
        # self.thick_slider.place(x=50, y=100)
        self.thick_slider.pack(fill='y')

        # --- check box to render visuals ---
        self.chbox_frame = tk.Frame(master, bg="lightblue")
        self.chbox_frame.pack()

        self.checkbox1Var=tk.BooleanVar()
        self.checkbox1=tk.Checkbutton(self.chbox_frame, text="Trailing Line", variable=self.checkbox1Var)
        self.checkbox1.pack(side='left')
        self.checkbox1Var.set(1)

        self.checkbox2Var=tk.BooleanVar()
        self.checkbox2=tk.Checkbutton(self.chbox_frame, text="Energy Rendering", variable=self.checkbox2Var)
        self.checkbox2.pack()
        self.checkbox2Var.set(1)

        # --- Drawing Canvas ---
        self.canvas = tk.Canvas(master, width=self.framesize.w, height=self.framesize.h, bg="white")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.start_drawing)  # Bind left-click to start drawing
        self.canvas.bind("<B1-Motion>", self.draw)  # Bind mouse drag with left button down
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)  # Bind left-click release

        # --- Bottom Frame ---
        self.button_frame = tk.Frame(master)
        self.button_frame.pack()#side='bottom')
        ## --- Text Box ---
        self.file_text = tk.StringVar()
        self.file_text.set(self.filename)
        self.textbox1  = tk.Entry(self.button_frame, textvariable=self.file_text, width=30)
        self.textbox1.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        # --- Buttons ---
        self.clear_button = tk.Button(self.button_frame, text="Clear Canvas", width=25, command=self.clear_canvas)
        self.clear_button.grid(row=2, column=0, columnspan=3)#pack(side=tk.BOTTOM)
        self.draw_debug_button = ttk.Button(self.button_frame, text="For Debug", width=10, command=self.update_sliders)
        self.draw_debug_button.grid(row=3, column=0, columnspan=3)#pack(side=tk.TOP)
        self.play_button = tk.Button(self.button_frame, text="Play", width=10, command=self.play_drawing)
        self.play_button.grid(row=1, column=0)#pack(side=tk.RIGHT)
        self.save_button = tk.Button(self.button_frame, text="Save", width=10, command=self.save_file)#save_drawing)
        self.save_button.grid(row=1, column=1)#pack(side=tk.RIGHT)
        self.load_button = tk.Button(self.button_frame, text="Load", width=10, command=self.open_file)#load_drawing)
        self.load_button.grid(row=1, column=2)#pack(side=tk.LEFT)

        # Drawing variables
        self.start_x = None
        self.start_y = None
        self.current_color = "#000000"  # Default to black
        self.current_thickness = 2  # Default to black

        # Storing variables
        self.drawn_lines = []  # Stores list of points and timestamps
        self.current_line_points = []
        # self.points = []
        self.start_time = 0
    
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

            self.clear_canvas()

    # --- Slider callback function ---
    def update_color(self, val):
        r = self.red_slider.get()
        g = self.green_slider.get()
        b = self.blue_slider.get()
        self.current_color = f"#{r:02x}{g:02x}{b:02x}"  # Convert RGB to hex color string
        
        ## color2haptics mapping
        self.frequency = int(r*220/255 - b*70/255) + 80
        if (g==0): self.modulation=0
        else: self.modulation = g//10+5
        print(f'F: {self.frequency}, M:{self.modulation}')
        self.update_sliders()

    def update_thickness(self, val):
        t = self.thick_slider.get()
        self.current_thickness = t  # 
        self.update_sliders()

    def update_sliders(self): ## update the line based on slider values.
        self.clear_canvas()
        for line_data in (self.drawn_lines):
            if not line_data:
                continue
            # print(len(line_data))
            self.current_line_points = []
            for i in range(1, len(line_data)):
                prev_x, prev_y, prev_time, *_ = line_data[i-1]
                curr_x, curr_y, curr_time, *_ = line_data[i]
                # if self.checkbox1Var.get():
                self.canvas.create_line(prev_x, prev_y, curr_x, curr_y, fill=self.current_color, width=2*self.current_thickness)
                
                if i == 1:
                    self.current_line_points.append((prev_x, prev_y, prev_time, self.current_color, self.current_thickness))
                    self.current_line_points.append((curr_x, curr_y, curr_time, self.current_color, self.current_thickness))
                else:
                    self.current_line_points.append((curr_x, curr_y, curr_time, self.current_color, self.current_thickness))
            
            self.drawn_lines = []
            self.drawn_lines.append(self.current_line_points)

    def set_sliders(self, hex_color, val): ## set slider values
        # Remove '#' if present
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        # Ensure valid length
        if len(hex_color) != 6:
            raise ValueError("Invalid hex color format. Expected 6 hexadecimal digits.")

        # Extract and convert each component
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        ## colors
        self.red_slider.set(r)
        self.green_slider.set(g)
        self.blue_slider.set(b)
        ## thickness
        self.thick_slider.set(val)

    # --- Play Save and load lines ---
    def play_drawing(self):
        # self.canvas.delete("all")  # Clear the canvas
        self.clear_canvas()
        for line_data in self.drawn_lines:
            if not line_data:
                    continue
            self.draw_lines_step_by_step(line_data)
    
    def save_drawing(self):
        with open(self.filepath, "w") as f:
            json.dump(self.drawn_lines, f)
            print(f"Content saved to: {self.filename}")
    
    def load_drawing(self):
        # self.filename = self.textbox1.get()
        # self.filepath = os.path.join(self.path,self.filename)
        # self.canvas.delete("all")  # Clear the canvas
        self.clear_canvas()
        try:
            with open(self.filepath, "r") as f:
                loaded_lines = json.load(f)
                
            self.now_time = time.time()
            self.drawn_lines = loaded_lines
            for line_data in loaded_lines:
                if not line_data:
                    continue
                _, _, _, self.current_color, self.current_thickness = line_data[0]
                self.set_sliders(self.current_color, self.current_thickness)
                self.draw_lines_step_by_step(line_data)
        except FileNotFoundError:
            print("No saved drawing found.")

    # --- Canvas drawing functions ---
    def start_drawing(self, event):
        self.clear_canvas()
        self.current_line_points = []
        self.drawn_lines = []
        self.start_time = time.time()  # Record start time
        self.Haptics_is_ON = True

        # if not self.mousebutton_pressed:
        #     self.mousebutton_pressed = True

        x, y = event.x, event.y
        self.current_line_points.append((x, y, 0, self.current_color, self.current_thickness))  
        dia = self.current_thickness*10

        ## draw mouse circle
        self.mouse_circle=self.canvas.create_oval(x-dia, y-dia, x+dia, y+dia, fill=self.current_color, outline='black')
        ## RENDER HAPTICS HERE
        player_pos = SimpleNamespace(x=x, y=y)
        act = self.set_actuators(player_pos=player_pos, line_thickness=self.current_thickness)
        self.update_act_size(act)

    def draw(self, event):
        timestamp = time.time() - self.start_time  # Time relative to starting draw
        x, y = event.x, event.y
        self.current_line_points.append((x, y, timestamp, self.current_color, self.current_thickness))
        dia = self.current_thickness*8
        if len(self.current_line_points) > 1 and self.checkbox1Var.get():
            prev_x, prev_y, *_ = self.current_line_points[-2]
            self.canvas.create_line(prev_x, prev_y, x, y, smooth=True, fill=self.current_color, width=2*self.current_thickness)
        
        ## draw mouse circle
        self.canvas.coords(self.mouse_circle, x-dia, y-dia, x+dia, y+dia)
        ## RENDER HAPTICS HERE
        player_pos = SimpleNamespace(x=x, y=y)
        act = self.set_actuators(player_pos=player_pos, line_thickness=self.current_thickness)
        self.update_act_size(act)
        # print((x, y, timestamp, self.current_color, self.current_thickness))

    def stop_drawing(self, event):
        # store last value to capture hold time
        x, y = event.x, event.y
        timestamp = time.time() - self.start_time  # Time relative to starting draw
        self.current_line_points.append((x, y, timestamp, self.current_color, self.current_thickness))
        if len(self.current_line_points) > 1 and self.checkbox1Var.get():
            prev_x, prev_y, *_ = self.current_line_points[-2]
            self.canvas.create_line(prev_x, prev_y, x, y, smooth=True, fill=self.current_color, width=2*self.current_thickness)

        self.Haptics_is_ON = False
        # self.mousebutton_pressed = False
        self.act = np.zeros(self.channels)
        if self.current_line_points:
            self.drawn_lines.append(self.current_line_points)
            self.current_line_points = []

        # self.clear_canvas()
        self.update_act_size(self.act, reset=1)
        self.canvas.coords(self.mouse_circle, 0, 0, 0, 0)

    def draw_lines_step_by_step(self, lines_to_draw, index=0):
        ''' re drawing function '''
        if index >= len(lines_to_draw) - 1: ## end of line 
            self.Haptics_is_ON = False
            print('-'*30)
            print('Canvas Drawing: Line length ', len(lines_to_draw))
            print('-'*30)
            act = np.zeros(self.channels)
            self.update_act_size(act, reset=1)
            return  # Done

        self.Haptics_is_ON = True
        
        prev_x, prev_y, prev_time, *_ = lines_to_draw[index]
        curr_x, curr_y, curr_time, line_color, line_thickness = lines_to_draw[index + 1]
        self.delay = int((curr_time - prev_time) * 1000)  # Delay in milliseconds
        # print(curr_time, self.delay, time.time() - self.now_time)
        self.canvas.create_line(prev_x, prev_y, curr_x, curr_y, fill=line_color, width=2*line_thickness)

        ## Apply Barycentric Algorithm
        player_pos = SimpleNamespace(x=curr_x, y=curr_y)
        act = self.set_actuators(player_pos=player_pos, line_thickness=line_thickness) # for haptics
        # print(f'Debug01: Player Position [{player_pos}], delay ({self.delay}) and actuator values: {act}')
        self.update_act_size(act) # for animations
        
        # # Schedule the next segment
        self.canvas.after(self.delay, lambda: self.draw_lines_step_by_step(lines_to_draw, index + 1))

    ## set actuator values (Barycentric rendering)
    def set_actuators(self, player_pos, line_thickness):
        act = np.zeros(self.channels) ## 
        amplitude = 0

        if player_pos.x<0.001: player_pos.x=0.001
        if player_pos.x>self.framesize.w-0.001: player_pos.x=self.framesize.w-0.001

        if player_pos.y<0.001: player_pos.y=0.001
        if player_pos.y>self.framesize.h-0.001: player_pos.y=self.framesize.h-0.001
        

        if self.checkbox2Var.get():
            result, act = barycentricEnergy(act, self.deviceDict['act_layout'], self.deviceDict['tri_layout'], [player_pos.x, player_pos.y])
        else:
            result, act = barycentricLinear(act, self.deviceDict['act_layout'], self.deviceDict['tri_layout'],[player_pos.x, player_pos.y])
        # result, act = barycentricSquare(act, self.deviceDict['act_layout'], self.deviceDict['tri_layout'], [player_pos.x, player_pos.y])
        if result == "Outside": 
            print("Point is outside the grid", player_pos, result)
        else: # set act intensity levels
            match (line_thickness):
                case 1:  amplitude = 500
                case 2:  amplitude = 600
                case 3:  amplitude = 700
                case 4:  amplitude = 800
                case 5:  amplitude = 900
                case 6:  amplitude = 999
                case _:  amplitude = 0
                # case 1:  amplitude = 400
                # case 2:  amplitude = 500
                # case 3:  amplitude = 600
                # case 4:  amplitude = 700
                # case 5:  amplitude = 750
                # case 6:  amplitude = 800
                # case 7:  amplitude = 850
                # case 8:  amplitude = 900
                # case 9:  amplitude = 950
                # case 10: amplitude = 999
                # case _:  amplitude = 0
            
            self.Haptics_is_ON = False
            for i in range(self.channels):
                act[i]=act[i]*amplitude
                if act[i]>999: act[i]=999
                self.act[i]=int(act[i])
            self.Haptics_is_ON = True

        # print(f'Debug01: Player Position [{player_pos}] and actuator values: {act}')
        return act

    ## Grid layout + visual animation 
    def draw_layout(self):
        #canvas, framesize, act_layout, tri_layout, act_size=20):
        # print(len(tri_layout.tolist()))
        tlayout = self.deviceDict['tri_layout'].tolist()

        for i in tlayout:#tri_layout:
            self.canvas.create_polygon(i, outline="grey", fill="", width=1)

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

    ## clear canvas and draw the layout
    def clear_canvas(self):
        self.canvas.delete("all")  # Deletes all items on the canvas
        self.draw_layout()
        self.init_act_grid()

    # --- Save and Open file dialog
    def save_file(self):
        self.filename = self.textbox1.get()
        self.filepath = asksaveasfilename(
            title="Save file as",
            initialdir=self.path,
            initialfile=self.filename,  # Optional: default filename
            defaultextension=".json",     # Optional: default extension
            filetypes=[("Haptic Drawings", "*.json"), ("All files", "*.*")]
        )
        self.filename = os.path.basename(self.filepath)
        self.textbox1.delete(0, tk.END) # Clear existing text (from index 0 to the end)
        self.textbox1.insert(0, self.filename) # Insert new text at the beginning (index 0)
        if self.filepath:
            # Do something with the selected file path, e.g., write content to it
            self.save_drawing()

    def open_file(self):
        self.filename = self.textbox1.get()
        self.filepath = askopenfilename(
            title="Select a file",
            initialdir=self.path,#"/",  # Optional: starting directory
            initialfile=self.filename,
            defaultextension=".json",     # Optional: default extension
            filetypes=[("Haptic Drawings", "*.json"), ("All files", "*.*")] # Optional: filter file types
        )
        self.filename = os.path.basename(self.filepath)
        self.textbox1.delete(0, tk.END) # Clear existing text (from index 0 to the end)
        self.textbox1.insert(0, self.filename) # Insert new text at the beginning (index 0)
        if self.filepath:
            # Do something with the selected file path, e.g., open and read it
            self.load_drawing()
            # with open(filepath, 'r') as file:
            #     content = file.read()
            #     print(f"File content:\n{content}")

# # Example usage:
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = DrawingApp(root)
#     root.mainloop()

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
        self.frequency, self.modulation = 400, 20

        ## Common frame for buttons, serial list for all table
        self.common_frame = tk.Frame(self.master)
        self.common_frame.pack(side="top", pady=10, padx=10)

        ## frame to set buttons on one end in a column
        self.button_frame = tk.Frame(self.common_frame)
        self.button_frame.pack(side="left", pady=0, padx=0)

        ## --- Haptic Toggle button ---
        self.toggle_button = tk.Button(self.button_frame, text="Haptic is OFF", relief="raised", command=self.toggle_hapticbutton_state)
        self.toggle_button.pack(side='top', pady=0)

        ## --- Export button ---
        self.export_button = tk.Button(self.button_frame, text="Export", relief="raised", command=self.export_hapticfile)
        self.export_button.pack(side='top', pady=0)

        self.checkboxBaseVar=tk.BooleanVar()
        self.checkboxBase=tk.Checkbutton(self.button_frame, text="Baseline adjustment", variable=self.checkboxBaseVar)
        self.checkboxBase.pack()
        self.checkboxBaseVar.set(0)

        ## frame for device and port selectors
        self.side_frame = tk.Frame(self.common_frame)
        self.side_frame.pack(side="left", pady=0, padx=0)

        ## --- device label
        tk.Label(self.side_frame, text="Select Device", font=("Helvetica", 16)).pack()

        ## --- Combobox for device selection
        device_list = ['CR Milano Vibe','GrayPad','8ch_triangle','12ch_2x6rectangle','4ch_2x2rectangle']
        self.device_selector = ttk.Combobox(self.side_frame, width=25, state="readonly", values=device_list)
        self.device_selector.pack(side='top', pady=0, padx = 40)
        self.device_selector.bind("<<ComboboxSelected>>", self.select_device)
        self.device_selector.current(1)
        ## --- Combobox for port selection
        self.port_selector = ttk.Combobox(self.side_frame, state="readonly", width=25)
        self.port_selector.pack(side='top', pady=0, padx = 40)
        ## --- refresh button
        tk.Button(self.side_frame, text="Refresh", command=self.refresh_ports).pack(side='top', pady=0)

        ## frame for label
        self.right_frame = tk.Frame(self.common_frame)
        self.right_frame.pack(side="left", pady=0, padx=0)

        self.port_labeltext = tk.StringVar()
        self.port_labeltext.set('port type: None')
        self.port_label=tk.Label(self.right_frame, textvariable=self.port_labeltext, font=("Helvetica", 16)).pack()

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
        self.grid_type = self.deviceDict['grid_type']

        self.port_labeltext.set(f'port type: {self.porttype}\ngrid type: {self.grid_type}\nchannels: {self.hchannels}')
        
        # print(self.act)
        print("Border: ", self.deviceDict['frame border'], ' port type: ', self.porttype, 'range', self.range, 'actuator types: ',self.actuator_type)
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

        ##
        self.frequency = self.haptic_canvas.frequency
        self.modulation = self.haptic_canvas.modulation

        ## reset actuators (creates jitters in rendering)
        # self.act = np.zeros(self.hchannels)

        ## --- for Haptic Canvas application
        if self.haptic_canvas.Haptics_is_ON and self.tab_index ==0: # if canvas is drawing
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
        self.haptic_canvas = DrawingApp(self.tab3, self.Haptics_is_ON)


    def create_pattern_tab_tbd(self):
        """Creates a tab for haptic pattern."""
        # self.tab3 = ttk.Frame(self.notebook)
        # self.notebook.add(self.tab3, text="Haptic Canvas")

        # Create a Canvas widget
        self.canvas = tk.Canvas(self.tab4, width=400, height=300, bg="white")
        self.canvas.pack()

        ttk.Label(self.tab4, text="Slider 1:").pack(pady=5)
        ttk.Scale(self.tab4, from_=0, to=100, orient="horizontal").pack(pady=5)

        tk.Label(self.tab4, text="Slider 2:").pack(pady=5)
        tk.Scale(self.tab4, from_=0, to=100, orient="horizontal").pack(pady=5)


        # Draw something on the canvas
        self.canvas.create_oval(50, 50, 150, 150, fill="blue")
        self.canvas.create_line(0, 0, 400, 300, fill="red", width=2)

    def create_video_tab(self):
        """Creates a tab for video playback."""
        # self.tab2 = ttk.Frame(self.notebook)
        # self.notebook.add(self.tab2, text="Video Tab")

        # Create a Label to display the video
        self.video_label = tk.Label(self.tab2)
        self.video_label.pack()

        # Initialize and play the video (replace 'your_video.mp4' with your video file)
        self.player = tkvideo("video.mp4", self.video_label, loop=1, size=(640, 360))
        self.player.play()

    def destructor(self):
        self.haptic_timer_object.cancel() # Stop the timer thread
        self.master.destroy()
        
if __name__ == "__main__":  
    root = tk.Tk()
    root.geometry("860x800")
    app = TabbedApplication(root)
    root.mainloop()

