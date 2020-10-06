try:
    import sys, string, os, arcpy, traceback, math
    def AddAndSubtractRadians(theta):
        return (theta + 1.57079632679, theta - 1.57079632679)       
    def Distance(x1, y1, x2, y2):
        '''Cartesian distance formula'''
        return float(math.pow(((math.pow((x2-x1),2)) + (math.pow((y2 - y1),2))),.5))   
    def CartesianToPolar(xy1, xy2):
        '''Given coordinate pairs as two lists or tuples, return the polar
        coordinates with theta in radians. Values are in true radians along the
        unit-circle, for example, 3.14 and not -0 like a regular python
        return.'''
        try:
            x1, y1, x2, y2 = float(xy1[0]), float(xy1[1]), float(xy2[0]), float(xy2[1])
            xdistance, ydistance = x2 - x1, y2 - y1
            distance = math.pow(((math.pow((x2 - x1),2)) + (math.pow((y2 - y1),2))),.5)
            if xdistance == 0:
                if y2 > y1:
                    theta = math.pi/2
                else:
                    theta = (3*math.pi)/2
            elif ydistance == 0:
                if x2 > x1:
                    theta = 0
                else:
                    theta = math.pi
            else:
                theta = math.atan(ydistance/xdistance)
                if xdistance > 0 and ydistance < 0:
                    theta = 2*math.pi + theta
                if xdistance < 0 and ydistance > 0:
                    theta = math.pi + theta
                if xdistance < 0 and ydistance < 0:
                    theta = math.pi + theta
            return [distance, theta]
        except:
            print"Error in CartesianToPolar()"  
    def PolarToCartesian(polarcoords):
        '''A tuple, or list, of polar values(distance, theta in radians) are
        converted to cartesian coords'''
        r = polarcoords[0]
        theta = polarcoords[1]
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        return [x, y]
    def gPrint(string):
        #print string
        arcpy.AddMessage(string) 
    def GetMidpointOfAStraightLine( x1, y1, x2, y2):
        midx = (x1 + x2)/2   
        midy = (y1 + y2)/2
        return [midx, midy]
    def GetSegmentLengths(thisrecordsgeometry):
        lengthlist = []
        positiontracker = 0
        totaldistance = 0
        try:
            for item in thisrecordsgeometry:
                x1 = thisrecordsgeometry[positiontracker][0]
                y1 = thisrecordsgeometry[positiontracker][1]
                x2 = thisrecordsgeometry[positiontracker +1][0]
                y2 = thisrecordsgeometry[positiontracker +1][1]
                segmentdistance = Distance(x1, y1, x2, y2)
                totaldistance = totaldistance + segmentdistance
                lengthlist.append(totaldistance)
                positiontracker += 1  
        except:
            pass
        return lengthlist
    def stringToBoolean(x):
        if x == 'true':
             x = True
        else:
             x = False
        return x
    gPrint("\n      Runing...Create Perpendicular Lines At The Midpoint of Line Features")
    gPrint("      A Two-Bit Algorithms product.\n      Copyright 2011 Gerry Gabrisch (gerry@gabrisch.us)\n")
    infc = arcpy.GetParameterAsText(0)
    distance = arcpy.GetParameterAsText(1)
    fcname = arcpy.GetParameterAsText(2)
    leftside = arcpy.GetParameterAsText(3)
    rightside = arcpy.GetParameterAsText(4)
    bothsides = arcpy.GetParameterAsText(5)
    
    leftside = stringToBoolean(leftside)
    rightside = stringToBoolean(rightside)
    bothsides = stringToBoolean(bothsides)
    
    gPrint("      Cracking Features...")
    #Get the input line files geometry as a python list.
    desc = arcpy.Describe(infc)
    shapefieldname = desc.ShapeFieldName
    rows = arcpy.SearchCursor(infc)
    listofpointgeometry = []
    gPrint("      Finding Midpoints...")
    for row in rows:
        feat = row.getValue(shapefieldname)
        midpointDistance = (feat.length/2)
        partnum = 0
        partcount = feat.partCount
        thisrecordsgeometry = []
        while partnum < partcount:
            part = feat.getPart(partnum)
            pnt = part.next()
            pntcount = 0
            while pnt:
                thetuple = [pnt.X, pnt.Y]
                thisrecordsgeometry.append(thetuple)
                pnt = part.next()
                pntcount += 1
            partnum += 1
        startnode = [thisrecordsgeometry[0][0], thisrecordsgeometry[0][1]]
        endnode = [thisrecordsgeometry[-1][0], thisrecordsgeometry[-1][1]]
        #If the line is straight, then do this simple calculation to get its midpoint....
        if len(thisrecordsgeometry) == 2:
            midpoint = GetMidpointOfAStraightLine( thisrecordsgeometry[0][0], thisrecordsgeometry[0][1],thisrecordsgeometry[1][0], thisrecordsgeometry[1][1])
        #If the line is made of more than two verticies, sum up the line segments until the center point is located...    
        else:
            listofsegmentlengths = GetSegmentLengths(thisrecordsgeometry)
            nodecounter = 1
            for item in listofsegmentlengths:
                if item < midpointDistance:
                    nodecounter += 1
                else:
                    distanceback = item - midpointDistance 
                    break
            polar = CartesianToPolar(thisrecordsgeometry[nodecounter], thisrecordsgeometry[nodecounter -1])            
            polardistancetomidpoint = [distanceback, polar[1]]
            midpointascartesiantemp = PolarToCartesian(polardistancetomidpoint)
            midx = thisrecordsgeometry[nodecounter][0] + midpointascartesiantemp[0]
            midy = thisrecordsgeometry[nodecounter] [1] + midpointascartesiantemp[1]
            midpoint = [midx,midy]
        listofpointgeometry.append([startnode,midpoint,endnode])  
    #Create the data models to store the new geometery....    
    featureList = []
    array = arcpy.Array()
    pnt = arcpy.Point()
    gPrint("      Defining Perpendicular Lines...")
    for pt in listofpointgeometry:
        startx = pt[0][0]
        starty = pt[0][1]
        midx = pt[1][0]
        midy = pt[1][1]
        endx = pt[2][0]
        endy = pt[2][1]
        #use the start point and end point to get a theta
        polarcoor = CartesianToPolar((startx,starty), (endx,endy))
        #Add and subtract the 90 degrees in radians from the line...
        ends = AddAndSubtractRadians(polarcoor[1])
        firstend = PolarToCartesian((float(distance),float(ends[0]))) 
        secondend = PolarToCartesian((float(distance),float(ends[1])))
        firstx2 = midx + firstend[0]
        firsty2 = midy + firstend[1]
        secondx2 = midx + secondend[0]
        secondy2 = midy + secondend[1]
        if bothsides:
            pnt.X, pnt.Y = firstx2 , firsty2
            array.add(pnt)
            pnt.X, pnt.Y = secondx2 , secondy2
            array.add(pnt)
            polyline = arcpy.Polyline(array)
            array.removeAll()
            featureList.append(polyline)
        if leftside:
            pnt.X, pnt.Y = midx , midy
            array.add(pnt)
            pnt.X, pnt.Y = firstx2 , firsty2
            array.add(pnt)
            polyline = arcpy.Polyline(array)
            array.removeAll()
            featureList.append(polyline)
        if rightside:
            pnt.X, pnt.Y = pnt.X, pnt.Y = midx , midy
            array.add(pnt)
            pnt.X, pnt.Y = secondx2 , secondy2
            array.add(pnt)
            polyline = arcpy.Polyline(array)
            array.removeAll()
            featureList.append(polyline)
    gPrint("      Creating New Feature Class...")
    arcpy.CopyFeatures_management(featureList, fcname)
    spatialRef = arcpy.Describe(infc).spatialReference
    arcpy.DefineProjection_management(fcname, spatialRef)   
    gPrint ("      Done")      
except arcpy.ExecuteError: 
    msgs = arcpy.GetMessages(2) 
    arcpy.AddError(msgs)  
    gPrint(msgs)
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)
    gPrint(pymsg + "\n")
    gPrint (msgs)