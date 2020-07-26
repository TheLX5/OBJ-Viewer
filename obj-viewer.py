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
                        filetypes=(("SNES Palette File","*.COL"),("All files","*,*"))
                        )
        if self.decode_col():
            col_file.set("COL File: "+os.path.split(self.filename)[-1])
            mainframe.animation_build_frame()

    def file_open_obj(self):
        self.filename = tk.filedialog.askopenfilename(
                        initialdir="./",
                        title="Select OBJ file",
                        filetypes=(("SNES Animation File","*.OBJ"),("All files","*,*"))
                        )
        if self.decode_obj():
            obj_file.set("OBJ File: "+os.path.split(self.filename)[-1])
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
        for k in range(128):
            decoded_obj["frame "+str(k)] = []
            for i in range(0x180):
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
        self.offset_label = tk.Label(self.frame_frame, text="VRAM Offset: ")
        self.offset_label.pack(side=tk.LEFT)
        self.offset_num = tk.Spinbox(self.frame_frame,
                                     from_=0, to=65536,
                                     increment=64,
                                     command=self.animation_build_frame,
                                     textvariable=default_offset)
        self.offset_num.bind("<Return>", self.animation_build_pose_return)
        self.offset_num.pack(side=tk.LEFT)
        self.frame_label = tk.Label(self.frame_frame, text="Animation frame: ")
        self.frame_label.pack(side=tk.LEFT)
        self.frame_num = tk.Spinbox(self.frame_frame,
                                    from_=0, to=127,
                                    increment=1,
                                    command=self.animation_build_frame,
                                    textvariable=default_frame)
        self.frame_num.bind("<Return>", self.animation_build_pose_return)
        self.frame_num.pack(side=tk.LEFT)
        self.frame_frame.pack()
        self.loaded_obj_label = tk.Label(self.animation_preview, textvariable=obj_file)
        self.loaded_obj_label.pack()
        self.loaded_col_label = tk.Label(self.animation_preview, textvariable=col_file)
        self.loaded_col_label.pack()
        self.loaded_cgx_label = tk.Label(self.animation_preview, textvariable=cgx_file)
        self.loaded_cgx_label.pack()

        self.frame_canvas = tk.Canvas(self.animation_preview,width=512,height=512)
        self.frame_canvas.pack()
        self.animation_build_frame()
        
    def animation_build_pose_return(self, event):
        self.animation_build_frame()
        
    def animation_build_frame(self):
        if decoded_cgx != [] and decoded_col != [] and decoded_obj != []:
            self.frame_canvas.delete("all")
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
            self.frame_canvas.create_rectangle(0,0,512,512,outline="", fill="#0060B8")
            for i in range(63, -1, -1):
                if (decoded_obj["frame "+str(frame_number)][(i)*6+0] & 0x80) == 0:
                    continue
                size = decoded_obj["frame "+str(frame_number)][(i)*6+0] & 0x01
                ydisp = decoded_obj["frame "+str(frame_number)][(i)*6+2]
                xdisp = decoded_obj["frame "+str(frame_number)][(i)*6+3]
                props = decoded_obj["frame "+str(frame_number)][(i)*6+4]
                tile = decoded_obj["frame "+str(frame_number)][(i)*6+5]
                pal_base = 128
                px = []
                center_x = 224
                center_y = 256
                if xdisp >= 0x80:
                    xdisp = self.twos_comp(xdisp, 8)
                if ydisp >= 0x80:
                    ydisp = self.twos_comp(ydisp, 8)
                offx = xdisp*2+center_x
                offy = ydisp*2+center_y
                tile_offset = (((props&1)<<8)+tile)<<6
                tile_pal = ((props&0xF)>>1)*16
                #print("size "+str(size)+"      offx: "+str(offx)+" offy:  "+str(offy)+"    xdisp: "+str(xdisp)+" ydisp: "+str(ydisp))


                if size == 1:

                    #Process tiles of 16x16
                    #COULD BE MADE SMALLER BUT I'M BAD AT PROGRAMMING
                    #IF IT WORKS, IT WORKS :D
                    for a in range(256):
                        px.append(0)
                    try:
                        for n in range(16):
                            for m in range(16):
                                px_col = m&7
                                px_row = (n&7)*(1<<3)
                                tile_col = (m&0x8)*(1<<3)
                                tile_row = (n&0x8)*(1<<7)
                                l = spr_offset+tile_offset+px_col+px_row+tile_col+tile_row
                                if decoded_cgx[l] == 0:
                                    px[m+(n*16)] = 0
                                else:
                                    px[m+(n*16)] = (decoded_cgx[l])+pal_base+tile_pal
                                #print("Pixel: "+str(px[m+(n*16)])+" "+str(m+(n*16)))
                                #print("Indices: "+str(px_col)+" "+str(px_row)+"   "+str(tile_col)+" "+str(tile_row))
                    except IndexError:
                                print ("Exceeded limits of CGX file. Change the VRAM Offset.")

                    if props&0x80 != 0:
                        #y-flip tile if needed
                        t = 0
                        v = len(px)-16
                        old_px = px.copy()
                        for u in range(len(px)):
                            if u&16 != t:
                                v=v-32
                            t=u&16
                            px[u] = old_px[v]
                            v=v+1

                    if props&0x40 != 0:
                        #x-flip tile if needed
                        t = 0
                        v = 15
                        s = 0
                        old_px = px.copy()
                        for u in range(len(px)):
                            if u&16 != t:
                                v=15
                            t=u&16
                            px[u] = old_px[t+v]
                            v=v-1
                    
                #draw tile
                    for y in range(16):
                        for x in range(16):
                            if px[x+y*16] != 0:
                                self.frame_canvas.create_rectangle(offx+x*2,offy+y*2,offx+x*2+2,offy+y*2+2,
                                                                   outline="",
                                                                   fill=decoded_col[px[x+y*16]])
                    #return
                else:
                    #Process tiles of 8x8
                    #COULD BE MADE SMALLER BUT I'M BAD AT PROGRAMMING
                    #IF IT WORKS, IT WORKS :D
                    for a in range(64):
                        px.append(0)
                    try:
                        for n in range(8):
                            for m in range(8):
                                px_col = m&7
                                px_row = (n&7)*(1<<3)
                                tile_col = (m&0x8)*(1<<3)
                                tile_row = (n&0x8)*(1<<7)
                                l = spr_offset+tile_offset+px_col+px_row+tile_col+tile_row
                                if decoded_cgx[l] == 0:
                                    px[m+(n*8)] = 0
                                else:
                                    px[m+(n*8)] = (decoded_cgx[l])+pal_base+tile_pal
                                #print("Pixel: "+str(px[m+(n*16)])+" "+str(m+(n*16)))
                                #print("Indices: "+str(px_col)+" "+str(px_row)+"   "+str(tile_col)+" "+str(tile_row))
                    except IndexError:
                                print ("Exceeded limits of CGX/VRAM file. Change the VRAM Offset.")

                    if props&0x80 != 0:
                        #y-flip tile if needed
                        t = 0
                        v = len(px)-8
                        old_px = px.copy()
                        for u in range(len(px)):
                            if u&8 != t:
                                v=v-16
                            t=u&8
                            px[u] = old_px[v]
                            v=v+1

                    if props&0x40 != 0:
                        #x-flip tile if needed
                        t = 0
                        v = 7
                        s = 0
                        old_px = px.copy()
                        for u in range(len(px)):
                            if u&0x38 != t:
                                v=7
                            t=u&0x38
                            #print ("u: "+str(u)+"   u&7: "+str(u&0x7)+"  v: "+str(v)+"  t: "+str(t)+"    t+v: "+str(t+v))
                            px[u] = old_px[t+v]
                            v=v-1
                    
                #draw tile
                    for y in range(8):
                        for x in range(8):
                            if px[x+y*8] != 0:
                                self.frame_canvas.create_rectangle(offx+x*2,offy+y*2,offx+x*2+2,offy+y*2+2,
                                                                   outline="",
                                                                   fill=decoded_col[px[x+y*8]])

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

    #setup main frames/parts of the program
    toolbar = Toolbar(root)
    mainframe = MainFrame(root)

    #setup window
    root.title("OBJ Viewer")
    root.geometry("535x635")
    root.resizable(False, False)
    root.mainloop()
