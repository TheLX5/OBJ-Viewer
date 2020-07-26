# OBJ Viewer
A small python script that lets you preview OBJ data if the required files are provided.

### REQUIREMENTS
* Python 3 with Tkinter
* Ttk module for Python (I forgot which version comes with Ttk, newer Python versions have Ttk by default, do your research)

### NOTES
* I'm not very proficient at high level languages so a lot of the code is REALLY bad and poorly thought out
* It's really slow when there's a lot of OAM tiles being drawn on the screen
* It may spam a little bit your console if you go out of bounds of the VRAM area

### DETAILS
Once you open the required files (OBJ/OBX, CGX, COL) under the File menu you can control specific parts of the area:
* The **VRAM Offset** spin box lets you move around the CGX/VRAM file without issues. The controls change the data offset by 64 bytes, but you can input your own offset as well (don't forget to press Enter!).
* The **Animation Frame** spin box lets you control the current animation frame being displayed based on the data from the OBJ file. You can watch up to 128 different frames with no problem (requires opening up .OBX files with the OBJ menu option). You can also input your own animation frame index as well.
* The **Object size** combo box lets you change the size of the tiles as you wish. Most games in the files make use of the default option, but there might be one that uses another option.
* The  **Camera X Offset** and  **Camera Y Offset** lets you pan the camera so you can adjust the current animation being displayed.
* The **Zoom** combo box offers a way to change the zoom level of the sprites on screen.
