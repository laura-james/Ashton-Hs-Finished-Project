# imports a tkinter for the UI
import tkinter as tk
# imports yaml library to read in yaml file to a dictionary
import yaml
# import files from matplotlib and seaborn for the heatmap
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                            NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import seaborn

# libraries for reading the file in the command line
import sys
import os

yaml_file = "C:\\yaml.yaml"
log_file = "C:\\new logs\\reduced log.log"
 
try:  # can also use replit environment to ensure correct method of reading files is used
    log = open(log_file, "r").read()  # reads WHOLE log file at once (not ideal)
except FileNotFoundError:
    file = open("replitlog.log")
    log = file.read()
    file.close()
logs = log.split("\n")  # splits every line


def read(yml_file):
    with open(yml_file, "r") as y_file:
        prime_service = yaml.safe_load(y_file)

    stgs, mks, cols, shps = prime_service["Trace"]["PipeStages"], prime_service["Trace"]["PipeMarkers"], [], []
    for item in mks:
        col, shp = item.split(" ")
        cols += [col]
        shps += [shp]
    return stgs, cols, shps

try:
    trace_info = read(yaml_file)
except FileNotFoundError:  # hardcoded so that it works in replit
    trace_info = (['Fetch', 'Decode', 'Rename', 'Dispatch', 'Issue', 'Complete', 'Retire'], 
                  ['red', 'blue', 'green', 'blue', 'blue', 'yellow', 'red'], 
                  ['rarrow', 'circle', 'diamond', 'rarrow', 'rarrow', 'circle', 'larrow'])


stage_choice, colour_choice, shape_choice = trace_info[0], trace_info[1], trace_info[2]
pipe_length = len(stage_choice)

# I record the number of lines here to scale the canvas appropiately
instr_count = len(logs)

# and the highest pipe timing for the x
max_pipe_time = 95000000

# how many lines are plotted in one chunk
chunk_size = 100

# array of indexes of the plotted lines, used for chunks
plotted_arr = []

# creates a list to determine how many chunks to start with
for lines in range(10):
    plotted_arr += [lines]

# determines initial spacing of grid lines
scale_x, scale_y, scale_factor = 28, 32, 4

# determines size of canvas from the scale and number of lines
wnd_x = (max_pipe_time + 500) * scale_x // 2
wnd_y = scale_y * (instr_count + 500)

# shape size for all plotted shapes
shape_size = 10

# determine offset of the instructions from the side of the viewing screen,
# if this is large then the instructions
# will appear further right on the screen
anchord_x = 50

# instantiates global variables to plot the stages
stage_choice = trace_info[0]
colour_choice = trace_info[1]
shape_choice = trace_info[2]

# records the number of stages
pipe_length = len(stage_choice)


def set_descr(instr, line_ind):
    """Splits instruction line into all pipeline timings and description"""
    out = []
    instr = instr.split(":")

    try: # try used to catch invalid log files
    # iterates over the indexes of the pipe stages
        for i in range(pipe_length):
            # adds all the first pipeline timing and line index
            # to make the coords for all the stages
            out += [[int(instr[i]), line_ind]]
    except:
        on_click("invalid log file")
        sys.exit(1)

    # checks if the instruction doesn't have any registers
    pc, id, descr_str = instr[-4], instr[-2], instr[-1]

    if descr_str == "":
        # if there isn't any registers and command, it replaces it with None
        command, regs = "None", "None"
    else:
        # adds to the output array the descriptor,
        # instruction address, command and registers
        descr_arr = descr_str.split(" ")
        regs = "".join(descr_arr[1:])
        command = descr_arr[0]
    out += [ (id, command, pc, regs) ]

    return out


def analyse_trace(log_arr):
    """Creates an array of all the points to plot and their descriptions"""
    descriptor = []
    # iterates over the whole log file
    # in the future, I will thread this in the background
    # if done properly my heatmpa can then be generated later

    for line_numb, line in enumerate(log_arr):
        # checks if line is not an empty string
        if line:
            # runs splitting function to get the description from a line
            descr_set = set_descr(line, line_numb+1)

            # adds to array, avoids using the set_descr() multiple times
            descriptor += [descr_set]

    return descriptor


def find_hot_pcs():
    """Used to find all the frequently used program counters"""
    # sets up dictionary
    pc_dict = {}

    # iterates over line's descriptions
    for inst_descr in inst_descrs:
        # Ignores the cycle timings for the shapes, uses actual description
        inst_info = inst_descr[-1]

        # sets instruction mnemonic, pc, registers to variables
        id, command, pc, regs = inst_info

        # if the pc is not in the dictionary,
        # it creates a new entry with that pc
        if pc not in pc_dict:
            pc_dict[pc] = 0

        # if the pc is in the dictionary, it adds one to the count
        pc_dict[pc] += 1

    # makes array for the number of times each pc is called
    # starts with a 0 item to adjust indexes
    hot_pcs = [1]

    # starts at 0 just in case of a [None] line
    hot_pc = 0

    # iterates again, exactly as before but adds it to an array to return
    for inst_descr in inst_descrs:
        inst_info = inst_descr[-1]
        id, command, pc, regs = inst_info

        # looks up the number of calls of that pc in the dictionary
        hot_pc = pc_dict[pc]

        # adds the number to the array
        hot_pcs += [hot_pc]

    return hot_pcs


def heat_pick(event):
    """Jumps to a line when the heatmap is interacted with"""
    # finds the mouse position on heatmap
    line_numb = int(event.mouseevent.xdata)

    # jumps to the line
    move_to_index(line_numb)


def heatmap(tkinter_root, heatmap_vals):
    """Function to bind the heatmap from seaborn into the tkinter window"""
    # for more colours:
    # https://seaborn.pydata.org/tutorial/color_palettes.html

    # instantiates and sets basic style
    seaborn.set_style(rc={'figure.facecolor': '#F0F0F0'})
    fig, ax = plt.subplots()

    # sets heatmap colours to array values
    # adjusts size and colour of the heatmap
    seaborn.heatmap(
        [heatmap_vals],
        cmap=plt.get_cmap("inferno_r", 1000),
        cbar_kws={'aspect': 3, "shrink": 3},
        yticklabels=False,
        picker=True)
    plt.subplots_adjust(
        left=0.017,
        bottom=0.338,
        right=1,
        top=0.643,
        wspace=0,
        hspace=0)

    ax.set(xlim = (1,instr_count+1))

    # links the heatmap to the tkinter root
    heat = FigureCanvasTkAgg(fig, master=tkinter_root)

    # renders heatmap and the function heat_pick() (to jump to a line)
    heat.get_tk_widget().config(height=200)
    heat.draw()
    heat.mpl_connect('pick_event', heat_pick)

    # renders a toolbar built into seaborn library
    toolbar = NavigationToolbar2Tk(heat, tkinter_root, pack_toolbar=False)
    toolbar.update()
    toolbar.pack(side=tk.BOTTOM, fill=tk.X)  # toolbar for zoom etc
    heat.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.X, expand=False)


class Shape:
    """Parent class with the information about the shape style"""
    def __init__(self, cur_canvas, st, col, sh):
        # passes in a canvas, there are two canvases
        # one for drawing instructions the other is a key
        self.canvas = cur_canvas
        self.stage = st
        self.colour = col
        self.shape = sh


class Larrow(Shape):
    """Each shape has a different method to draw it onto the canvas"""
    def draw(self, x, y, tags):
        points = [x + shape_size, y,
                  x - shape_size, y]
        self.canvas.create_line(points,
                                tags=tags,
                                arrow=tk.LAST,
                                width=shape_size,
                                fill=self.colour)


class Rarrow(Shape):
    def draw(self, x, y, tags):
        points = [x - shape_size, y,
                  x + shape_size, y]
        self.canvas.create_line(points,
                                tags=tags,
                                arrow=tk.LAST,
                                width=shape_size,
                                fill=self.colour)


class Circle(Shape):
    def draw(self, x, y, tags):
        points = [x - shape_size, y - shape_size,
                  x + shape_size, y + shape_size]
        self.canvas.create_oval(points,
                                tags=tags,
                                fill=self.colour)


class Diamond(Shape):
    def draw(self, x, y, tags):
        points = [x - shape_size, y,
                  x, y + shape_size,
                  x + shape_size, y,
                  x, y - shape_size]
        self.canvas.create_polygon(points,
                                   tags=tags,
                                   fill=self.colour)


def build_shape_instances(canv):
    dictionary = {}

    # iterates over the indexes for the pipe stages
    for index in range(pipe_length):
        # chooses the colour, stage, shape, from the arrays of
        # stage choice, colour_choice and shape_choice,
        # all assigned earlier by the yaml reader
        stage = stage_choice[index]
        colour = colour_choice[index]
        shape = shape_choice[index]

        # makes an instance of all the shape classes into the dictionary,
        # one instance for drawing onto the main canvas,
        # the other for drawing the shapes for the keys
        if shape == "larrow":
            dictionary[stage] = Larrow(canv, stage, colour, shape)

        elif shape == "rarrow":
            dictionary[stage] = Rarrow(canv, stage, colour, shape)

        elif shape == "circle":
            dictionary[stage] = Circle(canv, stage, colour, shape)

        elif shape == "diamond":
            dictionary[stage] = Diamond(canv, stage, colour, shape)

        else:
            on_click(f"'{shape}' in yaml not recognised, set to diamond")
            dictionary[stage] = Diamond(canv, stage, colour, "diamond")

    return dictionary


def chunk_jump(instr_line):
    """Called when the jump function is used"""
    global plotted_arr

    # finds the group of lines the target line is in
    mid_instr_set = instr_line // chunk_size

    # checks the chunks one before and after
    for instr_set in range(mid_instr_set-1, mid_instr_set+2):
        # checks if not the end of the log file
        if 0 <= instr_set <= instr_count//chunk_size:
            # checks if the target chunk of lines is plotted
            if instr_set not in plotted_arr:
                # then runs the function to plot the whole chunk
                plot_instr_set(instr_set)

                # adds them to the array,
                # records which lines have been plotted
                plotted_arr += [instr_set]


def find_time(y):
    """Finds the closest instruction to a y val given all coords"""

    # check not scrolled off-screen
    if y < 0 :
        y = 0

    # calculates where the canvas screen should be
    line_numb = y//scale_y

    # then sets the right pipe timings as a variable
    pipe_times = inst_descrs[line_numb]

    # starts looking for the correct x time, starts at 0
    x_pos = 0

    # iterates over the coords of the shapes
    for coords in pipe_times[:-1]:
        # finds the first one that isn't 0 to lock onto
        if coords[0] != 0:
            x_pos = coords[0]
            break

    return x_pos * scale_x - anchord_x


def move_to_index(dest_ind):
    """Used to avoid repeated code from incr functions"""

    # if out of bounds of the canvas, it just sets the position to the end,
    # reports an error message
    if dest_ind >= instr_count:
        on_click(f" Index {dest_ind} is out of range")
        dest_ind = instr_count-1

    # loads the correct chunk in
    chunk_jump(dest_ind)

    # using the method to calculate y positions initially,
    # use this in order to recalculate the correct postion,
    # this is also used in my mouse scroll function
    y_jump_pos = dest_ind * scale_y
    x_time = find_time(y_jump_pos)

    # calculates proportion of the canvas that the target coords are at
    # (this is just how tkinter does the moving of the scrolling frame)
    canvas.yview_moveto((y_jump_pos - scale_y) / wnd_y)
    canvas.xview_moveto(x_time / wnd_x)


def mouse_wheel(event):
    """Used to scroll with the mouse"""
    # caps out the speed,
    # so it doesn't get too fast when scrolling with a mouse
    max_speed = 15

    # fetches the input from the textbox
    try:
        mouse_jump = int(incr_bx.get(1.0, "end-1c"))
    except:
        incr_bx.delete('1.0', tk.END)
        on_click("Invalid scroll box input")
        incr_bx.insert(tk.END, '10')
        mouse_jump = 10

    # uses variable to cap speed
    if mouse_jump >= max_speed:
        mouse_jump = max_speed+1

    # adjusts to actual y position on the canvas
    mouse_jump *= scale_y

    # finds y position of canvas
    y0 = int(canvas.canvasy(0))

    new_pos = y0
    # tkinter syntax for scroll down events
    if event.num == 5 or event.delta < 0:
        # finds destination y position,
        # goes faster if mouse span more violently,
        # also has a line correction of +2 when taking from the texbox
        new_pos = y0 + mouse_jump*(-event.delta//120) + 2*scale_y

    # tkinter syntax for scroll up events
    if event.num == 4 or event.delta > 0:
        new_pos = y0 - mouse_jump*(event.delta//120) + 2*scale_y
        if new_pos < 0 :
            new_pos = 0

    # jumps to the correct line,
    # loads the chunks for the new canvas position
    line_numb = new_pos // scale_y

    # moves to correct line
    move_to_index(line_numb)


def jump_to(event):
    """Takes texbox info and jumps to the correct line"""
    # fetches input
    try:
        line_numb = int(jump_bx.get(1.0, "end-1c"))
    except:
        on_click("Invalid jump box input")
        line_numb = 1
    jump_bx.delete('1.0', tk.END)

    # moves canvas
    move_to_index(line_numb)


def incr_move_down(event):
    """Moves down by some lines, an alternative to the scroll wheel"""
    # fetches the number of lines to scroll by, with and index adjustment
    try:
        jump_incr = int(incr_bx.get(1.0, "end-1c"))+2
    except:
        incr_bx.delete('1.0', tk.END)
        on_click("Invalid scroll box input")
        incr_bx.insert(tk.END, '10')
        jump_incr = 10

    # finds y position of canvas
    y0 = int(canvas.canvasy(0))

    # calculates destination index
    ind = y0 // scale_y
    dest_ind = ind + jump_incr

    # uses the move function
    move_to_index(dest_ind)


def incr_move_up(event):
    """Used to move up by some lines, a repeat of incr_move_down"""
    try:
        jump_incr = int(incr_bx.get(1.0, "end-1c")) - 2
    except:
        incr_bx.delete('1.0', tk.END)
        on_click("Invalid scroll box input")
        incr_bx.insert(tk.END, '10')
        jump_incr = 10

    y0 = int(canvas.canvasy(0))
    ind = y0 // scale_y
    dest_ind = ind - jump_incr
    move_to_index(dest_ind)


def pan_left(event):
    """Moves canvas left and right"""
    # finds x position on canvas
    x0 = int(canvas.canvasx(0))

    # shifts along by an amount
    new_pos = x0 - 2*scale_x
    canvas.xview_moveto(new_pos / wnd_x)


def pan_right(event):
    """Identical to pan_left"""
    x0 = int(canvas.canvasx(0))
    new_pos = x0 + 3*scale_x
    canvas.xview_moveto(new_pos / wnd_x)


def zoom(factor_x, factor_y):
    # scales made global so that they can be changed
    global scale_y
    global scale_x

    # finds y position of canvas
    y0 = int(canvas.canvasy(0))

    # line has to be calculated before changing the scale
    line_numb = y0 // scale_y

    # some logic to avoid zooming in or out too far
    if  (scale_y <= 12 and factor_y < 0) or \
        (scale_x <= 12 and factor_x < 0) or \
        (scale_y >= 48 and factor_y > 0) or \
        (scale_x >= 48 and factor_x > 0):
        on_click("Cant go any further")
    else:
        # adjusts scales
        scale_x += factor_x
        scale_y += factor_y

        # calls redraw of canvas
        refresh(line_numb)


def shape_plot(ind, x, y, id, command, pc, reg, line_numb, last_val):
    """Used to plot a shape at any given coords"""
    # sz changes with the scale, so is made global
    global shape_size

    # tags to attatch to the shapes, this allows them to be hidden
    shp_tags = ["instr", stage_choice[ind], pc, command, reg]

    # finds average scale
    avrg_scale = (scale_x + scale_y) // 2

    # changes the shape sizes to the average scale
    shape_size = avrg_scale // 3

    # calls dictionary of classes to plot shape
    instances[stage_choice[ind]].draw(x, y, shp_tags)

    # checks if last stage,
    # then will plot descr, line number and graph the line
    if last_val and avrg_scale > 16:
        # defines font, tags and spacing on the descriptions,
        # two line numbers,
        # one for the index in the file
        # and one for the index in the original log file
        # if line_numb is the same as id, there's no need to print both
        if str(line_numb) == str(id):
            index = line_numb
        else:
            index = f"{line_numb}:  {id}:"

        text = f"{index}                 {pc}    {command}    {reg}"

        canvas.create_text(x + (scale_x * 2), y,
                           text=text,
                           font="Calibri " + str(avrg_scale // 2) + " bold",
                           tag="line_numb",
                           anchor="w")


    # calculate bounds for the x grid lines
    bound_l = x - chunk_size*scale_x*2
    bound_r =  x + chunk_size*scale_x*2

    # plot the x line
    x_line = canvas.create_line(bound_l, y,
                                bound_r, y,
                                fill=line_colour,
                                tag="x")

    # sends the line to the background
    # (so that the instructions appear on top)
    canvas.tag_lower(x_line)


def refresh(line_numb):
    """Used to redo screen when zoomed"""

    # plotted_arr global so that it can be reset when the zoom changes
    global plotted_arr

    # wipes the canvas of all items
    canvas.delete("all")

    # wipes the plotted array
    plotted_arr = []

    # jumps to line again so that the chunk is correctly loaded
    move_to_index(line_numb)


def plot_instr_set(line_set):
    """Used to plot a chunk of instructions in one go"""

    # plotted array is global to update which chunks are loaded
    global plotted_arr, last_stamp

    # loop ensures it doesn't plot past the end of instructions
    start = line_set*chunk_size
    end = min(line_set*chunk_size+chunk_size, instr_count)
    for line_numb in range(start, end):
        # if first value of chunk, sets a flag to true
        if line_numb == line_set*chunk_size:
            start_of_plot_flag = True
        else:
            start_of_plot_flag = False

        # each line's co_ords and descr pulled from pre-built array
        try:
            arr = inst_descrs[line_numb]
        except:
            on_click(f"Yaml file and log file do not match")
            sys.exit(1)

        # indexes the line number of instruction
        line = arr[0][1]

        # calculates y pos on canvas from line numb,
        # +1 draws everything down the canvas by 1 line
        y = (line_numb+1) * scale_y

        registers = None
        id, command, pc, registers = arr[-1]

        # finds the last value which has a non 0 pipe time
        last = False
        last_stage = None

        # iterates in reverse,
        # looking for the first item without a 0 pipe time
        for count, item in enumerate(reversed(arr[:-1])):
            if item[0] != 0:

                # records its index in the unreversed array
                # by minusing the count and 1 from the arrray
                last_stage = pipe_length- count - 1
                break

        if last_stage == None:
            on_click("invalid log file, "
                     "cycle timings must not all be 0s")
            sys.exit(1)
        # co_ords with descriptor removed,
        # pipe_ind is the pipeline stage number
        # and stages is the x coord before its scaled up
        for pipe_ind, stages in enumerate(arr[:-1]):
            # assigned with scale to tie two together when zooming
            x = stages[0] * scale_x

            # if first value of chunk
            if start_of_plot_flag and x >0:
                start_of_plot_flag = False
                # will dynamically plot y lines
                plot_y_lines(x, y)

            # doesn't plot pipe stages which don't have a cycle number
            if x != 0:
                # plots the shape,
                # last determines when to add line number
                if pipe_ind == last_stage:
                    last = True

                shape_plot(pipe_ind, x, y,
                           id, command, pc, registers,
                           line, last)


def plot_y_lines(x, y):
    """Plots the y lines for each chunk"""

    # defines the bounds left and right
    bound_l, bound_r = x - chunk_size*scale_x*2, x + chunk_size*scale_x*2

    # bounds above and below to reach the previous and next instruction
    bound_a, bound_b = y, y+chunk_size*scale_y

    # iterates between bounds with intervals of the scale_x
    for i in range(bound_l, bound_r, scale_x):
        # Creates vertical lines within the bounds of the chunk
        y_line = canvas.create_line(i, bound_a, i, bound_b,
                                    fill=line_colour, tag="y")
        # sends line to the background
        canvas.tag_lower(y_line)


def draw_key(menu):
    """Draws the key for hiding and showing different pipe stages"""
    # creates the frame for the key inside the menu frame
    key_frame = tk.Frame(menu)

    # sets the size of the shapes in the key
    key_w = shape_size * 4

    # creates a new mini canvas for the textbox shapes,
    # also packs it into the frame
    key_canv = tk.Canvas(key_frame, width=key_w)
    key_canv.pack(side=tk.LEFT, expand=True, fill=tk.Y)
    key_frame.pack(side=tk.TOP)

    # builds dictionary of key shapes
    key_instances = build_shape_instances(key_canv)

    # defines size of the second canvas to plot the shapes to use as a key
    height = 46

    # sets the style (colour, font etc.) to the same as everything else
    key_style = menu_style

    # sets width
    key_style["width"] = 12

    # iterates over the index of each pipe stage
    for i in range(pipe_length):
        # defines the current stage in drawing
        pipe_stage = stage_choice[i]

        # uses the premade dictionary to plot the shapes onto the key canvas
        key_instances[pipe_stage].draw(key_w//2,
                                       i*height+height//2,
                                       tags = stage_choice[i])

        # makes a frame for the buttons, inside the key_frame,
        # which is inside the menu frame
        button_frame = tk.Frame(key_frame, width=key_w, height=height)

        # positions button in frame
        button_frame.pack(side=tk.TOP)

        # sets the style and function of the button
        tk.Button(button_frame, **key_style, text=pipe_stage,
                  command=lambda n=i: hide_stage(n)).pack(side=tk.TOP)
    return key_canv


def hide_stage(stage_ind):
    # identifies stage being hidden/ shown
    shp = stage_choice[stage_ind]

    # finds the current state of the pipe stage
    state = canvas.itemcget(shp, 'state')

    # changes the state variable to it's opposite
    if state == "hidden":
        new_state = "normal"
    else:
        new_state = "hidden"

    # changes wether the stage is hidden or not,
    # for both the canvas and key canvas
    canvas.itemconfig(shp, state=new_state)
    key_canv.itemconfig(shp, state=new_state)


def draw_UI(root):
    global incr_bx, jump_bx

    # creates a frame for the additional textboxes
    menu = tk.Frame(root)

    # positions frame then sets the looks to avoid repeated code
    menu.pack(side=tk.RIGHT)

    # frame for textboxes
    txt_bx_frame = tk.Frame(menu)
    txt_bx_frame.pack(side=tk.TOP)

    # jump to line textbox label instantiated
    # and grouped into the menu frame
    jump_lb = tk.Label(txt_bx_frame, text="Jump to line",
                       font=("Ubuntu Mono", 13))
    jump_lb.pack(side=tk.TOP)

    # instantiates textbox for jumping
    jump_bx = tk.Text(txt_bx_frame, **menu_style)
    jump_bx.insert(tk.END, '1')

    # positions widget
    jump_bx.pack(side=tk.TOP)

    # similar to the jump box label
    incr_lb = tk.Label(txt_bx_frame, text="Scroll amount",
                       font=("Ubuntu Mono", 13))
    incr_lb.pack(side=tk.TOP)

    # similar to jump box text
    incr_bx = tk.Text(txt_bx_frame, **menu_style)
    incr_bx.insert(tk.END, '10')
    incr_bx.pack(side=tk.TOP)

    # empty spacer between boxes
    tk.Label(menu, height=4).pack(side=tk.TOP)

    # draws in the shapes onto the canvas for the key
    key_canv = draw_key(menu)

    # another empty spacer
    tk.Label(menu, height=4).pack(side=tk.TOP)

    # now the zoom buttons are instantiated
    tk.Button(menu, **menu_style, text="Zoom X+",
              command=lambda: zoom(scale_factor, 0)).pack(side=tk.TOP)
    tk.Button(menu, **menu_style, text="Zoom X-",
              command=lambda: zoom(-scale_factor, 0)).pack(side=tk.TOP)
    tk.Button(menu, **menu_style, text="Zoom Y+",
              command=lambda: zoom(0, scale_factor)).pack(side=tk.TOP)
    tk.Button(menu, **menu_style, text="Zoom Y-",
              command=lambda: zoom(0, -scale_factor)).pack(side=tk.TOP)
    tk.Button(menu, **menu_style, text="Zoom XY+",
              command=lambda: zoom(scale_factor,
                                   scale_factor)).pack(side=tk.TOP)
    tk.Button(menu, **menu_style, text="Zoom XY-",
              command=lambda: zoom(-scale_factor,
                                   -scale_factor)).pack(side=tk.TOP)

    # binds event for the scroll wheel to be used
    root.bind("<MouseWheel>", mouse_wheel)

    # binds return key to the function to jump lines
    root.bind('<Return>', jump_to)

    # bind arrow keys
    root.bind('<Left>', pan_left)
    root.bind("<Right>", pan_right)
    root.bind("<Up>", incr_move_up)
    root.bind("<Down>", incr_move_down)

    # instantiates frame w and h there for help to identify it
    trace = tk.Frame(root)

    # expands frame to fill the open window to avoid blank areas
    trace.pack(expand=True, fill=tk.BOTH)

    # hex colours for background
    back_colour = '#BABABA'

    # creates plain canvas in window
    canvas = tk.Canvas(trace, height=1000, width=1700,
                       scrollregion=(0, 0, wnd_x, wnd_y),
                       bg=back_colour, borderwidth=10,
                       relief="ridge", background=back_colour)

    # horizontal scroll bar linked to frame
    hbar = tk.Scrollbar(trace, orient=tk.HORIZONTAL)

    # locates and stretches bar
    hbar.pack(side=tk.BOTTOM, fill=tk.X)

    # configures bar to link to canvas
    hbar.config(command=canvas.xview)

    # identical to hbar
    vbar = tk.Scrollbar(trace, orient=tk.VERTICAL)
    vbar.pack(side=tk.RIGHT, fill=tk.Y)
    vbar.config(command=canvas.yview)

    # sets the scroll bars to the canvas
    canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

    # for drawing maps to lh first and expands past border
    canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

    return canvas, key_canv


# makes a global variable for plot_instr_set function used in heatmap
inst_descrs = analyse_trace(logs)

# reassigns instruction count to the
# number of valid instruction descriptions, generated by analyse trace
instr_count = len(inst_descrs)

# creates the array of PC heats
hot_pcs = find_hot_pcs()

# hex colours for background
line_colour = '#e6e3e3'

# sets menu style for use across all textboxes
menu_style = {"height": 1, "width": 13, "bg": "grey", "fg": "white",
              "border": 5, "font": ("Ubuntu Mono", 15)}

# connects to a tkinter root
root = tk.Tk()
root.title("CPU Trace Viewer")

# command to resize and place tkinter window on the users screen
root.geometry('2000x1300+0+0')

# draws canvas with the size of screen
canvas, key_canv = draw_UI(root)

# Makes a dictionary of shape instances for the canvas and key canvas
instances = build_shape_instances(canvas)

# draws the first chunk
refresh(0)

# runs the heatmap
heatmap(root, hot_pcs)

root.mainloop()  # opens window to run forever until closed by user
