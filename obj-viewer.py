##################################################################################
# OBJ-VIewer v1.1

##################################################################################
# Libs

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import webbrowser
import os

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
        if self.decode_cgx():
            cgx_file.set("CGX File: "+os.path.split(self.filename)[-1])
            mainframe.animation_build_frame()
        
    def file_open_col(self):
        self.filename = tk.filedialog.askopenfilename(
                        initialdir="./",
                        title="Select COL file",
                        filetypes=(("SNES Palette File","*.COL"),("All files","*.*"))
                        )
        if self.decode_col():
            col_file.set("COL File: "+os.path.split(self.filename)[-1])
            mainframe.animation_build_frame()

    def file_open_obj(self):
        self.filename = tk.filedialog.askopenfilename(
                        initialdir="./",
                        title="Select OBJ file",
                        filetypes=(("SNES Animation File","*.OBJ"),("All files","*.*"))
                        )
        global obj_loaded
        obj_loaded = 0
        if self.decode_obj():
            obj_file.set("OBJ File: "+os.path.split(self.filename)[-1])
            mainframe.animation_build_frame()

    def file_open_obx(self):
        self.filename = tk.filedialog.askopenfilename(
                        initialdir="./",
                        title="Select OBX file",
                        filetypes=(("SNES Extended Animation File","*.OBX"),("All files","*.*"))
                        )
        global obj_loaded
        obj_loaded = 1
        if self.decode_obj():
            obj_file.set("OBX File: "+os.path.split(self.filename)[-1])
            mainframe.animation_build_frame()

    def links_github(self):
        self.website = "https://github.com/TheLX5/OBJ-Viewer"
        webbrowser.open(self.website,1)

    def links_patreon(self):
        self.website = "https://www.patreon.com/lx5"
        webbrowser.open(self.website,1)

##################################################################################
# Decode data

    def decode_cgx(self):
        try:
            with open(self.filename, "rb") as f:
                self.cgx_data = f.read()
            decoded_cgx.clear()
        except FileNotFoundError:
            return False
        for i in range(len(self.cgx_data)>>5):
            for j in range(8):
                for h in range(8):
                    pixel = 0
                    for l in range(2):
                        for k in range(2):
                            if (self.cgx_data[(i*0x20)+(l*0x10)+(j*2)+k]&(1<<(7-h))) != 0:
                                pixel = pixel|(1<<(l*2+k))
                    decoded_cgx.append(pixel)
        return True
            
                
    def decode_col(self):
        try:
            with open(self.filename, "rb") as f:
                self.col_data = f.read()
            decoded_col.clear()
        except FileNotFoundError:
            return False
        k=0
        for i in range(len(self.col_data)>>1):
            current_color = self.col_data[k]|(self.col_data[k+1]<<8)
            color_red = hex((current_color&31)<<3)[2:].zfill(2)
            color_green = hex(((current_color>>5)&31)<<3)[2:].zfill(2)
            color_blue = hex(((current_color>>10)&31)<<3)[2:].zfill(2)
            color = "#"+color_red+color_green+color_blue
            decoded_col.append(color)
            k = k+2
        return True

    def decode_obj(self):
        try:
            with open(self.filename, "rb") as f:
                self.obj_data = f.read()
            decoded_obj.clear()
        except FileNotFoundError:
            return False

        if obj_loaded == 0:
            obj_range = 0x180
        elif obj_loaded == 1:
            obj_range = 0x300

        for k in range(128):
            decoded_obj["frame "+str(k)] = []
            for i in range(obj_range):
                try:
                    decoded_obj["frame "+str(k)].append(self.obj_data[i+(0x180*k)])
                except:
                    decoded_obj["frame "+str(k)].append(0)
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
        #self.animation_page_frame_2 = tk.Frame(self.animation_page)
        #self.animation_page_frame_3 = tk.Frame(self.animation_page)
    
        self.animation_preview = tk.LabelFrame(self.animation_page_frame_1,text="Animation Preview",padx=5,pady=5)
        self.animation_preview.grid(column=1, row=2, padx=3, pady=3, sticky=tk.N)
        self.animation_preview_widget()
        
        self.animation_page_frame_1.pack(side=tk.LEFT, anchor=tk.N)
        #self.animation_page_frame_2.pack(side=tk.LEFT, anchor=tk.N)
        #self.animation_page_frame_3.pack(side=tk.LEFT, anchor=tk.N)
        
    def animation_preview_widget(self):
        self.frame_frame = tk.Frame(self.animation_preview)

        self.frame_label = tk.Label(self.frame_frame, text="Animation frame:")
        self.frame_label.pack(side=tk.LEFT, padx=3)
        self.frame_num = tk.Spinbox(self.frame_frame,
                                    from_=0, to=127,
                                    increment=1,
                                    width=8,
                                    command=self.animation_build_frame,
                                    textvariable=default_frame)
        self.frame_num.bind("<Return>", self.animation_build_pose_return)
        self.frame_num.pack(side=tk.LEFT)

        self.offset_label = tk.Label(self.frame_frame, text="VRAM Offset:")
        self.offset_label.pack(side=tk.LEFT, padx=3)
        self.offset_num = tk.Spinbox(self.frame_frame,
                                     from_=0, to=65536,
                                     increment=64,
                                     width=8,
                                     command=self.animation_build_frame,
                                     textvariable=default_offset)
        self.offset_num.bind("<Return>", self.animation_build_pose_return)
        self.offset_num.pack(side=tk.LEFT)

        self.size_label = tk.Label(self.frame_frame, text="Object size:")
        self.size_label.pack(side=tk.LEFT,padx=3)
        self.size_num = ttk.Combobox(self.frame_frame,
                                     state="readonly",
                                     values=obj_sizes)
        self.size_num.config(width=15)
        self.size_num.set("8x8 16x16")
        self.size_num.bind("<Return>", self.animation_build_pose_return)
        self.size_num.bind("<<ComboboxSelected>>", self.animation_build_pose_return)
        self.size_num.pack(side=tk.LEFT)

        self.frame_frame.pack(pady=2)


        self.camera_frame = tk.Frame(self.animation_preview)


        self.center_x_label = tk.Label(self.camera_frame, text="Camera X Offset:")
        self.center_x_label.pack(side=tk.LEFT, padx=3)
        self.center_x_num = tk.Spinbox(self.camera_frame,
                                     from_=0, to=512,
                                     increment=1,
                                     width=4,
                                     command=self.animation_build_frame,
                                     textvariable=default_center_x)
        self.center_x_num.bind("<Return>", self.animation_build_pose_return)
        self.center_x_num.pack(side=tk.LEFT)
        
        self.center_y_label = tk.Label(self.camera_frame, text="Camera Y Offset:")
        self.center_y_label.pack(side=tk.LEFT, padx=3)
        self.center_y_num = tk.Spinbox(self.camera_frame,
                                     from_=0, to=512,
                                     increment=1,
                                     width=4,
                                     command=self.animation_build_frame,
                                     textvariable=default_center_y)
        self.center_y_num.bind("<Return>", self.animation_build_pose_return)
        self.center_y_num.pack(side=tk.LEFT)

        self.zoom_label = tk.Label(self.camera_frame, text="Zoom:")
        self.zoom_label.pack(side=tk.LEFT,padx=3)
        self.zoom_num = ttk.Combobox(self.camera_frame,
                                     state="readonly",
                                     values=zoom_values)
        self.zoom_num.config(width=7)
        self.zoom_num.set("x2")
        self.zoom_num.bind("<Return>", self.animation_build_pose_return)
        self.zoom_num.bind("<<ComboboxSelected>>", self.animation_build_pose_return)
        self.zoom_num.pack(side=tk.LEFT)
        
        self.camera_frame.pack(pady=2)


        self.loaded_obj_label = tk.Label(self.animation_preview, textvariable=obj_file)
        self.loaded_obj_label.pack(anchor=tk.W)
        self.loaded_cgx_label = tk.Label(self.animation_preview, textvariable=cgx_file)
        self.loaded_cgx_label.pack(anchor=tk.W)
        self.loaded_col_label = tk.Label(self.animation_preview, textvariable=col_file)
        self.loaded_col_label.pack(anchor=tk.W)

        self.frame_canvas = tk.Canvas(self.animation_preview,width=512,height=512)
        self.frame_canvas.pack()
        self.animation_build_frame()
        
    def animation_build_pose_return(self, event):
        self.animation_build_frame()
        
    def animation_build_frame(self):
        if decoded_cgx != [] and decoded_col != [] and decoded_obj != []:
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
            
            self.frame_canvas.delete("all")
            self.frame_canvas.create_rectangle(0,0,512,512,outline="", fill="#0060B8")

            try:
                frame_number = int(self.frame_num.get())
            except ValueError:
                default_frame.set("0")
                frame_number = 0
                print ("Invalid data in Animation Frame field. Resetting value...")
            try:
                spr_offset = int(self.offset_num.get())
            except ValueError:
                default_offset.set("0")
                spr_offset = 0
                print ("Invalid data in VRAM Offset field. Resetting value...")
                
            try:
                center_x = int(default_center_x.get())
            except:
                default_center_x.set("256")
                center_x = 0
                print ("Invalid data in Camera X Offset field. Resetting value...")
            try:
                center_y = int(default_center_y.get())
            except:
                default_center_y.set("256")
                center_y = 0
                print ("Invalid data in Camera Y Offset field. Resetting value...")

            pal_base = 128
            current_size = size_settings[str(self.size_num.current())]
            current_zoom = zoom_settings[str(self.zoom_num.current())]

            if obj_loaded == 0:
                oam = 63
            elif obj_loaded == 1:
                oam = 127

            for i in range(oam, -1, -1):
                current_obj = decoded_obj["frame "+str(frame_number)]
                if (current_obj[i*6+0] & 0x80) == 0:
                    continue
                size = (current_obj[i*6+0] & 0x01) * 2
                ydisp = current_obj[i*6+2]
                xdisp = current_obj[i*6+3]
                props = current_obj[i*6+4]
                tile = current_obj[i*6+5]

                if xdisp >= 0x80:
                    xdisp = self.twos_comp(xdisp, 8)
                if ydisp >= 0x80:
                    ydisp = self.twos_comp(ydisp, 8)
                offx = xdisp*current_zoom+center_x
                offy = ydisp*current_zoom+center_y

                tile_offset = (((props&1)<<8)+tile)<<6
                tile_pal = ((props&0xF)>>1)*16 + pal_base

                size_x = current_size[0+size]
                size_y = current_size[1+size]
                total_pixels = size_x*size_y

            #Process tiles
            #COULD BE MADE MUCH FASTER BUT I'M BAD AT PROGRAMMING
            #IF IT WORKS, IT WORKS :D
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

            #draw tile
                for y in range(size_y):
                    for x in range(size_x):
                        if px[x+y*size_x] != 0:
                            self.frame_canvas.create_rectangle(offx+x*current_zoom,
                                                               offy+y*current_zoom,
                                                               offx+x*current_zoom+current_zoom,
                                                               offy+y*current_zoom+current_zoom,
                                                               outline="",
                                                               fill=decoded_col[px[x+y*size_x]])

    #taken from stack overflow LOL
    #https://stackoverflow.com/a/9147327
    def twos_comp(self, val, bits):
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val                         # return positive value as is
            
##################################################################################
# MAIN

if __name__ == "__main__":
    root = tk.Tk()

    #setup global vars
    decoded_cgx = []
    decoded_col = []
    decoded_obj = {}

    obj_loaded = 0 
            #valid values
            # 0: OBJ
            # 1: OBX
            # 2: OBZ (not implemented)
    
    obj_file = tk.StringVar()
    obj_file.set("OBJ File: ")
    cgx_file = tk.StringVar()
    cgx_file.set("CGX File: ")
    col_file = tk.StringVar()
    col_file.set("COL File: ")
    default_offset = tk.StringVar()
    default_offset.set("32768")
    default_frame = tk.StringVar()
    default_frame.set("0")
    
    default_center_x = tk.StringVar()
    default_center_x.set("256")
    default_center_y = tk.StringVar()
    default_center_y.set("256")

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
    object_size = tk.StringVar()
    object_size.set(obj_sizes[0])

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
    zoom = tk.StringVar()
    zoom.set(zoom_values[0])

    #setup main frames/parts of the program
    toolbar = Toolbar(root)
    mainframe = MainFrame(root)

    #setup window
    root.title("OBJ Viewer")
    root.geometry("535x663")
    root.resizable(False, False)
    root.mainloop()
