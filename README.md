# OBJ Viewer
A python script that lets you preview frames and animations from SNES OBJ files if the required files are provided.

## Requirements
* Python 3 with Tkinter
* Ttk module for Python (I forgot which version comes with Ttk, newer Python versions have Ttk by default, do your research)
* Pillow module for Python (`python -m pip install pillow` or `pip3 install pillow`)

## Notes
* I'm not very proficient at high level languages so a lot of the code is REALLY bad and poorly thought out
* It may spam a little bit your console if you go out of bounds of the VRAM area
* OBX files are **PARTIALLY** supported at this moment. They make use of the second byte on each entry which is currently unknown to me.
* Opening files while CGX Preview and/or COL Preview windows are active will **SLOW DOWN** the loading of such files, this also applies when changing the CGRAM Offset.

## Program details

#### General
You can use the UP and DOWN keys to quickly change the Spin boxes.
The sequence playback should be very potato friendly loading a sequence however, it's kinda slow.

#### File Paths
The current loaded files will show their full path in this section. You can freely copy its contents and trim them if necessary.

#### Frame/Sequence Preview
Canvas where the current loaded frame or sequence are shown.

#### Frame Controls
This whole section lets you control the current frame if no sequences are playing.
* **Frame number**: This lets you to control which frame is shown on the preview area.
* **Export frame**: Exports the current frame without background as a **.png** file in the script's directory.
* **VRAM Offset**: Controls the current offset in VRAM, in other words, it lets you move around the CGX/VRAM file without issues. Useful offsets: 0, 8192, 16384, 24576 (will display warnings)
* **CGRAM Offset**: Controls the current offset in CGRAM, in other words, it lets you move around the COL file.
* **Object size**: Determines the OAM size for the tiles displayed on the preview area. This rarely changes, but you're free to experiment.
* **Camera X Offset**: Horizonal position of the animation on the preview area.
* **Camera Y Offset**: Vertical position of the animation on the preview area.
* **Zoom**: Current zoom on the tiles being shown.
* **Reset configuration**: Resets the whole Frame Controls area to their default values.

#### Sequence Controls
Here you can play sequences of frames embedded on the OBJ and OBX files.
* **Sequence number**: Which sequence should be played.
* **Loops**: Number of times the sequence should be repeated. Setting it to 0 will cause the animation to play forever.
* **Start Sequence**: Starts the current selected sequence and displays it on the previewer. Note that Frame Controls widgets are disabled during a sequence playback due to performance concerns. The **Sequence number** and **Loops** spin boxes are not listened to during a sequence playback either.
* **Stop Sequence**: Stops the current sequence playback.
* **Export Sequence frames**: Exports every frame in a sequence to a folder with the OBJ/OBX name in the script's folder. Do note that this may take a while to generate, be patient. Only available during a sequence playback.

#### Conversion
Converts the current **OBJ** file loaded to a SCad compatible format. **OBX** are **NOT** supported. You don't need to load COL and CGX files to perform this operation.

#### Background Color
Changes the preview area color depending on the values of the spin boxes. It **only** accepts integers, it doesn't support hexadecimal values.

## OBJ/OBX Details
OBJ and OBX files are very similar to how OAM works on the SNES. They're almost OAM dumps of the real thing.

There are up to 32 unique frames on a OBJ file (64 frames on OBX files). Each frame contains 6 byte entries and OBJ files have 64 available entry slots (OBX have 128) per frame.

#### OBJ/OBX Format 
Each entry in the frames has the following format:
* Byte 1: Display tile (bit 7), tile size (bit 0)
* Byte 2: Unknown usage (mentioned in SCad docs as Group Info in their SOB format)
* Byte 3: Displacement on Y axis (0x0-0x7F down, 0xFF-0x80 up)
* Byte 4: Displacement on X axis (0x0-0x7F right, 0xFF-0x80 left)
* Byte 5: Attribute data (YXPPCCCT)
* Byte 6: Tile number/ID

#### Sequence Format
Sequence data can be found 0xE0 bytes after the 0x20 bytes tool string, in most cases is at offset 0x3100 (0xC100 for OBX) and its format is fairly straight forward. There's only 0x10 (0x20 for OBX?) possible sequences and each sequence can have up to 0x10 (0x20 for OBX) frames with each having its own amount of time that will be displayed on screen.

Format: [Duration #1] [Frame #1] [Duration #2] [Frame #2] [...] [Duration #16] [Frame #16]

Notes:
* Duration means how long the frame will be shown, OBJ Viewer treats this duration by multiplying it by 16ms, SCad does something similar as well.
* Frame is the number of the frame that will be shown on the animation at that specific moment.
* If both Duration and Frame are 0 in a sequence the sequence ends.
* There's space to put more frames on a sequence, but SCad treats that data as X/Y displacements, even if these are never read by the tool upon loading a .OBJ file.

#### Tool versions and revisions
The software NAK1989 S-CG-CAD had some different versions and revisions according to the files in Hino's folder, and some of them modified the OBJ format a little bit. The version 1.10 below revision 920000 and version 1.23 had the same format. Version 1.10 above revision 920000 swapped Byte 5 and Byte 6 from the standard entry format and reverses the tile priority order, making it the same to SCad's format. Version 1.23 added support for OBX files.

*I need confirmation on the revision number for version 1.10 about the format change and OBX support starting from version 1.23

#### SCad conversion details
SCad almost accepts the default OBJ files, but they need a few changes before being displayed correctly, which is why I included a way to convert them to be SCad compatible.
* Bytes 5 and 6 should be swapped for each entry.
* Tile priority is reversed. It's determined from bottom to top, instead of from top to bottom.

## Changelog
#### Version 3.2
* Added support for .BAK files in the File Explorer frames at the right
* Fixed OBX files being decoded as OBJ when loading them from the OBJ/OBX Explorer

#### Version 3.1
* Added a way to export CGX and COL files as images

#### Version 3.0
* Added windows to preview contents from CGX and COL files
* Added a file explorer for OBJ, OBX, CGX and COL files
* Added support for different versions of the OBJ format (and possibly OBX as well)
* Fixed OBX files being treated as OBJ files by the decoder
* Added more print statements to properly inform the user about what's happening behind the scenes

#### Version 2.0
* New UI
* Support for sequence playback
* Optimized the program to use images instead of tkinter's rectangles to draw on the preview area.
* Added controls to offset CGRAM
* Added a way to export frames as .png images
* Added a way to change the background color

#### Version 1.1
* Added proper OBX support
* Added a way to change the Object Sizes
* Added a way to offset the camera
* Added a way to change zoom levels
* Justified to the left the current loaded files
* Made the code smaller, but not faster

#### Version 1.0
* Initial release
