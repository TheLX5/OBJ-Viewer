##################################################################################
# OBJ-VIewer v2.0

##################################################################################
# Libs

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import webbrowser
import os
import time
import shutil

UI_REFRESH = 16 # your preferred refresh rate in milleseconds
UI_DELTA = 0.000001 # nanosecond scale iterative filter step size
UI_DEPTH = 10 # depth of ui_refreshes moving average

##################################################################################
# Toolbar stuff

class Toolbar(tk.Frame):
    def __init__(self, master):
        self.master = master
            
        self.frame = tk.Frame(self.master)
        self.menubar = tk.Menu(self.frame)
        
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open OBJ file", command=self.file_open_obj)
        self.filemenu.add_command(label="Open OBX file", command=self.file_open_obx)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Open CGX file", command=self.file_open_vram)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Open COL file", command=self.file_open_col)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Close", command=root.destroy)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
                
        self.linksmenu = tk.Menu(self.menubar, tearoff=0)
        self.linksmenu.add_command(label="GitHub repo", command=self.links_github)
        self.linksmenu.add_command(label="Patreon page", command=self.links_patreon)
        self.menubar.add_cascade(label="Links", menu=self.linksmenu)
                
        self.master.config(menu=self.menubar)
                
    def file_open_vram(self):
        self.filename = tk.filedialog.askopenfilename(
                        initialdir="./",
                        title="Select CGX file",
                        filetypes=(("SNES Graphics File","*.CGX"),("All files","*.*"))
                        )
        if self.decode_cgx() == True:
            cgx_file_label.set("CGX File")
            cgx_file_path.set(self.filename)

            mainframe.animation_build_pose()

            print ("Succesfully loaded "+self.filename)
        


    def file_open_col(self):
        self.filename = tk.filedialog.askopenfilename(
                        initialdir="./",
                        title="Select COL file",
                        filetypes=(("SNES Palette File","*.COL"),("All files","*.*"))
                        )
        if self.decode_col() == True:
            col_file_label.set("COL File")
            col_file_path.set(self.filename)

            mainframe.animation_build_pose()

            print ("Succesfully loaded "+self.filename)



    def file_open_obj(self):
        self.filename = tk.filedialog.askopenfilename(
                        initialdir="./",
                        title="Select OBJ file",
                        filetypes=(("SNES Animation File","*.OBJ"),("All files","*.*"))
                        )
        global obj_loaded
        global anim_filename
        obj_loaded = 0
        if self.decode_obj() == True:
            anim_filename = os.path.split(self.filename)[-1].split(".")[0]
            obj_file_label.set("OBJ File")
            obj_file_path.set(self.filename)

            mainframe.animation_build_pose()
            mainframe.convert_to_scad_button.state(["!disabled"])

            print ("Succesfully loaded "+self.filename)



    def file_open_obx(self):
        self.filename = tk.filedialog.askopenfilename(
                        initialdir="./",
                        title="Select OBX file",
                        filetypes=(("SNES Extended Animation File","*.OBX"),("All files","*.*"))
                        )
        global obj_loaded
        global anim_filename
        obj_loaded = 1
        if self.decode_obj() == True:
            anim_filename = os.path.split(self.filename)[-1].split(".")[0]
            obj_file_label.set("OBX File")
            obj_file_path.set(self.filename)

            mainframe.animation_build_pose()
            mainframe.convert_to_scad_button.state(["disabled"])

            print ("Succesfully loaded "+self.filename)
            

    def links_github(self):
        self.website = "https://github.com/TheLX5/OBJ-Viewer"
        webbrowser.open(self.website,1)

    def links_patreon(self):
        self.website = "https://www.patreon.com/lx5"
        webbrowser.open(self.website,1)

##################################################################################
# Decode data

    def decode_cgx(self):
        global decoded_cgx, decoded_extra_cgx
        try:
            with open(self.filename, "rb") as f:
                self.cgx_data = f.read()
                self.cgx_data = self.cgx_data[:-0x500]
                f.seek(len(self.cgx_data)+0x100)
                self.extra_cgx_data = f.read()
        except:
            return False
        decoded_cgx.clear()
        for i in range(len(self.cgx_data)>>5):
            for j in range(8):
                for h in range(8):
                    pixel = 0
                    for l in range(2):
                        for k in range(2):
                            if (self.cgx_data[(i*0x20)+(l*0x10)+(j*2)+k]&(1<<(7-h))) != 0:
                                pixel = pixel|(1<<(l*2+k))
                    decoded_cgx.append(pixel)
        
        decoded_extra_cgx = self.extra_cgx_data

        return True
            
                
    def decode_col(self):
        global decoded_col, decoded_extra_col
        try:
            with open(self.filename, "rb") as f:
                self.col_data = f.read()
                self.col_data = self.col_data[:-0x200]
                f.seek(len(self.col_data)+0x100)
                self.extra_col_data = f.read()
        except:
            return False
        k=0
        decoded_col.clear()
        for i in range(len(self.col_data)>>1):
            current_color = self.col_data[k]|(self.col_data[k+1]<<8)
            color_red = (current_color&31) << 3
            color_green = ((current_color>>5)&31) << 3
            color_blue = ((current_color>>10)&31) << 3
            color_alpha = 255
            if i & 0xF == 0:
                color_alpha = 0
            color = (color_red, color_green, color_blue, color_alpha)
            decoded_col.append(color)
            k = k+2

        decoded_extra_col = self.extra_col_data
        
        return True

    def decode_obj(self):
        global decoded_obj, decoded_extra_obj, actual_obj_data

        if obj_loaded == 0:
            obj_range = 0x180
            cut = 0x500
        elif obj_loaded == 1:
            obj_range = 0x300
            cut = 0x900
        
        try:
            with open(self.filename, "rb") as f:
                self.obj_data = f.read()
                actual_obj_data = self.obj_data[:-cut]
                f.seek(len(actual_obj_data)+0x100)
                self.extra_obj_data = f.read()
        except:
            return False

        decoded_obj.clear()

        for k in range(128):
            decoded_obj["frame "+str(k)] = []
            for i in range(obj_range):
                try:
                    decoded_obj["frame "+str(k)].append(self.obj_data[i+(0x180*k)])
                except:
                    decoded_obj["frame "+str(k)].append(0)
        
        decoded_extra_obj = self.extra_obj_data

        return True

            
##################################################################################
# Main window

class MainFrame(tk.Frame):
    def __init__(self, master):
        self.master = master
            
        #create notebook
            #removed tabs, might come back later if i add more stuff to this tool
            #self.tabs = ttk.Notebook(master)
        
            #add Animation Viewer tab
            #self.animation_page = ttk.Frame(self.tabs)
            #self.tabs.add(self.animation_page, text=" Animation Viewer ")
            
        self.animation_tab()
        
            #create tabs
            #self.tabs.pack(expand=1, fill="both")
        
##################################################################################
# Animation configs tab

    def animation_tab(self):
        self.animation_page_frame_1 = tk.Frame(self.master)
        self.animation_page_frame_2 = tk.Frame(self.master)
        #self.animation_page_frame_3 = tk.Frame(self.animation_page)
    
        self.animation_paths = tk.LabelFrame(self.animation_page_frame_1,text="File Paths",padx=5,pady=5)
        self.animation_paths.pack(fill=tk.X, expand=True)
        self.animation_paths_widget()

        self.animation_preview = tk.LabelFrame(self.animation_page_frame_1,text="Frame/Sequence Preview",padx=5,pady=5)
        self.animation_preview.pack(fill=tk.BOTH, expand=True)
        self.animation_preview_widget()

        self.animation_controls = tk.LabelFrame(self.animation_page_frame_2,text="Frame Controls",padx=5,pady=5)
        self.animation_controls.pack(fill=tk.X, expand=True)
        self.animation_controls_widget()

        self.animation_sequence = tk.LabelFrame(self.animation_page_frame_2,text="Sequence Controls",padx=5,pady=5)
        self.animation_sequence.pack(fill=tk.X, expand=True)
        self.animation_sequence_widget()

        self.animation_conversion = tk.LabelFrame(self.animation_page_frame_2,text="Conversion",padx=5,pady=5)
        self.animation_conversion.pack(fill=tk.X, expand=True)
        self.animation_conversion_widget()

        self.animation_background = tk.LabelFrame(self.animation_page_frame_2,text="Background Color",padx=5,pady=5)
        self.animation_background.pack(fill=tk.X, expand=True)
        self.animation_background_widget()
        
        self.animation_page_frame_1.pack(side=tk.LEFT, anchor=tk.N, padx=4)
        self.animation_page_frame_2.pack(side=tk.LEFT, anchor=tk.N, fill=tk.X, expand=True, padx=4)
        #self.animation_page_frame_3.pack(side=tk.LEFT, anchor=tk.N)
        
##################################################################################
# Background colors

    def animation_background_widget(self):
        self.background_controls = tk.Frame(self.animation_background)
        
        i=0

        self.bg_red_label = ttk.Label(self.background_controls, text="Red value")
        self.bg_red_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.bg_red_num = ttk.Spinbox(self.background_controls,
                                      from_=0, to=255,
                                      increment=1,
                                      width=8,
                                      wrap=0,
                                      command=self.background_color_update,
                                      textvariable=default_red_color)
        self.bg_red_num.bind("<Return>", self.background_color_update_return)
        self.bg_red_num.grid(row=i, column=1, padx=3, sticky=tk.W+tk.E)
        i = i+1

        self.bg_green_label = ttk.Label(self.background_controls, text="Green value")
        self.bg_green_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.bg_green_num = ttk.Spinbox(self.background_controls,
                                      from_=0, to=255,
                                      increment=1,
                                      width=8,
                                      wrap=0,
                                      command=self.background_color_update,
                                      textvariable=default_green_color)
        self.bg_green_num.bind("<Return>", self.background_color_update_return)
        self.bg_green_num.grid(row=i, column=1, padx=3, sticky=tk.W+tk.E)
        i = i+1

        self.bg_blue_label = ttk.Label(self.background_controls, text="Blue value")
        self.bg_blue_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.bg_blue_num = ttk.Spinbox(self.background_controls,
                                      from_=0, to=255,
                                      increment=1,
                                      width=8,
                                      wrap=0,
                                      command=self.background_color_update,
                                      textvariable=default_blue_color)
        self.bg_blue_num.bind("<Return>", self.background_color_update_return)
        self.bg_blue_num.grid(row=i, column=1, padx=3, sticky=tk.W+tk.E)
        i = i+1

        self.background_controls.grid_columnconfigure(1, weight=1)
        self.background_controls.pack(anchor=tk.W, pady=2, fill=tk.X, expand=1)
    
    def background_color_update(self):
        global bg_color
        try:
            new_red_color = hex(int(self.bg_red_num.get()))
        except ValueError:
            default_red_color.set("0")
            new_red_color = hex(0)
            print ("Invalid data in Red value field. Resetting value...")
        try:
            new_green_color = hex(int(self.bg_green_num.get()))
        except ValueError:
            default_green_color.set("96")
            new_green_color = hex(96)
            print ("Invalid data in Green value field. Resetting value...")
        try:
            new_blue_color = hex(int(self.bg_blue_num.get()))
        except ValueError:
            default_blue_color.set("184")
            new_blue_color = hex(184)
            print ("Invalid data in Blue value field. Resetting value...")
        
        bg_color = "#"+new_red_color[2:].zfill(2)+new_green_color[2:].zfill(2)+new_blue_color[2:].zfill(2)

        self.frame_canvas.itemconfig(self.background_rectangle, fill=bg_color)

    def background_color_update_return(self, event):
        self.background_color_update()

##################################################################################
# Conversion

    def animation_conversion_widget(self):
        self.frame_conversion = tk.Frame(self.animation_conversion)

        i = 0
        self.convert_to_scad_button = ttk.Button(self.frame_conversion, text="Convert OBJ to SCad OBJ", command=self.convert_to_scad)
        self.convert_to_scad_button.grid(row=i, column=0, padx=3, pady=3, columnspan=2, sticky=tk.W+tk.E)
        self.convert_to_scad_button.state(["disabled"])
        i = i+1

        self.frame_conversion.grid_columnconfigure(1, weight=1)
        self.frame_conversion.pack(anchor=tk.W, pady=2, fill=tk.X, expand=1)

    def convert_to_scad(self):
        global actual_obj_data, obj_loaded, obj_file_path
        if decoded_obj != {}:
            
            with open(obj_file_path.get(), "rb") as f:
                f.seek(len(actual_obj_data))
                self.extra_obj_data = f.read()

            with open("scad-"+anim_filename+".obj", "wb") as f:
                scad_data = []

                j = 0
                if obj_loaded == 0:
                    k = 63
                else:
                    k = 127

                for i in range(int((len(actual_obj_data))/6)):
                    data = [
                        actual_obj_data[k*6+0+j],               # display
                        actual_obj_data[k*6+1+j],               # unknown
                        actual_obj_data[k*6+2+j],               # y-disp
                        actual_obj_data[k*6+3+j],               # x-disp
                        actual_obj_data[k*6+5+j],               # props
                        actual_obj_data[k*6+4+j]]               # tile

                    scad_data = scad_data + data

                    k = k-1
                    if k == -1:
                        if obj_loaded == 0:
                            k = 63
                        else:
                            k = 127
                        j = j+((k+1)*6)
                
                extra_data_range = 0x400*(obj_loaded+1) + 0x100
                for i in range(extra_data_range):
                    scad_data.append(self.extra_obj_data[i])

                f.write(bytes(scad_data))
                f.close()

            print ("Frame and sequence data from "+anim_filename+" converted to be SCad compatible. You can find it the script's directory.")
        else:
            print ("Tried to convert an empty OBJ!")


##################################################################################
# Frame controls

    def animation_controls_widget(self):
        self.frame_frame_controls = tk.Frame(self.animation_controls)

        i = 0

        self.anim_frame_label = ttk.Label(self.frame_frame_controls, text="Frame number")
        self.anim_frame_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.anim_frame_num = ttk.Spinbox(self.frame_frame_controls,
                                          from_=0, to=127,
                                          increment=1,
                                          width=8,
                                          wrap=1,
                                          command=self.animation_build_pose,
                                          textvariable=default_frame)
        self.anim_frame_num.bind("<Return>", self.animation_build_pose_return)
        self.anim_frame_num.grid(row=i, column=1, padx=3, sticky=tk.W+tk.E)
        i = i+1


        self.sequence_start = ttk.Button(self.frame_frame_controls, text="Export frame", command=self.animation_export_frame)
        self.sequence_start.grid(row=i, column=0, padx=3, pady=3, columnspan=2, sticky=tk.W+tk.E)
        i = i+1



        self.frame_controls_sep_1 = ttk.Separator(self.frame_frame_controls, orient="horizontal")
        self.frame_controls_sep_1.grid(row=i, column=0, padx=3, pady=3, columnspan=2, sticky=tk.W+tk.E)
        i = i+1



        self.offset_label = ttk.Label(self.frame_frame_controls, text="VRAM Offset")
        self.offset_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.offset_num = ttk.Spinbox(self.frame_frame_controls,
                                      from_=0, to=65536,
                                      increment=32,
                                      width=8,
                                      wrap=1,
                                      command=self.animation_build_pose,
                                      textvariable=default_offset)
        self.offset_num.bind("<Return>", self.animation_build_pose_return)
        self.offset_num.grid(row=i, column=1, padx=3, sticky=tk.W+tk.E)
        i = i+1


        self.cgram_label = ttk.Label(self.frame_frame_controls, text="CGRAM Offset")
        self.cgram_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.cgram_num = ttk.Spinbox(self.frame_frame_controls,
                                     from_=0, to=128,
                                     increment=16,
                                     width=8,
                                     wrap=1,
                                     command=self.animation_build_pose,
                                     textvariable=default_cgram)
        self.cgram_num.bind("<Return>", self.animation_build_pose_return)
        self.cgram_num.grid(row=i, column=1, padx=3, sticky=tk.W+tk.E)
        i = i+1


        self.size_label = ttk.Label(self.frame_frame_controls, text="Object size")
        self.size_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.size_num = ttk.Combobox(self.frame_frame_controls,
                                     state="readonly",
                                     values=obj_sizes)
        self.size_num.config(width=15)
        self.size_num.set("8x8 16x16")
        self.size_num.bind("<Return>", self.animation_build_pose_return)
        self.size_num.bind("<<ComboboxSelected>>", self.animation_build_pose_return)
        self.size_num.grid(row=i, column=1, padx=3, sticky=tk.W+tk.E)
        i = i+1




        self.frame_controls_sep_2 = ttk.Separator(self.frame_frame_controls, orient="horizontal")
        self.frame_controls_sep_2.grid(row=i, column=0, padx=3, pady=3, columnspan=2, sticky=tk.W+tk.E)
        i = i+1


        self.center_x_label = ttk.Label(self.frame_frame_controls, text="Camera X Offset")
        self.center_x_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.center_x_num = ttk.Spinbox(self.frame_frame_controls,
                                        from_=0, to=512,
                                        increment=4,
                                        width=4,
                                        wrap=1,
                                        command=self.animation_build_pose,
                                        textvariable=default_center_x)
        self.center_x_num.bind("<Return>", self.animation_build_pose_return)
        self.center_x_num.grid(row=i, column=1, padx=3, pady=3, sticky=tk.W+tk.E)
        i = i+1


        self.center_y_label = ttk.Label(self.frame_frame_controls, text="Camera Y Offset")
        self.center_y_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.center_y_num = ttk.Spinbox(self.frame_frame_controls,
                                        from_=0, to=512,
                                        increment=4,
                                        width=4,
                                        wrap=1,
                                        command=self.animation_build_pose,
                                        textvariable=default_center_y)
        self.center_y_num.bind("<Return>", self.animation_build_pose_return)
        self.center_y_num.grid(row=i, column=1, padx=3, pady=3, sticky=tk.W+tk.E)
        i = i+1


        self.zoom_label = ttk.Label(self.frame_frame_controls, text="Zoom")
        self.zoom_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.zoom_num = ttk.Combobox(self.frame_frame_controls,
                                     state="readonly",
                                     values=zoom_values)
        self.zoom_num.config(width=7)
        self.zoom_num.set("x2")
        self.zoom_num.bind("<Return>", self.animation_build_pose_return)
        self.zoom_num.bind("<<ComboboxSelected>>", self.animation_build_pose_return)
        self.zoom_num.grid(row=i, column=1, padx=3, pady=3, sticky=tk.W+tk.E)
        i = i+1

        self.frame_controls_sep_4 = ttk.Separator(self.frame_frame_controls, orient="horizontal")
        self.frame_controls_sep_4.grid(row=i, column=0, padx=3, pady=3, columnspan=2, sticky=tk.W+tk.E)
        i = i+1




        self.sequence_stop = ttk.Button(self.frame_frame_controls, text="Reset configuration", command=self.animation_reset_values)
        self.sequence_stop.grid(row=i, column=0, padx=3, pady=3, columnspan=2, sticky=tk.W+tk.E)
        i = i+1



        self.frame_frame_controls.grid_columnconfigure(1, weight=1)
        self.frame_frame_controls.pack(anchor=tk.W, pady=2, fill=tk.X, expand=1)

    def animation_export_frame(self):
        if (decoded_cgx != []) & (decoded_col != []) & (decoded_obj != {}):
            print ("Dumping current frame...")
            
            obj_frame = self.create_frame(int(self.anim_frame_num.get()), 0)
            obj_frame.save("exported_frame_"+anim_filename+".png")
            
            print ("Done!")
        else:
            print ("Cannot dump the current frame, load the required COL, CGX and OBJ files.")

    def animation_reset_values(self):
        global default_center_x, default_center_y, default_cgram, default_frame
        global default_offset, zoom, object_size, obj_sizes, zoom_values

        default_offset.set("16384")
        default_cgram.set("128")
        default_frame.set("0")
        default_center_x.set("256")
        default_center_y.set("256")
        object_size.set(obj_sizes[0])
        self.size_num.set(obj_sizes[0])
        zoom.set(zoom_values[0])
        self.zoom_num.set(zoom_values[1])

        self.animation_build_frame()

    def animation_build_pose(self):
        self.animation_build_frame()

    def animation_build_pose_return(self, event):
        self.animation_build_frame()
        
    def animation_build_frame(self):
        if (decoded_cgx != []) & (decoded_col != []) & (decoded_obj != {}):
            try:
                frame_number = int(self.anim_frame_num.get())
            except ValueError:
                default_frame.set("0")
                frame_number = 0
                print ("Invalid data in Frame number field. Resetting value...")

            print ("Showing frame "+str(frame_number))

            global bg_color
            self.frame_canvas.delete("all")
            self.background_rectangle = self.frame_canvas.create_rectangle(0,0,512,512, outline="", fill=bg_color)
            self.frame_canvas.create_image(256, 256, image=self.create_frame(frame_number, 1))

##################################################################################
# File paths

    def animation_paths_widget(self):
        self.frame_file_indicators = tk.Frame(self.animation_paths)
        i = 0

        self.loaded_obj_label = ttk.Label(self.frame_file_indicators, textvariable=obj_file_label)
        self.loaded_obj_label.grid(row=i, column=0, pady=3, sticky=tk.W)
        self.loaded_obj_entry = ttk.Entry(self.frame_file_indicators, textvariable=obj_file_path)
        self.loaded_obj_entry.grid(row=i, column=1, pady=3, sticky=tk.W+tk.E)
        i = i+1


        self.loaded_cgx_label = ttk.Label(self.frame_file_indicators, textvariable=cgx_file_label)
        self.loaded_cgx_label.grid(row=i, column=0, pady=3, sticky=tk.W)
        self.loaded_cgx_entry = ttk.Entry(self.frame_file_indicators, textvariable=cgx_file_path)
        self.loaded_cgx_entry.grid(row=i, column=1, pady=3, sticky=tk.W+tk.E)
        i = i+1


        self.loaded_col_label = ttk.Label(self.frame_file_indicators, textvariable=col_file_label)
        self.loaded_col_label.grid(row=i, column=0, sticky=tk.W)
        self.loaded_col_entry = ttk.Entry(self.frame_file_indicators, textvariable=col_file_path)
        self.loaded_col_entry.grid(row=i, column=1, pady=3, sticky=tk.W+tk.E)
        i = i+1
        

        self.frame_file_indicators.grid_columnconfigure(1, weight=1)

        self.frame_file_indicators.pack(fill=tk.X, expand=1)


##################################################################################
# Frame/Sequence Preview

    def animation_preview_widget(self):
        self.frame_canvas = tk.Canvas(self.animation_preview, width=512, height=512)
        self.frame_canvas.pack(fill=tk.BOTH, expand=1)
        self.frame_canvas.delete("all")
        self.background_rectangle = self.frame_canvas.create_rectangle(0,0,512,512, outline="", fill=bg_color)

##################################################################################
# Sequence controls

    def animation_sequence_widget(self):
        self.frame_sequence = tk.Frame(self.animation_sequence)
        i = 0


        self.sequence_label = ttk.Label(self.frame_sequence, text="Sequence number")
        self.sequence_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.sequence_num = ttk.Spinbox(self.frame_sequence,
                                        from_=0, to=15,
                                        increment=1,
                                        width=4,
                                        wrap=1,
                                        textvariable=default_sequence_num)
        self.sequence_num.grid(row=i, column=1, padx=3, pady=3, sticky=tk.W+tk.E)
        i = i+1

        self.sequence_loop_label = ttk.Label(self.frame_sequence, text="Loops")
        self.sequence_loop_label.grid(row=i, column=0, padx=3, pady=3, sticky=tk.W)
        self.sequence_loop_num = ttk.Spinbox(self.frame_sequence,
                                             from_=0, to=16,
                                             increment=1,
                                             width=4,
                                             wrap=1,
                                             textvariable=default_sequence_loop_num)
        self.sequence_loop_num.grid(row=i, column=1, padx=3, pady=3, sticky=tk.W+tk.E)
        i = i+1


        self.sequence_start_btn = ttk.Button(self.frame_sequence, text="Start Sequence", command=self.sequence_start_button)
        self.sequence_start_btn.grid(row=i, column=0, padx=3, pady=3, columnspan=2, sticky=tk.W+tk.E)
        i = i+1

        self.sequence_stop_btn = ttk.Button(self.frame_sequence, text="Stop Sequence", command=self.sequence_stop_button)
        self.sequence_stop_btn.grid(row=i, column=0, padx=3, pady=3, columnspan=2, sticky=tk.W+tk.E)
        self.sequence_stop_btn.state(["disabled"])
        i = i+1




        self.frame_sequence_sep_1 = ttk.Separator(self.frame_sequence, orient="horizontal")
        self.frame_sequence_sep_1.grid(row=i, column=0, padx=3, pady=3, columnspan=2, sticky=tk.W+tk.E)
        i = i+1



        self.sequence_frames = ttk.Button(self.frame_sequence, text="Export Sequence frames", command=self.sequence_export_frames)
        self.sequence_frames.grid(row=i, column=0, padx=3, pady=3, columnspan=2, sticky=tk.W+tk.E)
        self.sequence_frames.state(["disabled"])
        i = i+1

        self.frame_sequence.grid_columnconfigure(1, weight=1)
        self.frame_sequence.pack(anchor=tk.W, pady=2, fill=tk.X, expand=1)


    def sequence_export_frames(self):
        global frames
        print ("---- DUMPING SEQUENCE FRAMES ----")
        self.sequence_stop_button()
        if self.create_animated_image(1):
            print ("Dumped "+str(len(frames))+" frames from sequence "+self.sequence_num.get()+" successfully!")
        else:
            print ("Cannot dump frames, load the required COL, CGX and OBJ files")

    def sequence_start_button(self):
        global current_playback
        print ("---- SEQUENCE PLAYBACK ----")
        if self.create_animated_image(0):
            self.sequence_start_btn.state(["disabled"])
            self.sequence_stop_btn.state(["!disabled"])
            self.sequence_frames.state(["!disabled"])

            for child in self.frame_frame_controls.winfo_children():
                child.state(["disabled"])
        else:
            print ("Cannot play sequence data, load the required COL, CGX and OBJ files")

    def sequence_stop_button(self):
        global current_playback, bg_color

        if current_playback:
            self.frame_canvas.after_cancel(current_playback)
            current_playback = None

            self.sequence_start_btn.state(["!disabled"])
            self.sequence_stop_btn.state(["disabled"])
            self.sequence_frames.state(["disabled"])

            for child in self.frame_frame_controls.winfo_children():
                child.state(["!disabled"])

            self.frame_canvas.delete("all")
            self.background_rectangle = self.frame_canvas.create_rectangle(0,0,512,512, outline="", fill=bg_color)

            self.animation_build_frame()
        

    def create_animated_image(self, get_images):
        if (decoded_cgx != []) & (decoded_col != []) & (decoded_obj != {}):
            global frames, current_playback, last_image, sequence_loop, default_sequence_loop_num, obj_loaded

            try:
                current_sequence = int(self.sequence_num.get())
            except ValueError:
                default_frame.set("0")
                current_sequence = 0
                print ("Invalid data in Frame number field. Resetting value...")
            if get_images == 0:    
                try:
                    sequence_loop = int(self.sequence_loop_num.get())
                except ValueError:
                    default_sequence_loop_num.set("0")
                    sequence_loop = 0
                    print ("Invalid data in Frame number field. Resetting value...")

                if sequence_loop == 0:
                    sequence_loop = None

            j=0
            frames = []
            if get_images == 1:
                try:
                    os.mkdir("exported_frames_"+anim_filename)
                    print ("Creating directory...")
                except OSError:
                    shutil.rmtree("exported_frames_"+anim_filename)
                    os.mkdir("exported_frames_"+anim_filename)
                    print ("Directory exists, removing files inside it...")
                print ("Creating frames for image dump...")
            else:
                print ("Creating frames for sequence playback...")

            if obj_loaded == 0:
                frames_in_sequences = 32
            else:
                frames_in_sequences = 64

            for x in range(frames_in_sequences):
                index = (current_sequence*0x40*(obj_loaded+1)) + (x*2)
                duration = decoded_extra_obj[index]
                frame_num = decoded_extra_obj[index+1]
                if (duration == 0) & (frame_num == 0):
                    break
                for k in range(duration):
                    obj_frame = self.create_frame(frame_num, 1^get_images)
                    if get_images == 1:
                        obj_frame.save("exported_frames_"+anim_filename+"/frame_"+str(j).zfill(4)+".png")
                    frames.append(obj_frame)
                    j=j+1

            if get_images == 0:
                if sequence_loop is None:
                    print ("Playing sequence "+str(current_sequence)+" from "+obj_file_path.get())
                else:
                    print ("Playing sequence "+str(current_sequence)+" from "+obj_file_path.get()+" "+str(sequence_loop)+" times.")
                last_image = 0
                current_playback = self.frame_canvas.after(0, self.play_animation)

            return 1
        return None

    def play_animation(self):
        global last_refresh, ui_refreshes, last_refresh, ui_delta, last_image, frames, current_playback, sequence_loop, bg_color

        now = time.time()
        ui_refreshes.append(now-last_refresh)
        ui_refreshes = ui_refreshes[-UI_DEPTH:]
        ui_refresh = sum(ui_refreshes) / len(ui_refreshes)
        last_refresh = now
        refresh_error = abs(UI_REFRESH_SEC-ui_refresh)
        if float('%.5f' % ui_refresh) < (UI_REFRESH_SEC):
            ui_delta += UI_DELTA
        if float('%.5f' % ui_refresh) > (UI_REFRESH_SEC):
            ui_delta -= UI_DELTA

        #do
        
        self.frame_canvas.delete("all")
        self.background_rectangle = self.frame_canvas.create_rectangle(0,0,512,512, outline="", fill=bg_color)
        self.frame_canvas.create_image(256, 256, image=frames[last_image])
        last_image = last_image+1
        if last_image >= len(frames):
            last_image = 0
            if sequence_loop is not None:
                if sequence_loop != 0:
                    sequence_loop = sequence_loop-1

        pause = int(1000 *
                    min(UI_REFRESH_SEC, (
                        max(0, (
                            2 * UI_REFRESH_SEC - ui_refresh + ui_delta)))))
        if sequence_loop is None:
            self.frame_canvas.after_cancel(current_playback)
            current_playback = self.frame_canvas.after(pause, self.play_animation)
        elif sequence_loop > 0:
            self.frame_canvas.after_cancel(current_playback)
            current_playback = self.frame_canvas.after(pause, self.play_animation)
        else:
            self.sequence_stop_button()


##################################################################################
# General methods

    def create_frame(self, current_frame_number, convert):
        global main_image
        
        main_image = Image.new('RGBA', (512, 512))

        try:
            spr_offset = int(self.offset_num.get())*2
        except ValueError:
            default_offset.set("0")
            spr_offset = 0
            print ("Invalid data in VRAM Offset field. Resetting value...")
            
        try:
            center_x = int(default_center_x.get())
        except:
            default_center_x.set("256")
            center_x = 256
            print ("Invalid data in Camera X Offset field. Resetting value...")
        try:
            center_y = int(default_center_y.get())
        except:
            default_center_y.set("256")
            center_y = 256
            print ("Invalid data in Camera Y Offset field. Resetting value...")

        current_obj = decoded_obj["frame "+str(current_frame_number)]

        try:
            pal_base = int(default_cgram.get())
        except:
            default_cgram.set("128")
            pal_base = 128
            print ("Invalid data in CGRAM Offset field. Resetting value...")


        current_size = size_settings[str(self.size_num.current())]
        current_zoom = zoom_settings[str(self.zoom_num.current())]

        if obj_loaded == 0:
            oam = 63
        elif obj_loaded == 1:
            oam = 127

        k = 0
        for i in range(oam, -1, -1):
            if (current_obj[i*6+0] & 0x80) == 0:
                continue
            size = (current_obj[i*6+0] & 0x01) * 2
            ydisp = current_obj[i*6+2]
            xdisp = current_obj[i*6+3]
            props = current_obj[i*6+4]
            tile = current_obj[i*6+5]

            tile_offset = (((props&1)<<8)+tile)<<6
            tile_pal = ((props&0xF)>>1)*16 + pal_base

            size_x = current_size[0+size]
            size_y = current_size[1+size]
            total_pixels = size_x*size_y

            px = []
            for a in range(total_pixels):
                px.append(0)
            try:
                for n in range(size_y):
                    for m in range(size_x):
                        px_col = m&0x7
                        px_row = (n&0x7)*(1<<3)
                        tile_col = (m&0xFFF8)*(1<<3)
                        tile_row = (n&0xFFF8)*(1<<7)
                        l = spr_offset + tile_offset + tile_col + tile_row + px_col + px_row
                        if decoded_cgx[l] == 0:
                            px[m+(n*size_x)] = 0
                        else:
                            px[m+(n*size_x)] = decoded_cgx[l] + tile_pal
            except IndexError:
                        print ("Exceeded limits of CGX file. Change the VRAM Offset.")

            if props&0x80 != 0:
                #y-flip tile if needed
                t = 0
                v = len(px)-size_x
                old_px = px.copy()
                for u in range(len(px)):
                    if u&size_x != t:
                        v=v-(size_x*2)
                    t=u&size_x
                    px[u] = old_px[v]
                    v=v+1

            if props&0x40 != 0:
                #x-flip tile if needed
                t = 0
                v = size_x-1
                old_px = px.copy()
                s = total_pixels-size_x
                for u in range(len(px)):
                    if u&s != t:
                        v=size_x-1
                    t=u&s
                    px[u] = old_px[t+v]
                    v=v-1

        #generate tile image
            current_image = Image.new('RGBA', (size_x, size_y))
            current_image_pixels = current_image.load()

            if xdisp >= 0x80:
                xdisp = self.twos_comp(xdisp, 8)
            if ydisp >= 0x80:
                ydisp = self.twos_comp(ydisp, 8)

            offx = xdisp*current_zoom+center_x
            offy = ydisp*current_zoom+center_y

            for y in range(size_y):
                for x in range(size_x):
                    if px[x+y*size_x] != 0:
                        try:
                            current_image_pixels[x, y] = decoded_col[px[x+y*size_x]]
                        except:
                            pass
            
            current_image = current_image.resize((size_x*current_zoom, size_y*current_zoom), Image.NEAREST)
            main_image.paste(current_image, (offx, offy), current_image)
            k=k+1
        
        if convert == 1:
            main_image = ImageTk.PhotoImage(image=main_image)

        return main_image


    #taken from stack overflow
    #https://stackoverflow.com/a/9147327
    def twos_comp(self, val, bits):
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val                         # return positive value as is
            
##################################################################################
# MAIN

if __name__ == "__main__":
    root = tk.Tk()

    obj_sizes = [
        "8x8 16x16",
        "8x8 32x32",
        "8x8 64x64",
        "16x16 32x32",
        "16x16 64x64",
        "32x32 64x64",
        "16x32 32x64",
        "16x32 32x32"
    ]

    zoom_values = [
        "x1",
        "x2",
        "x3",
        "x4",
        "x5",
        "x6",
        "x7",
        "x8"
    ]

    size_settings = {
        "0": [8,8,16,16],
        "1": [8,8,32,32],
        "2": [8,8,64,64],
        "3": [16,16,32,32],
        "4": [16,16,64,64],
        "5": [32,32,64,64],
        "6": [16,32,32,64],
        "7": [16,32,32,32]
    }
    zoom_settings = {
        "0": 1,
        "1": 2,
        "2": 3,
        "3": 4,
        "4": 5,
        "5": 6,
        "6": 7,
        "7": 8
    }

    #setup global vars
    decoded_cgx = []
    decoded_extra_cgx = []
    decoded_col = []
    decoded_extra_col = []
    decoded_obj = {}
    actual_obj_data = b""
    decoded_extra_obj = []

    main_image = ""
    anim_filename = ""
    current_image = ""
    last_image = None
    frames = []

    current_playback = None
    UI_REFRESH_SEC = UI_REFRESH/1000
    ui_refreshes = []
    last_refresh = time.time()
    ui_delta = 0
    obj_loaded = 0 
            #valid values
            # 0: OBJ
            # 1: OBX
            # 2: OBZ (not implemented)
    
    obj_file_label = tk.StringVar()
    obj_file_label.set("OBJ File")
    obj_file_path = tk.StringVar()
    obj_file_path.set("")
    
    cgx_file_label = tk.StringVar()
    cgx_file_label.set("CGX File")
    cgx_file_path = tk.StringVar()
    cgx_file_path.set("")
    
    col_file_label = tk.StringVar()
    col_file_label.set("COL File")
    col_file_path = tk.StringVar()
    col_file_path.set("")

    default_offset = tk.StringVar()
    default_offset.set("16384")
    default_cgram = tk.StringVar()
    default_cgram.set("128")
    default_frame = tk.StringVar()
    default_frame.set("0")
    
    default_center_x = tk.StringVar()
    default_center_x.set("256")
    default_center_y = tk.StringVar()
    default_center_y.set("256")

    object_size = tk.StringVar()
    object_size.set(obj_sizes[0])

    zoom = tk.StringVar()
    zoom.set(zoom_values[0])

    
    default_sequence_num = tk.StringVar()
    default_sequence_num.set("0")
    default_sequence_loop_num = tk.StringVar()
    default_sequence_loop_num.set("0")
    sequence_loop = None

    default_red_color = tk.StringVar()
    default_red_color.set("00")
    default_blue_color = tk.StringVar()
    default_blue_color.set("184")
    default_green_color = tk.StringVar()
    default_green_color.set("96")
    bg_color = "#0060B8"

    #setup main frames/parts of the program
    toolbar = Toolbar(root)
    mainframe = MainFrame(root)

    #setup window
    root.title("OBJ Viewer")
    root.geometry("790x659")
    root.resizable(False, False)
    root.mainloop()
