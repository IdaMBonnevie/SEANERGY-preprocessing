# Purpose of script: 
#Preprocessing step 2 
#Script input to the tool called 'Preprocessing Step 2'. 
#It combines more binary .tif files into one final binary .tif file. 

# DATE OF CREATION: 28-10-2019
# AUTHOR: Ida Maria Bonnevie

#All the Python modules in the import statement needs to be installed. 
#An ESRI ArcMap license with Spatial Analyst extension activated is required for the tool to run as a script tool in ArcMap. 


# Toolvalidator script inputted in tool: 
#import arcpy
#class ToolValidator(object):
#    """Class for validating a tool's parameter values 
#    and controlling the behavior of the tool's dialog."""
#    def __init__(self):
#        """Setup arcpy and the list of tool parameters."""
#        self.params = arcpy.GetParameterInfo()
#
#    def initializeParameters(self):
#        """Refine the properties of a tool's parameters. 
#        This method is called when the tool is opened."""
#        return
#
#    def updateParameters(self):
#        """Modify the values and properties of parameters before 
#        internal validation is performed. This method 
#        is called whenever a parameter has been changed."""
#
#        if self.params[0].altered and self.params[1].altered:
#            self.params[2].enabled = True
#        else: 
#            self.params[2].enabled = False
#        return
#
#    def updateMessages(self):
#        """Modify the messages created by internal validation for each tool
#        parameter.  This method is called after internal validation."""
#        return


# import modules:
import arcpy 
import os
import time
from datetime import datetime


# functions: 
def createNewPath(outputpath):
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

def printTime(starttime, starttimetobeupdated):
    overallminutes = int(time.time()-starttime)/60
    overallseconds = int((((time.time()-starttime)/60)-(int(time.time()-starttime)/60))*60)
    procminutes = int(time.time()-starttimetobeupdated)/60
    procseconds = int((((time.time()-starttimetobeupdated)/60)-(int(time.time()-starttimetobeupdated)/60))*60) 
    dateTimeObj = datetime.now()
    timestamp = str(dateTimeObj.hour) + ':' + str(dateTimeObj.minute) + ':' + str(dateTimeObj.second)
    printline = "with processing time {}min {}sec, out of cumulated passed {}min {}sec, timestamp:{} \n".format(procminutes,procseconds,overallminutes,overallseconds,timestamp)
    starttimetobeupdated = time.time()
    return (printline, starttimetobeupdated) 

def resetTime(starttimetobeupdated):
    starttimetobeupdated = time.time()
    dateTimeObj = datetime.now()
    timestamp = str(dateTimeObj.hour) + ':' + str(dateTimeObj.minute) + ':' + str(dateTimeObj.second)
    print("starting process, timestamp:{}".format(timestamp))
    return (starttimetobeupdated) 



def BinaryCombinationOf2Rasters(inputpath1, inputpath2, outputpath):
    outras = arcpy.sa.Int(arcpy.sa.Con(((arcpy.sa.Raster(inputpath1) + arcpy.sa.Raster(inputpath2)) == 2),1,(arcpy.sa.Raster(inputpath1) + arcpy.sa.Raster(inputpath2))))
    outras.save(outputpath)

def BinaryCombinationOf3Rasters(inputpath1, inputpath2, inputpath3, outputpath):
    outras = arcpy.sa.Int(arcpy.sa.Con(((arcpy.sa.Raster(inputpath1) + arcpy.sa.Raster(inputpath2) + arcpy.sa.Raster(inputpath3) == 2) | (arcpy.sa.Raster(inputpath1) + arcpy.sa.Raster(inputpath2) + arcpy.sa.Raster(inputpath3) == 3)),1,(arcpy.sa.Raster(inputpath1) + arcpy.sa.Raster(inputpath2) + arcpy.sa.Raster(inputpath3))))    
    outras.save(outputpath)


# parameters
#parameter0 = input marine use binary raster 1
inputdataset1 = arcpy.GetParameterAsText(0)

#parameter1 = input marine use binary raster 2
inputdataset2 = arcpy.GetParameterAsText(1)

#parameter2 = input marine use binary raster 3
try:
    inputdataset3 = arcpy.GetParameterAsText(2)
except: 
    inputdataset3 = ""

#parameter3 = outputname of final raster
outputname = arcpy.GetParameterAsText(3)

#parameter4 = template raster to snap to
rasterToSnapTo = arcpy.GetParameterAsText(4)

#extra script parameters: 
final_folder = "final_rasterinputs"


# start timing: 
starttime = time.time()
starttimetobeupdated = starttime

# environment:
arcpy.CheckOutExtension("spatial")
arcpy.env.extent = rasterToSnapTo #"4109000 3289000 5539000 4913000"
arcpy.env.snapRaster = rasterToSnapTo
arcpy.env.overwriteOutput=True
os.chdir(os.path.dirname(__file__))
arcpy.env.mask = rasterToSnapTo
#rasterToSnapTo_result = arcpy.MakeRasterLayer_management(arcpy.sa.Raster(rasterToSnapTo), rasterToSnapTo[:-4]) 
#rasterToSnapToLayer1 = rasterToSnapTo_result.getOutput(0)
arcpy.env.cellSize = rasterToSnapTo # "1000"


# main code: 
arcpy.AddMessage("\n")
starttimetobeupdated = resetTime(starttimetobeupdated)
createNewPath(os.path.join(os.path.dirname(__file__),final_folder))
if inputdataset3 == "":
    BinaryCombinationOf2Rasters(inputdataset1, inputdataset2, os.path.join(os.path.dirname(__file__),final_folder,outputname))
else: 
    BinaryCombinationOf3Rasters(inputdataset1, inputdataset2, inputdataset3, os.path.join(os.path.dirname(__file__),final_folder,outputname))
(printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("Preprocessing step 2 has been calculated, {}\n".format(printline))
