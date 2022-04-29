# #Across valley topograpic profile
# #Daniel Hensel
# #04/05/2022


#Import desired libraries
import pandas
import requests, os, zipfile, arcpy, pandas as pd,sys, io, numpy, gdal, arcpy.sa

#Set workspace, try if it exists and set ouput overite to true

#All data changing for different projects is done here
#
#
#
arcpy.env.workspace = r"D:\data\BIG_TH" #If changing for alternate data change this line to directory
if not arcpy.Exists(arcpy.env.workspace):
    print("Workspace does not exist")

arcpy.env.overwriteOutput = True


UTM = arcpy.env.workspace + r"\bounds\26913.prj" #Change this line for correct prj file
big_th = arcpy.env.workspace + r"\acrossline.shp" #Change this line for correct line file
raster = arcpy.env.workspace + r"\USGS_one_meter_x47y448_CO_SoPlatteRiver_Lot2b_2013.tif" # Change for DEM/Raster Dataset with elevation

#
#
#Nothing after this point needs changed

file = arcpy.env.workspace + r"\Big_Thompson.zip"
#Ammend current zipfile

zip = zipfile.ZipFile(file, 'a')

#Set file variables & File location for UTM 13N & #Set ouput variable for UTM projection
#boundbox = arcpy.env.workspace + r"\Big_Thompson_Buffer.shp"

#If there is data that is reprojected

out = arcpy.env.workspace + r"\Streams_UTM"
bthom = out + ".shp"

#Extract the data from the zipfile
try:
    zip.extractall(arcpy.env.workspace)
except:
    print("Couldn't extract the data from ", file)

#Provide a list of feature classes within the data

lfc = arcpy.ListFeatureClasses()

#Return the name of refernce system in each class

for f in lfc:
    spat = arcpy.Describe(f).SpatialReference
    print(spat.name)
    if spat.name == "NAD_1983_UTM_Zone_13N":
        print("Already in UTM 13N")
    else:
        arcpy.Project_management(f, out, UTM)

#Project the data into UTM












#Set variables for points along lines tool

bthom = out + ".shp"
stag = arcpy.env.workspace + r"\Streams_pointed.shp"

#Run points along lines tool

#Two different ways to do this but I found the second was better for the matlab code I want to run
#arcpy.GeneratePointsAlongLines_management(st_vrain,stag,"PERCENTAGE",Percentage=10)

arcpy.GeneratePointsAlongLines_management(big_th, stag, 'DISTANCE', Distance='25 meters',Include_End_Points='END_POINTS')

#Add a field "Distance" to the points attributes

try:
     arcpy.AddField_management(stag,"Distance","DOUBLE")
except:
     print(arcpy.GetMessages())

#Calculate the field to set the 25m intervals for correct use in further MatLab code
#Muller equation code requres a profile of 250m in length 25m apart; hence the bounding box and intervals
expression = "!FID! * 25"
arcpy.CalculateField_management(stag,"Distance",expression)

#This works but only for this spesific research area, my goal is to come back to this during the final project and use a
# spatial join as well as the tool "Split line" and then compiling the results in the table for use for other field areas




#Set variable for DEM data

raster = arcpy.env.workspace + r"\USGS_one_meter_x47y448_CO_SoPlatteRiver_Lot2b_2013.tif"

#Use the add surface information tool to add elevation points to the csv
arcpy.sa.AddSurfaceInformation(stag,raster,"Z")

#Set output csv file

outf = arcpy.env.workspace + "\output.csv"


# Using https://community.esri.com/t5/python-questions/export-attribute-table-to-csv/td-p/254585 I was able to export Distance and Z to a csv without headers

nparr = arcpy.da.FeatureClassToNumPyArray(stag, ['Distance','Z'])
numpy.savetxt(outf, nparr, delimiter=",", fmt="%s")

#Set pandas dataframe to change over estimated value

df = pd.read_csv(outf)

print("Dataframe for", outf, "created")

#Change last endpoint to the correctly measured length so the over estimation is corrected
#Use a search cursor to determine shape length and round it, that should be the endpoints distance from start
for f in arcpy.da.SearchCursor(big_th, 'SHAPE@LENGTH'):
    leng = round(f[0])
df.at[5,'0.0']= leng
print(df)

#Rename headers to Distane and Elevation

col_Names=["Distance (m)","Elevation (m)"]

dfo= pd.read_csv(outf,names=col_Names)

#Save the dataframe to a csv file

dfo.to_csv(outf,index = False)




#If the spatial join and geoprocessing is done above delete this section because it will not be needed, for now it needs to stay to correct for the last endpoint.

print("Distance and elev column calculated in an exported csv for use with Manning Equation")





