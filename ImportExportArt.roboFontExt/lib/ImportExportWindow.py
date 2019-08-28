import os
import math
from plistlib import load, dump
from AppKit import *

import vanilla
from fontTools.pens.cocoaPen import CocoaPen
from fontTools.svgLib import SVGPath
from mojo.UI import PutFile, GetFile
from mojo.events import addObserver, removeObserver

try:
    import drawBot as db
    HASDRAWBOT = True
except:
    HASDRAWBOT = False
    
    
    
    
"""
Import/Export Art
by Andy Clymer
2019_08_28
"""




def colorText(text, color="black", sizeStyle="regular", style=None, url=None):

    sizeStyleMap = {
        "regular":  NSRegularControlSize,
        "small":    NSSmallControlSize,
        "mini":     NSMiniControlSize}
    colors = {
        "red":      NSColor.redColor(),
        "green":    NSColor.greenColor(),
        "blue":     NSColor.blueColor(),
        "cyan":     NSColor.cyanColor(),
        "magenta":  NSColor.magentaColor(),
        "yellow":   NSColor.yellowColor(),
        "gray":     NSColor.grayColor(),
        "lightGray":NSColor.lightGrayColor()}
        
    attrs = {}
    
    if sizeStyle in sizeStyleMap:
        nsSizeConstant = sizeStyleMap[sizeStyle]
    else: nsSizeConstant = sizeStyleMap["regular"]
    # Color attribute
    if color in colors:
        attrs[NSForegroundColorAttributeName] = colors[color]
    # Font style attribute   
    if style == "bold":
        attrs[NSFontAttributeName] = NSFont.boldSystemFontOfSize_(NSFont.systemFontSizeForControlSize_(nsSizeConstant))
    else: attrs[NSFontAttributeName] = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(nsSizeConstant))
    # URL
    if url:
        attrs[NSLinkAttributeName] = url
    # Build the string with these attributes:
    string = NSMutableAttributedString.alloc().initWithString_attributes_(text, attrs)

    return string



txt = "Import/Export Art"
titleText = colorText(txt, style="bold")
# 
txt = "1︎⃣ Export a SVG image from the UFO"
descriptionExport = colorText(txt, style="bold")
txt = "\n\nA “svg” image made up of a grid of glyph drawings will be saved, along with a companion “plist” file containing some additional glyph data."
descriptionExport.appendAttributedString_(colorText(txt, sizeStyle="small"))

txt = "2︎⃣ Edit the SVG in Illustrator"
descriptionEdit = colorText(txt, style="bold")
txt = "\n\nDo whatever you want to the “svg”, as long as you don't scale the document or move the glyphs out of their position. Once you're finished in Illustrator, “Expand Appearance” and “Outline Stroke” to flatten out your drawing. Don't modify the “plist” file but keep it on hand."
descriptionEdit.appendAttributedString_(colorText(txt, sizeStyle="small"))

txt = "3︎⃣ Import the SVG into your UFO"
descriptionImport = colorText(txt, style="bold")
txt = "\n\nMake sure that the “svg” and “plist” files are in the same folder and still have the same file name (with exception of the file extension) and choose either one to import into the UFO. The “plist” file will help make sure the glyph drawings end up in the correct position in your UFO file.\n\nIf your drawing is very complex, the import will be very slow. Maybe save a copy of your UFO before importing just in case!"
descriptionImport.appendAttributedString_(colorText(txt, sizeStyle="small"))

txt = "First, install DrawBot"
nodrawbotText = colorText(txt, style="bold")
txt = "\n\nThis extension requires that you also install the DrawBot extension, which can be installed with Mechaninc 2, or can be downloaded here:\n\n"
nodrawbotText.appendAttributedString_(colorText(txt, sizeStyle="small"))
txt = "https://github.com/typemytype/drawBotRoboFontExtension"
nodrawbotText.appendAttributedString_(colorText(txt, sizeStyle="small", url="https://github.com/typemytype/drawBotRoboFontExtension"))



class ImportExportArtWindow:
    
    def __init__(self):
                
        self.pageScale = 0.1 # Scale the SVG so that glyphs aren't 1000 ps points in size
        self.bufferFactor = 3 # The scale of the buffer within the grid (1 = glyphs touch)
        
        self.fontList = []
        self.fontNameList = []
        
        if not HASDRAWBOT:
        
            self.w = vanilla.Window((300, 200), "Import/Export Art")
            
            self.w.title = vanilla.TextBox((10, 10, -10, 25), titleText)
            self.w.warningBox = vanilla.Box((10, 40, -10, 150))
            self.w.warningBox.nodrawbot = vanilla.TextBox((10, 10, -10, -10), nodrawbotText)
            self.w.open()
        
        else:
        
            self.w = vanilla.Window((300, 780), "Import/Export Art")
        
            self.w.title = vanilla.TextBox((10, 10, -10, 25), titleText)
            self.w.titleFont = vanilla.TextBox((10, 40, -10, 25), "Source/Destination UFO")
            self.w.fontChoice = vanilla.PopUpButton((10, 60, -10, 25), self.fontNameList)
            # Export
            self.w.exportBox = vanilla.Box((10, 105, -10, 185))
            self.w.exportBox.title = vanilla.TextBox((10, 10, -10, 100), descriptionExport)
            self.w.exportBox.glyphChoice = vanilla.PopUpButton((10, 110, -10, 25), ["Selected glyphs", "All glyphs"])
            self.w.exportBox.exportButton = vanilla.SquareButton((10, 140, -10, 25), "Export SVG", callback=self.exportCallback)
            # Edit
            self.w.editBox = vanilla.Box((10, 305, -10, 165))
            self.w.editBox.title = vanilla.TextBox((10, 10, -10, 200), descriptionEdit)
            # Import
            self.w.importBox = vanilla.Box((10, 485, -10, 285))
            self.w.importBox.title = vanilla.TextBox((10, 10, -10, 190), descriptionImport)
            self.w.importBox.layerChoice = vanilla.PopUpButton((10, 210, -10, 25), ["Into the “foreground“ layer", "Into a new layer called “import“"])
            self.w.importBox.importButton = vanilla.SquareButton((10, 240, -10, 25), "Import SVG", callback=self.importCallback)
        
            self.w.bind("close", self.closeCallback)
            self.w.open()
            self.buildFontList(None)
        
            addObserver(self, "buildFontList", "fontDidOpen")
            addObserver(self, "buildFontList", "newFontDidOpen")
            addObserver(self, "buildFontList", "fontDidClose")
        
    
    def closeCallback(self, sender):
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "newFontDidOpen")
        removeObserver(self, "fontDidClose")
        
    
    def buildFontList(self, info):
        self.fontList = []
        self.fontNameList = []
        for f in AllFonts():
            self.fontList.append(f)
            fontName = "%s %s" % (str(f.info.familyName), str(f.info.styleName))
            self.fontNameList.append(fontName)
        self.w.fontChoice.setItems(self.fontNameList)
        doEnable = len(self.fontList)
        self.w.exportBox.glyphChoice.enable(doEnable)
        self.w.exportBox.exportButton.enable(doEnable)
        self.w.importBox.layerChoice.enable(doEnable)
        self.w.importBox.importButton.enable(doEnable)
            
        
        
    def exportCallback(self, sender):
        if len(self.fontList):
            fontChoice = self.w.fontChoice.get()
            f = self.fontList[fontChoice]
            if f.path:
                fileName = os.path.splitext(os.path.split(f.path)[1])[0] + ".svg"
            else: fileName = "GlyphExport.svg"
            savePath = PutFile(message="Choose a location to save the glyph image...", fileName=fileName)
            if not savePath == None:
                self.doExport(f, savePath)
    
    
    def importCallback(self, sender):
        if len(self.fontList):
            fontChoice = self.w.fontChoice.get()
            f = self.fontList[fontChoice]
            filePath = GetFile(message="Choose the SVG file to import...")
            if not filePath == None:
                if os.path.splitext(filePath)[1] == ".svg":
                    otherExt = ".plist"
                else: otherExt = ".svg"
                otherPath = os.path.splitext(filePath)[0] + otherExt
                if os.path.exists(otherPath):
                    self.doImport(f, filePath)
                else:
                    print("Can't find the other file!")
        
        
        
    def doExport(self, f, savePath):
        # Export an image of the glyphs
        
        # Collect the glyph names from this font
        glyphNames = []
        glyphChoice = self.w.exportBox.glyphChoice.get() 
        if glyphChoice == 0:
            glyphNames = list(f.selection)
        elif glyphChoice == 1:
            if 'public.glyphOrder' in f.lib.keys():
                allNames = f.lib['public.glyphOrder']
            else:
                allNames = list(f.keys())
                allNames.sort()
            # Only keep glyphs that have art
            for gn in allNames:
                g = f[gn]
                if len(g.contours):
                    glyphNames.append(gn)
                

        # Find the maximum glyph bounds, to figure out the grid spacing
        xMax = 0
        yMax = 0
        for gn in glyphNames:
            g = f[gn]
            bounds = g.bounds
            if bounds:
                thisXMax = bounds[2] - bounds[0]
                thisYMax = bounds[3] - bounds[1]
                if thisXMax > xMax:
                    xMax = thisXMax
                if thisYMax > yMax:
                    yMax = thisYMax
        xMax = int(math.ceil(xMax)) * self.pageScale
        yMax = int(math.ceil(yMax)) * self.pageScale

        # Figure out how many rows of glyphs we'll need, to lay them out in a square grid
        if len(glyphNames) < 1:
            rowCount = 1
        else: rowCount = math.ceil(math.sqrt(len(glyphNames)))
        colCount = math.ceil(len(glyphNames) / rowCount)

        # Work out the page dimensions, with glyphs centered up on a grid of xMax and yMax with a buffer to give a little space to work with
        pageWidth = ((colCount + 1) * xMax * self.bufferFactor)
        pageHeight = ((rowCount + 1) * yMax * self.bufferFactor)

        # Start drawing, keeping track of where each glyph was placed
        glyphLocations = []
        db.newDrawing()
        db.newPage(pageWidth, pageHeight)
        gIdx = 0
        for rowNumber in range(rowCount):
            for colNumber in range(colCount):
                if gIdx < len(glyphNames):
                    gridID = "%s-%s" % (colNumber, rowNumber)
                    gName = glyphNames[gIdx]
                    glyph = f[gName]
                    # Find the position to draw the glyph
                    # The glyph will be drawn centered on the center of each grid location
                    locX = ((colNumber * xMax * self.bufferFactor) + xMax * self.bufferFactor)
                    locY = (pageHeight - (rowNumber * yMax * self.bufferFactor) - (yMax * self.bufferFactor))
                    # Adjust the grid location to center the glyph drawing
                    locX += -glyph.width * 0.5 * self.pageScale
                    locY += -yMax * 0.5
                    glyphLocations.append((gName, gridID))
                    # Draw the glyph
                    with db.savedState():
                        db.translate(locX, locY)
                        db.scale(self.pageScale, self.pageScale)
                        pen = CocoaPen(f)
                        glyph.draw(pen)
                        glyphPath = pen.path
                        path = db.BezierPath()
                        path.setNSBezierPath(glyphPath)
                        db.drawPath(path)
                        # Draw the glyph bounding box, for testing
                        if False:
                            db.fill(None)
                            db.stroke(0)
                            db.strokeWidth(10)
                            db.rect(0, 0, xMax, yMax)
                gIdx += 1

        # Prepare a settings document to save, with the number of rows, columns, spacing, scale, and glyph positions
        drawingData = {}
        drawingData["pageScale"] = self.pageScale
        drawingData["bufferFactor"] = self.bufferFactor
        drawingData["pageWidth"] = pageWidth
        drawingData["pageHeight"] = pageHeight
        drawingData["xMax"] = xMax
        drawingData["yMax"] = yMax
        drawingData["rowCount"] = rowCount
        drawingData["colCount"] = colCount
        drawingData["glyphLocations"] = glyphLocations

        # Save
        db.saveImage(savePath)
        plistPath = os.path.splitext(savePath)[0] + ".plist"
        with open(plistPath, "wb") as plistFile:
            dump(drawingData, plistFile)
            
    
    
    def doImport(self, f, filePath):
        layerChoice = self.w.importBox.layerChoice.get()
        # Format the path names
        plistPath = os.path.splitext(filePath)[0] + ".plist"
        svgPath = os.path.splitext(filePath)[0] + ".svg"
        # Import the SVG
        outline = SVGPath(svgPath)
        svgGlyph = RGlyph()
        pen = svgGlyph.getPen()
        outline.draw(pen)

        # Read the Plist
        with open(plistPath, 'rb') as plistFile:
            plistData = load(plistFile)
            thisPageScale = plistData["pageScale"] # Use the pageScale and bufferFactor from the file, not from the extension prefs
            thisBufferFactor = plistData["bufferFactor"]
            xMax = plistData["xMax"] / thisPageScale
            yMax = plistData["yMax"] / thisPageScale
            rowCount = plistData["rowCount"]
            colCount = plistData["colCount"]
            pageWidth = plistData["pageWidth"] / thisPageScale
            pageHeight = plistData["pageHeight"] / thisPageScale
            glyphLocations = plistData["glyphLocations"]
            
            # Scale the glyph back to the normal size
            svgGlyph.scaleBy((1 / thisPageScale, 1 / thisPageScale))
            
            # Flip and move the SVG Glyph so that it's in the correct orientation
            svgGlyph.scaleBy((1, -1))
            svgGlyph.moveBy((0, pageHeight))
            
            # Find the location that grid location starts (which will be at the center of each glyph drawing)
            # Same as the export
            gridLocs = {}
            for rowNumber in range(rowCount):
                for colNumber in range(colCount):
                    gridID = "%s-%s" % (colNumber, rowNumber)
                    locX = ((colNumber * xMax * thisBufferFactor) + xMax * thisBufferFactor)
                    locY = (pageHeight - (rowNumber * yMax * thisBufferFactor) - (yMax * thisBufferFactor))
                    gridLocs[gridID] = (locX, locY)
            
            # Find which contours from the SVG belong in which of the grid locations
            # Hold the contours aside by their index for now
            sortedContours = {}
            for cIdx, contour in enumerate(svgGlyph.contours):
                for gridID, gridLoc in gridLocs.items():
                    if contour.bounds[0] > gridLoc[0]-xMax and contour.bounds[2] < gridLoc[0]+xMax:
                        if contour.bounds[1] > gridLoc[1]-yMax and contour.bounds[3] < gridLoc[1]+yMax:
                            if not gridID in sortedContours:
                                sortedContours[gridID] = []
                            sortedContours[gridID].append(cIdx)

            # Draw the contours into glyphs
            for gn, gridID in glyphLocations:
                if not gn in f.keys():
                    f.newGlyph(gn)
                g = f[gn]
                if layerChoice == [0]:
                    # Import into the foregronud
                    gl = g.getLayer("backup")
                    gl.appendGlyph(g)
                    gl.width = g.width
                    g.clear()
                    destGlyph = g
                else:
                    # Import into the "import" layer
                    gl = g.getLayer("import")
                    gl.clear()
                    gl.width = g.width
                    destGlyph = gl
                # Import
                if gridID in sortedContours:
                    for cIdx in sortedContours[gridID]:
                        c = svgGlyph.contours[cIdx]
                        destGlyph.appendContour(c)
                # Move to the center of the grid location
                destGlyph.moveBy((-gridLocs[gridID][0], -gridLocs[gridID][1]))
                # ...and offset since the glyph drawing was centered up on the grid location
                destGlyph.moveBy((g.width * 0.5, yMax * 0.5))
                # Small amount of cleanup, remove single-point contours
                for c in destGlyph.contours:
                    if len(c.points) == 1:
                        destGlyph.removeContour(c)
                destGlyph.changed()


            
ImportExportArtWindow()    


