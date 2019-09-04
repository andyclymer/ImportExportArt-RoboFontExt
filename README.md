# Import/Export Art, RoboFont Extension

by Andy Clymer

This extension will export a SVG image of a selection of glyphs for filtering and processing outside of RoboFont, and then can import the glyphs out of the SVG file back into the same position they came from in the UFO, leaving their kerning and spacing intact.

It requires that you’ve already installed DrawBot, which can be found as an extension in Mechanic 2 or can be downloaded here: https://github.com/typemytype/drawBotRoboFontExtension

### Exporting

Choose a font and a range of glyphs to export.

The extension will export two files: a “svg” image made up of a grid of glyph drawings, and a “plist” file with some additional glyph data. There’s no need to edit the “plist” file, it will only be needed when the glyphs are imported later.

### Editing

The “svg” file can be edited in any way you desire, as long as the glyph drawings aren’t moved or scaled out of their position (i.e. moving every glyph to the left will shift every glyph when the file is imported). 

After editing the “svg” and before saving your changes from Illustrator, you will need to run the `Object > Expand Appearance` menu item to flatten any filtering you may have done to the image, and also `Object > Path > Outline Stroke` to outline stroked contours. Color and transparency will be ignored when the glyph drawings are imported, so it’s best to flatten your drawing down to simple black contours that are cut out of each other with the “Pathfinder” tool instead of overlaying a white contour on top of a black contour to divide a shape.

Complex drawings might take a long time to import, and could slow down RoboFont if they have too many points. It’s recommended that you try your filtering/editing technique on a smaller character set before attempting to import a large number of glyphs.

### Importing

Choose whether the imported drawing should be drawn into the default foreground layer (in which case any art in the foreground would be copied to a “backup” layer), or choose to import into a new layer which will be named “import”.

Before importing your edited “svg” file, it’s important that the “svg” and its related “plist” file share the same file name (with the exception of the file extension) and are in the same folder. When prompted to choose a file while importing, you can choose either the “svg” or the “plist” file. 

Reminder: if your drawing is too complex, the import will be very slow. Maybe save a copy of your UFO before importing just in case if anything goes wrong!
