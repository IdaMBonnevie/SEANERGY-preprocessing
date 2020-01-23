# Purpose of script: 
#Preprocessing step 1 
#Script input to the tool called 'Preprocessing Step 1'. 
#It converts a marine use input (either shapefile or .tif raster file) to a binary .tif file. 

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
#
#        if self.params[0].altered:
#            if self.params[0].value.value[-4:] == ".shp": 
#                self.params[1].enabled = True
#            else: 
#                self.params[1].enabled = False
#        else: 
#            self.params[1].enabled = False
#        if self.params[0].altered:
#            self.params[3].enabled = True
#        else: 
#            self.params[3].enabled = False
#        if self.params[1].value == True and self.params[1].enabled == True:         
#            self.params[2].enabled = True
#            self.params[3].enabled = False
#        else: 
#            self.params[2].enabled = False
#        if self.params[3].value == True and self.params[3].enabled == True:         
#            self.params[4].enabled = True
#            self.params[1].enabled = False
#        else: 
#            self.params[4].enabled = False
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
def addField(outputpath, fieldtype, fieldname = "valuefield", precision = "", 
              decimals = "", field_length = ""): 
    if fieldtype == "TEXT":
        arcpy.AddField_management(outputpath, fieldname, fieldtype, precision, 
                                  decimals, field_length, "", "NULLABLE", 
                                  "NON_REQUIRED", "")        
    else: 
        arcpy.AddField_management(outputpath, fieldname, fieldtype, precision, decimals, "", "", "NULLABLE", "NON_REQUIRED", "")

def bufferShapefile(inputpath, outputpath, buffersize, line_side="FULL", line_end_type="ROUND", dissolve_option="ALL"): 
    arcpy.Buffer_analysis(inputpath, outputpath, buffersize, line_side, line_end_type, dissolve_option)

def calculateField(outputpath, valuefield, valueToInput, expression_type="VB"): 
    arcpy.CalculateField_management(outputpath, valuefield, valueToInput, expression_type, "")

def copyFeatures(inputpath, outputpath): 
    arcpy.CopyFeatures_management(inputpath, outputpath, "", "0", "0", "0")

def createNewPath(outputpath):
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

def nullsToZeroForRaster(inputpath, outputpath):
    outras = arcpy.sa.Int(arcpy.sa.Con(arcpy.sa.IsNull(arcpy.sa.Raster(inputpath)),0,1))
    outras.save(outputpath)

def polygonToRaster(inputpath, outputpath): 
    arcpy.PolygonToRaster_conversion(inputpath, "valuefield", outputpath, "MAXIMUM_COMBINED_AREA", "valuefield", "1000")

def polylineToRaster(inputpath, outputpath): 
    arcpy.PolylineToRaster_conversion(inputpath, "valuefield", outputpath, "MAXIMUM_COMBINED_LENGTH", "valuefield", "1000")

def pointToRaster(inputpath, outputpath): 
    arcpy.PointToRaster_conversion(inputpath, "valuefield", outputpath, "MEAN", "NONE", "1000")

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

def rasterToRasterProcess(rast1, rast2, rast3, selectSomeData, raster_threshold):
    if selectSomeData == "true" and raster_threshold != 0:
        try: 
            thresholdsForRaster(rast1, raster_threshold, rast2) 
            nullsToZeroForRaster(rast2, rast3) 
        except: 
            arcpy.AddMessage("ERROR: Something is probably wrong with the raster selection input: \n".format(raster_threshold))            
    else: 
        nullsToZeroForRaster(rast1, rast3) 

def resetTime(starttimetobeupdated):
    starttimetobeupdated = time.time()
    dateTimeObj = datetime.now()
    timestamp = str(dateTimeObj.hour) + ':' + str(dateTimeObj.minute) + ':' + str(dateTimeObj.second)
    print("starting process, timestamp:{}".format(timestamp))
    return (starttimetobeupdated) 

def selectFunction(inputpath, outputpath, whereclause, deletestate = "yes"):
    selecteddata = arcpy.MakeFeatureLayer_management(inputpath, inputpath[:-4], whereclause)
    if deletestate == "yes":
        copyFeatures(inputpath[:-4], outputpath)
        arcpy.Delete_management(inputpath[:-4])
    elif deletestate == "no":
        return selecteddata

def shapefileToRasterProcess(inputdatasetandpath, feat1, feat2, rast1, rast2, useBuffer, buffer_threshold, selectSomeData, selection_threshold):
    if useBuffer == "false": 
        copyFeatures(inputdatasetandpath, feat1)
    elif useBuffer == "true" and buffer_threshold != 0: 
        try: 
            bufferShapefile(inputdatasetandpath, feat1, buffer_threshold)
        except: 
            arcpy.AddMessage("ERROR: Something is probably wrong with the buffer input: \n".format(buffer_threshold))
    desc = arcpy.Describe(feat1)
    geometryType = desc.shapeType
    if selectSomeData == "true" and selection_threshold != 0: 
        try: 
            selectFunction(feat1, feat2, selection_threshold)   
            addField(feat2, "SHORT")     
            calculateField(feat2, "valuefield", "1")
            if str(geometryType) == 'Polygon':
                polygonToRaster(feat2, rast1)
            elif str(geometryType) == 'Point':
                pointToRaster(feat2, rast1)
            elif str(geometryType) == 'Polyline':
                polylineToRaster(feat2, rast1)
        except: 
            arcpy.AddMessage("ERROR: Something is probably wrong with the shapefile selection input: \n".format(selection_threshold))
    elif selectSomeData == "false":
        addField(feat1, "SHORT") #       
        calculateField(feat1, "valuefield", "1")        
        if str(geometryType) == 'Polygon':
            polygonToRaster(feat1, rast1)
        elif str(geometryType) == 'Point':
            pointToRaster(feat1, rast1) 
        elif str(geometryType) == 'Polyline':
            polylineToRaster(feat1, rast1) 
    nullsToZeroForRaster(rast1, rast2) 

def thresholdsForRaster(inputpath, threshold, outputpath):
    outras = arcpy.sa.Int(arcpy.sa.SetNull((arcpy.sa.Raster(inputpath) < threshold),1))
    outras.save(outputpath)


# parameters
#parameter0 = input dataset to convert to binary use raster
inputdatasetandpath = arcpy.GetParameterAsText(0)
inputpath, inputdataset = os.path.split(inputdatasetandpath)
outputdatasetdraft1 = ''.join(e for e in inputdataset if e.isalnum()) # removes weird characters from inputname
outputdatasetdraft2 = outputdatasetdraft1[:-3].lower()+'.'+ outputdatasetdraft1[-3:].lower() # adds dot to inputname after removal of weird characters

#parameter1 = whether buffer is used or not (true or false)
useBuffer = arcpy.GetParameterAsText(1)
if useBuffer != 'true': 
    useBuffer = 'false'

#parameter2 = threshold of buffer
#example: "3000 Meters" / "1500 Meters"
try:
    buffer_threshold = arcpy.GetParameterAsText(2)
except: 
    buffer_threshold = ""

#parameter3 = whether a selection should be made or not (true or false)
selectSomeData = arcpy.GetParameterAsText(3)
if selectSomeData != 'true': 
    selectSomeData = 'false'
    
#parameter4 = threshold of shapefile selection
#example if shapefile: '"Sum_BMus" >= 331936.1 OR "Sum_ComC" >= 19654.' / '"SUM" >= 164.8'
#example if raster: 0.7 / (160829./100) / 0.25
if inputdataset[-4:] == ".shp":
    selection_threshold = arcpy.GetParameterAsText(4)
elif inputdataset[-4:] == ".tif":
    selection_threshold = float(arcpy.GetParameterAsText(4).replace(",","."))

#parameter5 = template raster to snap to
rasterToSnapTo = arcpy.GetParameterAsText(5)

#extra script parameters: 
processfolder = "preparationprocess"
finalfolder = "finalstep1_rasterinputs"


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
arcpy.env.cellSize = rasterToSnapTo # "1000"


# main code: 
arcpy.AddMessage("\n")
starttimetobeupdated = resetTime(starttimetobeupdated)
createNewPath(os.path.join(os.path.dirname(__file__),processfolder))
createNewPath(os.path.join(os.path.dirname(__file__),finalfolder))
tif_outputdraft1 = processfolder+"\\"+outputdatasetdraft2[:-4]+"_draft1.tif"
if outputdatasetdraft2[-4:] == ".shp":
    shp_outputdraft1 = processfolder+"\\"+outputdatasetdraft2[:-4]+"_draft1.shp"
    shp_outputdraft2 = processfolder+"\\"+outputdatasetdraft2[:-4]+"_draft2.shp"
    tif_output = finalfolder+"\\"+outputdatasetdraft2[:-4]+"_final.tif"
    shapefileToRasterProcess(inputdatasetandpath, shp_outputdraft1, shp_outputdraft2, tif_outputdraft1, tif_output, useBuffer, buffer_threshold, selectSomeData, selection_threshold)
elif inputdataset[-4:] == ".tif": 
    tif_output = finalfolder+"\\"+outputdatasetdraft2[:-4]+"_final.tif"   
    rasterToRasterProcess(inputdatasetandpath, tif_outputdraft1, tif_output, selectSomeData, selection_threshold)
(printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("Preprocessing step 1 has been calculated, {}\n".format(printline))

