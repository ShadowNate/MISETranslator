Monkey Island SE Series Translator
============================================
This application was built for the fan-translation of LucasArts' Monkey Island Special Edition Series
by the Classic Adventures In Greek team. It's been tested with the Steam versions of SoMI:SE and Monkey Island 2:SE.
It is an open source project.


Beta version
============================================
Note that this version of MI:SE Series Translator is considered a beta version and is still under active development.
Not all functionality is yet implemented or available. Please read the known issues bellow for more details.
Any feedback about bugs or improvement suggestions and related comments can be sent to classic.adventures.in.greek@gmail.com 


Modifying the source code and running with Python 2.7
============================================
In order to run the modules with Python, you will need:
* Python 2.7 (tested with Python 2.7.5 32-bit)
* Python Library PyQt4 (tested with v4.10.2): http://www.riverbankcomputing.co.uk/software/pyqt/download
* Python Imaging Library (PIL) (tested with v1.1.7): http://www.pythonware.com/products/pil/

Use the 32bit versions.

The main module of the source code is MISEDialogTranslate.py. 


Installation
============================================
Extract the zip file, or copy its contents to a new folder, and then run the included executable (.exe).
The following files:
- MISEDialogTranslateUIWin.ui
- MISERepackUIWin.ui
- MISEFontsTranslateUIDlg.ui

must be in the 'ui' subfolder of the application's folder.

The file:
- trampol.sqlite (if you have an existing one with saved sessions, use that one instead of the one that is included in the cleandb subfolder)

must be with the executable within the same folder, for the application to work as intended.


Backups - Updating
============================================
Please keep regular backups of the following files:
- trampol.sqlite (main DB) 
- any of your active translation files (typically named as XXXX_000x.nnn (e.g. speech_0001.info). 
	
For backing up the translation files there's an option inside the GUI (the backup button)
The trampol.sqlite file is located in the MI:SE Series Translator tool's installation 
folder. This file contains useful information about previous translation sessions that could be overwritten by 
an empty trampol.sqlite when you upgrade to a new version (via copy-paste).


Library Reordering Cards (MI2:SE)
============================================
In order to reorder the library cards you will need to have the monkey2.001 original resource file (classic/en subfolder of the game's resources) 
in the same path as the fr.uitext.info.

You should open the fr.uitext.info for translation, and when you press the Submit button, 
a dialogue prompt will ask you about re-ordering the library, as well. If you choose YES, 
then a monkey2.001-copy file will be created in the same path as fr.uitext.info. 
You should copy this file to the game's installation folder (into subfolder classic/en). 
Create this subfolders if they don't exist). Rename the file from "monkey2.001-copy" to "monkey2.001".

Note that the following cards for books: 
- "Treasure - Big Whoop: Unclaimed Bonanza or Myth?", 
- "Quotations - Famous Pirate Quotations", 
- "Recipes, Voodoo - The Joy of Hex" 

can't be moved (must maintain their ids, which are identical to their placement in the library). 
So you will have to come up with some translation tricks to make them fit in the lexical order. 
Also, note that some of these have "Reference cards" to them, so their translation should be adjusted as well, to keep consistency. 

Finally, note typically you should start from a saved game before having acquired any books from the library.

If you restore a saved game where you have books from the library, their description will be possibly wrong. 
The way to clear this up, would be to return them all to the librarian, and re-acquire them via the 
library card system of the library. To "clear-up" the Pirate Quotation's book, you would (probably) 
have to go back to the Phatt governor's mansion and re-switch the books (twice, once to get the book back 
on the governor and twice to get it back). (Returning it to the library and re-acquiring it would work as well - I think).


Overriding the default encoding
============================================
In order to override the default encoding (windows-1253 (Greek)) you will need an extra text file named "overrideEncoding.txt" in your translator tool folder.
This file needs to have only one line with two tab separated entries:
* encoding (ASCII) and 
* characters-list

Convert the file to UTF-8 without BOM (e.g. using Notepad++) and save. 

A sample line in the "overrideEncoding.txt" would be:
* windows-1253	ΆΈΉΊΌΎΏΐΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΪΫάέήίΰαβγδεζηθικλμνξοπρςστυφχψωϊϋόύώ

Note that the order of the given letters would be best to match their appearing order in the ASCII table for the corresponding codepage (here: for Greek e.g. http://msdn.microsoft.com/en-gb/goglobal/cc305146).
Also, it is important that this identical string of letters MUST be used to create new (extended) fonts with the fonts' mod tool.
Finally, note that each game has a limited number of new characters that can be imported, because the translator will use the limited and (seemingly) available empty "slots" in the original font files. 
Currently, the number of empty slots for each game is set to 70. 


Using the fonts' mod tool
============================================
The translator tool is intended to be used by translator teams that can't re-use the Latin alphabet, because their native language contains many non-Latin characters. 
In such cases the font mod tool MUST be used to create extended font files. 
In general, all FONT (.font) and corresponding PNG (.png) files must be replaced by the modified ones created by the font mod tool. Different font/PNG files correspond to 
different menus/dialogues and also various resolution settings.

Typically, the font tool is used as follows:
* In the first field (fonts PNG file) you indicate the full path to an original PNG file for a in-game font. (e.g. MinisterT_bo_16.png)
* In the second field (custom row file) you indicate the full path to a custom made PNG file. 
  This PNG file should be an image of the sequence of the language characters (ordered EXACTLY as indicated in the overrideEncoding.txt file)
  The background should be transparent. (e.g. MinisterT16_bo_BookmanOldStyle_12WithBorder.png)
* In the third field (original font file) you indicate the full path to the corresponding ORIGINAL font file (.font) (e.g. MinisterT_bo_16.font)
* Finally in the two remaining fields "Letter space top to top" and "Letter space left to left" you indicate the minimum margins between the characters in the custom row PNG file, in pixels.  
  Typically the first value should be a few pixels greater than the height of the highest language character, and the second value should be a few pixels greater than the minimum space between two characters in the custom row PNG file. If you don't get these values right, you may re-adjust them and press the "Calculate" or "Recalculate" buttons. The field "Imported Characters" on the right should provide a clue whether all of your characters were imported. Also, the "Draw outlines" function should provide the outlines around the characters to verify whether they will be drawn correctly.

After pressing the "Calculate"(or "Recalculate") button, if there were no errors and the process finished successfully, the two remaining text fields ("output PNG file" and "output font file" ) will indicate the files where the modifications were stored. If everything seems ok in the preview image, you may copy these files in the "fonts" directory of the Monkey Island game to test the results in game.

You can adjust the positioning of a font character within a sentence by explicitly and manually modifying the values in the "Detected Characters" table on the right. Typically, the values that should be modified are the ones in
the columns Indnt (indent: the margin within a letter box, after which the letter begins. Can be negative), wid (width: the width of the character), kern (kerning: the margin after the end of the character, where the box for the next letter should begin). 

You can click on the "Preview sentence" button to open the "Preview Sentence" dialogue. By default this dialogue will demonstrate how the original and target language pangrams (sentences that include all letters of the respective
alphabets) will appear in-game (approximately - as the game sometime treats specific font colour values differently depending on the game-context). You can also add custom sentences to preview their in-game versions.

WARNING: the explicit manual changes to font letters positioning MUST be saved by clicking on the "Submit new values" button, under the "Detected Characters" table. 
WARNING 2: the explicit manual changes to font letters positioning WILL BE OVERWRITTEN without any prompt, if you click on the "Calculate" or "Recalculate" buttons, because those will recreate the extended font files from scratch. 


Using the repacker tool
============================================
Preparatory steps:
* Use bgbennyboy's MISE Explorer to extract all files (raw) from the ORIGINAL monkey1.pak or monkey2.pak resource files in a sandbox folder (e.g. named "extractedAllOrigWithModifications")
* Overwrite any resource files with modified ones as needed.

In order to re-pack the files in the sandbox folder you need to select from the Monkey SE repaker UI:
* The game name (MI1:SE or MI2:SE) from the drop-down list
* The path to the ORIGINAL pak file. Do not point to a modified pak file here.
* The path to the (sandbox) folder of extracted files.

If the repacker finishes successfully a modded.pak file will be created in the same folder with the translator tool.
Copy this file to the game's installation directory and rename it appropriately (monkey1.pak or monkey2.pak).
Keep a backup of the original pak file, just in case.


Known Issues
============================================
- All dialogue translation sessions (connections between original files and their respective active translation files) 
	keep absolute paths for the involved files. This means that these sessions won't work
	if the files are moved or the Translator's installation folder is changed.
	A new session will start if any of the involved files in an stored session has been moved or deleted.
	You can still import text from a previously extracted (to .txt from the menu option) translation.
	Additionally, you can load a previous backup or copy of your translation file into a new session 
	by using the Load Translation in Session (Ctrl+T shortcut).
- If certain font files are missing for your locale, you may see square symbols instead of your translated text.
	The Font Crafting tool (accessible via the Translator's menu "Tools" option) is needed for expanding the font file
	to include specific locale charsets. This tool includes a preview capability, to demonstrate approximately
	how the changed fonts will work in sentences in-game (indent, spacing, kerning).
- The Translator tool will produce translations that will replace the French translation for the games. You'll have to
	set the game's language to French in order to view your custom translation in-game.
- Spell-checking has not yet been integrated. You will have to extract the translation to a text file, check it separately 
	and re-import it.
- For the Dialogue Translator no auto-save feature is implemented. You need to click on the Submit button to save any changes or any imports from extracted files.
- Certain special characters will appear as 0x## (where ## is a hex 2-digit number) within the text. You can remove them if deemed 
	necessary (usually it is apparent whether the special character can be omitted; most of the special characters that are
	also in the English translation are to be kept).
- The extracted text files may include a 0x0A special character in addition to the special characters shown in the tool's GUI.
	This 0x0A indicates a "new line" within a quote and should NOT be removed from the extracted text file. 
- For the Font Crafting tool the Calculate and Recalculate both will auto-save the changes (overwriting your previous target copies) 
	and prompt to overwrite an existing session (if one was active/loaded). Clicking these buttons will also overwrite any explicit manual 
	changes made in the indent, spacing, kerning of the font characters (via the table on the right).


Special Thanks
============================================
- bgbennyboy for making available as open-source tools over at Quick And Easy Software (http://quickandeasysoftware.net/)
  several valuable apps for extracting game resource files and importing images,
- The guys over at the "scumm" subsection of  lucasforums (http://www.lucasforums.com/forumdisplay.php?f=363) for various observations and notes on the format of the games' resource files.
- The guys from the Hungarian Translation team (Kenand, Bela) for providing important info about the re-ordering of the library catalogue in MI2:SE
- Any beta testers :)