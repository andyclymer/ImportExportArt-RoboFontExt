from __future__ import absolute_import
from __future__ import print_function
import os
from mojo.extensions import ExtensionBundle


basePath = os.path.dirname(__file__)
extensionPath = os.path.join(basePath, "ImportExportArt.roboFontExt")
libPath = os.path.join(basePath, "lib")
htmlPath = os.path.join(basePath, "html")

B = ExtensionBundle()

B.name = "Import/Export Art"
B.version = "1.2"
B.developer = "Andy Clymer"
B.developerURL = 'http://www.andyclymer.com/'

B.mainScript = "ImportExportWindow.py"
B.launchAtStartUp = False
B.addToMenu = [
    {
        'path' : 'ImportExportWindow.py',
        'preferredName': 'Import/Export Art...',
        'shortKey' : '',
    }]
    
B.requiresVersionMajor = '3'
B.requiresVersionMinor = '1'
B.infoDictionary["html"] = True

B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, pycOnly=False)

print("Done")