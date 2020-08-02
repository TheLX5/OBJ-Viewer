# OBJ Viewer
A python script that lets you preview frames and animations from SNES OBJ files if the required files are provided.

## REQUIREMENTS
* Python 3 with Tkinter
* Ttk module for Python (I forgot which version comes with Ttk, newer Python versions have Ttk by default, do your research)
* Pillow module (`python -m pip install pillow` or `pip3 install pillow`)

## NOTES
* I'm not very proficient at high level languages so a lot of the code is REALLY bad and poorly thought out
* It may spam a little bit your console if you go out of bounds of the VRAM area
* OBX files are **PARTIALLY** supported at this moment. They make use of the second byte on each entry which is currently unknown to me and their displays on the preview area doesn't seem correct.

## PROGRAM DETAILS

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

#### OBJ/OBJ Format
Each entry in the frames has the following format:
* Byte 1: Display tile (bit 7), tile size (bit 0)
* Byte 2: Group info (unknown usage, mentioned in SCad docs)
* Byte 3: Displacement on Y axis (0x0-0x7F down, 0xFF-0x80 up)
* Byte 4: Displacement on X axis (0x0-0x7F right, 0xFF-0x80 left)
* Byte 5: Attribute data (YXPPCCCT)
* Byte 6: Tile number/ID

#### Sequence Format
Sequence data can be found 0x100 bytes later before the tool string, in most cases is at offset 0x3100 (0xC100 for OBX) and its format is fairly straight forward. There's only 0x10 (0x20 for OBX?) possible sequences and each sequence can have up to 0x10 (0x20 for OBX) frames with each having its own amount of time that will be displayed on screen.

Format: [Duration #1] [Frame #1] [Duration #2] [Frame #2] [...] [Duration #16] [Frame #16]

Notes:
* Duration means how long the frame will be shown, OBJ Viewer treats this duration by multiplying it by 16ms, SCad does something similar as well.
* Frame is the number of the frame that will be shown on the animation at that specific moment.
* If both Duration and Frame are 0 in a sequence the sequence ends.
* There's space to put more frames on a sequence, but SCad treats that data as X/Y displacements, even if these are never read by the tool upon loading a .OBJ file.


#### SCad conversion details
SCad almost accepts the default OBJ files, but they need a few changes before being displayed correctly, which is why I included a way to conver them to be SCad compatible.
* Bytes 5 and 6 should be swapped for each entry.
* Tile priority is reversed. It's determined from top to bottom, instead of from bottom to top.
