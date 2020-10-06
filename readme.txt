Create Perpendicular Lines, takes a line shapefile and generates perpendicular lines to each record.   
The new perpendicular line intersect the original record at the mid-point of that line segment.  
The resulting geometry is written to a text file which can then be converted to a new shapefile 
using the Create Features from Text File tool in ArcToolbox.

The input line file should be single part line file (multipart line files will give false results).

The original line file should be in a projected coordinate system.

The tool gets the slope for each line segment and a perpendicular slope using the starting and 
ending line x, y coordinates.  The perpendicular angle is used in conjunction with the mid-point 
coordinates, and the distance value,  to generate a new line by solving for the x,y coordinate 
ends of the perpendicular line.  The distance value (user defined) will be the distance along the 
most appropriate x or y axis to extend the new perpendicular line.  So, be warned, the distance 
value in not the distance along the perpendicular line axis, it is the distance gained in the x or
y direction depending on value of the original slope.  
