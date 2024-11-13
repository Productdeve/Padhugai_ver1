from array import array
from datetime import date
import numpy as np
# import pandas as pd
# import subprocess
# import json
# from datetime import datetime as dtc
# from datetime import datetime
# import numpy
# from django.shortcuts import render
# from rest_framework import status
# # Create your views here.
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from scipy.integrate import cumtrapz
# from scipy.signal import find_peaks
# from scipy.ndimage import gaussian_filter1d
#
# from .models import UserModel, PatientModel, SessionModel
# from django.http import JsonResponse
# from .serializers import UserSerializer
# from django.db import connection
# from django.forms.models import model_to_dict
# import cv2
# import datetime
# import os

from array import array
from datetime import date
import numpy as np
import pandas as pd
import subprocess
import json
from datetime import datetime as dtc
# import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from numpy.linalg import norm
import numpy
from django.shortcuts import render
from rest_framework import status
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from scipy.integrate import cumtrapz
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from .models import UserModel, PatientModel, SessionModel
from django.http import JsonResponse
from .serializers import UserSerializer
from django.db import connection
from django.forms.models import model_to_dict
import cv2
import datetime
from skimage.filters import threshold_otsu
import os
import random

from .queries import reportminmaxavgPresQuery,reportcopstepsQuery,reportswingQuery,reportstanceQuery
from .queries import reportstrideQuery,reportcadQuery,reportstridelenvelQuery
fset=0

@api_view(["GET","POST"])
def login(request):
    print("checking here")
    email =request.data["email"]
    passwd =request.data["passwd"]
    print(email,passwd)
    users = UserModel.objects.raw(
        'select 1 as id, username,userid, rolename,usertype, domain FROM Userz where emailid= %s and passwd = crypt(%s,passwd)',
        [email, passwd])
    if users:
        for u in users:
             print(u.username, u.usertype, u.userid)
        return JsonResponse({'status': 'Success' , 'userid': u.userid, 'rolename':u.rolename, 'domain':u.domain, 'name':u.username, 'usertype':u.usertype})
    else:
        return JsonResponse({'status': 'Error'})

@api_view(["GET","POST"])
def videos(request):
    print("checking here")
    users = UserModel.objects.raw('select 1 as id, username,userid, rolename, domain FROM Userz where emailid= %s and passwd = crypt(%s,passwd)',[email, passwd])
    for u in users:
        print(u.username, u.userid,u.rolename, u.domain)
    if not users :
        return JsonResponse({'status': 'Error'})
    else:
        return JsonResponse({'status': 'Success' , 'userid': u.userid, 'rolename':u.rolename, 'domain':u.domain, 'name':u.username})




@api_view(["POST"])
def setanalyticsflags(request):
    uid = request.data["userid"]
    imean = request.data["insolemean"]
    ipeak = request.data["insolepeak"]
    cop = request.data["cop"]
    th = request.data["toehead"]
    sl = request.data["stridelength"]
    fa = request.data["footangle"]
    speed = request.data["speed"]
    with connection.cursor() as cursor:
        cursor.execute("Update userz set insolemean=%s , insolepeak=%s, cop=%s, toehead=%s, stridelength=%s, footangle=%s, speed=%s where userid =%s",[imean,ipeak,cop,th,sl,fa,speed,uid])
        connection.commit()
        count = cursor.rowcount
    print(count, "Record Updated successfully ")
    if count:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})



@api_view(["POST"])
def getanalyticsflags(request):
    print("started")
    uid = request.data["userid"]
    print(uid)

    with connection.cursor() as cursor:
        print(
            'select insolemean, insolepeak, cop, toehead, stridelength, footangle, speed from userz where emailid =%s",[uid]')
        cursor.execute("select insolemean, insolepeak, cop, toehead, stridelength, footangle, speed from userz where emailid =%s",[uid])
        c = cursor.fetchone()

    if c:
        return JsonResponse({'status': 'Success', 'insolemean':c[0], 'insolepeak':c[1], 'cop':c[2], 'toehead':c[3], 'stridelength':c[4],'footangle':c[5],'speed':c[6]})
    else:
        return JsonResponse({'status': 'Error'})






@api_view(["GET","POST"])
def checksproduct(request):
    prodid = request.data["productid"]
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM Userdevice WHERE udevid = %s", [prodid])
        p=cursor.fetchone()
    #print(p)
    print(p[0])
    #isthere=p[0]
    if p:
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def getproddetails(request):
    prodid = request.data["productid"]
    with connection.cursor() as cursor:
       cursor.execute("select macaddress from hardwaremake where makeid = (select leftmakeid from userdevice where udevid =%s ) UNION ALL (select macaddress from hardwaremake where makeid = (select rightmakeid from userdevice where udevid =%s ))", [prodid,prodid])
       macid= cursor.fetchall()
       m=cursor.rowcount
    if macid :
        if  m == 1 :
            lmid= macid[0][0]
            rmid = macid[0][0]
        else:
            lmid = macid[0][0]
            rmid = macid[1][0]  # next tuple's first value

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        with connection.cursor() as cursor:
            try:
                p= cursor.execute("select solesize, noofsensors from insole where insoleid = (select leftinsoleid from userdevice where udevid =%s ); ", [prodid])
                insoles= cursor.fetchall()
                print(insoles)
                solesize = insoles[0][0]
                noofsens = insoles[0][1]
            except Exception as e:
                print(e)
        #solesize = insoles[0][0]
        #noofsens = insoles[0][1]  # next tuple's first value
        print("Completed")
        return JsonResponse({'status': 'Success', 'leftmac': lmid, 'rightmac':rmid, 'size':str(solesize), 'totalsensors':str(noofsens) })
    else:
        return JsonResponse({'status': 'Error'})


@api_view(["POST"])
def deviceregister(request):
    email = request.data["email"]
    prodid = request.data["productid"]
    devname = request.data["devicename"]

    with connection.cursor() as cursor:
       cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
       cursor.execute("update userdevice set email = %s, devicename= %s, registeredtime = CURRENT_TIMESTAMP(0),devactivestatus=true where udevid=%s", [email,devname,prodid])
       connection.commit()
       count = cursor.rowcount
       print(count, "Record Updated successfully ")
    if count:
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def checkifregistered(request):
    email = request.data["email"]
    with connection.cursor() as cursor:
       cursor.execute("select count(*) from userdevice where email=%s and devactivestatus=true", [email])
       count = cursor.fetchone()
    if count:
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})

@api_view(["GET","POST"])
def getdevdetails(request):
    email = request.data["email"]
    arr2 = []
    with connection.cursor() as cursor:
        cursor.execute("select registeredtime, udevid ,devicename, samplingrate from userdevice where email=%s and devactivestatus=TRUE and blockedstatus=false order by devicename asc" , [email])
        count = cursor.fetchall()
    if count:
        for c in count:
            arr2.append({"time": c[0], "deviceid": c[1], "devicename": c[2], "samplingrate": c[3]})
        return Response(arr2)
    else:
        return JsonResponse({'status': 'Error'})



@api_view(["GET","POST"])
def getadmindevdetails(request):
    arr2 = []
    with connection.cursor() as cursor:
        cursor.execute("select macaddress from hardwaremake where makestatus=true")
        count = cursor.fetchall()
    if count :
        for c in count:
           arr2.append({"id": c[0]})
        return Response(arr2)
    else:
        return JsonResponse({'status': 'Error'})


@api_view(["POST"])
def devdelete(request):
    prodid = request.data["productid"]
    with connection.cursor() as cursor:
       cursor.execute("update userdevice set devactivestatus=False where udevid=%s", [prodid])
       connection.commit()
       count = cursor.rowcount
       print(count, "Record Deleted successfully ")
    if count:
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})




@api_view(["GET","POST"])
def admingetpairdetails(request):
    arr2 = []
    with connection.cursor() as cursor:
        cursor.execute("select registeredtime, udevid,leftmakeid,rightmakeid,devactivestatus,email,devicename,blockedstatus,samplingrate from userdevice")
        count = cursor.fetchall()
    if count :
        for c in count:
            with connection.cursor() as cursor:
               ids1 = c[2]
               p = cursor.execute("select macaddress from hardwaremake where makeid=%s",[ids1])
               insoles = cursor.fetchall()
               for p in insoles:
                   leftid = p[0]
                   with connection.cursor() as cursor1:
                       ids2 = c[3]
                       q = cursor1.execute("select macaddress from hardwaremake where makeid=%s", [ids2])
                       insoles1 = cursor1.fetchall()
                       for q in insoles1:
                            rightid = q[0]
                       arr2.append({"time": c[0], "deviceid": c[1], "leftid": leftid, "rightid": rightid, "status": c[4], "email": c[5], "devicename": c[6], "block": c[7], "sampling": c[8]})
        return Response(arr2)
    else:
        return JsonResponse({'status': 'Error'})






@api_view(["POST"])
def deletehardwaremac(request):
    print("started")
    prodid = request.data["productid"]
    print(prodid)
    with connection.cursor() as cursor:
       cursor.execute("update hardwaremake set makestatus=False where macaddress=%s", [prodid])
       connection.commit()
       count = cursor.rowcount
       print(count, "Record Deleted successfully ")
    if count:
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})



@api_view(["POST"])
def playeradd(request):
    email = request.data["email"]
    pid = request.data["playerid"]
    pname = request.data["playername"]
    age = request.data["age"]
    weight = request.data["weight"]
    gender = request.data["gender"]
    cid = request.data["userid"]
    with connection.cursor() as cursor:
       cursor.execute("select count(*) from playerdetails where playerid =%s", [pid])
       count = cursor.fetchone()
    if count[0] == 0 :
       try:  #no such player exists
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
            query = """INSERT INTO playerdetails(emailid,playerid,playername,age,weight,gender,coachid, registeredtime,registereddate) values(%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP(0),current_date)"""
            cursor.execute(query, [email, pid, pname, age, weight, gender,cid])
            connection.commit()
            count1 = cursor.rowcount
            print(count1, "Player  Added successfully ")
       except Exception as e:
         print(e)

       if count1:
             return JsonResponse({'status': 'Success'})
       else:
             return JsonResponse({'status': 'Error'})
    else:
        #such a player exists so change playerstatus
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE PLAYERDETAILS SET playerstatus = true,playername=%s,age=%s,weight=%s WHERE playerid =%s", [pname,age,weight,pid])
            return JsonResponse({'status': 'Success'})
        except Exception as e:
            print(e)

# player delete api???



@api_view(["GET","POST"])
def checkplayer(request):
    email = request.data["email"]
    with connection.cursor() as cursor:
       cursor.execute("select count(*) from playerdetails where emailid =%s and playerstatus= true", [email])
       count = cursor.fetchone()
    if count:
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def checksession(request):
    sid = request.data["sid"]
    with connection.cursor() as cursor:
       cursor.execute("select count(*) from subsessionactivity where sessionid =%s and subactstatus= true", [sid])
       count = cursor.fetchone()
    if count :
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})


@api_view(["POST"])
def storelogreport(request):
    email = request.data["emailid"]
    repdetails = request.data["report"]
    with connection.cursor() as cursor:
        p=cursor.execute("insert into logreport(date, emailid, report) values(CURRENT_DATE, %s,%s)", [email,repdetails])
        rc = cursor.rowcount
    if rc:
        return JsonResponse({'status': "success"})
    else :
         return  JsonResponse({'status':"error"})




@api_view(["GET","POST"])
def getplayerdetails(request):
    print("here")
    email = request.data["email"]
    arr2=[]
    with connection.cursor() as cursor:
       try:
        print(email)
        cursor.execute("select playername,age,gender,weight,registeredtime,registeredtime,playerid from playerdetails where emailid =%s and playerstatus= true order by playername,playerid", [email])
        count = cursor.fetchall()
        print(">>>>>>>>>>>>>>>>>>>>>")
        
        print(count)
        if count :
            for c in count:
                 arr2.append({"name":c[0], "age":c[1], "gender":c[2], "weight":c[3], "time":c[4], "date": c[5], "playerid":c[6]})
            print(" next .....", arr2)
            # time, name, age, weight, gender, uuid
            return Response(arr2)
        else:
            return JsonResponse({'status': 'Error'})

       except Exception as e:
           print(e)


@api_view(["GET","POST"])
def getsession(request):
    sid = request.data["sid"]
    arr2=[]
    with connection.cursor() as cursor:
       cursor.execute("select startdate,enddate,activityname from subsessionactivity where ssactivityid =%s", [sid])
       count = cursor.fetchall()
       if count:
           for c in count:
               arr2.append({"start":c[0], "end":c[1], "name":c[2]})
           print(" next .....",arr2)
           #time, name, age, weight, gender, uuid
           return Response(arr2);
       else:
           return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def getsessiondetails(request):
    sid = request.data["sid"]
    arr2=[]
    with connection.cursor() as cursor:
       cursor.execute("select ssactivityid,startdate,enddate,activityname from subsessionactivity where sessionid =%s and subactstatus= true", [sid])
       count = cursor.fetchall()
       if count:
           for c in count:
               arr2.append({"id":c[0], "start":c[1], "end":c[2], "name":c[3]})
           print(" next .....",arr2)
           #time, name, age, weight, gender, uuid
           return Response(arr2);
       else:
           return JsonResponse({'status': 'Error'})

# api for session delete??

@api_view(["GET","POST"])
def getvideoid(request):
    vid = request.data["videoid"]
    arr2=[]
    with connection.cursor() as cursor:
       cursor.execute("select vhours,vmins,vsecs,videostatus,description from videofile where videoid =%s", [vid])
       count = cursor.fetchall()
       if count:
           for c in count:
               arr2.append({"vhours":c[0], "vmins":c[1], "vsecs":c[2], "videostatus":c[3], "description":c[4]})
           print(" next .....",arr2)
           return Response(arr2);
       else:
           return JsonResponse({'status': 'Error'})



@api_view(["GET","POST"])
def getvideometadata(request):
    vid = request.data["videourl"]
    arr2 =[]
    video_url=vid
    print("video url",video_url)
    command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_url]
    output = subprocess.check_output(command).decode('utf-8')
    metadata = json.loads(output)
    print(metadata)
    print(json.dumps(metadata, indent=4))
    cdt=metadata['streams'][0]['tags']['creation_time']
    arr2.append({"createddate": cdt})
    return Response(arr2)



@api_view(["GET","POST"])
def updatevideo(request):
    vid = request.data["videoid"]
    vsecs = request.data["vsecs"]
    vmins = request.data["vmins"]
    vhour = request.data["vhour"]
    status = request.data["status"]

    with connection.cursor() as cursor:
        p = cursor.execute("SELECT description from videofile where videoid=%s", [vid])
        c = cursor.fetchone()
    vidurl = c[0]
    print("video url: ", c[0])
    cap = cv2.VideoCapture(vidurl)
    print("Accessing video and its details.................................")
    fps = cap.get(cv2.CAP_PROP_FPS)
    print('opencv .....frames per second =', fps)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Total frames in the video", total)
    seconds1 = round(total / fps)
    video_time = datetime.timedelta(seconds=seconds1)
    print(f"duration in seconds: {seconds1}")
    print("---------------- video and its details.................................")

    with connection.cursor() as cursor:
       cursor.execute("update videofile set vhours=%s,vmins=%s,vsecs=%s,videostatus=%s,fps=%s where videoid =%s", [vhour,vmins,vsecs,status,fps,vid])
       connection.commit()
       count1 = cursor.rowcount
       print(count1, "Player  Deleted successfully ")
    if count1:
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def getplayerdetailsid(request):
        email = request.data["playerid"]
        arr2 = []
        with connection.cursor() as cursor:
            cursor.execute("select playername,age,gender,weight,registereddate,playerid from playerdetails where "
                           "playerid =%s",
                [email])
            count = cursor.fetchall()
            if count:
                for c in count:
                    arr2.append({"name": c[0], "age": str(c[1]), "gender": c[2], "weight": str(c[3]), "time": c[4], "playerid": str(c[5]), "status":"Success"})
                print(" next .....", arr2)
                # time, name, age, weight, gender, uuid
                return Response(arr2);
            else:
               return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def peakvalues(request):
        start = request.data["start"]
        end = request.data["end"]
        sid = request.data["sid"]
        dir = request.data["dir"]
        arr2 = []
        with connection.cursor() as cursor:
            cursor.execute('select s1,s2,s3,s4,s5,capturedtime from sensordata where sessionid = %s and capturedtime>=%s and capturedtime<= %s and soletype = %s' ,
                [sid,start,end,dir])
            count = cursor.fetchall()
            if count :
                for c in count:
                    fmax = max(c[0],c[1],c[2],c[3],c[4])
                    arr2.append({"month": c[5], "sales": fmax})
                print(" next .....", arr2)
                # time, name, age, weight, gender, uuid
                return Response(arr2);
            else:
               return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def meanvalues(request):
        start = request.data["start"]
        end = request.data["end"]
        sid = request.data["sid"]
        dir = request.data["dir"]
        arr2 = []
        with connection.cursor() as cursor:
            cursor.execute('select s1,s2,s3,s4,s5,capturedtime from sensordata where sessionid = %s and capturedtime>=%s and capturedtime<= %s and soletype = %s' ,
                [sid,start,end,dir])
            count = cursor.fetchall()
            for c in count:
                fmax = c[0]+c[1]+c[2]+c[3]+c[4]
                fmax = fmax/5
                arr2.append({"month": c[5], "sales": fmax})
        print(" next .....", arr2)
        # time, name, age, weight, gender, uuid
        if count:
            return Response(arr2);
        else:
            return JsonResponse({'status': 'Error'})







@api_view(["GET","POST"])
def lcopvalues(request):
        start = request.data["start"]
        end = request.data["end"]
        sid = request.data["sid"]
        dir = request.data["dir"]
        arr2 = []
        with connection.cursor() as cursor:
            cursor.execute('select s1,s2,s3,s4,s5,capturedtime from sensordata where sessionid = %s and capturedtime>=%s and capturedtime<= %s and soletype = %s' ,
                [sid,start,end,dir])
            count = cursor.fetchall()
            for c in count:
                xcop = (c[0] * 70) + (c[1] * 23) + (c[2] * 19) + (c[3] * 40) + (c[4] * 57)
                ptot = (c[0] + c[1] + c[2] + c[3] + c[4])
                # xcop = (c[0] * 70) + (c[1] * 23) + (c[3] * 40) + (c[4] * 57)
                # ptot = (c[0] + c[1] + c[3] + c[4])
                xcopf = xcop / ptot
                ycop = (c[0] * 201) + (c[1] * 183) + (c[2] * 127) + (c[3] * 48) + (c[4] * 33)
                # ycop = (c[0] * 201) + (c[1] * 183)  + (c[3] * 48) + (c[4] * 33)
                ycopf = ycop/ptot
                xcopf = int(xcopf)
                ycopf = int(ycopf)

                arr2.append({"month": xcopf, "sales": ycopf})
        print(" next .....", arr2)
        # time, name, age, weight, gender, uuid
        if count:
            return Response(arr2);
        else:
            return JsonResponse({'status': 'Error'})



@api_view(["GET","POST"])
def rcopvalues(request):
        start = request.data["start"]
        end = request.data["end"]
        sid = request.data["sid"]
        dir = request.data["dir"]
        arr2 = []
        with connection.cursor() as cursor:
            cursor.execute('select s1,s2,s3,s4,s5,capturedtime from sensordata where sessionid = %s and capturedtime>=%s and capturedtime<= %s and soletype = %s' ,
                [sid,start,end,dir])
            count = cursor.fetchall()
            t1 = 0;
            t2 = 0;
            t3 = 40;
            t4 = 110;
            for c in count:
                xcop = (c[0] * 19) + (c[1] * 66) + (c[2] * 68) + (c[3] * 41) + (c[4] * 26)
                ptot = (c[0] + c[1] + c[2] + c[3] + c[4])
                xcopf = xcop / ptot
                ycop = (c[0] * 201) + (c[1] * 181) + (c[2] * 131) + (c[3] * 46) + (c[4] * 34)
                ycopf = ycop / ptot
                xcopf = int(xcopf)
                ycopf = int(ycopf)
                t1 = max(xcopf, t1)
                t3 = min(xcopf, t3)
                t2 = max(ycopf, t2)
                t4 = min(ycopf, t4)
                arr2.append({"month": xcopf, "sales": ycopf})
        print(" next .....", arr2)
        # time, name, age, weight, gender, uuid
        if count:
            print(t1);
            print(t2);
            print(t3)
            print(t4)
            return Response(arr2);
        else:
            return JsonResponse({'status': 'Error'})



@api_view(["GET","POST"])
def footvalues(request):
        start = request.data["start"]
        end = request.data["end"]
        sid = request.data["sid"]
        dir = request.data["dir"]
        arr2 = []
        with connection.cursor() as cursor:
            cursor.execute('select s1,s2,s3,s4,s5,capturedtime from sensordata where sessionid = %s and capturedtime>=%s and capturedtime<= %s and soletype = %s' ,
                [sid,start,end,dir])
            count = cursor.fetchall()
            for c in count:
                toe = c[0]+c[1]+c[2]
                toe = toe/3
                heel = c[3]+c[4]
                heel = heel/2

                arr2.append({"month": c[5], "sales": toe, "sales1": heel})
        print(" next .....", arr2)
        # time, name, age, weight, gender, uuid
        if count:
            return Response(arr2);
        else:
            return JsonResponse({'status': 'Error'})



@api_view(["POST"])
def playerdelete(request):
    pid = request.data["playerid"]
    with connection.cursor() as cursor:
        cursor.execute("UPDATE PLAYERDETAILS SET playerstatus = false WHERE playerid =%s",[pid])
        connection.commit()
        count1 = cursor.rowcount
        print(count1, "Player  Deleted successfully ")
    if count1:
           return JsonResponse({'status': 'Success'})
    else:
           return JsonResponse({'status': 'Error'})


@api_view(["POST"])
def historydelete(request):
    pid = request.data["historyid"]
    with connection.cursor() as cursor:
        cursor.execute("UPDATE SESSIONACTIVITY SET sessionstatus = false WHERE sessionid =%s",[pid])
        connection.commit()
        count1 = cursor.rowcount
        print(count1, "Player  Deleted successfully ")
    if count1:
           return JsonResponse({'status': 'Success'})
    else:
           return JsonResponse({'status': 'Error'})



@api_view(["GET","POST"])
def trainingplayerstatus(request):
    pid = request.data["playerid"]
    with connection.cursor() as cursor:
        cursor.execute("SELECT playerid FROM sessionactivity WHERE playerid =%s and sessionstatus=true",[pid])
        count1 = cursor.rowcount
        print(count1, "Players  there ")
    if count1:
           return JsonResponse({'status': 'Success'})
    else:
           return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def getmaxvaluestatus(request):
    pid = request.data["sessionid"]
    with connection.cursor() as cursor:
        cursor.execute("select capturedtime from sensordata where sessionid =%s AND soletype='L' ORDER BY sensordataid DESC LIMIT 1",
                       [pid])
        count = cursor.fetchall()
        if count :
            for c in count:
                print(c[0])
    with connection.cursor() as cursor:
        cursor.execute("select capturedtime from sensordata where sessionid =%s AND soletype='R' ORDER BY sensordataid DESC LIMIT 1",
                       [pid])
        count = cursor.fetchall()
        if count :
            for s in count:
                print(s[0])
    if count:
           return JsonResponse({'status': 'Success', 'Left': str(c[0]), 'Right':str(s[0])})
    else:
           return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def getmaxtimestatus(request):
    pid = request.data["sessionid"]
    print(pid)
    with connection.cursor() as cursor:
        cursor.execute("select starttime from sessionactivity where sessionid =%s",[pid])
        print("query completed")
        count = cursor.fetchone()
        print(count[0])
        if count:
            try:
                date = count[0].strftime("%Y-%m-%d %H:%M:%S")
                print("date: %s" % date)
            except Exception as e:
                print(e)
            return JsonResponse({'status': 'Success', 'Left': date, 'Right':date})
        else:
             return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def trainingplayerhistory(request):
    pid = request.data["playerid"]
    print(pid)

    #date,sessionid,mode,video
    #mode: Online /Offline
    #video -> 0 or1   0-notavailable,1-available
    sessions = []
    mode = []
    dats = []
    totsens=[]
    vid = []
    sta =0
    arr =[]
    print(pid)
    with connection.cursor() as cursor:
        cursor.execute("SELECT sessionid,mode,videoid,date,udevid,totalsensors FROM sessionactivity WHERE playerid =%s and sessionstatus=true order by sessionid desc",[pid])
        count1 = cursor.rowcount
        ssns = cursor.fetchall()
        print(count1, "sessions are there ")
    if ssns :
        for s in ssns:
            print("sessionsid:",s[0],"  mode:",s[1], "  videoid:",s[2], " date:",s[3],"  totalsensors: ",s[5])
            sessions.append(s[0])
            mode.append(s[1])
            dats.append(s[3])
            totsens.append(s[5])
            print("working")
            with connection.cursor() as cursor:
              cursor.execute("SELECT fileavailability,description FROM videofile WHERE videoid =%s", [s[2]])
              videos = cursor.fetchone()
            print("videoid :",s[2]," video availability: ",videos[0])
            if videos[0]:
                  sta = 1
                  vid = s[2]
            else :
                  sta = 0
                  vid = s[2]

            arr.append({"testid": s[0], "date": s[3], "mode": s[1], "status": sta, "video": videos[1], "videoid": vid, "deviceid": s[4],"totalsensors":s[5]})

    if count1:
           return Response(arr)
    else:
           return JsonResponse({'status': 'Error'})


@api_view(["GET","POST"])
def macadminlist(request):
    arr2 = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT makeid,macaddress FROM hardwaremake WHERE makestatus=true")
        count1 = cursor.rowcount
        dl = cursor.fetchall()
    if dl:
        for c in dl:
                arr2.append(
                    {"id": c[0],"macid": c[1]})
        return Response(arr2)
    else:
        return Response(arr2)




@api_view(["GET","POST"])
def listofdevices(request):
    email = request.data["email"]
    arr2 = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT devicename FROM USERDEVICE WHERE email =%s and devactivestatus=true and blockedstatus = false",[email] )
        count1 = cursor.rowcount
        dl = cursor.fetchall()
        print(count1, "Players  there ")
    if dl:
        for c in dl:
                arr2.append(
                    {"devicename": c[0]})
        return Response(arr2)
    else:
        return Response(arr2)



@api_view(["GET","POST"])
def listofplayers(request):
    email = request.data["email"]
    arr2=[]
    with connection.cursor() as cursor:
        cursor.execute(
            "select playername,age,gender,weight,registeredtime,playerid from playerdetails where emailid =%s and playerstatus= true order by playername,playerid asc",
            [email])
        count = cursor.fetchall()
    if count:
        for c in count:
            arr2.append({"name": c[0], "age": c[1], "gender": c[2], "weight": c[3], "time": c[4], "playerid": str(c[5])})
        print(" next .....", arr2)
        # time, name, age, weight, gender, uuid
        return Response(arr2);
    else:
        return Response (arr2);


@api_view(["GET","POST"])
def infoondevices(request):
    dname = request.data["devicename"]
    with connection.cursor() as cursor:
        cursor.execute(
            "select macaddress from hardwaremake where makeid = (select leftmakeid from userdevice where devicename =%s ) UNION (select macaddress from hardwaremake where makeid = (select rightmakeid from userdevice where devicename =%s ))",
            [dname, dname])
        macid = cursor.fetchall()
        m = cursor.rowcount;
    if macid :
        if m == 1:
            lmid = macid[0][0]
            rmid = macid[0][0]
        else:
            lmid = macid[0][0]
            rmid = macid[1][0]  # next tuple's first value

        with connection.cursor() as cursor:
            cursor.execute(
                "select udevid from userdevice where devicename =%s",
                [dname])
            devid = cursor.fetchone()
            m = cursor.rowcount;
        if devid:
            with connection.cursor() as cursor:
                p = cursor.execute(
                    "select solesize, noofsensors from insole where insoleid = (select leftinsoleid from userdevice where devicename =%s ) ",
                    [dname])
                insoles = cursor.fetchall()
            solesize = insoles[0][0]
            noofsens = insoles[0][1]  # next tuple's first value
            if macid:
                return JsonResponse(
                    {'status': 'Success', 'leftmac': lmid, 'rightmac': rmid, 'size': solesize, 'totalsensors': str(noofsens), 'devicename':dname, 'deviceid':str(devid[0])})
            else:
                return JsonResponse({'status': 'Error'})
        else:  # no such devicename for which devid exists!!
            return JsonResponse({'status': 'Error'})

    else: # no such devicename exists!!
        return JsonResponse({'status': 'Error'})

@api_view(["POST"])
def startsession(request):
    """
    playerid, leftmac, rightmac, deviceid, mode
    status: Success / Error
    mode: Online / Offline
    returns -->sessionid
    it  starts  session  starttime  insterd  using  current_time
    """

    pid = request.data["playerid"]
    print(pid)
    lmacaddr = request.data["leftmac"]
    print(lmacaddr)
    rmacaddr = request.data["rightmac"]
    print(rmacaddr)
    email = request.data["email"]
    print(email)
    deviceid = request.data["deviceid"]
    print(deviceid)
    modtype = request.data["mode"]
    print(modtype)
    try:
         sid = request.data["sessionid"]
    except Exception as e:
         sid = request.data["sessionId"]
    print(sid)
    totsens = request.data["totalsensor"]
    print(totsens)
    print("startingsession() .....................................checking here")
    print(pid, lmacaddr,rmacaddr,deviceid,modtype,sid)
    z=0
    with connection.cursor() as cursor:
        print("here 123..............................")
        c=cursor.execute("insert into VideoFile(Fileref) values ('')")
        v = cursor.execute("select max(videoid) from videofile")
        vid = cursor.fetchone()
        print("videoid is",vid[0])

        c = cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
        try:
            c3 = cursor.execute("Insert into activesession(sessionid,deviceid,status,type,email)values(%s,%s,%s,%s,%s)",[sid,deviceid,"0",modtype,email])
            rc3 = cursor.rowcount
        except Exception as e:
            print(e)
        if rc3:
            print("added to active session table.......")
        else:
            print("error.......... may be sessionid already there....")
        c2 = cursor.execute(
            "insert into SessionActivity(sessionid,udevID,playerid,videoid,starttime,date,mode,totalsensors) values(%s,%s,%s,%s,CURRENT_TIMESTAMP(0),CURRENT_DATE,%s,%s)",[sid,deviceid,pid,vid[0],modtype,totsens])
        rc2 = cursor.rowcount
    if c2:
           print("both tables added successfully!...............................")
           return JsonResponse({'status': 'success'})
    else:
           print("error");
           return JsonResponse({'status': 'error'})



@api_view(["POST"])
def storesensordat(request):
    print("here");
    ssnid = request.data["sessionid"]
    s1 = request.data["s1"]
    s2 = request.data["s2"]
    s3 = request.data["s3"]
    s4 = request.data["s4"]
    s5 = request.data["s5"]
    s6 = request.data["s6"]
    s7 = request.data["s7"]
    s8 = request.data["s8"]
    s9 = request.data["s9"]
    s10 = request.data["s10"]
    s11 = request.data["s11"]
    time = request.data["reltime"]
    stype = request.data["soltype"]
    macid = 0

    with connection.cursor() as cursor:
       try:
           cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
           p = cursor.execute("insert into sensordata(sessionid,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,soletype,capturedtime,macid,timelocal) "
                           "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,current_timestamp)",[ssnid,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,stype,time,macid])
       except Exception as e:
           print(e)
    if not p:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


@api_view(["GET","POST"])
def getsensorvalues(request):
    ssnid = request.data["sessionid"]

    with connection.cursor() as cursor:
        p = cursor.execute("select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,soletype,capturedtime,macid,timelocal from sensordata where sessionid = %s",[ssnid])
        c = cursor.fetchall()
    if not p:
        return JsonResponse({'status': 'success', 'sensordata':c})
    else:
        return JsonResponse({'status': 'error'})


@api_view(["GET","POST"])
def checksensorvalues(request):
    ssnid = request.data["sessionId"]
    try:

      with connection.cursor() as cursor:
        p = cursor.execute("select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,soletype,capturedtime,timelocal from sensordata where sessionid = %s order by sensordataid desc limit 1",[ssnid])
        c = cursor.fetchall()
      if p:
        if cursor.rowcount == 1:
            return JsonResponse({'status': 'exist'})
        else:
          return JsonResponse({'status': 'exist'})

    except Exception as e:
        print(e)





@api_view(["POST"])
def sessionend(request):
    ssnid = request.data["sessionid"]
    with connection.cursor() as cursor:
        cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
        p = cursor.execute("UPDATE sessionactivity set endtime =LOCALTIMESTAMP(0) where sessionid =%s ",[ssnid] )
        p1 = cursor.execute("UPDATE activesession set status =%s where sessionid =%s ", ["1",ssnid])
    if not p:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})



@api_view(["GET","POST"])
def datavisualprocess(request):
    ssnid = request.data["ssnid"]
    left ='L'
    right ='R'
    with connection.cursor() as cursor:
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s', [left, ssnid]);
        pats = cursor.fetchall()
    lxcops=[]
    lycops=[]
    lmean=[]
    lpeak=[]
    ltime=[]
    for p in pats:
        xcop=  (p[0] * 70) + (p[1] *23) + (p[2] *19) + (p[3]*40) +(p[4]*57)
        ycop = (p[0] * 201) + (p[1] * 183) + (p[2] * 127) + (p[3] * 48) + (p[4] * 33)
        ptot=(p[0] + p[1] + p[2] + p[3] + p[4])
        xcopf = xcop/ptot
        ycopf = ycop/ptot
        lxcops.append(xcopf)
        lycops.append(ycopf)
        lmax = max(p[1],p[2],p[3],p[4],p[5])
        mean = ptot/5
        lmean.append(mean)
        lpeak.append(lmax)
        ltime.append(p[5])

    with connection.cursor() as cursor:
        cursor.execute('select sensordataid, sessionid, s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s', [right, ssnid]);
        pats = cursor.fetchall()
    rxcops = []
    rycops = []
    rmean = []
    rpeak = []
    rtime = []
    for p in pats:
        xcop = (p[0] * 70) + (p[1] * 23) + (p[2] * 19) + (p[3] * 40) + (p[4] * 57)
        ycop = (p[0] * 201) + (p[1] * 183) + (p[2] * 127) + (p[3] * 48) + (p[4] * 33)
        ptot = (p[0] + p[1] + p[2] + p[3] + p[4])
        xcopf = xcop / ptot
        ycopf = ycop / ptot

        rxcops.append(xcopf)
        rycops.append(ycopf)
        rmax = max(p[0], p[1], p[2], p[3], p[4])
        mean = ptot / 5
        rmean.append(mean)
        rpeak.append(rmax)
        rtime.append(p[5])

    if not pats:
           return JsonResponse({'status': 'error' })
    else:
          return JsonResponse({'status': 'success', 'result': pats, 'leftxcop':lxcops, 'leftycop':lycops, 'leftmean':lmean, 'leftpeak':lpeak ,'leftime':ltime ,'rightxcop':rxcops, 'rightycop':rycops, 'rightmean':rmean,'rightpeak':rpeak, 'righttime':rtime})













@api_view(["POST"])
def startsubact(request):
        # sactid = request.data["subactid"]
        ssnid = request.data["sessionid"]
        stime = request.data["starttime"]
        etime = request.data["endtime"]
        aname = request.data["activityname"]
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
            p = cursor.execute("INSERT into subsessionactivity(sessionid,startdate,enddate,activityname) values(%s,%s,%s,%s)", [ssnid,stime,etime,aname])
            cursor.execute('SELECT max(ssactivityid) from subsessionactivity where sessionid=%s', [ssnid]);
            for s in cursor.fetchone():
                print(s)
        if p:
            return JsonResponse({'status': 'Success'})
        else:
            return JsonResponse({'status': 'Error'})


@api_view(["POST"])
def videoinsert(request):
        # sactid = request.data["subactid"]
        ssnid = request.data["id"]
        video = request.data["video"]
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
            p = cursor.execute("UPDATE videofile set description=%s,framecut=false WHERE videoid=%s", [video,ssnid])
        if not p:
            return JsonResponse({'status': 'Success'})
        else:
            return JsonResponse({'status': 'Error'})

@api_view(["POST"])
def videoedit(request):
        # sactid = request.data["subactid"]
        vid = request.data["videoid"]
        video_file = request.data["video"]        # video link address
        ##########delete frmae details of videoid (old ones)
        with connection.cursor() as cursor:
            p = cursor.execute(
                "DELETE FROM videodetails where videoid=%s",[vid])
            if p:
                  return JsonResponse({'status': 'Error'})

       ############### get25framesec
            # video_file = 'C:/Users/MYPC/Downloads/c8701.mp4'
            # video_file = 'C:/Users/MYPC/Videos/final.mp4'                       # 30 fps and  25 secs
            cap = cv2.VideoCapture(video_file)
            frame_interval = 25
            # frame_interval=30   #you can specify how many frames you want in one slot.
            # to compute each frame's duration
            frameduration = []
            slotduration = []
            #####################################
            fps = cap.get(cv2.CAP_PROP_FPS)
            print('opencv .....frames per second =', fps)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print("Total frames in the video", total)
            seconds1 = round(total / fps)
            video_time = datetime.timedelta(seconds=seconds1)
            print(f"duration in seconds: {seconds1}")
            #####################################
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            total_duration = total_frames * 1000.0 / fps
            btime = 1000 // fps
            frame_index = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                duration = frame_index * 1000.0 / fps

                print("frame#:", frame_index, "msec:", duration)
                frameduration.append({'frame#': frame_index, 'msec': duration})
                actualtime = btime + duration
                with connection.cursor() as cursor:
                    cursor.execute("insert into videodetails(videoid,frames,msecs,actualfps) values(%s,%s,%s,%s)",
                                   [vid, frame_index, duration, actualtime])
                if frame_index % frame_interval == 0:
                    slotduration.append({'frame#': frame_index, 'msec': duration})

                frame_index += 1

            cap.release()
            print(frameduration)
            print(slotduration)
            with connection.cursor() as cursor:
                cursor.execute("update videofile set framescut=true, videostatus= true, fps=%s where videoid = %s", [fps, vid])

            return JsonResponse({'fps': frameduration,
                                 'slot': slotduration})  # each frame duration in fps  and i use convention that 25 or 30 frames  as you specify as one slot so its duration is in slotduration

@api_view(["POST"])
def storearraysensordat(request):
    ssnid = request.data["sessionid"]
    #saar should be  <sensor values from s1..s11>,solytype,capturedtime
    sarr= request.data["sensorvalues"]
    macid = 0

    with connection.cursor() as cursor:
        cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
        try:
          for sval in sarr:
            p = cursor.execute(
                "insert into sensordata(sessionid,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,timelocal) "
                "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,current_timestamp)",
                [ssnid,sval[0], sval[1],sval[2], sval[3], sval[4], sval[5], sval[6], sval[7],sval[8], sval[9], sval[10],sval[11],sval[12],sval[13],sval[14]])
        except Exception as e:
            print(e)
        if not p:
            done =1
        else:
             done =0

    if done==1:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})




@api_view(["POST"])
def subsessiondelete(request):
        # sactid = request.data["subactid"]
        ssnid = request.data["sessionid"]
        activityid = request.data["activityid"]
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
            p = cursor.execute("UPDATE subsessionactivity set subactstatus=false WHERE ssactivityid=%s AND sessionid=%s", [activityid,ssnid])
        if  p:
            return JsonResponse({'status': 'Success'})
        else:
            return JsonResponse({'status': 'Error'})

@api_view(["POST"])
def endsubact(request):
        ssactid = request.data["ssactivityid"]
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
            p = cursor.execute("UPDATE subsessionactivity set endtime =LOCALTIMESTAMP(0) where ssactivityid =%s ",
                               [ssactid])
        if not p:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})


# give starttime and endtime ie., capturedtime column from sensordata table
@api_view(["GET","POST"])
def getsubactivitydata(request):
        ssnid = request.data["sessionid"]
        stime = request.data["starttime"]
        etime = request.data["endtime"]
        with connection.cursor() as cursor:
            p = cursor.execute(
                "SELECT s1,s2,s3,s4,s5,s6,s7,s8,s9,10,s11,capturedtime,soletype,timelocal from sensordata where capturedtime >= %s and capturedtime <= %s and sessionid =%s",
                [stime, etime, ssnid])
            c=cursor.fetchall()
        if not p:
            return JsonResponse({'status': 'success', 'data': c})
        else:
            return JsonResponse({'status': 'error'})


@api_view(["GET","POST"])
def datafromvidmeans(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]

    left ='L'
    right ='R'
    lmean = []
    rmean = []
    with connection.cursor() as cursor:
        cursor.execute('SELECT count(*),soletype from sensordata where  sessionid=%s  and capturedtime >= %s and capturedtime <= %s group by soletype',[ssnid,stime,etime])
        rlcnts = cursor.fetchall()
        print(rlcnts)
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s', [left, ssnid,stime,etime]);
        slval = cursor.fetchall()
        finalarr =[]
        for p in slval:
            ptot = (p[0] + p[1] + p[2] + p[3] + p[4])
            mean = ptot / 5
            lmean.append(mean)
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                       [right, ssnid,stime,etime]);
        srval = cursor.fetchall()
        for q in srval:
            ptot1 = (q[0] + q[1] + q[2] + q[3] + q[4])
            mean1 = ptot1 / 5
            rmean.append(mean1)
        cursor.execute(
            'select s1,s2,s3,s4,s5, capturedtime from sensordata where sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
            [ssnid, stime, etime]);
        allval = cursor.fetchall()

    rcnts= rlcnts[1][0]
    lcnts= rlcnts[0][0]
    print("right count: ",rcnts,"   left count: ",lcnts)
    tc = min(lcnts,rcnts)

    ts=0
    time=[]
    t = (etime - stime) // tc
    for s in range(0,tc):
        ts=ts+t
        time.append(ts)
    print(time)

    m = min(lcnts,rcnts);
    print(m)

    for i in range(tc):
         left = lmean[i]
         right = rmean[i]
         timef = time[i]
         finalarr.append({"month": timef, "sales": left, "sales1": right})

    return Response(finalarr)



@api_view(["GET","POST"])
def datafromvidpeaks(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]

    left ='L'
    right ='R'
    rpeak = []
    lpeak = []
    with connection.cursor() as cursor:
        cursor.execute('SELECT count(*),soletype from sensordata where  sessionid=%s  and capturedtime >= %s and capturedtime <= %s group by soletype',[ssnid,stime,etime])
        rlcnts = cursor.fetchall()
        print(rlcnts)
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s', [left, ssnid,stime,etime]);
        slval = cursor.fetchall()
        finalarr =[]
        for p in slval:
            lmax = max(p[0], p[1], p[2], p[3], p[4])
            lpeak.append(lmax)
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                       [right, ssnid,stime,etime]);
        srval = cursor.fetchall()
        for q in srval:
            rmax = max(q[0], q[1], q[2], q[3], q[4])
            rpeak.append(rmax)
        cursor.execute(
            'select s1,s2,s3,s4,s5, capturedtime from sensordata where sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
            [ssnid, stime, etime]);
        allval = cursor.fetchall()

    rcnts= rlcnts[1][0]
    lcnts= rlcnts[0][0]
    print("right count: ",rcnts,"   left count: ",lcnts)
    tc = min(lcnts,rcnts)

    ts=0
    time=[]
    t = (etime - stime) // tc
    for s in range(0,tc):
        ts=ts+t
        time.append(ts)
    print(time)

    m = min(lcnts,rcnts);
    print(m)

    for i in range(tc):
         left = lpeak[i]
         right = rpeak[i]
         timef = time[i]
         finalarr.append({"month": timef, "sales": left, "sales1": right})


    return Response(finalarr)



@api_view(["GET","POST"])
def datafromvidfoottrans(request):
    stime = request.data["start"]
    ssnid = request.data["ssnid"]
    etime = request.data["end"]

    left ='L'
    right ='R'
    rtoe = []
    rheal = []
    ltoe = []
    lheal = []

    with connection.cursor() as cursor:
        cursor.execute('SELECT count(*),soletype from sensordata where  sessionid=%s  and capturedtime >= %s and capturedtime <= %s group by soletype',[ssnid,stime,etime])
        rlcnts = cursor.fetchall()
        print(rlcnts)
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s', [left, ssnid,stime,etime]);
        slval = cursor.fetchall()
        finalarr =[]
        for p in slval:
            lmax = (p[0] + p[1] + p[2])
            lmax = lmax / 3
            ltoe.append(lmax)
            lmax1 = (p[3] + p[4])
            lmax1 = lmax1 / 2
            lheal.append(lmax1)
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                       [right, ssnid,stime,etime]);
        srval = cursor.fetchall()
        for q in srval:
            rmax = (q[0] + q[1] + q[2])
            rmax = rmax / 3
            rtoe.append(rmax)
            rmax1 = (q[3] + q[4])
            rmax1 = rmax1 / 2
            rheal.append(rmax1)
        cursor.execute(
            'select s1,s2,s3,s4,s5, capturedtime from sensordata where sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
            [ssnid, stime, etime]);
        allval = cursor.fetchall()

    rcnts= rlcnts[1][0]
    lcnts= rlcnts[0][0]
    print("right count: ",rcnts,"   left count: ",lcnts)
    tc = min(lcnts,rcnts)

    ts=0
    time=[]
    t = (etime - stime) // tc
    for s in range(0,tc):
        ts=ts+t
        time.append(ts)
    print(time)

    m = min(lcnts,rcnts);
    print(m)

    for i in range(tc):
         lefttoe = ltoe[i]
         righttoe = rtoe[i]
         leftheal = lheal[i]
         rightheal = rheal[i]
         timef = time[i]
         finalarr.append({"month": timef, "lefttoe": lefttoe, "leftheal": leftheal, "righttoe": righttoe, "rightheal": rightheal})


    return Response(finalarr)

@api_view(["GET","POST"])
def datafromvidfoots(request):
    stime = request.data["start"]
    ssnid = request.data["ssnid"]
    etime = request.data["end"]
    type = request.data["type"]

    left ='L'
    right ='R'
    rpeak = []
    lpeak = []
    with connection.cursor() as cursor:
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s', [type, ssnid,stime,etime]);
        slval = cursor.fetchall()
        finalarr =[]
        for p in slval:
            lmax = (p[0]+p[1]+p[2])
            lmax = lmax/3
            lpeak.append(lmax)
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                       [type, ssnid,stime,etime]);
        srval = cursor.fetchall()
        for q in srval:
            rmax = (q[3]+q[4])
            rmax = rmax/2
            rpeak.append(rmax)

        cursor.execute(
            'select s1,s2,s3,s4,s5, capturedtime from sensordata where sessionid=%s  and capturedtime >= %s and capturedtime <= %s',[ssnid, stime, etime]);
        allval = cursor.fetchall()

    print(lpeak)
    tc = len(lpeak)

    ts=0
    time=[]
    t = (etime - stime) // tc
    for s in range(0,tc):
        ts=ts+t
        time.append(ts)
    print(time)


    for i in range(tc):
         left = lpeak[i]
         right = rpeak[i]
         timef = time[i]
         finalarr.append({"month": timef, "sales": left, "sales1": right})


    return Response(finalarr)






@api_view(["GET","POST"])
def strides(request):
    stime = request.data["start"]
    ssnid = request.data["ssnid"]
    etime = request.data["end"]

    left ='L'
    right ='R'
    rpeak = []
    lpeak = []
    finalarr =[]
    with connection.cursor() as cursor:
        cursor.execute("SELECT s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='L'",[stime, etime, ssnid])
        cnt = cursor.rowcount
        p=cursor.fetchall()
        print(p)

    df = pd.DataFrame(p)
    acc_x = df.iloc[:, 0].values
    acc_y = df.iloc[:, 1].values
    acc_z = df.iloc[:, 2].values
    print(acc_x)

    for j in range(len(acc_x)):
         acc_x[j] = float(acc_x[j])
    for i in range(len(acc_y)):
         acc_y[i] = float(acc_y[i])
    for k in range(len(acc_z)):
         acc_z[k] = float(acc_z[k])

    g = 0.98
    acc_y = acc_y - g
    accleration = [acc_x, acc_y, acc_z]
    dt = 0.0175  # 1/43
    t = numpy.arange(0, len(acc_x) * dt, dt)
    vel_x = cumtrapz(acc_x, t, initial=0)
    vel_y = cumtrapz(acc_y, t, initial=0)
    vel_z = cumtrapz(acc_z, t, initial=0)
    velocity = list(zip(vel_x, vel_y, vel_z))
    vel_xy = list(zip(vel_x, vel_y))
    print(vel_x)
    vx = vel_x.astype(float)
    vy = vel_y.astype(float)
    print(vx)
    sp = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(vx, vy)]
    sp_max = np.max(sp)
    sp_avg = np.mean(sp)
    print("speed=", sp_max)
    print("avg=", sp_avg)
    #print(sp)

    #stride length calculation
    disp_x = cumtrapz(vel_x, t, initial=0)
    disp_y = cumtrapz(vel_y, t, initial=0)
    disp_z = cumtrapz(vel_z, t, initial=0)
    displacement = list(zip(disp_x, disp_y, disp_z))
    dx = disp_x.astype(float)
    dy = disp_y.astype(float)
    sl = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(dx, dy)]
    sl_max = np.max(sl)
    print("sl_max=", sl_max)
    # print(sl)
    t1 = float(12.64)
    # max_sl = max(sl)
    speed = sl_max / t1
    print("speed=", speed)
    tc = len(sl)
    ts=0
    time=[]


    t = (etime - stime) // tc
    for s in range(0,tc):
        ts=ts+t
        time.append(ts)
    print(time)

    finalarr.append({"month": 0, "sales": 0, "sales1": 0})
    for i in range(tc):
         left = round(sl[i],3)
         right = round(sp[i],3)
         timef = time[i]
         finalarr.append({"month": timef, "sales": left, "sales1": right})


    return Response(finalarr)



# stride metrics as graph..
@api_view(["GET","POST"])
def strides21(request):
    stime = request.data["start"]
    ssnid = request.data["ssnid"]
    etime = request.data["end"]

    left ='L'
    right ='R'
    lastStride = 0;
    rpeak = []
    lpeak = []
    finalarr =[]
    with connection.cursor() as cursor:
        cursor.execute("SELECT s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='L'",[stime, etime, ssnid])
        cnt = cursor.rowcount
        p=cursor.fetchall()
        print(p)

    df = pd.DataFrame(p)
    acc_x = df.iloc[:, 0].values
    acc_y = df.iloc[:, 1].values
    acc_z = df.iloc[:, 2].values
    print(acc_x)

    for j in range(len(acc_x)):
         acc_x[j] = float(acc_x[j])
    for i in range(len(acc_y)):
         acc_y[i] = float(acc_y[i])
    for k in range(len(acc_z)):
         acc_z[k] = float(acc_z[k])

    g = 0.98
    acc_y = acc_y - g
    accleration = [acc_x, acc_y, acc_z]
    dt = 0.0175  # 1/43
    t = numpy.arange(0, len(acc_x) * dt, dt)
    vel_x = cumtrapz(acc_x, t, initial=0)
    vel_y = cumtrapz(acc_y, t, initial=0)
    vel_z = cumtrapz(acc_z, t, initial=0)
    velocity = list(zip(vel_x, vel_y, vel_z))
    vel_xy = list(zip(vel_x, vel_y))
    print(vel_x)
    vx = vel_x.astype(float)
    vy = vel_y.astype(float)
    print(vx)
    sp = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(vx, vy)]
    sp_max = np.max(sp)
    sp_avg = np.mean(sp)
    print("speed=", sp_max)
    print("avg=", sp_avg)
    #print(sp)

    #stride length calculation
    disp_x = cumtrapz(vel_x, t, initial=0)
    disp_y = cumtrapz(vel_y, t, initial=0)
    disp_z = cumtrapz(vel_z, t, initial=0)
    displacement = list(zip(disp_x, disp_y, disp_z))
    dx = disp_x.astype(float)
    dy = disp_y.astype(float)
    sl = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(dx, dy)]
    sl_max = np.max(sl)
    print("sl_max=", sl_max)
    # print(sl)
    t1 = float(12.64)
    # max_sl = max(sl)
    speed = sl_max / t1
    print("speed=", speed)
    tc = len(sl)
    ts=0
    time=[]
    # t = (etime - stime) // tc
    t = (etime - stime) // 250         # is it always 250  unit time is 250??? is that agreed??
    noofbars=t
    for s in range(0,tc):
        ts=ts+t
        time.append(ts)
    ntime=[]
    for i in range(1,tc):
        ts=abs(time[i]-time[i-1])
        ntime.append(ts)
    print("time is", time, len(time))
    print("sl is:", sl)
    finalarr.append({"time": 0, "stride0": 0, "stride1": 0, "speed": 0})
    prevstride=0
    k=0
    for i in range(1,noofbars+1):
        dist1=[]
        tim=[]
        l=0
        for j in time:
            if (j>=k+0) and (j<=k+249):
                tim.append(j)
                dist1.append(sl[l])
                l=l+1
        # dist = cumtrapz(dist1, tim, initial=0)
        dist= [s1 * nt for s1, nt in
                         zip(sl, range(1, len(time) + 1))]

        print("starts =================================================", k, "==========")
        print("time: ",tim)
        print("dist:", dist1)
        print("dist integerated :",dist)
        print("ends =================================================",k,"==========")
        finalarr.append({"time": k+250, "stride0": prevstride, "stride1": dist, "speed": 0})
        prevstride=dist
        k=k+251
    print(finalarr)
    # finalarr.append({"time": 0, "stride": 0, "speed": 0})
    # for i in range(tc):
    #      left = round(sl[i],3)
    #      right = round(sp[i],3)
    #      timef = time[i]
    #      finalarr.append({"time": timef, "stride": left, "speed": right})


    # finalarr.append({"time": 0, "stride0": 0 ,"stride1": 0 , "speed": 0})
    # for i in range(tc):
    #      left = round(sl[i],3)
    #      right = round(sp[i],3)
    #      timef = time[i]
    #      finalarr.append({"time": timef, "stride0": lastStride ,"stride1": left , "speed": right})
    #      lastStride = left

    return Response(finalarr)








@api_view(["GET","POST"])
def datafromvidwalks(request):
    ssnid = request.data["sid"]  #40500
    stime = request.data["start"]  #100
    etime = request.data["end"]    #300
    with connection.cursor() as cursor:
        cursor.execute("SELECT s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='L'",[stime, etime, ssnid])
        cnt = cursor.rowcount
        p=cursor.fetchall()
        print(p)

    df = pd.DataFrame(p)
    #print(df)
    # velcoity calculation
    acc_x = df.iloc[:, 0].values
    acc_y = df.iloc[:, 1].values
    acc_z = df.iloc[:, 2].values
    print(acc_x)

    for j in range(len(acc_x)):
         acc_x[j] = float(acc_x[j])
    for i in range(len(acc_y)):
         acc_y[i] = float(acc_y[i])
    for k in range(len(acc_z)):
         acc_z[k] = float(acc_z[k])

    g = 0.98
    acc_y = acc_y - g
    accleration = [acc_x, acc_y, acc_z]
    dt = 0.0175  # 1/43
    t = numpy.arange(0, len(acc_x) * dt, dt)
    vel_x = cumtrapz(acc_x, t, initial=0)
    vel_y = cumtrapz(acc_y, t, initial=0)
    vel_z = cumtrapz(acc_z, t, initial=0)
    # velocity = [vel_x, vel_y, vel_z]
    velocity = list(zip(vel_x, vel_y, vel_z))
    vel_xy = list(zip(vel_x, vel_y))
    print(vel_x)

    #speed calculation
    #vx = [vel_x]  # Assuming vel_x is a list of x-velocities
    #vy = [vel_y]  # Assuming vel_y is a list of y-velocities
    vx = vel_x.astype(float)
    vy = vel_y.astype(float)
    print(vx)
    sp = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(vx, vy)]
    sp_max = np.max(sp)
    sp_avg = np.mean(sp)
    print("speed=", sp_max)
    print("avg=", sp_avg)
    #print(sp)

    #stride length calculation
    disp_x = cumtrapz(vel_x, t, initial=0)
    disp_y = cumtrapz(vel_y, t, initial=0)
    disp_z = cumtrapz(vel_z, t, initial=0)
    displacement = list(zip(disp_x, disp_y, disp_z))
    #dx = [disp_x]  # Assuming vel_x is a list of x-velocities
    #dy = [disp_y]  # Assuming vel_y is a list of y-velocities
    dx = disp_x.astype(float)
    dy = disp_y.astype(float)
    sl = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(dx, dy)]
    sl_max = np.max(sl)
    print("sl_max=", sl_max)
    # print(sl)
    t1 = float(12.64)
    # max_sl = max(sl)
    speed = sl_max / t1
    print("speed=", speed)

    # graph stridelength vs time,  speed vs time
    return JsonResponse({'stridelength': sl, 'slmax': sl_max, 'speed': sp, 'speedmax': sp_max})









@api_view(["GET","POST"])
def finalmean(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left ='L'
    right ='R'
    lmean = []
    ltime =[]
    rtime =[]
    rmean = []
    finalarr =[]
    lcount =0
    rcount =0
    with connection.cursor() as cursor:
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s', [left, ssnid,stime,etime]);
        slval = cursor.fetchall()

    for p in slval:
        ptot = (p[0] + p[1] + p[2] + p[3] + p[4])
        mean = ptot / 5
        lmean.append(mean)
        mapped_value = map_range(p[5], stime, etime, 0, 3000)
        mapped_value = round(mapped_value, 0)
        ltime.append(mapped_value)
        lcount = lcount + 1
    print(lcount)

    with connection.cursor() as cursor:
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s', [right, ssnid,stime,etime]);
        rlval = cursor.fetchall()
        for q in rlval:
            qtot = (q[0] + q[1] + q[2] + q[3] + q[4])
            mean1 = qtot / 5
            rmean.append(mean1)
            mapped_value1 = map_range(q[5], stime, etime, 0, 3000)
            mapped_value1 = round(mapped_value1, 0)
            rtime.append(mapped_value1)
            rcount = rcount+1
        print(rcount)

    tc = min(lcount, rcount)
    if (lcount<rcount):
        print("Left Minimum")
        lmean = lmean[:len(rmean)]
        ltime = ltime[:len(rtime)]

    else:
        print("Right Minimum")
        rmean = rmean[:len(lmean)]
        rtime = rtime[:len(ltime)]


    for i in range(tc):
        fleft = lmean[i]
        fright = rmean[i]
        flefttime = ltime[i]
        frighttime = rtime[i]
        finalarr.append({"left": fleft, "lefttime": flefttime, "right": fright, "righttime": frighttime})

    return Response(finalarr)

############################################## FSR Metrics##################################################

@api_view(["GET","POST"])
def finalpkmntoeheel(request):
    # try:
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]


    print(stime,ssnid,etime)

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left ='L'
    right ='R'
    lpeak = []
    rpeak = []
    lmean = []
    rmean = []
    ltime =[]
    rtime =[]
    lefttoe=[]
    righttoe=[]
    rightheal=[]
    leftheal=[]
    finalarr =[]
    with connection.cursor() as cursor:
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid', [left, ssnid,stime,etime]);
        slval = cursor.fetchall()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Left Count>>>>>>>>>>>>>>>>>>>>")
        lrcount = cursor.rowcount
        print(lrcount)

        for p in slval:
            ptot = round(max(p[0], p[1], p[2], p[3], p[4]),3) # peak value
            if ptot >= 778:
                ptot = (0.1439 * ptot) - 109.31
            elif 778 > ptot > 18:
                ptot = (0.0035 * ptot) - 0.063
            elif ptot <= 18:
                ptot = 0

            ptot = ptot*1

            ptot1 = (p[0]+ p[1]+ p[2]+ p[3]+ p[4])
            ptot1 = round(ptot1/5,3)             # mean of all
            if ptot1 >= 778:
                ptot1 = (0.1439 * ptot1) - 109.31
            elif 778 > ptot1 > 18:
                ptot1 = (0.0035 * ptot1) - 0.063
            elif ptot1 <= 18:
                ptot1 = 0
            ptot1 = ptot1 * 1

            ptot2 = p[0]+p[1]+p[2]
            ptot2 = round(ptot2/3,2)          # toe
            if ptot2 >= 778:
                ptot2 = (0.1439 * ptot2) - 109.31
            elif 778 > ptot2 > 18:
                ptot2 = (0.0035 * ptot2) - 0.063
            elif ptot2 <= 18:
                ptot2 = 0
            ptot2 = ptot2 * 1
            ptot3 = p[3]+p[4]
            ptot3 = round(ptot3/2,2)        #heel
            if ptot3 >= 778:
                ptot3 = (0.1439 * ptot3) - 109.31
            elif 778 > ptot3 > 18:
                ptot3 = (0.0035 * ptot3) - 0.063
            elif ptot3 <= 18:
                ptot3 = 0

            ptot3 = ptot3 * 1
            lpeak.append(ptot)
            lmean.append(ptot1)
            lefttoe.append(ptot2)
            leftheal.append(ptot3)
            ltime.append(p[5])     #time


    with connection.cursor() as cursor:
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid', [right, ssnid,stime,etime]);
        rlval = cursor.fetchall()
        rrcount = cursor.rowcount
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Right Count>>>>>>>>>>>>>>>>>>>>")
        print(rrcount)
        fc = min(lrcount,rrcount)

        for q in rlval:
            qtot = round(max(q[0],q[1],q[2],q[3],q[4]),2) #peak
            if qtot >= 778:
                qtot = (0.1439 * qtot) - 109.31
            elif 778 > qtot > 18:
                qtot = (0.0035 * qtot) - 0.063
            elif qtot <= 18:
                qtot = 0
            qtot = qtot * 1

            qtot1 = (q[0] + q[1] + q[2] + q[3] + q[4]) #mean
            qtot1 = round(qtot1 / 5,2)
            if qtot1 >= 778:
                qtot1 = (0.1439 * qtot1) - 109.31
            elif 778 > qtot1 > 18:
                qtot1 = (0.0035 * qtot1) - 0.063
            elif qtot1 <= 18:
                qtot1 = 0
            qtot1 = qtot1 * 1
            qtot2 = q[0] + q[1] + q[2]
            qtot2 = round(qtot2 / 3,2)                    #toe
            if qtot2 >= 778:
                qtot2 = (0.1439 * qtot2) - 109.31
            elif 778 > qtot2 > 18:
                qtot2 = (0.0035 * qtot2) - 0.063
            elif qtot2 <= 18:
                qtot2 = 0
            qtot2 = qtot2 * 1

            qtot3 = q[3] + q[4]
            qtot3 = round(qtot3 / 2,2)                 #heel
            if qtot3 >= 778:
                qtot3 = (0.1439 * qtot3) - 109.31
            elif 778 > qtot3 > 18:
                qtot3 = (0.0035 * qtot3) - 0.063
            elif qtot3 <= 18:
                qtot3 = 0
            qtot3 = qtot3 * 1
            rpeak.append(qtot)
            rmean.append(qtot1)
            righttoe.append(qtot2)
            rightheal.append(qtot3)
            rtime.append(q[5])     #time

        print(">>>>>>>>>>>>>>>count")
        print(fc)
        caltime = 3000/fc
        caltime = round(caltime)
        print("caltime",caltime)
        print("len of ltime and lmean are : ",len(ltime),len(lmean))

        print("ltime: ........", ltime, "lmean:...",lmean)
        print("len of rtime and rmean are : ", len(rtime), len(rmean))

        print("rtime: ........", rtime,"rmean.........",rmean)
        finalarr=[]
        pc = 0
        slm = slp =  slt = slh = 0
        nv=1
        fleftarr = []
        for i, lm, lp, lt, lh in zip(ltime, lmean, lpeak, lefttoe, leftheal):
            v = (i - ltime[0])
            if ((200 * pc) <= v < (200 * (pc + 1))):
                # print("values are  within range",v,lm)
                slm = slm + lm
                slp = slp + lp
                slt = slt + lt
                slh = slh + lh

                nv = nv + 1
            else:
                # print("pc is ",pc)
                # print("values are at border", pc, "is now moved to ",pc+1, v, lm,"avg mean: ",round(float(slm/nv)),"peak :",round(float(slp/nv)),"toe avg is:",round(float(slt/nv)),"Heel avg is",round(float(slh/nv)))
                fleftarr.append(
                    {"leftpeak": round(float(slp / nv)), "leftmean": round(float(slm / nv)),
                     "leftheal": round(float(slh / nv)), "lefttoe": round(float(slt / nv)), "time": (pc * 200)})
                print("fleftarr...........", fleftarr,"pc is ...",pc)
                pc = pc + 1
                slm = slp  = slt = slh = 0
                nv=1
        # print("values are at border", pc, "is now moved to ", pc + 1, v, lm, "avg mean: ", round(float(slm / nv)),
        #       "peak :", round(float(slp / nv)), "toe avg is:", round(float(slt / nv)), "Heel avg is",
        #       round(float(slh / nv)))

        fleftarr.append(
            {"leftpeak": round(float(slp / nv)), "leftmean": round(float(slm / nv)),
             "leftheal": round(float(slh / nv)), "lefttoe": round(float(slt / nv)), "time": (pc * 200)})
        # right values........................................................
        # print("FINAL     leftarr final ................",fleftarr)
        pc = 0
        srm = srp  = srt = srh = 0
        nv=1
        frightarr = []

        for i, rm, rp, rt, rh in zip(rtime, rmean, rpeak, righttoe, rightheal):
            v = (i - rtime[0])
            if ((200 * pc) <= v < (200 * (pc + 1))):
                print("values are  within range", v)
                srm = srm + rm
                srp = srp + rp
                srt = srt + rt
                srh = srh + rh

                nv = nv + 1
            else:
                frightarr.append({"rightpeak": round(float(srp / nv)),"rightmean": round(float(srm / nv)),"rightheal": round(float(srh / nv)),
                                  "righttoe": round(float(srt / nv)),"time": (pc * 200)})
                print("frightarr...........", frightarr,"pc is ............. ",pc)
                pc = pc + 1
                srm = srp = srt = srh = 0
                nv=1
        frightarr.append({"rightpeak": round(float(srp / nv)), "rightmean": round(float(srm / nv)),
                          "rightheal": round(float(srh / nv)),
                          "righttoe": round(float(srt / nv)), "time": (pc * 200)})

    print("finally here....left len:",len(fleftarr), " right len:",len(frightarr))
    mval= min(len(fleftarr), len(frightarr))
    finalarr=[]
    print(mval,finalarr)
    print("left", fleftarr[0], "   right:", frightarr[0])
    print("left", fleftarr[1], "   right:", frightarr[1])
    print("left", fleftarr[2], "   right:", frightarr[2])
    for  i in range(0, mval):
        print("left",fleftarr[i],"   right:",frightarr[i])
        finalarr.append({"leftpeak": fleftarr[i]["leftpeak"], "rightpeak": frightarr[i]["rightpeak"],
                                 "leftmean": fleftarr[i]["leftmean"], "rightmean": frightarr[i]["rightmean"],
                                 "leftheal": fleftarr[i]["leftheal"], "rightheal": frightarr[i]["rightheal"],
                                 "lefttoe": fleftarr[i]["lefttoe"], "righttoe": frightarr[i]["righttoe"],
                                 "time": (i * 200)})
        print(finalarr)
    return Response(finalarr)

######################################################################################################################
# #final mean  peak toe heel

@api_view(["GET","POST"])
def finalpkmntoeheelmod(request):
  # try:
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]
    nos = request.data["totalsensors"]


    print(stime,ssnid,etime)

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left ='L'
    right ='R'
    lpeak = []
    rpeak = []
    lmean = []
    rmean = []
    ltime =[]
    rtime =[]
    lefttoe=[]
    righttoe=[]
    rightheal=[]
    leftheal=[]
    finalarr =[]

    if (nos == 11):
            ###################################### for 5 fsr's  data  ############## LEFT INSOLE
            with connection.cursor() as cursor:
                cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid', [left, ssnid,stime,etime]);
                slval = cursor.fetchall()
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Left Count>>>>>>>>>>>>>>>>>>>>")
                lrcount = cursor.rowcount
                print(lrcount)

                for p in slval:
                    ptot = round(max(p[0], p[1], p[2], p[3], p[4]),3) # peak value
                    if ptot >= 778:
                        ptot = (0.1439 * ptot) - 109.31
                    elif 778 > ptot > 18:
                        ptot = (0.0035 * ptot) - 0.063
                    elif ptot <= 18:
                        ptot = 0

                    ptot = ptot*1

                    ptot1 = (p[0]+ p[1]+ p[2]+ p[3]+ p[4])
                    ptot1 = round(ptot1/5,3)             # mean of all
                    if ptot1 >= 778:
                        ptot1 = (0.1439 * ptot1) - 109.31
                    elif 778 > ptot1 > 18:
                        ptot1 = (0.0035 * ptot1) - 0.063
                    elif ptot1 <= 18:
                        ptot1 = 0
                    ptot1 = ptot1 * 1

                    ptot2 = p[0]+p[1]+p[2]
                    ptot2 = round(ptot2/3,2)          # toe
                    if ptot2 >= 778:
                        ptot2 = (0.1439 * ptot2) - 109.31
                    elif 778 > ptot2 > 18:
                        ptot2 = (0.0035 * ptot2) - 0.063
                    elif ptot2 <= 18:
                        ptot2 = 0
                    ptot2 = ptot2 * 1
                    ptot3 = p[3]+p[4]
                    ptot3 = round(ptot3/2,2)        #heel
                    if ptot3 >= 778:
                        ptot3 = (0.1439 * ptot3) - 109.31
                    elif 778 > ptot3 > 18:
                        ptot3 = (0.0035 * ptot3) - 0.063
                    elif ptot3 <= 18:
                        ptot3 = 0

                    ptot3 = ptot3 * 1
                    lpeak.append(ptot)
                    lmean.append(ptot1)
                    lefttoe.append(ptot2)
                    leftheal.append(ptot3)
                    ltime.append(p[5])     #time

            ###################################### for 5 fsr's  data  ############## RIGHT INSOLE ################
            with connection.cursor() as cursor:
                cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid', [right, ssnid,stime,etime]);
                rlval = cursor.fetchall()
                rrcount = cursor.rowcount
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Right Count>>>>>>>>>>>>>>>>>>>>")
                print(rrcount)
                fc = min(lrcount,rrcount)

                for q in rlval:
                    qtot = round(max(q[0],q[1],q[2],q[3],q[4]),2) #peak
                    if qtot >= 778:
                        qtot = (0.1439 * qtot) - 109.31
                    elif 778 > qtot > 18:
                        qtot = (0.0035 * qtot) - 0.063
                    elif qtot <= 18:
                        qtot = 0
                    qtot = qtot * 1

                    qtot1 = (q[0] + q[1] + q[2] + q[3] + q[4]) #mean
                    qtot1 = round(qtot1 / 5,2)
                    if qtot1 >= 778:
                        qtot1 = (0.1439 * qtot1) - 109.31
                    elif 778 > qtot1 > 18:
                        qtot1 = (0.0035 * qtot1) - 0.063
                    elif qtot1 <= 18:
                        qtot1 = 0
                    qtot1 = qtot1 * 1
                    qtot2 = q[0] + q[1] + q[2]
                    qtot2 = round(qtot2 / 3,2)                    #toe
                    if qtot2 >= 778:
                        qtot2 = (0.1439 * qtot2) - 109.31
                    elif 778 > qtot2 > 18:
                        qtot2 = (0.0035 * qtot2) - 0.063
                    elif qtot2 <= 18:
                        qtot2 = 0
                    qtot2 = qtot2 * 1

                    qtot3 = q[3] + q[4]
                    qtot3 = round(qtot3 / 2,2)                 #heel
                    if qtot3 >= 778:
                        qtot3 = (0.1439 * qtot3) - 109.31
                    elif 778 > qtot3 > 18:
                        qtot3 = (0.0035 * qtot3) - 0.063
                    elif qtot3 <= 18:
                        qtot3 = 0
                    qtot3 = qtot3 * 1
                    rpeak.append(qtot)
                    rmean.append(qtot1)
                    righttoe.append(qtot2)
                    rightheal.append(qtot3)
                    rtime.append(q[5])     #time
    else :
        ###################################### for 10 fsr's  data  ############## LEFT INSOLE
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid',
                [left, ssnid, stime, etime])
            slval = cursor.fetchall()
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Left Count>>>>>>>>>>>>>>>>>>>>")
            lrcount = cursor.rowcount
            print(lrcount)

            for p in slval:
                ptot = round(max(p[0], p[1], p[2], p[3], p[4], p[5], p[6],p[7],p[8],p[9]), 3)  # peak value
                if ptot >= 778:
                    ptot = (0.1439 * ptot) - 109.31
                elif 778 > ptot > 18:
                    ptot = (0.0035 * ptot) - 0.063
                elif ptot <= 18:
                    ptot = 0

                ptot = ptot * 1

                ptot1 = (p[0]+ p[1]+ p[2] + p[3] + p[4] + p[5] + p[6] + p[7] + p[8] + p[9])
                ptot1 = round(ptot1 / 10, 3)  # mean of all
                if ptot1 >= 778:
                    ptot1 = (0.1439 * ptot1) - 109.31
                elif 778 > ptot1 > 18:
                    ptot1 = (0.0035 * ptot1) - 0.063
                elif ptot1 <= 18:
                    ptot1 = 0
                ptot1 = ptot1 * 1

                #s3,s4,s5,s6 for toe on both leg and  s8,s9,s10 for heel on both legs
                ptot2 = (p[2] + p[3] + p[4] + p[5])
                ptot2 = round((ptot2 / 4), 2)  # toe
                if ptot2 >= 778:
                    ptot2 = (0.1439 * ptot2) - 109.31
                elif 778 > ptot2 > 18:
                    ptot2 = (0.0035 * ptot2) - 0.063
                elif ptot2 <= 18:
                    ptot2 = 0
                ptot2 = ptot2 * 1

                ptot3 = (p[7] + p[8] + p[9])
                ptot3 = round((ptot3 / 3), 2)  # heel
                if ptot3 >= 778:
                    ptot3 = (0.1439 * ptot3) - 109.31
                elif 778 > ptot3 > 18:
                    ptot3 = (0.0035 * ptot3) - 0.063
                elif ptot3 <= 18:
                    ptot3 = 0

                ptot3 = ptot3 * 1
                lpeak.append(ptot)
                lmean.append(ptot1)
                lefttoe.append(ptot2)
                leftheal.append(ptot3)
                ltime.append(p[5])  # time

        ###################################### for 10 fsr's  data  ############## RIGHT INSOLE ################
        with connection.cursor() as cursor:
            cursor.execute("select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid",
                [right, ssnid, stime, etime])
            rlval = cursor.fetchall()
            rrcount = cursor.rowcount
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Right Count>>>>>>>>>>>>>>>>>>>>")
            print(rrcount)
            fc = min(lrcount, rrcount)

            for q in rlval:
                qtot = round(max(p[0], p[1], p[2], p[3], p[4], p[5], p[6],p[7],p[8],p[9]), 3)  # peak
                if qtot >= 778:
                    qtot = (0.1439 * qtot) - 109.31
                elif 778 > qtot > 18:
                    qtot = (0.0035 * qtot) - 0.063
                elif qtot <= 18:
                    qtot = 0
                qtot = qtot * 1

                qtot1 = (p[0]+ p[1]+ p[2] + p[3] + p[4] + p[5] + p[6] + p[7] + p[8] + p[9])  # mean
                qtot1 = round((qtot1 / 5), 2)
                if qtot1 >= 778:
                    qtot1 = (0.1439 * qtot1) - 109.31
                elif 778 > qtot1 > 18:
                    qtot1 = (0.0035 * qtot1) - 0.063
                elif qtot1 <= 18:
                    qtot1 = 0
                qtot1 = qtot1 * 1

                # s3,s4,s5,s6 for toe on both leg and  s8,s9,s10 for heel on both legs
                qtot2 = (q[2] + q[3] + q[4] + q[5])
                qtot2 = round((qtot2 / 4), 2)  # toe
                if qtot2 >= 778:
                    qtot2 = (0.1439 * qtot2) - 109.31
                elif 778 > qtot2 > 18:
                    qtot2 = (0.0035 * qtot2) - 0.063
                elif qtot2 <= 18:
                    qtot2 = 0
                qtot2 = qtot2 * 1

                qtot3 = (q[7] + q[8] + q[9])
                qtot3 = round((qtot3 / 3), 2)  # heel
                if qtot3 >= 778:
                    qtot3 = (0.1439 * qtot3) - 109.31
                elif 778 > qtot3 > 18:
                    qtot3 = (0.0035 * qtot3) - 0.063
                elif qtot3 <= 18:
                    qtot3 = 0
                qtot3 = qtot3 * 1
                rpeak.append(qtot)
                rmean.append(qtot1)
                righttoe.append(qtot2)
                rightheal.append(qtot3)
                rtime.append(q[5])  # time


        print(">>>>>>>>>>>>>>>count")
        print(fc)
        caltime = 3000/fc
        caltime = round(caltime)
        print("caltime",caltime)
        print("len of ltime and lmean are : ",len(ltime),len(lmean))

        print("ltime: ........", ltime, "lmean:...",lmean)
        print("len of rtime and rmean are : ", len(rtime), len(rmean))

        print("rtime: ........", rtime,"rmean.........",rmean)
        finalarr=[]
        pc = 0
        slm = slp = nv = slt = slh = 0
        fleftarr = []
        for i, lm, lp, lt, lh in zip(ltime, lmean, lpeak, lefttoe, leftheal):
            v = (i - ltime[0])
            if ((200 * pc) <= v < (200 * (pc + 1))):
                # print("values are  within range",v,lm)
                slm = slm + lm
                slp = slp + lp
                slt = slt + lt
                slh = slh + lh

                nv = nv + 1
            else:
                # print("pc is ",pc)
                # print("values are at border", pc, "is now moved to ",pc+1, v, lm,"avg mean: ",round(float(slm/nv)),"peak :",round(float(slp/nv)),"toe avg is:",round(float(slt/nv)),"Heel avg is",round(float(slh/nv)))
                fleftarr.append(
                    {"leftpeak": round(float(slp / nv)), "leftmean": round(float(slm / nv)),
                     "leftheal": round(float(slh / nv)), "lefttoe": round(float(slt / nv)), "time": (pc * 200)})
                print("fleftarr...........", fleftarr)
                pc = pc + 1
                slm = slp = nv = slt = slh = 0
        # print("values are at border", pc, "is now moved to ", pc + 1, v, lm, "avg mean: ", round(float(slm / nv)),
        #       "peak :", round(float(slp / nv)), "toe avg is:", round(float(slt / nv)), "Heel avg is",
        #       round(float(slh / nv)))

        fleftarr.append(
            {"leftpeak": round(float(slp / nv)), "leftmean": round(float(slm / nv)),
             "leftheal": round(float(slh / nv)), "lefttoe": round(float(slt / nv)), "time": (pc * 200)})

        # right values........................................................
        # print("FINAL     leftarr final ................",fleftarr)
        pc = 0
        srm = srp = nv = srt = srh = 0
        # finalarr.append(
        #     {"leftpeak": 0, "rightpeak": 0, "leftmean": 0, "rightmean": 0, "leftheal": 0, "rightheal": 0, "lefttoe": 0,
        #      "righttoe": 0, "time": 0})
        for i, rm, rp, rt, rh in zip(rtime, rmean, rpeak, righttoe, rightheal):
            v = (i - rtime[0])
            if ((200 * pc) <= v < (200 * (pc + 1))):
                # print("values are  within range", v, rm)
                srm = srm + rm
                srp = srp + rp
                srt = srt + rt
                srh = srh + rh

                nv = nv + 1
            else:
                # print("pc is ", pc)
                # print("values are at border", pc, "is now moved to ", pc + 1, v, rm,srm, "avg mean: ",
                #       round(float(srm / nv)), "peak :", round(float(srp / nv)), "toe avg is:", round(float(srt / nv)),
                #       "Heel avg is", round(float(srh / nv)))
                finalarr.append({"leftpeak": fleftarr[(pc - 1)]["leftpeak"], "rightpeak": round(float(srp / nv)),
                                 "leftmean": fleftarr[(pc - 1)]["leftmean"], "rightmean": round(float(srm / nv)),
                                 "leftheal": fleftarr[(pc - 1)]["leftheal"], "rightheal": round(float(srh / nv)),
                                 "lefttoe": fleftarr[(pc - 1)]["lefttoe"], "righttoe": round(float(srt / nv)),
                                 "time": (pc * 200)})
                print("finalarr...........", finalarr)
                pc = pc + 1
                srm = srp = nv = srt = srh = 0
        # print("values after border 3000", pc, "is now moved to ", pc + 1, v, rm, srm, "avg mean: ",
        #       round(float(srm / nv)), "peak :", round(float(srp / nv)), "toe avg is:", round(float(srt / nv)),
        #       "Heel avg is", round(float(srh / nv)))
        finalarr.append({"leftpeak": fleftarr[pc]["leftpeak"], "rightpeak": round(float(srp / nv)),
                         "leftmean": fleftarr[pc]["leftmean"], "rightmean": round(float(srm / nv)),
                         "leftheal": fleftarr[pc]["leftheal"], "rightheal": round(float(srh / nv)),
                         "lefttoe": fleftarr[pc]["lefttoe"], "righttoe": round(float(srt / nv)),
                         "time": (pc * 200)})

        print(finalarr)
    return Response(finalarr)

#######################################################################################################################

@api_view(["GET","POST"])
def finalpkmntoeheelmodified(request):
  # try:
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]
    nos = request.data["totalsensors"]


    print(stime,ssnid,etime)

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left ='L'
    right ='R'
    lpeak = []
    rpeak = []
    lmean = []
    rmean = []
    ltime =[]
    rtime =[]
    lefttoe=[]
    righttoe=[]
    rightheal=[]
    leftheal=[]
    finalarr =[]

    if (nos == 11):
            print("11 sensor data....  left insole mnpktoeheel processing..........")
            ###################################### for 11 sensor data ############## LEFT INSOLE
            with connection.cursor() as cursor:
                cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid', [left, ssnid,stime,etime]);
                slval = cursor.fetchall()
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Left Count>>>>>>>>>>>>>>>>>>>>")
                lrcount = cursor.rowcount
                print(lrcount)

                for p in slval:
                    ptot = round(max(p[0], p[1], p[2], p[3], p[4]),3) # peak value
                    if ptot >= 778:
                        ptot = (0.1439 * ptot) - 109.31
                    elif 778 > ptot > 18:
                        ptot = (0.0035 * ptot) - 0.063
                    elif ptot <= 18:
                        ptot = 0

                    ptot1 = (p[0]+ p[1]+ p[2]+ p[3]+ p[4])
                    ptot1 = round(ptot1/5,3)             # mean of all
                    if ptot1 >= 778:
                        ptot1 = (0.1439 * ptot1) - 109.31
                    elif 778 > ptot1 > 18:
                        ptot1 = (0.0035 * ptot1) - 0.063
                    elif ptot1 <= 18:
                        ptot1 = 0
                  
                    ptot2 = p[0]+p[1]+p[2]
                    ptot2 = round(ptot2/3,2)          # toe
                    if ptot2 >= 778:
                        ptot2 = (0.1439 * ptot2) - 109.31
                    elif 778 > ptot2 > 18:
                        ptot2 = (0.0035 * ptot2) - 0.063
                    elif ptot2 <= 18:
                        ptot2 = 0

                    ptot3 = p[3]+p[4]
                    ptot3 = round(ptot3/2,2)        #heel
                    if ptot3 >= 778:
                        ptot3 = (0.1439 * ptot3) - 109.31
                    elif 778 > ptot3 > 18:
                        ptot3 = (0.0035 * ptot3) - 0.063
                    elif ptot3 <= 18:
                        ptot3 = 0
                    ptot3 = ptot3 * 1

                    lpeak.append(ptot)
                    lmean.append(ptot1)
                    lefttoe.append(ptot2)
                    leftheal.append(ptot3)
                    ltime.append(p[5])     #time
            print("left insole .... pk, mn, toe and heel:", ltime, leftmean, leftpeak, lefttoe,leftheal)
            print("right insole 11 sensor data processing pmntoeheel................................")
            ###################################### for 11 sensor data  ############## RIGHT INSOLE ################
            with connection.cursor() as cursor:
                cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid', [right, ssnid,stime,etime]);
                rlval = cursor.fetchall()
                rrcount = cursor.rowcount
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Right Count>>>>>>>>>>>>>>>>>>>>")
                print(rrcount)
                fc = min(lrcount,rrcount)

                for q in rlval:
                    qtot = round(max(q[0],q[1],q[2],q[3],q[4]),2) #peak
                    if qtot >= 778:
                        qtot = (0.1439 * qtot) - 109.31
                    elif 778 > qtot > 18:
                        qtot = (0.0035 * qtot) - 0.063
                    elif qtot <= 18:
                        qtot = 0

                    qtot1 = (q[0] + q[1] + q[2] + q[3] + q[4]) #mean
                    qtot1 = round(qtot1 / 5,2)
                    if qtot1 >= 778:
                        qtot1 = (0.1439 * qtot1) - 109.31
                    elif 778 > qtot1 > 18:
                        qtot1 = (0.0035 * qtot1) - 0.063
                    elif qtot1 <= 18:
                        qtot1 = 0

                    qtot2 = q[0] + q[1] + q[2]
                    qtot2 = round(qtot2 / 3,2)                    #toe
                    if qtot2 >= 778:
                        qtot2 = (0.1439 * qtot2) - 109.31
                    elif 778 > qtot2 > 18:
                        qtot2 = (0.0035 * qtot2) - 0.063
                    elif qtot2 <= 18:
                        qtot2 = 0

                    qtot3 = q[3] + q[4]
                    qtot3 = round(qtot3 / 2,2)                 #heel
                    if qtot3 >= 778:
                        qtot3 = (0.1439 * qtot3) - 109.31
                    elif 778 > qtot3 > 18:
                        qtot3 = (0.0035 * qtot3) - 0.063
                    elif qtot3 <= 18:
                        qtot3 = 0

                    rpeak.append(qtot)
                    rmean.append(qtot1)
                    righttoe.append(qtot2)
                    rightheal.append(qtot3)
                    rtime.append(q[5])     #time
    else :
        ###################################### for 16 sensor data ############## LEFT INSOLE
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid',
                [left, ssnid, stime, etime])
            slval = cursor.fetchall()
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Left Count>>>>>>>>>>>>>>>>>>>>")
            lrcount = cursor.rowcount
            print(lrcount)

            for p in slval:
                ptot = round(max(p[0], p[1], p[2], p[3], p[4], p[5], p[6],p[7],p[8],p[9]), 3)  # peak value
                if ptot >= 778:
                    ptot = (0.1439 * ptot) - 109.31
                elif 778 > ptot > 18:
                    ptot = (0.0035 * ptot) - 0.063
                elif ptot <= 18:
                    ptot = 0

                ptot1 = (p[0]+ p[1]+ p[2] + p[3] + p[4] + p[5] + p[6] + p[7] + p[8] + p[9])
                ptot1 = round(ptot1 / 10, 3)  # mean of all
                if ptot1 >= 778:
                    ptot1 = (0.1439 * ptot1) - 109.31
                elif 778 > ptot1 > 18:
                    ptot1 = (0.0035 * ptot1) - 0.063
                elif ptot1 <= 18:
                    ptot1 = 0

                #s3,s4,s5,s6 for toe on both leg and  s8,s9,s10 for heel on both legs
                ptot2 = (p[2] + p[3] + p[4] + p[5])
                ptot2 = round((ptot2 / 4), 2)  # toe
                if ptot2 >= 778:
                    ptot2 = (0.1439 * ptot2) - 109.31
                elif 778 > ptot2 > 18:
                    ptot2 = (0.0035 * ptot2) - 0.063
                elif ptot2 <= 18:
                    ptot2 = 0

                ptot3 = (p[7] + p[8] + p[9])
                ptot3 = round((ptot3 / 3), 2)  # heel
                if ptot3 >= 778:
                    ptot3 = (0.1439 * ptot3) - 109.31
                elif 778 > ptot3 > 18:
                    ptot3 = (0.0035 * ptot3) - 0.063
                elif ptot3 <= 18:
                    ptot3 = 0

                lpeak.append(ptot)
                lmean.append(ptot1)
                lefttoe.append(ptot2)
                leftheal.append(ptot3)
                ltime.append(p[5])  # time

        ###################################### for 16 sensor data   ############## RIGHT INSOLE ################
        with connection.cursor() as cursor:
            cursor.execute("select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid",
                [right, ssnid, stime, etime])
            rlval = cursor.fetchall()
            rrcount = cursor.rowcount
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Right Count>>>>>>>>>>>>>>>>>>>>")
            print(rrcount)
            fc = min(lrcount, rrcount)

            for q in rlval:
                qtot = round(max(p[0], p[1], p[2], p[3], p[4], p[5], p[6],p[7],p[8],p[9]), 3)  # peak
                if qtot >= 778:
                    qtot = (0.1439 * qtot) - 109.31
                elif 778 > qtot > 18:
                    qtot = (0.0035 * qtot) - 0.063
                elif qtot <= 18:
                    qtot = 0

                qtot1 = (p[0]+ p[1]+ p[2] + p[3] + p[4] + p[5] + p[6] + p[7] + p[8] + p[9])  # mean
                qtot1 = round((qtot1 / 10), 2)
                if qtot1 >= 778:
                    qtot1 = (0.1439 * qtot1) - 109.31
                elif 778 > qtot1 > 18:
                    qtot1 = (0.0035 * qtot1) - 0.063
                elif qtot1 <= 18:
                    qtot1 = 0
            
                # s3,s4,s5,s6 for toe on both leg and  s8,s9,s10 for heel on both legs
                qtot2 = (q[2] + q[3] + q[4] + q[5])
                qtot2 = round((qtot2 / 4), 2)  # toe
                if qtot2 >= 778:
                    qtot2 = (0.1439 * qtot2) - 109.31
                elif 778 > qtot2 > 18:
                    qtot2 = (0.0035 * qtot2) - 0.063
                elif qtot2 <= 18:
                    qtot2 = 0
            
                qtot3 = (q[7] + q[8] + q[9])
                qtot3 = round((qtot3 / 3), 2)  # heel
                if qtot3 >= 778:
                    qtot3 = (0.1439 * qtot3) - 109.31
                elif 778 > qtot3 > 18:
                    qtot3 = (0.0035 * qtot3) - 0.063
                elif qtot3 <= 18:
                    qtot3 = 0
            

                rpeak.append(qtot)
                rmean.append(qtot1)
                righttoe.append(qtot2)
                rightheal.append(qtot3)
                rtime.append(q[5])  # time

        print("right insole, right time",rtime," right mean",rmean,"  right peak",rpeak,"right toe" ,rtoe, " right heel" , rheel)
        print(">>>>>>>>>>>>>>>count")
        print(fc)
        caltime = 3000/fc
        caltime = round(caltime)
        print("caltime",caltime)
        print("len of ltime and lmean are : ",len(ltime),len(lmean))

        print("ltime: ........", ltime, "lmean:...",lmean)
        print("len of rtime and rmean are : ", len(rtime), len(rmean))

        print("rtime: ........", rtime,"rmean.........",rmean)
        finalarr=[]
        pc = 0
        slm = slp = nv = slt = slh = 0
        fleftarr = []
        for i, lm, lp, lt, lh in zip(ltime, lmean, lpeak, lefttoe, leftheal):
            v = (i - ltime[0])
            if ((200 * pc) <= v < (200 * (pc + 1))):
                # print("values are  within range",v,lm)
                slm = slm + lm
                slp = slp + lp
                slt = slt + lt
                slh = slh + lh

                nv = nv + 1
            else:
                # print("pc is ",pc)
                # print("values are at border", pc, "is now moved to ",pc+1, v, lm,"avg mean: ",round(float(slm/nv)),"peak :",round(float(slp/nv)),"toe avg is:",round(float(slt/nv)),"Heel avg is",round(float(slh/nv)))
                fleftarr.append(
                    {"leftpeak": round(float(slp / nv)), "leftmean": round(float(slm / nv)),
                     "leftheal": round(float(slh / nv)), "lefttoe": round(float(slt / nv)), "time": (pc * 200)})
                print("fleftarr...........", fleftarr)
                pc = pc + 1
                slm = slp = nv = slt = slh = 0
        # print("values are at border", pc, "is now moved to ", pc + 1, v, lm, "avg mean: ", round(float(slm / nv)),
        #       "peak :", round(float(slp / nv)), "toe avg is:", round(float(slt / nv)), "Heel avg is",
        #       round(float(slh / nv)))

        fleftarr.append(
            {"leftpeak": round(float(slp / nv)), "leftmean": round(float(slm / nv)),
             "leftheal": round(float(slh / nv)), "lefttoe": round(float(slt / nv)), "time": (pc * 200)})

        # right values........................................................
        # print("FINAL     leftarr final ................",fleftarr)
        pc = 0
        srm = srp = nv = srt = srh = 0
        # finalarr.append(
        #     {"leftpeak": 0, "rightpeak": 0, "leftmean": 0, "rightmean": 0, "leftheal": 0, "rightheal": 0, "lefttoe": 0,
        #      "righttoe": 0, "time": 0})
        for i, rm, rp, rt, rh in zip(rtime, rmean, rpeak, righttoe, rightheal):
            v = (i - rtime[0])
            if ((200 * pc) <= v < (200 * (pc + 1))):
                # print("values are  within range", v, rm)
                srm = srm + rm
                srp = srp + rp
                srt = srt + rt
                srh = srh + rh

                nv = nv + 1
            else:
                # print("pc is ", pc)
                # print("values are at border", pc, "is now moved to ", pc + 1, v, rm,srm, "avg mean: ",
                #       round(float(srm / nv)), "peak :", round(float(srp / nv)), "toe avg is:", round(float(srt / nv)),
                #       "Heel avg is", round(float(srh / nv)))
                finalarr.append({"leftpeak": fleftarr[(pc - 1)]["leftpeak"], "rightpeak": round(float(srp / nv)),
                                 "leftmean": fleftarr[(pc - 1)]["leftmean"], "rightmean": round(float(srm / nv)),
                                 "leftheal": fleftarr[(pc - 1)]["leftheal"], "rightheal": round(float(srh / nv)),
                                 "lefttoe": fleftarr[(pc - 1)]["lefttoe"], "righttoe": round(float(srt / nv)),
                                 "time": (pc * 200)})
                print("finalarr...........", finalarr)
                pc = pc + 1
                srm = srp = nv = srt = srh = 0
        # print("values after border 3000", pc, "is now moved to ", pc + 1, v, rm, srm, "avg mean: ",
        #       round(float(srm / nv)), "peak :", round(float(srp / nv)), "toe avg is:", round(float(srt / nv)),
        #       "Heel avg is", round(float(srh / nv)))
        finalarr.append({"leftpeak": fleftarr[pc]["leftpeak"], "rightpeak": round(float(srp / nv)),
                         "leftmean": fleftarr[pc]["leftmean"], "rightmean": round(float(srm / nv)),
                         "leftheal": fleftarr[pc]["leftheal"], "rightheal": round(float(srh / nv)),
                         "lefttoe": fleftarr[pc]["lefttoe"], "righttoe": round(float(srt / nv)),
                         "time": (pc * 200)})

        print(finalarr)
    return Response(finalarr)










################### strideno, stride distance,time,velocity for right and left  ONLINE GRAPHS##########################



@api_view(["GET","POST"])
def finalimumetrics(request):
    ssnid = request.data["ssnid"]
    lstime = request.data["leftstime"]
    letime = request.data["leftetime"]
    rstime = request.data["rightstime"]
    retime = request.data["rightetime"]

    # step1
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from scipy.signal import butter, filtfilt
    from numpy.linalg import norm
    import sys

    ta = []

    # step 2 - AHRS class
    class AHRS:
        def __init__(self, *args):
            self.SamplePeriod = 1 / 40
            self.Quaternion = [1, 0, 0, 0]
            self.Kp = 2
            self.Ki = 0
            self.KpInit = 200
            self.InitPeriod = 5
            self.q = [1, 0, 0, 0]
            self.IntError = [0, 0, 0]
            self.KpRamped = None
            for i in range(0, len(args), 2):
                if args[i] == 'SamplePeriod':
                    self.SamplePeriod = args[i + 1]
                elif args[i] == 'Quaternion':
                    self.Quaternion = args[i + 1]
                    self.q = self.quaternConj(self.Quaternion)
                elif args[i] == 'Kp':
                    self.Kp = args[i + 1]
                elif args[i] == 'Ki':
                    self.Ki = args[i + 1]
                elif args[i] == 'KpInit':
                    self.KpInit = args[i + 1]
                elif args[i] == 'InitPeriod':
                    self.InitPeriod = args[i + 1]
                else:
                    raise ValueError('Invalid argument')
            self.KpRamped = self.KpInit

        def Update(self, Gyroscope, Accelerometer, Magnetometer):
            raise NotImplementedError('This method is unimplemented')

        def UpdateIMU(self, Gyroscope, Accelerometer):
            if norm(Accelerometer) == 0:
                print('Accelerometer magnitude is zero. Algorithm update aborted.')
                return
            else:
                Accelerometer = Accelerometer / norm(Accelerometer)
            v = [2 * (self.q[1] * self.q[3] - self.q[0] * self.q[2]),
                 2 * (self.q[2] * self.q[3] + self.q[0] * self.q[1]),
                 self.q[0] ** 2 - self.q[1] ** 2 - self.q[2] ** 2 + self.q[3] ** 2]
            error = np.cross(v, Accelerometer)
            self.IntError = self.IntError + error
            Ref = Gyroscope - (self.Kp * error + self.Ki * self.IntError)
            pDot = 0.5 * self.quaternProd(self.q, [0, float(Ref[0]), float(Ref[1]), float(Ref[2])])
            self.q = self.q + pDot * self.SamplePeriod
            self.q = self.q / norm(self.q)
            self.Quaternion = self.quaternConj(self.q)

        def quaternProd(self, a, b):
            # Ensure a and b are lists or arrays
            a = np.array(a)
            b = np.array(b)

            ab = np.array([
                a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
                a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
                a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
                a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]
            ])
            return ab

        def quaternConj(self, q):
            qConj = [q[0], -q[1], -q[2], -q[3]]
            return qConj

    # step3

    def quaternProd(a, b):
        ab = [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
              a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
              a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
              a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]]
        # print(ab)
        return ab

    def quaternConj(q):
        qConj = [q[0], -q[1], -q[2], -q[3]]
        # print(qConj)
        return qConj

    def quaternRotate(v, q):
        row, col = v.shape
        v0XYZ = quaternProd(quaternProd(q, np.hstack((np.zeros((row, 1)), v))), quaternConj(q))
        v = np.array(v0XYZ)[:, 1:4]
        return v

    def extract_ranges(t, heel, toe, threshold=650):
        # Detect peaks using the specified method
        peaks = []
        for i in range(1, len(heel) - 1):  # 1 to last index
            if heel[i - 1] < heel[i] >= heel[i + 1] and heel[i] > threshold:
                peaks.append(i)
                # prev value less than present it is grator than or equal to next and grater than threshould
        # if not peaks:  # Check if the list is empty
        #     print("peak list is empty. Cannot extract ranges.")
        #     return []
        # Identify clusters of nearby peaks
        clustered_peaks = []
        current_cluster = [peaks[0]]
        for i in range(1, len(peaks)):
            if peaks[i] - peaks[i - 1] <= 5:
                current_cluster.append(peaks[i])
            else:
                # Calculate the median of the current cluster and store it
                clustered_peaks.append(int(np.median(current_cluster)))
                current_cluster = [peaks[i]]

        # Include the last cluster
        # clustered_peaks.append(int(np.median(current_cluster)))

        # Get corresponding time values for peaks
        peak_times = [t[i] for i in clustered_peaks]

        # Store first_intersection_time values in an array
        first_intersection_times = []
        samples_for_first_intersection = []
        indices_for_first_intersection = []

        # Plot the original signal and the identified peaks
        plt.plot(t, heel, label='Heel Pressure')
        plt.plot(t, toe, label='Toe Pressure')
        plt.plot(peak_times, [heel[i] for i in clustered_peaks], 'gx')

        # Plot segments between intersections
        for i in range(len(clustered_peaks)):
            if i < len(clustered_peaks) - 1:
                start_index = clustered_peaks[i]
                end_index = clustered_peaks[i + 1]

                # Find the first intersection point between 'heel' and 'toe' signals
                # intersections = np.where(np.diff(np.sign(heel[start_index:end_index] - toe[start_index:end_index])))[0]
                heel_array = np.array(heel[start_index:end_index])
                toe_array = np.array(toe[start_index:end_index])

                intersections = np.where(np.diff(np.sign(heel_array - toe_array)))[0]

                if len(intersections) > 0:
                    # Get the time value of the first intersection
                    first_intersection_time = t[start_index:end_index][intersections[0]]
                    first_intersection_times.append(first_intersection_time)

                    # Store corresponding samples and indices
                    sample_index = start_index + intersections[0]
                    samples_for_first_intersection.append(heel[sample_index])
                    indices_for_first_intersection.append(sample_index)

                    # Plot the segment between consecutive intersections
                    plt.axvline(first_intersection_time, color='red', linestyle='--')

        # Store start time, end time, and first intersection times in a single array
        time_array = [t[0]] + first_intersection_times + [t[-1]]
        ta = time_array
        # print(time_array)
        indices_for_first_intersection = [0] + indices_for_first_intersection + [len(heel) - 1]

        # Print the array of start_time, end_time, first_intersection_times, and corresponding samples and indices
        #     print("Stride Time:", time_array)
        #     print("Samples:", samples_for_first_intersection)
        #     print("Sample Indices:", indices_for_first_intersection)

        return indices_for_first_intersection
    #########################################################left data
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='L' order by sessiondataid",
            [lstime, letime, ssnid])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    print(p)
    aa = pd.DataFrame(p)

    s1 = aa.iloc[:, 0]
    s2 = aa.iloc[:, 1]
    s3 = aa.iloc[:, 2]
    toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]

    s4 = aa.iloc[:, 3]
    s5 = aa.iloc[:, 4]
    heel = [sum(x) / len(x) for x in zip(s4, s5)]
    t = aa[:, 1]
    t1 = aa[:, 1]

    Fs = 40
    # Extract ranges using the function
    ranges = extract_ranges(t, heel, toe)
    # rts= extract_ranges(t,heel,toe)
    # ranges,tim=rts
    # ranges = [int(x) for x in franges]
    tim_array = []
    for ty in range(0, len(ranges)):
        print(t[ranges[ty]], end=" ")
        tim_array.append(int(t[ranges[ty]]))
    # Initialize an empty list to store all position values values
    # print("times",tim_array)
    print("ranges", ranges)
    print("time values", tim_array)

    max_pos_values = []
    max_pos_time = []
    print("len of ranges", len(ranges))
    # Perform processing for each range
    for i in range(len(ranges) - 1):
        print("ï th value.........................................................", i)
        start_index = ranges[i]
        end_index = ranges[i + 1]

        accX = aa[start_index:end_index, 7] / 9.8
        accY = aa[start_index:end_index, 8] / 9.8
        accZ = aa[start_index:end_index, 9] / 9.8
        gyrX = aa[start_index:end_index, 10] * 57.29
        gyrY = aa[start_index:end_index, 11] * 57.29
        gyrZ = aa[start_index:end_index, 12] * 57.29
        t = aa[start_index:end_index, 1]
        t11 = t
        L1 = len(t)
        time = np.arange(L1)
        print("time is ..............", t)
        # step4

        acc_mag = np.sqrt(accX ** 2 + accY ** 2 + accZ ** 2)

        # Detect stationary periods
        sample_period = 1 / Fs
        filt_cutoff = 0.0001

        # High-pass filter accelerometer data
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'high')
        acc_magFilt = filtfilt(b, a, acc_mag)
        acc_magFilt = np.abs(acc_magFilt)

        # Low-pass filter accelerometer data
        filt_cutoff = 5
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'low')
        acc_magFilt = filtfilt(b, a, acc_magFilt)

        # Threshold detection
        stationary = acc_magFilt < (0.03)

        # step 5
        # Compute orientation
        quat = np.zeros((len(time), 4))
        AHRSalgorithm = AHRS('SamplePeriod', 1 / Fs, 'Kp', 1, 'KpInit', 1)

        # Initial convergence
        initPeriod = 2
        indexSel = np.arange(np.argmax(time > (time[0] + initPeriod)))
        for i in range(2000):
            AHRSalgorithm.UpdateIMU([0, 0, 0],
                                    [np.mean(accX[indexSel]), np.mean(accY[indexSel]), np.mean(accZ[indexSel])])

        # For all data
        for t in range(len(time)):
            if stationary[t]:
                AHRSalgorithm.Kp = 0.01
            else:
                AHRSalgorithm.Kp = 0.01
            AHRSalgorithm.UpdateIMU(np.deg2rad([gyrX[t], gyrY[t], gyrZ[t]]), [accX[t], accY[t], accZ[t]])
            quat[t, :] = AHRSalgorithm.Quaternion
            # print((quat[t,:]))

        # Compute translational accelerations
        # Rotate accelerations from sensor frame to Earth frame
        # Function to rotate vector v by quaternion q
        def quatern_conj(q):
            if q.ndim == 1:
                return np.array([q[0], -q[1], -q[2], -q[3]])
            elif q.ndim == 2:
                return np.array([q[:, 0], -q[:, 1], -q[:, 2], -q[:, 3]]).T
            else:
                raise ValueError("Invalid dimension for quaternion array")

        def quatern_rotate(v, q):
            q_conj = quatern_conj(q)
            v_quat = np.concatenate(([0], v))
            result_quat = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)
            return result_quat[1:]

        def quaternion_multiply(q1, q2):
            w1, x1, y1, z1 = q1
            w2, x2, y2, z2 = q2
            w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
            x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
            y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
            z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
            return np.array([w, x, y, z])

        # step6

        # compute transilational acceleration

        acc1 = np.column_stack((accX, accY, accZ))
        quat_conj = quatern_conj(quat)
        # print(quat_conj)

        acc2 = np.array([quatern_rotate(row, quat_conj[i, :]) for i, row in enumerate(acc1)])
        # print(acc2 )

        acc = acc2 * 9.8

        acc[:, 2] -= 9.8

        time = np.array(time)

        # step 7
        # Integrate acceleration to yield velocity
        vel = np.zeros(acc.shape)
        for t in range(1, vel.shape[0]):
            vel[t, :] = vel[t - 1, :] + acc[t, :] * sample_period
            if stationary[t] == 1:
                vel[t, :] = [0, 0, 0]  # apply ZUPT update when foot stationary

        # plt.figure()
        # plt.plot(vel)
        # plt.show()

        # Compute integral drift during non-stationary periods
        velDrift = np.zeros(vel.shape)
        stationaryStart = np.where(np.diff(stationary) == 1)[0]
        stationaryEnd = np.where(np.diff(stationary) == -1)[0]
        for i in range(len(stationaryEnd)):
            driftRate = vel[stationaryStart[i] - 1, :] / (stationaryStart[i] - stationaryEnd[i])
            enum = np.arange(1, stationaryStart[i] - stationaryEnd[i] + 1)
            drift = np.column_stack((enum * driftRate[0], enum * driftRate[1], enum * driftRate[2]))
            velDrift[stationaryEnd[i]:stationaryStart[i] - 1, :] = drift

        # Remove integral drift
        vel = vel - velDrift

        # Compute translational position

        # Integrate velocity to yield position
        pos = np.zeros(vel.shape)
        for t in range(1, pos.shape[0]):
            pos[t, :] = pos[t - 1, :] + vel[t, :] * sample_period

        # Plot translational position
        # y axis for ward, backward movement (new insole)
        # x axis for up/down
        # mahipal old data which uses x(forward/backward)

        # plt.figure(figsize=(9, 6))
        # plt.plot(time, pos[:, 0], 'r')
        # plt.plot(time, pos[:, 1], 'g')
        # plt.title('Position')
        # plt.xlabel('samples')
        # plt.ylabel('Position (m)')
        # plt.legend(['X', 'Y', 'Z'])
        # plt.show()
        posX = np.abs(pos[:, 1])
        # pos[:,0] means x axis(old insole(mahipal data)). pos[:,1] for new insole(yaxis is x here)
        # print(posX)
        print(np.max(posX))
        max_pos = np.max(posX)
        # print("t11 is ",t11, time)
        #
        # # Find the index of the maximum value in sl
        # max_index = np.argmax(posX1)
        #
        # # Get the corresponding time from tm
        # # max_time = t11[max_index]
        # max_time = t11[max_index]
        # # Get the maximum value in sl
        # max_pos = np.max(posX1)

        max_pos_values.append(max_pos)
        print("max_pos_values", max_pos_values)
        print("sum of distance:", np.sum(max_pos_values))
        # max_pos_time.append(max_time)
        # print(np.sum(max_pos_values))
        # print("last",posX1[len(posX1)- 1])

        # a = (max_pos + posX1[len(posX1)- 1])/2
        # print("a=",a)
        # print(np.mean(posX1[len(posX1)- 1]))
        max_pos_array = np.array(max_pos_values)
    print("finally sl............", max_pos_values)
    print("finally time ..............", tim_array)
    # # print("finally time............",max_pos_time)
    #
    #
    timestart = tim_array[1]
    sc = 1
    leftstride = []
    tsum = 0
    print(len(max_pos_values))
    for ts in range(2, (len(max_pos_values) - 1)):
        print(ts, tim_array[ts], max_pos_values[ts])
        tt = tim_array[ts] - timestart
        leftstride.append({"strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),
                           "velocity": (max_pos_values[ts] / float(tt * 0.001))})
        timestart = tim_array[ts]
        sc = sc + 1
        tsum = tsum + max_pos_values[ts]

    print("finally left stride :", leftstride)
    print("total distance :", tsum, "m/s2")

    #########################################################right data
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='R' order by sessiondataid",
            [rstime, retime, ssnid])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    print(p)
    aa = pd.DataFrame(p)

    s1 = aa.iloc[:, 0]
    s2 = aa.iloc[:, 1]
    s3 = aa.iloc[:, 2]
    toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]

    s4 = aa.iloc[:, 3]
    s5 = aa.iloc[:, 4]
    heel = [sum(x) / len(x) for x in zip(s4, s5)]
    t = aa[:, 1]
    t1 = aa[:, 1]

    Fs = 40
    # Extract ranges using the function
    ranges = extract_ranges(t, heel, toe)
    # rts= extract_ranges(t,heel,toe)
    # ranges,tim=rts
    # ranges = [int(x) for x in franges]
    tim_array = []
    for ty in range(0, len(ranges)):
        print(t[ranges[ty]], end=" ")
        tim_array.append(int(t[ranges[ty]]))
    # Initialize an empty list to store all position values values
    # print("times",tim_array)
    print("ranges", ranges)
    print("time values", tim_array)

    max_pos_values = []
    max_pos_time = []
    print("len of ranges", len(ranges))
    # Perform processing for each range
    for i in range(len(ranges) - 1):
        print("ï th value.........................................................", i)
        start_index = ranges[i]
        end_index = ranges[i + 1]

        accX = aa[start_index:end_index, 7] / 9.8
        accY = aa[start_index:end_index, 8] / 9.8
        accZ = aa[start_index:end_index, 9] / 9.8
        gyrX = aa[start_index:end_index, 10] * 57.29
        gyrY = aa[start_index:end_index, 11] * 57.29
        gyrZ = aa[start_index:end_index, 12] * 57.29
        t = aa[start_index:end_index, 1]
        t11 = t
        L1 = len(t)
        time = np.arange(L1)
        print("time is ..............", t)
        # step4

        acc_mag = np.sqrt(accX ** 2 + accY ** 2 + accZ ** 2)

        # Detect stationary periods
        sample_period = 1 / Fs
        filt_cutoff = 0.0001

        # High-pass filter accelerometer data
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'high')
        acc_magFilt = filtfilt(b, a, acc_mag)
        acc_magFilt = np.abs(acc_magFilt)

        # Low-pass filter accelerometer data
        filt_cutoff = 5
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'low')
        acc_magFilt = filtfilt(b, a, acc_magFilt)

        # Threshold detection
        stationary = acc_magFilt < (0.03)

        # step 5
        # Compute orientation
        quat = np.zeros((len(time), 4))
        AHRSalgorithm = AHRS('SamplePeriod', 1 / Fs, 'Kp', 1, 'KpInit', 1)

        # Initial convergence
        initPeriod = 2
        indexSel = np.arange(np.argmax(time > (time[0] + initPeriod)))
        for i in range(2000):
            AHRSalgorithm.UpdateIMU([0, 0, 0],
                                    [np.mean(accX[indexSel]), np.mean(accY[indexSel]), np.mean(accZ[indexSel])])

        # For all data
        for t in range(len(time)):
            if stationary[t]:
                AHRSalgorithm.Kp = 0.01
            else:
                AHRSalgorithm.Kp = 0.01
            AHRSalgorithm.UpdateIMU(np.deg2rad([gyrX[t], gyrY[t], gyrZ[t]]), [accX[t], accY[t], accZ[t]])
            quat[t, :] = AHRSalgorithm.Quaternion
            # print((quat[t,:]))

        # Compute translational accelerations
        # Rotate accelerations from sensor frame to Earth frame
        # Function to rotate vector v by quaternion q
        def quatern_conj(q):
            if q.ndim == 1:
                return np.array([q[0], -q[1], -q[2], -q[3]])
            elif q.ndim == 2:
                return np.array([q[:, 0], -q[:, 1], -q[:, 2], -q[:, 3]]).T
            else:
                raise ValueError("Invalid dimension for quaternion array")

        def quatern_rotate(v, q):
            q_conj = quatern_conj(q)
            v_quat = np.concatenate(([0], v))
            result_quat = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)
            return result_quat[1:]

        def quaternion_multiply(q1, q2):
            w1, x1, y1, z1 = q1
            w2, x2, y2, z2 = q2
            w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
            x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
            y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
            z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
            return np.array([w, x, y, z])

        # step6

        # compute transilational acceleration

        acc1 = np.column_stack((accX, accY, accZ))
        quat_conj = quatern_conj(quat)
        # print(quat_conj)

        acc2 = np.array([quatern_rotate(row, quat_conj[i, :]) for i, row in enumerate(acc1)])
        # print(acc2 )

        acc = acc2 * 9.8

        acc[:, 2] -= 9.8

        time = np.array(time)

        # step 7
        # Integrate acceleration to yield velocity
        vel = np.zeros(acc.shape)
        for t in range(1, vel.shape[0]):
            vel[t, :] = vel[t - 1, :] + acc[t, :] * sample_period
            if stationary[t] == 1:
                vel[t, :] = [0, 0, 0]  # apply ZUPT update when foot stationary

        # plt.figure()
        # plt.plot(vel)
        # plt.show()

        # Compute integral drift during non-stationary periods
        velDrift = np.zeros(vel.shape)
        stationaryStart = np.where(np.diff(stationary) == 1)[0]
        stationaryEnd = np.where(np.diff(stationary) == -1)[0]
        for i in range(len(stationaryEnd)):
            driftRate = vel[stationaryStart[i] - 1, :] / (stationaryStart[i] - stationaryEnd[i])
            enum = np.arange(1, stationaryStart[i] - stationaryEnd[i] + 1)
            drift = np.column_stack((enum * driftRate[0], enum * driftRate[1], enum * driftRate[2]))
            velDrift[stationaryEnd[i]:stationaryStart[i] - 1, :] = drift

        # Remove integral drift
        vel = vel - velDrift

        # Compute translational position

        # Integrate velocity to yield position
        pos = np.zeros(vel.shape)
        for t in range(1, pos.shape[0]):
            pos[t, :] = pos[t - 1, :] + vel[t, :] * sample_period

        # Plot translational position
        # y axis for ward, backward movement (new insole)
        # x axis for up/down
        # mahipal old data which uses x(forward/backward)

        # plt.figure(figsize=(9, 6))
        # plt.plot(time, pos[:, 0], 'r')
        # plt.plot(time, pos[:, 1], 'g')
        #
        # plt.title('Position')
        # plt.xlabel('samples')
        # plt.ylabel('Position (m)')
        # plt.legend(['X', 'Y', 'Z'])
        # plt.show()
        posX = np.abs(pos[:, 1])
        # pos[:,0] means x axis(old insole(mahipal data)). pos[:,1] for new insole(yaxis is x here)
        # print(posX)
        print(np.max(posX))
        max_pos = np.max(posX)
        # print("t11 is ",t11, time)
        #
        # # Find the index of the maximum value in sl
        # max_index = np.argmax(posX1)
        #
        # # Get the corresponding time from tm
        # # max_time = t11[max_index]
        # max_time = t11[max_index]
        # # Get the maximum value in sl
        # max_pos = np.max(posX1)

        max_pos_values.append(max_pos)
        print("max_pos_values", max_pos_values)
        print("sum of distance:", np.sum(max_pos_values))
        # max_pos_time.append(max_time)
        # print(np.sum(max_pos_values))
        # print("last",posX1[len(posX1)- 1])

        # a = (max_pos + posX1[len(posX1)- 1])/2
        # print("a=",a)
        # print(np.mean(posX1[len(posX1)- 1]))
        max_pos_array = np.array(max_pos_values)
    print("finally sl............", max_pos_values)
    print("finally time ..............", tim_array)
    # # print("finally time............",max_pos_time)
    #
    #
    timestart = tim_array[1]
    sc = 1
    righttstride = []
    tsumr = 0
    print(len(max_pos_values))
    for ts in range(2, (len(max_pos_values) - 1)):
        print(ts, tim_array[ts], max_pos_values[ts])
        tt = tim_array[ts] - timestart
        rightstride.append({"strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),
                           "velocity": (max_pos_values[ts] / float(tt * 0.001))})
        timestart = tim_array[ts]
        sc = sc + 1
        tsumr = tsumr + max_pos_values[ts]

    print("finally right stride :", rightstride)
    print("total distance :", tsumr, "m/s2")
    totrows = min(len(leftstride), len(rightstride))
    finarr = []
    for r1 in range(0, totrows):
        finarr.append({"leftsno": leftstride[r1]["strideno"], "rightsno": rightstride[r1]["strideno"],
                       "lefttime": leftstride[r1]["time"],
                       "righttime": rightstride[r1]["time"], "leftdist": leftstride[r1]["dist"],
                       "rightdist": rightstride[r1]["dist"],
                       "leftvelo": leftstride[r1]["velocity"], "rightvelo": rightstride[r1]["velocity"]})
    print("total distance: ", (tsum + tsumr))


    return Response(finarr)
######################################################################################################################



@api_view(["GET","POST"])
def finalhealtoes(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left ='L'
    right ='R'
    ltoe = []
    lheal = []
    ltime =[]
    rtime =[]
    rtoe =[]
    rheal = []
    finalarr =[]
    lcount =0
    rcount =0
    with connection.cursor() as cursor:
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s', [left, ssnid,stime,etime]);
        slval = cursor.fetchall()
        for p in slval:
            ptot = (p[0]+p[1]+p[2])
            ptot = ptot/3
            ltoe.append(ptot)
            ptot1 = (p[3] + p[4])
            ptot1 = ptot1 / 2
            lheal.append(ptot1)
            mapped_value = map_range(p[5], stime, etime, 0, 3000)
            mapped_value = round(mapped_value,0)
            ltime.append(mapped_value)
            lcount=lcount+1
        print(lcount)

    with connection.cursor() as cursor:
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s', [right, ssnid,stime,etime]);
        rlval = cursor.fetchall()
        for q in rlval:
            qtot = (q[0]+q[1]+q[2])
            qtot = qtot/3
            rtoe.append(qtot)
            qtot1 = (q[3] + q[4])
            qtot1 = qtot1 / 2
            rheal.append(qtot1)
            mapped_value1 = map_range(q[5], stime, etime, 0, 3000)
            mapped_value1 = round(mapped_value1, 0)
            rtime.append(mapped_value1)
            rcount = rcount+1
        print(rcount)

    tc = min(lcount, rcount)
    if (lcount<rcount):
        print("Left Minimum")
        ltoe = ltoe[:len(rtoe)]
        lheal = lheal[:len(rheal)]
        ltime = ltime[:len(rtime)]

    else:
        print("Right Minimum")
        rtoe = rtoe[:len(ltoe)]
        rheal = rheal[:len(lheal)]
        rtime = rtime[:len(ltime)]


    for i in range(tc):
        flefttoe = ltoe[i]
        fleftheal = lheal[i]
        frighttoe = rtoe[i]
        frightheal = rheal[i]
        flefttime = ltime[i]
        frighttime = rtime[i]
        finalarr.append({"leftheal": fleftheal,"lefttoe": flefttoe, "lefttime": flefttime, "rightheal": frightheal, "righttoe": frighttoe, "righttime": frighttime})

    return Response(finalarr)








@api_view(["GET","POST"])
def finalcentreofpressure(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left ='L'
    right ='R'
    lcopx = []
    lcopy = []
    ltime =[]
    rtime =[]
    rcopx =[]
    rcopy = []
    finalarr =[]
    lcount =0
    rcount =0

    ###################################### for 5 fsr's  data  ############## LEFT INSOLE
    with connection.cursor() as cursor:
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s', [left, ssnid,stime,etime]);
        slval = cursor.fetchall()
        for p in slval:
            xcop = (p[0] * 70) + (p[1] * 23) + (p[3] * 40) + (p[4] * 57)  #sensor 2 coordiantes  ??????
            ptot = (p[0] + p[1] + p[3] + p[4])
            if ptot >0:
                xcopf = xcop / ptot
            else :
               xcopf = 0
            ycop = (p[0] * 201) + (p[1] * 183) + (p[3] * 48) + (p[4] * 33)
            if ptot > 0:
                ycopf = ycop / ptot
            else:
                ycopf = 0
            xcopf = int(xcopf)
            ycopf = int(ycopf)
            lcopx.append(xcopf)
            lcopy.append(ycopf)
            mapped_value = map_range(p[5], stime, etime, 0, 3000)
            mapped_value = round(mapped_value,0)
            ltime.append(mapped_value)
            lcount=lcount+1
        print("lcount",lcount)

    ###################################### for 5 fsr's  data  ############## RIGHT INSOLE ################
    with connection.cursor() as cursor:
        cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s', [right, ssnid,stime,etime]);
        rlval = cursor.fetchall()
        for c in rlval:
            xcop1 = (c[0] * 19) + (c[1] * 66) + (c[2] * 68) + (c[3] * 41) + (c[4] * 26)
            ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
            if ptot1 >0 :
                xcopf1 = xcop1 / ptot1
            else :
                xcopf1
            ycop1 = (c[0] * 201) + (c[1] * 181) + (c[2] * 131) + (c[3] * 46) + (c[4] * 34)
            if ptot1 >0 :
                ycopf1 = ycop1 / ptot1
            else :
                ycopf1
            xcopf1 = int(xcopf1)
            ycopf1 = int(ycopf1)
            rcopx.append(xcopf1)
            rcopy.append(ycopf1)
            mapped_value1 = map_range(c[5], stime, etime, 0, 3000)
            mapped_value1 = round(mapped_value1, 0)
            rtime.append(mapped_value1)
            rcount = rcount+1
        print("rcount",rcount)

    tc = min(lcount, rcount)
    print("tc is",tc)
    if (lcount<rcount):
        print("Left Minimum")
        lcopx = lcopx[:len(rcopx)]
        lcopy = lcopy[:len(rcopy)]
        ltime = ltime[:len(rtime)]

    else:
        print("Right Minimum")
        rcopx = rcopx[:len(lcopx)]
        rcopy = rcopy[:len(lcopy)]
        rtime = rtime[:len(ltime)]


    for i in range(tc):
        fleftcopx = lcopx[i]
        fleftcopy = lcopy[i]
        frightcopx = rcopx[i]
        frightcopy = rcopy[i]
        ftime = rtime[i]
        finalarr.append({"leftcopx": fleftcopx,"leftcopy": fleftcopy, "time": ftime, "rightcopx": frightcopx, "rightcopy": frightcopy})

    return Response(finalarr)


@api_view(["GET","POST"])
def strideinfo(request):           # online stride  reading
     ssnid = request.data["sid"]
     print(ssnid)

     try:
        with connection.cursor() as cursor:
            # p = cursor.execute("select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by starttime limit 11",[ssnid])
            p = cursor.execute("select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by strideno limit 11",[ssnid])
            rcnt = cursor.rowcount
            rstride =cursor.fetchall()
        print("right stride :", rstride)
        with connection.cursor() as cursor:
            # p = cursor.execute("select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by starttime desc limit 11",[ssnid])
            p = cursor.execute(
                "select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by strideno desc limit 11",
                [ssnid])
            lcnt = cursor.rowcount
            lstride = cursor.fetchall()
        print("left stride:",lstride)

        finarr = []
        for r1 in range(min(lcnt, rcnt)):
            finarr.append({
                "leftstrideno": lstride[r1][0],
                "rightstrideno": rstride[r1][0],
                "leftdistance": lstride[r1][1],
                "rightdistance": rstride[r1][1],
                "leftstridevel": lstride[r1][2],
                "rightstridevel": rstride[r1][2]
            })

        if lcnt == 0 and rcnt > 0:
            for r1 in range(rcnt):
                finarr.append({
                    "leftstrideno": 0,
                    "rightstrideno": rstride[r1][0],
                    "leftdistance": 0,
                    "rightdistance": rstride[r1][1],
                    "leftstridevel": 0,
                    "rightstridevel": rstride[r1][2]
                })
        elif rcnt == 0  and lcnt >0:
             for r1 in range(lcnt):
                finarr.append({
                    "leftstrideno": lstride[r1][0],
                    "rightstrideno": 0,
                    "leftdistance": lstride[r1][1],
                    "rightdistance": 0,
                    "leftstridevel": lstride[r1][2],
                    "rightstridevel": 0
                })
        elif (rcnt - lcnt) > 0 :
            for r1 in range(lcnt+1,rcnt):
                finarr.append({
                    "leftstrideno": 0,
                    "rightstrideno": rstride[r1][0],
                    "leftdistance": 0,
                    "rightdistance": rstride[r1][1],
                    "leftstridevel": 0,
                    "rightstridevel": rstride[r1][2]
                })
        elif (lcnt - rcnt) > 0:
            for r1 in range(rcnt + 1, lcnt):
                finarr.append({
                    "leftstrideno": lstride[r1][0],
                    "rightstrideno": 0,
                    "leftdistance": lstride[r1][1],
                    "rightdistance": 0,
                    "leftstridevel": lstride[r1][2],
                    "rightstridevel": 0
                })

        print(finarr)


     except Exception as e:
         print(e)
     return Response(finarr)





@api_view(["GET","POST"])
def finalcentreofpressuremod(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]
    nos = request.data["totalsensors"]

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left = 'L'
    right = 'R'
    lcopx = []
    lcopy = []
    ltime = []
    rtime = []
    rcopx = []
    rcopy = []
    finalarr = []
    lcount = 0
    rcount = 0
    if (nos == 11):
        ###################################### for 5 fsr's  data  ############## LEFT INSOLE
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [left, ssnid, stime, etime]);
            slval = cursor.fetchall()
            for p in slval:
                xcop = (p[0] * 70) + (p[1] * 23) + (p[3] * 40) + (p[3] * 57)  # NOTE: someone removed p[2]  from this statement as that sensor wasn't working.
                ptot = (p[0] + p[1] + p[3] + p[4])  # NOTE: someone removed p[2]  from this statement as that sensor wasn't working.
                if ptot > 0:
                    xcopf = xcop / ptot
                else:
                    xcopf = 0
                ycop = (p[0] * 201) + (p[1] * 183) + (p[3] * 48) + (p[4] * 33)  # NOTE: someone removed p[2]  from this statement as that sensor wasn't working.
                if ptot > 0:
                    ycopf = ycop / ptot
                else:
                    ycopf = 0

                xcopf = int(xcopf)
                ycopf = int(ycopf)
                lcopx.append(xcopf)
                lcopy.append(ycopf)
                mapped_value = map_range(p[5], stime, etime, 0, 3000)
                mapped_value = round(mapped_value, 0)
                ltime.append(mapped_value)
                lcount = lcount + 1
            # print(lcount)

        ###################################### for 5 fsr's  data  ############## RIGHT INSOLE ################
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [right, ssnid, stime, etime])
            rlval = cursor.fetchall()
            for c in rlval:
                xcop1 = (c[0] * 19) + (c[1] * 66) + (c[2] * 68) + (c[3] * 41) + (c[4] * 26)
                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
                if ptot1 >0:
                    xcopf1 = xcop1 / ptot1
                else :
                    xcopf1 = 0
                ycop1 = (c[0] * 201) + (c[1] * 181) + (c[2] * 131) + (c[3] * 46) + (c[4] * 34)
                if ptot1 >0:
                    ycopf1 = ycop1 / ptot1
                else :
                    ycopf1 = 0

                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                mapped_value1 = map_range(c[5], stime, etime, 0, 3000)
                mapped_value1 = round(mapped_value1, 0)
                rtime.append(mapped_value1)
                rcount = rcount + 1
            # print(rcount)
    else:
        ################## for 10 fsr's  data  ################# LEFT INSOLE  ##############
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [left, ssnid, stime, etime]);
            slval = cursor.fetchall()
        for p in ssvals:
            xcop = (p[0] * 28.89) + (p[1] * 21.58) + (p[2] * 19.10) + (p[3] * 47.62) + (p[4] * 80.44) + (
                        p[5] * 82.47) + (p[6] * 77.08) + (p[7] * 71.93) + (p[8] * 53.02) + (p[9] * 33.83)
            ptot = (p[0] + p[1] + p[3] + p[4])
            if ptot > 0:
                xcopf = xcop / ptot
            else:
                xcopf = 0
            ycop = (p[0] * 135.71) + (p[1] * 172.68) + (p[2] * 210.84) + (p[3] * 214.09) + (p[4] * 239.99) + (
                        p[5] * 206.10) + (p[6] * 163.06) + (p[7] * 79.17) + (p[8] * 33.46) + (p[9] * 78.84)
            if ptot > 0:
                ycopf = ycop / ptot
            else:
                ycopf = 0
            xcopf = int(xcopf)
            ycopf = int(ycopf)
            lcopx.append(xcopf)
            lcopy.append(ycopf)
            mapped_value = map_range(p[5], stime, etime, 0, 3000)
            mapped_value = round(mapped_value, 0)
            ltime.append(mapped_value)
            lcount = lcount + 1
            # print(lcount)

        #################### for 10 fsr's  data  ################# RIGHT INSOLE  ##############
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [right, ssnid, stime, etime]);
            rlval = cursor.fetchall()
            for c in rlval:
                xcop1 = (c[0] * 74.13) + (c[1] * 81.44) + (c[2] * 83.92) + (c[3] * 55.40) + (c[4] * 22.57) + (
                            c[5] * 20.54) + (c[6] * 25.94) + (c[7] * 31.09) + (c[8] * 50) + (c[9] * 69.19)
                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
                if ptot1 >0:
                    xcopf1 = xcop1 / ptot1
                else :
                    xcopf1= 0

                ycop1 = (c[0] * 134.88) + (c[1] * 171.80) + (c[2] * 209.95) + (c[3] * 213.21) + (c[4] * 239.10) + (
                            c[5] * 205.22) + (c[6] * 162.18) + (c[7] * 78.28) + (c[8] * 32.58) + (c[9] * 77.95)
                if ptot1 >0 :
                    ycopf1 = ycop1 / ptot1
                else:
                    ycopf1 = 0
                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                mapped_value1 = map_range(c[5], stime, etime, 0, 3000)
                mapped_value1 = round(mapped_value1, 0)
                rtime.append(mapped_value1)
                rcount = rcount + 1
                # print(rcount)

    tc = min(lcount, rcount)
    if (lcount < rcount):
        # print("Left Minimum")
        lcopx = lcopx[:len(rcopx)]
        lcopy = lcopy[:len(rcopy)]
        ltime = ltime[:len(rtime)]

    else:
        # print("Right Minimum")
        rcopx = rcopx[:len(lcopx)]
        rcopy = rcopy[:len(lcopy)]
        rtime = rtime[:len(ltime)]

    for i in range(tc):
        fleftcopx = lcopx[i]
        fleftcopy = lcopy[i]
        frightcopx = rcopx[i]
        frightcopy = rcopy[i]
        ftime = rtime[i]
        finalarr.append({"leftcopx": fleftcopx, "leftcopy": fleftcopy, "time": ftime, "rightcopx": frightcopx,
                         "rightcopy": frightcopy})

    return Response(finalarr)


#############################################################################################################################################################





@api_view(["GET","POST"])
def finalcentreofpressuremod(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]
    nos = request.data["totalsensors"]

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left = 'L'
    right = 'R'
    lcopx = []
    lcopy = []
    ltime = []
    rtime = []
    rcopx = []
    rcopy = []
    finalarr = []
    lcount = 0
    rcount = 0
    if (nos == 11):
        ###################################### for 11 sensor data  ############## LEFT INSOLE
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [left, ssnid, stime, etime]);
            slval = cursor.fetchall()
            for p in slval:
                xcop = (p[0] * 70) + (p[1] * 23) + (p[3] * 40) + (p[3] * 57)  # NOTE: someone removed p[2]  from this statement as that sensor wasn't working.
                ptot = (p[0] + p[1] + p[3] + p[4])  # NOTE: someone removed p[2]  from this statement as that sensor wasn't working.
                if ptot > 0:
                    xcopf = xcop / ptot
                else:
                    xcopf = 0
                ycop = (p[0] * 201) + (p[1] * 183) + (p[3] * 48) + (p[4] * 33)  # NOTE: someone removed p[2]  from this statement as that sensor wasn't working.
                if ptot > 0:
                    ycopf = ycop / ptot
                else:
                    ycopf = 0

                xcopf = int(xcopf)
                ycopf = int(ycopf)
                lcopx.append(xcopf)
                lcopy.append(ycopf)
                mapped_value = map_range(p[5], stime, etime, 0, 3000)
                mapped_value = round(mapped_value, 0)
                ltime.append(mapped_value)
                lcount = lcount + 1
            # print(lcount)

        ###################################### for 11 sensor data  ############## RIGHT INSOLE ################
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [right, ssnid, stime, etime])
            rlval = cursor.fetchall()
            for c in rlval:
                xcop1 = (c[0] * 19) + (c[1] * 66) + (c[2] * 68) + (c[3] * 41) + (c[4] * 26)
                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
                if ptot1 >0:
                    xcopf1 = xcop1 / ptot1
                else :
                    xcopf1 = 0
                ycop1 = (c[0] * 201) + (c[1] * 181) + (c[2] * 131) + (c[3] * 46) + (c[4] * 34)
                if ptot1 >0:
                    ycopf1 = ycop1 / ptot1
                else :
                    ycopf1 = 0

                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                mapped_value1 = map_range(c[5], stime, etime, 0, 3000)
                mapped_value1 = round(mapped_value1, 0)
                rtime.append(mapped_value1)
                rcount = rcount + 1
            # print(rcount)
    else:
        ################## for 16 sensor  data  ################# LEFT INSOLE  ##############
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [left, ssnid, stime, etime]);
            slval = cursor.fetchall()
        for p in ssvals:
            xcop = (p[0] * 28.89) + (p[1] * 21.58) + (p[2] * 19.10) + (p[3] * 47.62) + (p[4] * 80.44) + (
                        p[5] * 82.47) + (p[6] * 77.08) + (p[7] * 71.93) + (p[8] * 53.02) + (p[9] * 33.83)
            ptot = (p[0] + p[1] + p[3] + p[4])
            if ptot > 0:
                xcopf = xcop / ptot
            else:
                xcopf = 0
            ycop = (p[0] * 135.71) + (p[1] * 172.68) + (p[2] * 210.84) + (p[3] * 214.09) + (p[4] * 239.99) + (
                        p[5] * 206.10) + (p[6] * 163.06) + (p[7] * 79.17) + (p[8] * 33.46) + (p[9] * 78.84)
            if ptot > 0:
                ycopf = ycop / ptot
            else:
                ycopf = 0
            xcopf = int(xcopf)
            ycopf = int(ycopf)
            lcopx.append(xcopf)
            lcopy.append(ycopf)
            mapped_value = map_range(p[5], stime, etime, 0, 3000)
            mapped_value = round(mapped_value, 0)
            ltime.append(mapped_value)
            lcount = lcount + 1
            # print(lcount)

        #################### for 16 sensor data  ################# RIGHT INSOLE  ##############
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [right, ssnid, stime, etime]);
            rlval = cursor.fetchall()
            for c in rlval:
                xcop1 = (c[0] * 74.13) + (c[1] * 81.44) + (c[2] * 83.92) + (c[3] * 55.40) + (c[4] * 22.57) + (
                            c[5] * 20.54) + (c[6] * 25.94) + (c[7] * 31.09) + (c[8] * 50) + (c[9] * 69.19)
                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
                if ptot1 >0:
                    xcopf1 = xcop1 / ptot1
                else :
                    xcopf1= 0

                ycop1 = (c[0] * 134.88) + (c[1] * 171.80) + (c[2] * 209.95) + (c[3] * 213.21) + (c[4] * 239.10) + (
                            c[5] * 205.22) + (c[6] * 162.18) + (c[7] * 78.28) + (c[8] * 32.58) + (c[9] * 77.95)
                if ptot1 >0 :
                    ycopf1 = ycop1 / ptot1
                else:
                    ycopf1 = 0
                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                mapped_value1 = map_range(c[5], stime, etime, 0, 3000)
                mapped_value1 = round(mapped_value1, 0)
                rtime.append(mapped_value1)
                rcount = rcount + 1
                # print(rcount)

    tc = min(lcount, rcount)
    if (lcount < rcount):
        # print("Left Minimum")
        lcopx = lcopx[:len(rcopx)]
        lcopy = lcopy[:len(rcopy)]
        ltime = ltime[:len(rtime)]

    else:
        # print("Right Minimum")
        rcopx = rcopx[:len(lcopx)]
        rcopy = rcopy[:len(lcopy)]
        rtime = rtime[:len(ltime)]

    for i in range(tc):
        fleftcopx = lcopx[i]
        fleftcopy = lcopy[i]
        frightcopx = rcopx[i]
        frightcopy = rcopy[i]
        ftime = rtime[i]
        finalarr.append({"leftcopx": fleftcopx, "leftcopy": fleftcopy, "time": ftime, "rightcopx": frightcopx,
                         "rightcopy": frightcopy})

    return Response(finalarr)





#############################################################################################################################################################



@api_view(["GET","POST"])
def finalcentreofpressuremodified(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]
    nos = request.data["totalsensors"]

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left = 'L'
    right = 'R'
    lcopx = []
    lcopy = []
    ltime = []
    rtime = []
    rcopx = []
    rcopy = []
    finalarr = []
    lcount = 0
    rcount = 0
    if (nos == 11):
        ###################################### for 11 sensor  data  ############## LEFT INSOLE
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [left, ssnid, stime, etime])
            slval = cursor.fetchall()
            for p in slval:
                xcop = (p[0] * 70) + (p[1] * 23) + (p[2] * 40) + (p[3] * 57) +(p[4] * 26)  
                ptot = (p[0] + p[1] + p[3] + p[4])  
                if ptot > 0:
                    xcopf = xcop / ptot
                else:
                    xcopf = 0
                ycop = (p[0] * 201) + (p[1] * 183) + (p[2] * 131) + (p[3] * 48) + (p[4] * 34)  
                if ptot > 0:
                    ycopf = ycop / ptot
                else:
                    ycopf = 0

                xcopf = int(xcopf)
                ycopf = int(ycopf)
                lcopx.append(xcopf)
                lcopy.append(ycopf)
                mapped_value = map_range(p[5], stime, etime, 0, 3000)
                mapped_value = round(mapped_value, 0)
                ltime.append(mapped_value)
                lcount = lcount + 1
            # print(lcount)

        ###################################### for 11 sensor data  ############## RIGHT INSOLE ################
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [right, ssnid, stime, etime])
            rlval = cursor.fetchall()
            for c in rlval:
                xcop1 = (c[0] * 19) + (c[1] * 66) + (c[2] * 68) + (c[3] * 41) + (c[4] * 26)
                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
                if ptot1 >0:
                    xcopf1 = xcop1 / ptot1
                else :
                    xcopf1 = 0
                ycop1 = (c[0] * 201) + (c[1] * 181) + (c[2] * 131) + (c[3] * 46) + (c[4] * 34)
                if ptot1 >0:
                    ycopf1 = ycop1 / ptot1
                else :
                    ycopf1 = 0

                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                mapped_value1 = map_range(c[5], stime, etime, 0, 3000)
                mapped_value1 = round(mapped_value1, 0)
                rtime.append(mapped_value1)
                rcount = rcount + 1
            # print(rcount)
    else:
        ################## for 16 sensor data  ################# LEFT INSOLE  ##############
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [left, ssnid, stime, etime]);
            slval = cursor.fetchall()
        for p in ssvals:
            # xcop = (p[0] * 28.89) + (p[1] * 21.58) + (p[2] * 19.10) + (p[3] * 47.62) + (p[4] * 80.44) + (
            #             p[5] * 82.47) + (p[6] * 77.08) + (p[7] * 71.93) + (p[8] * 53.02) + (p[9] * 33.83)
            xcop= ((p[0] * 31.99) + (p[1] * 27.69) + (p[2] * 26.23) + (p[3] * 43.01) + (p[4] * 63.21) + (p[5] * 63.51) + (p[6] * 60.34) + (p[7] * 57.31) + (p[8] * 46.18) + (p[9] * 34.90))
            ptot = (p[0] + p[1] + p[3] + p[4])
            if ptot > 0:
                xcopf = xcop / ptot
            else:
                xcopf = 0
            ycop = (p[0] * 135.71) + (p[1] * 172.68) + (p[2] * 210.84) + (p[3] * 214.09) + (p[4] * 239.99) + (p[5] * 206.10) + (p[6] * 163.06) + (p[7] * 79.17) + (p[8] * 33.46) + (p[9] * 78.84)
            if ptot > 0:
                ycopf = ycop / ptot
            else:
                ycopf = 0
            xcopf = int(xcopf)
            ycopf = int(ycopf)
            lcopx.append(xcopf)
            lcopy.append(ycopf)
            mapped_value = map_range(p[5], stime, etime, 0, 3000)
            mapped_value = round(mapped_value, 0)
            ltime.append(mapped_value)
            lcount = lcount + 1
            # print(lcount)

        #################### for 16 sensor data  ################# RIGHT INSOLE  ##############
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [right, ssnid, stime, etime]);
            rlval = cursor.fetchall()
            for c in rlval:
                # xcop1 = (c[0] * 74.13) + (c[1] * 81.44) + (c[2] * 83.92) + (c[3] * 55.40) + (c[4] * 22.57) + (
                #             c[5] * 20.54) + (c[6] * 25.94) + (c[7] * 31.09) + (c[8] * 50) + (c[9] * 69.19)
                xcop1 = ((c[0] * 52.37) + (c[1] * 57.48) + (c[2] * 59.23) + (c[3] * 39.10) + (c[4] * 15.93) + (c[5] * 14.49) + (c[6] * 18.31) + (c[7] * 21.94) + (c[8] * 35.29) + (c[9] * 48.84))
                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
                if ptot1 >0:
                    xcopf1 = xcop1 / ptot1
                else :
                    xcopf1= 0

                ycop1 = (c[0] * 134.88) + (c[1] * 171.80) + (c[2] * 209.95) + (c[3] * 213.21) + (c[4] * 239.10) + (
                            c[5] * 205.22) + (c[6] * 162.18) + (c[7] * 78.28) + (c[8] * 32.58) + (c[9] * 77.95)
                if ptot1 >0 :
                    ycopf1 = ycop1 / ptot1
                else:
                    ycopf1 = 0
                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                mapped_value1 = map_range(c[5], stime, etime, 0, 3000)
                mapped_value1 = round(mapped_value1, 0)
                rtime.append(mapped_value1)
                rcount = rcount + 1
                # print(rcount)

    tc = min(lcount, rcount)
    if (lcount < rcount):
        # print("Left Minimum")
        lcopx = lcopx[:len(rcopx)]
        lcopy = lcopy[:len(rcopy)]
        ltime = ltime[:len(rtime)]

    else:
        # print("Right Minimum")
        rcopx = rcopx[:len(lcopx)]
        rcopy = rcopy[:len(lcopy)]
        rtime = rtime[:len(ltime)]

    for i in range(tc):
        fleftcopx = lcopx[i]
        fleftcopy = lcopy[i]
        frightcopx = rcopx[i]
        frightcopy = rcopy[i]
        ftime = rtime[i]
        finalarr.append({"leftcopx": fleftcopx, "leftcopy": fleftcopy, "time": ftime, "rightcopx": frightcopx,
                         "rightcopy": frightcopy})

    return Response(finalarr)


@api_view(["GET","POST"])
def finalcentreofpressuremodified1121(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]
    nos = request.data["totalsensors"]

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left = 'L'
    right = 'R'
    lcopx = []
    lcopy = []
    ltime = []
    rtime = []
    rcopx = []
    rcopy = []
    finalarr = []
    lcount = 0
    rcount = 0
    if (nos == 11):
        with connection.cursor() as cursor:
                cursor.execute("SELECT xcoord, ycoord from insole where insoleid=(select leftinsoleid from userdevice where udevid = (select udevid from sessionactivity where sessionid=%s))",[ssnid])
                xyvals = cursor.fetchall()
        
        ###################################### for 11 sensor  data  ############## LEFT INSOLE
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [left, ssnid, stime, etime]);
            slval = cursor.fetchall()
            for p in slval:
                # xcop = (p[0] * 70) + (p[1] * 23) + (p[2] * 40) + (p[3] * 57) +(p[4] * 26)  
                xcop = (p[0] * xyvals[0][0][0]) + (p[1] *xyvals[0][0][1]) + (p[2] * xyvals[0][0][2]) + (p[3] * xyvals[0][0][3]) +(p[4] * xyvals[0][0][4])  
                ptot = (p[0] + p[1] + p[3] + p[4])  
                if ptot > 0:
                    xcopf = xcop / ptot
                else:
                    xcopf = 0
                # ycop = (p[0] * 201) + (p[1] * 183) + (p[2] * 131) + (p[3] * 48) + (p[4] * 34)  
                ycop = (p[0] * xyvals[0][1][0]) + (p[1] * xyvals[0][1][1]) + (p[2] * xyvals[0][1][2]) + (p[3] * xyvals[0][1][3]) + (p[4] * xyvals[0][1][4])  
                if ptot > 0:
                    ycopf = ycop / ptot
                else:
                    ycopf = 0

                xcopf = int(xcopf)
                ycopf = int(ycopf)
                lcopx.append(xcopf)
                lcopy.append(ycopf)
                mapped_value = map_range(p[5], stime, etime, 0, 3000)
                mapped_value = round(mapped_value, 0)
                ltime.append(mapped_value)
                lcount = lcount + 1
            # print(lcount)

        ###################################### for 11 sensor data  ############## RIGHT INSOLE ################
        with connection.cursor() as cursor:
                cursor.execute("SELECT xcoord, ycoord from insole where insoleid=(select rightinsoleid from userdevice where udevid = (select udevid from sessionactivity where sessionid=%s))",[ssnid])
                xyvals = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [right, ssnid, stime, etime])
            rlval = cursor.fetchall()
            for c in rlval:
                # xcop1 = (c[0] * 19) + (c[1] * 66) + (c[2] * 68) + (c[3] * 41) + (c[4] * 26)
                xcop1 = (c[0] * xyvals[0][0][0]) + (c[1] * xyvals[0][0][1]) + (c[2] * xyvals[0][0][2]) + (c[3] * xyvals[0][0][3]) + (c[4] * xyvals[0][0][4])
                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
                if ptot1 >0:
                    xcopf1 = xcop1 / ptot1
                else :
                    xcopf1 = 0
                # ycop1 = (c[0] * 201) + (c[1] * 181) + (c[2] * 131) + (c[3] * 46) + (c[4] * 34)
                ycop1 = (c[0] * xyvals[0][1][0]) + (c[1] * xyvals[0][1][1]) + (c[2] * xyvals[0][1][2]) + (c[3] * xyvals[0][1][3]) + (c[4] * xyvals[0][1][4])
                if ptot1 >0:
                    ycopf1 = ycop1 / ptot1
                else :
                    ycopf1 = 0

                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                mapped_value1 = map_range(c[5], stime, etime, 0, 3000)
                mapped_value1 = round(mapped_value1, 0)
                rtime.append(mapped_value1)
                rcount = rcount + 1
            # print(rcount)
    else:
        ################## for 16 sensor data  ################# LEFT INSOLE  ##############
        with connection.cursor() as cursor:
                cursor.execute("SELECT xcoord, ycoord from insole where insoleid=(select leftinsoleid from userdevice where udevid = (select udevid from sessionactivity where sessionid=%s))",[ssnid])
                xyvals = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [left, ssnid, stime, etime]);
            slval = cursor.fetchall()
        for p in ssvals:
            # xcop = (p[0] * 28.89) + (p[1] * 21.58) + (p[2] * 19.10) + (p[3] * 47.62) + (p[4] * 80.44) + (
            #             p[5] * 82.47) + (p[6] * 77.08) + (p[7] * 71.93) + (p[8] * 53.02) + (p[9] * 33.83)
            # xcop= ((p[0] * 31.99) + (p[1] * 27.69) + (p[2] * 26.23) + (p[3] * 43.01) + (p[4] * 63.21) + (p[5] * 63.51) + (p[6] * 60.34) + (p[7] * 57.31) + (p[8] * 46.18) + (p[9] * 34.90))
            xcop= ((p[0] * xyvals[0][0][0]) + (p[1] * xyvals[0][0][1]) + (p[2] * xyvals[0][0][2]) + (p[3] * xyvals[0][0][3]) + (p[4] * xyvals[0][0][4]) + (p[5] * xyvals[0][0][5]) + (p[6] * xyvals[0][0][6]) + (p[7] * xyvals[0][0][7]) + (p[8] * xyvals[0][0][8]) + (p[9] * xyvals[0][0][9]))
            ptot = (p[0] + p[1] + p[3] + p[4])
            if ptot > 0:
                xcopf = xcop / ptot
            else:
                xcopf = 0
            # ycop = (p[0] * 135.71) + (p[1] * 172.68) + (p[2] * 210.84) + (p[3] * 214.09) + (p[4] * 239.99) + (p[5] * 206.10) + (p[6] * 163.06) + (p[7] * 79.17) + (p[8] * 33.46) + (p[9] * 78.84)
            ycop = (p[0] * xyvals[0][1][0]) + (p[1] * xyvals[0][1][1]) + (p[2] * xyvals[0][1][2]) + (p[3] * xyvals[0][1][3]) + (p[4] * xyvals[0][1][4]) + (p[5] * xyvals[0][1][5]) + (p[6] * xyvals[0][1][6]) + (p[7] * xyvals[0][1][7]) + (p[8] * xyvals[0][1][8]) + (p[9] * xyvals[0][1][9])
            if ptot > 0:
                ycopf = ycop / ptot
            else:
                ycopf = 0
            xcopf = int(xcopf)
            ycopf = int(ycopf)
            lcopx.append(xcopf)
            lcopy.append(ycopf)
            mapped_value = map_range(p[5], stime, etime, 0, 3000)
            mapped_value = round(mapped_value, 0)
            ltime.append(mapped_value)
            lcount = lcount + 1
            # print(lcount)

        #################### for 16 sensor data  ################# RIGHT INSOLE  ##############
        with connection.cursor() as cursor:
                cursor.execute("SELECT xcoord, ycoord from insole where insoleid=(select rightinsoleid from userdevice where udevid = (select udevid from sessionactivity where sessionid=%s))",[ssnid])
                xyvals = cursor.fetchall()
        
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s',
                [right, ssnid, stime, etime]);
            rlval = cursor.fetchall()
            for c in rlval:
                # xcop1 = (c[0] * 74.13) + (c[1] * 81.44) + (c[2] * 83.92) + (c[3] * 55.40) + (c[4] * 22.57) + (
                #             c[5] * 20.54) + (c[6] * 25.94) + (c[7] * 31.09) + (c[8] * 50) + (c[9] * 69.19)
                # xcop1 = ((c[0] * 52.37) + (c[1] * 57.48) + (c[2] * 59.23) + (c[3] * 39.10) + (c[4] * 15.93) + (c[5] * 14.49) + (c[6] * 18.31) + (c[7] * 21.94) + (c[8] * 35.29) + (c[9] * 48.84))
                xcop1 = ((c[0] * xyvals[0][0][0]) + (c[1] * xyvals[0][0][1]) + (c[2] * xyvals[0][0][2]) + (c[3] * xyvals[0][0][3]) + (c[4] * xyvals[0][0][4]) + (c[5] * xyvals[0][0][5]) + (c[6] * xyvals[0][0][6]) + (c[7] * xyvals[0][0][7]) + (c[8] * xyvals[0][0][8]) + (c[9] * xyvals[0][0][9]))

                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
                if ptot1 >0:
                    xcopf1 = xcop1 / ptot1
                else :
                    xcopf1= 0

                # ycop1 = (c[0] * 134.88) + (c[1] * 171.80) + (c[2] * 209.95) + (c[3] * 213.21) + (c[4] * 239.10) + (c[5] * 205.22) + (c[6] * 162.18) + (c[7] * 78.28) + (c[8] * 32.58) + (c[9] * 77.95) 
                ycop1 = (c[0] * xyvals[0][1][0]) + (c[1] * xyvals[0][1][1]) + (c[2] * xyvals[0][1][2]) + (c[3] * xyvals[0][1][3]) + (c[4] * xyvals[0][1][4]) + (c[5] * xyvals[0][1][5]) + (c[6] * xyvals[0][1][6]) + (c[7] * xyvals[0][1][7]) + (c[8] * xyvals[0][1][8]) + (c[9] * xyvals[0][1][9])
            
                if ptot1 >0 :
                    ycopf1 = ycop1 / ptot1
                else:
                    ycopf1 = 0
                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                mapped_value1 = map_range(c[5], stime, etime, 0, 3000)
                mapped_value1 = round(mapped_value1, 0)
                rtime.append(mapped_value1)
                rcount = rcount + 1
                # print(rcount)

    tc = min(lcount, rcount)
    if (lcount < rcount):
        # print("Left Minimum")
        lcopx = lcopx[:len(rcopx)]
        lcopy = lcopy[:len(rcopy)]
        ltime = ltime[:len(rtime)]

    else:
        # print("Right Minimum")
        rcopx = rcopx[:len(lcopx)]
        rcopy = rcopy[:len(lcopy)]
        rtime = rtime[:len(ltime)]

    for i in range(tc):
        fleftcopx = lcopx[i]
        fleftcopy = lcopy[i]
        frightcopx = rcopx[i]
        frightcopy = rcopy[i]
        ftime = rtime[i]
        finalarr.append({"leftcopx": fleftcopx, "leftcopy": fleftcopy, "time": ftime, "rightcopx": frightcopx,
                         "rightcopy": frightcopy})

    return Response(finalarr)





##########################################################################################################################################################


@api_view(["GET","POST"])
def angleMetrics(request):
    ssnid = request.data["ssnid"]  #40500
    stime = request.data["starttime"]  #100
    etime = request.data["endtime"]    #300    #L or R
    print("here.........")
    finalarr=[]
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT s9,10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='L'",
            [stime, etime, ssnid])
        lcnt = cursor.rowcount
        pl = cursor.fetchall()

        cursor.execute(
            "SELECT s9,10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='R'",
            [stime, etime, ssnid])
        rcnt = cursor.rowcount
        pr = cursor.fetchall()


    dfl = pd.DataFrame(pl)
    lgx = dfl.iloc[:, 0].values
    lgy = dfl.iloc[:, 1].values
    lgz = dfl.iloc[:, 2].values


    dfr = pd.DataFrame(pr)
    rgx = dfr.iloc[:, 0].values
    rgy = dfr.iloc[:, 1].values
    rgz = dfr.iloc[:, 2].values


    for j1 in range(len(lgx)):
         lgx[j1] = float(lgx[j1])
    for i1 in range(len(lgy)):
         lgy[i1] = float(lgy[i1])
    for k1 in range(len(lgz)):
         lgz[k1] = float(lgz[k1])

    for j2 in range(len(rgx)):
        rgx[j2] = float(rgx[j2])
    for i2 in range(len(rgy)):
        rgy[i2] = float(rgy[i2])
    for k2 in range(len(rgz)):
        rgz[k2] = float(rgz[k2])

    Fs = 40
    dt1 = 1/Fs


    t1 = np.arange(0, len(lgx) * dt1, dt1)
    t2 = np.arange(0, len(rgx) * dt1, dt1)
    lg_x = cumtrapz(lgx, t1, initial=0)
    lg_y = cumtrapz(lgy, t1, initial=0)
    lg_z = cumtrapz(lgz, t1, initial=0)
    rg_x = cumtrapz(rgx, t2, initial=0)
    rg_y = cumtrapz(rgy, t2, initial=0)
    rg_z = cumtrapz(rgz, t2, initial=0)


    langle = [lg_x, lg_y, lg_z]
    rangle = [rg_x, rg_y, rg_z]
    dl = np.array(langle, dtype=np.float64)
    dl = dl.T
    dr = np.array(rangle, dtype=np.float64)
    dr = dr.T
    ltotal_angle = np.linalg.norm(dl, ord=2, axis=1)
    mangl=np.max(ltotal_angle)
    langvals = []
    rtotal_angle = np.linalg.norm(dr, ord=2, axis=1)
    mangr = np.max(rtotal_angle)
    rangvals = []

    tc = min(len(ltotal_angle),len(rtotal_angle))

    lcount = len(ltotal_angle)
    rcount = len(rtotal_angle)


    if (lcount < rcount):
        print("Left Minimum")
        ltotal_angle = ltotal_angle[:len(rtotal_angle)]
        t1 = t1[:len(t2)]
    else:
        print("Right Minimum")
        ltotal_angle = ltotal_angle[:len(rtotal_angle)]
        t2 = t2[:len(t1)]

    print(ltotal_angle[1])
    t1f=[]
    t2f=[]


    for i in range(tc):
        print(i)
        langvals = ltotal_angle[i]
        rangvals = rtotal_angle[i]
        t1f = t1[i]
        t2f = t2[i]
        lmaxfootangle = mangl
        rmaxfootangle = mangr
        finalarr.append({"langle": round(langvals,2),"rangle": round(rangvals,2), "ltime": round(t1f,2), "rtime": round(t2f,2), "lmax": round(lmaxfootangle,3), "rmax": round(rmaxfootangle,3)})


    return Response(finalarr)

    # for i in range(cnt):
    #     angvals.append({'angle': round(total_angle[i],2), 'time': round(t[i],2),'footanglemax': round(mangl,2)})
    # return Response(angvals)


@api_view(["GET","POST"])
def getallsecondsframes(request):
    #video_url = request.data["videoref"]
    print("new")
    vid = request.data["videoid"]
    #video_url='http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4'
    video_url='C:/Users/MYPC/Downloads/new.mp4'

    video = cv2.VideoCapture('C:/Users/MYPC/Downloads/new.mp4')
    fps = video.get(cv2.CAP_PROP_FPS)
    print('opencv .....frames per second =', fps)
    total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))  #12125 expected   495 12375    extra 250 what to do??
    print("Total frames in the video",total)
    seconds = round(total / fps)
    video_time = datetime.timedelta(seconds=seconds)
    print(f"duration in seconds: {seconds}")

    command = ['ffprobe', '-v', 'error', '-hide_banner','-print_format','json','-select_streams','v:0','-show_packets', '-show_streams', video_url]
    output = subprocess.check_output(command).decode('utf-8')
    metadata = json.loads(output)
    #print(metadata, output)

    seconds=1
    framecnt=0
    fps=[]
    totframes= int(metadata['streams'][0]['nb_frames'])
    for i in range(0,totframes):
        msecs = float(metadata['packets'][i]['pts_time'])*1000
        if  msecs < seconds *1000  :
             msecs = msecs + (float(metadata['packets'][i]['pts_time'])*1000)
             framecnt = framecnt + 1
        else:
             fps.append({'second': (seconds-1), 'frames': framecnt,'msecs': msecs})
             msecs = float(metadata['packets'][i]['pts_time'])*1000
             framecnt = 1
             seconds = seconds + 1

    fps.append({'second': (seconds-1), 'frames': framecnt, 'msecs': msecs})
    print(fps)
    """
     for f in fps:
         # print(f['second'])
         with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
            p = cursor.execute("insert into videodetails(videoid,starttime,frames,msecs) values(%s,%s,%s,%s,%s)",
                    [vid, f['second'],f['frames'],(f['frames']*1000)])
     """
    return fps

@api_view(["GET","POST"])
def geteachframemsec(request):
        # video_url = request.data["videoref"]
        print("new")
        #vid = request.data["videoid"]
        # video_url='http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4'
        video_url = 'C:/Users/MYPC/Downloads/c8701.mp4'

        video = cv2.VideoCapture('C:/Users/MYPC/Downloads/new.mp4')
        fps = video.get(cv2.CAP_PROP_FPS)
        print('opencv .....frames per second =', fps)
        total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))  # 12125 expected   495 12375    extra 250 what to do??
        print("Total frames in the video", total)
        seconds = round(total / fps)
        video_time = datetime.timedelta(seconds=seconds)
        print(f"duration in seconds: {seconds}")

        command = ['ffprobe', '-v', 'error', '-hide_banner', '-print_format', 'json', '-select_streams', 'v:0',
                   '-show_packets', '-show_streams', video_url]
        output = subprocess.check_output(command).decode('utf-8')
        metadata = json.loads(output)
        # print(metadata, output)
        fps = []
        totframes = int(metadata['streams'][0]['nb_frames'])
        for i in range(1, totframes):
            msecs = float(metadata['packets'][i]['pts_time']) * 1000
            print("frame number:", i, "msec:", ((metadata['packets'][i]['pts_time']) * 1000))
            fps.append({'frame number': i, 'msec': msecs })
        print(fps)
        return JsonResponse({'fps':fps})


# this api will help polling till video to frame cut is completed
#framecut column in videofile will be set true if video to frame cut is completed.
@api_view(["GET","POST"])
def get25framemsec(request):
  try:
    vid = request.data["videoid"]
    video_file = request.data["video"]
    #video_file = 'C:/Users/MYPC/Downloads/c8701.mp4'
    #video_file = 'C:/Users/MYPC/Videos/final.mp4'                       # 30 fps and  25 secs
    with connection.cursor() as cursor:
        cursor.execute("Delete from videodetails where videoid=%s",[vid])

    cap = cv2.VideoCapture(video_file)
    frameduration = []
    slotduration=[]

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = 10  #25
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Total frames in the video", total)
    seconds1 = round(total / fps)
    print(f"duration in seconds: {seconds1}")
    print("======================fps of ",video_file ,"is: ", fps)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_duration = total_frames * 1000.0 / fps
    btime = 1000//fps
    frame_index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        duration = frame_index * 1000.0 / fps

        print("frame#:", frame_index, "msec:", duration)
        frameduration.append({'frame#': frame_index, 'msec': duration})
        actualtime = btime + duration
        with connection.cursor() as cursor:
            cursor.execute("insert into videodetails(videoid,frames,msecs,actualfps) values(%s,%s,%s,%s)",
                           [vid, frame_index, duration,actualtime])
        if frame_index % frame_interval == 0:
            slotduration.append({'frame#':frame_index, 'msec':duration})
        frame_index += 1

    cap.release()
    print(frameduration)
    print(slotduration)
    with connection.cursor() as cursor:
        cursor.execute("update videofile set framecut=true, fps=%s where videoid = %s",[fps,vid])
  except Exception as e:
      print(e)

  return JsonResponse({'fps': frameduration, 'slot':slotduration})     # each frame duration in fps  and i use convention that 25 or 30 frames  as you specify as one slot so its duration is in slotduration


@api_view(["GET","POST"])
def getsubactivityframes(request):
    vid = request.data["videoid"]
    stime = request.data["starttime"]
    etime = request.data["endtime"]
    print(vid, stime,etime)
    with connection.cursor() as cursor:
        cursor.execute("SELECT frames, msecs from videodetails where videoid=%s and msecs>=%s and msecs<=%s",[vid, stime, etime])
        subframes = cursor.fetchall()
        print(subframes)
    fvals = []
    for s in subframes:
        print(s)
        fvals.append({'frame': s[0], 'msecs': s[1]})
    print(fvals)

    video = cv2.VideoCapture('C:/Users/MYPC/Downloads/new.mp4')
    pname = "/Users/MYPC/Downloads/paadhuimages/"
    i=1
    for s in subframes:
            t_msec = s[1]
            video.set(cv2.CAP_PROP_POS_MSEC, t_msec)
            ret, frame = video.read()
            picname = pname +"frame"+str(i)+".jpg"
            cv2.imwrite(picname, frame)
            i=i+1

    return Response(fvals)


@api_view(["GET","POST"])
def subactvideoandframemsecs(request):
    vid = request.data["videoid"]
    stime = request.data["starttime"]
    etime = request.data["endtime"]

    print(vid, stime, etime)
    ### gets msecs and frames for the specified stime and etime
    with connection.cursor() as cursor:
        cursor.execute("SELECT frames, msecs from videodetails where videoid=%s and msecs>=%s and msecs<=%s",
                       [vid, stime, etime])
        subframes = cursor.fetchall()
        print(subframes)
    fvals = []
    for s in subframes:
        print(s)
        fvals.append({'frame': s[0], 'msecs': s[1]})
    print(fvals)

    ### open that video to get that clip
    video = cv2.VideoCapture('C:/Users/MYPC/Downloads/new.mp4')
    fps = video.get(cv2.CAP_PROP_FPS)
    w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print('opencv .....frames per second =', fps, " width: ", w, " height: ", h)
    frameSize = (w, h)
    ### creates the clip from the starttime to endtime
    out = cv2.VideoWriter('C:/Users/umag1/Downloads/output_video.mp4', cv2.VideoWriter_fourcc(*'DIVX'), fps, frameSize)
    for s in subframes:
        t_msec = s[1]
        video.set(cv2.CAP_PROP_POS_MSEC, t_msec)
        ret, frame = video.read()
        out.write(frame)

    return Response(fvals)




@api_view(["GET","POST"])
def getsensorxycoords(request):
    mid = request.data["insoleid"]


    with connection.cursor() as cursor:
        cursor.execute("SELECT xcoord, ycoord from insole where insoleid=%s",[mid])
        xyvals = cursor.fetchall()
    for i in xyvals:
        print("x coord: ",i[0],"   ycoord: ",i[1])
    return JsonResponse({"xyvals":xyvals})


@api_view(["POST"])
def setsensorxycoords(request):
    mid = request.data["insoleid"]
    xv = request.data["xpos"]
    yv = request.data["ypos"]
    with connection.cursor() as cursor:
        p = cursor.execute("UPDATE insole set xcoord= %s, ycoord =%s where insoleid=%s",[xv,yv,mid])

    return JsonResponse({"status":p})


#gets the start and endtime's  frames msec from videodetails table.
@api_view(["POST"])
def getframemsec(request):
    vid = request.data["videoid"]
    stime = request.data["starttime"]
    etime = request.data["endtime"]
    video = cv2.VideoCapture('C:/Users/MYPC/Downloads/c8701.mp4')
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    total_duration = total_frames * 1000.0 / fps
    fpos = (stime * fps) /1000.0
    frame_index = 0
    while True:
        ret, frame = video.read()
        if not ret:
            break
        duration = frame_index * 1000.0 / fps
        if duration == stime:
           sfpos = frame_index
        if duration == etime:
           efpos = frame_index
    print("starting time frame#:", sfpos, "ending time frame#:", efpos)
    with connection.cursor() as cursor:
        cursor.execute("SELECT msec where frame=%s and vid=%s",[sfpos,vid])
        st=cursor.fetchone()
        cursor.execute("SELECT msec where frame=%s and vid=%s", [efpos, vid])
        et = cursor.fetchone()
    return JsonResponse({"smsec":st, "emsec":et})


@api_view(["GET","POST"])
def ADCcalibrate(request):
    ssnid = request.data["sessionid"]

    with connection.cursor() as cursor:
        p = cursor.execute(
            "select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,capturedtime, timelocal,soletype,macid from sensordata where sessionid = %s",[ssnid])
        c = cursor.fetchall()
    print(c)
    calibrate = []
    for d in c:
        for i in range(0, 5):
            if d[i] >= 778:
                f = 0.1439 * d[i] - 109.31
            elif d[i] < 778 and d[i] > 18:
                f = 0.0035 * d[i] - 0.063
            elif d[i] <= 18:
                f = 0
            calibrate.append(f)
    print(calibrate)
    if not p:
        return JsonResponse({'status': 'success', 'uncalibrated': c, 'sensordata': calibrate})
    else:
        return JsonResponse({'status': 'error'})

@api_view(["GET","POST"])
def getsensorhealth(request):
    mid = request.data["insoleid"]
    # sval= request.data["sensorhealth"]

    # print(sval)
    with connection.cursor() as cursor:
        p=cursor.execute("SELECT sensorhealth from insole where insoleid=%s",[mid])
        c = cursor.fetchone()

    print(c,c[0])

    if not p:
        return JsonResponse({'status': 'success', "health": c[0]})
    else:
        return JsonResponse({'status': 'error'})


@api_view(["GET","POST"])
def setsensorhealth(request):
    mid = request.data["insoleid"]
    sval= request.data["sensorhealth"]  # input should be [true,false,true,true]

    print(sval)
    with connection.cursor() as cursor:
        p=cursor.execute("UPDATE insole set sensorhealth = %s where insoleid=%s",[sval, mid])
    if not p:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})




# for given msec of video find the framenumber
@api_view(["POST"])
def getframenoformsec(request):
        vid = request.data["videofile"]
        wtime = request.data["wtime"]
        cap = cv2.VideoCapture(vid)
        fps = cap.get(cv2.CAP_PROP_FPS)
        btime = fps // 1000

        return JsonResponse({"time": wtime, "frameno": fnum})


#  it take vid, start and end times , it returns the frame number, msec and actual fps  from videodetails table(lookup table..
@api_view(["GET","POST"])
def frameactualtime(request):
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    vid = request.data["videoid"]
    stime = request.data["starttime"]
    etime = request.data["endtime"]
    print(vid)
    print(stime)
    print(etime)
    with connection.cursor() as cursor:
        p = cursor.execute("SELECT description from videofile where videoid=%s",[vid])
        c = cursor.fetchone()
    vidurl=c[0]
    print("video url: ",c[0])
    cap = cv2.VideoCapture(vidurl)
    print("Accessing video and its details.................................")
    fps = cap.get(cv2.CAP_PROP_FPS)
    print('opencv .....frames per second =', fps)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Total frames in the video", total)
    seconds1 = round(total / fps)
    video_time = datetime.timedelta(seconds=seconds1)
    print(f"duration in seconds: {seconds1}")
    print("---------------- video and its details.................................")
    try:
      with connection.cursor() as cursor:
        cursor.execute("select msecs from videodetails where videoid= %s and actualfps >=%s order by  actualfps  asc limit 1",[vid,stime])
        c=cursor.fetchone()
        print("api frameactual time......... returns ")
        print("start msecs:", c[0])
        cursor.execute("select msecs from videodetails where videoid= %s and actualfps <=%s ORDER BY vdid DESC limit 1", [vid, etime])
        c1 = cursor.fetchone()
        print("end time ....returns ", c1)
    except Exception as e:
        print(e)


    return JsonResponse({'starttime': c[0] , 'endtime':c1[0]})







# stride metrics as graph..
@api_view(["GET","POST"])
def strides1(request):
    stime = request.data["start"]
    ssnid = request.data["ssnid"]
    etime = request.data["end"]

    left ='L'
    right ='R'
    rpeak = []
    lpeak = []
    finalarr =[]
    with connection.cursor() as cursor:
        cursor.execute("SELECT s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='L'",[stime, etime, ssnid])
        cnt = cursor.rowcount
        p=cursor.fetchall()
        print(p)

    df = pd.DataFrame(p)
    acc_x = df.iloc[:, 0].values
    acc_y = df.iloc[:, 1].values
    acc_z = df.iloc[:, 2].values
    print(acc_x)

    for j in range(len(acc_x)):
         acc_x[j] = float(acc_x[j])
    for i in range(len(acc_y)):
         acc_y[i] = float(acc_y[i])
    for k in range(len(acc_z)):
         acc_z[k] = float(acc_z[k])

    g = 0.98
    acc_y = acc_y - g
    accleration = [acc_x, acc_y, acc_z]
    dt = 0.0175  # 1/43
    t = numpy.arange(0, len(acc_x) * dt, dt)
    vel_x = cumtrapz(acc_x, t, initial=0)
    vel_y = cumtrapz(acc_y, t, initial=0)
    vel_z = cumtrapz(acc_z, t, initial=0)
    velocity = list(zip(vel_x, vel_y, vel_z))
    vel_xy = list(zip(vel_x, vel_y))
    print(vel_x)
    vx = vel_x.astype(float)
    vy = vel_y.astype(float)
    print(vx)
    sp = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(vx, vy)]
    sp_max = np.max(sp)
    sp_avg = np.mean(sp)
    print("speed=", sp_max)
    print("avg=", sp_avg)
    #print(sp)

    #stride length calculation
    disp_x = cumtrapz(vel_x, t, initial=0)
    disp_y = cumtrapz(vel_y, t, initial=0)
    disp_z = cumtrapz(vel_z, t, initial=0)
    displacement = list(zip(disp_x, disp_y, disp_z))
    dx = disp_x.astype(float)
    dy = disp_y.astype(float)
    sl = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(dx, dy)]
    sl_max = np.max(sl)
    print("sl_max=", sl_max)
    # print(sl)
    t1 = float(12.64)
    # max_sl = max(sl)
    speed = sl_max / t1
    print("speed=", speed)
    tc = len(sl)
    ts=0
    time=[]
    # t = (etime - stime) // tc
    dt = (etime - stime) // tc         # is it always 250  unit time is 250??? is that agreed??
    for s in range(0,tc):
        ts=ts+dt
        time.append(ts)
    print("times is...")
    print(time, "len of timeis:",len(time))
    ntime=[]
    for i in range(1,tc):
         ts=abs(time[i]-time[i-1])
         ntime.append(ts)
    print(ntime)
    print(sl)
    # finalarr=[]
    # # finalarr.append({"time": 0, "stride0": 0, "stride1":0 ,"speed": 0})
    # prevleft =0
    # left = 0
    # right = 0
    # speed =0
    # timef =0
    # print("tc is ",tc)
    # k=1
    # for i in range(tc):
    #
    #    if (time[i] > (k*250)) :
    #        finalarr.append({"time": timef, "stride0": prevleft, "stride1": left, "speed": right})
    #        prevleft =left
    #        k = k+1
    #    else:
    #          left = round(sl[i],3)
    #          right = round(sp[i],3)
    #          timef = time[i]

    finalarr=[]
    times=t
    k = 250
    d = 0
    j = 1
    for i in range(0, len(times)):
        if times[i] <= k:
            d = d + sl[i]

        else:
            print("time:", k, "displacement:", d)
            finalarr.append({'time':k, 'displ': d})
            j = j + 1
            k = j * 250

    print(finalarr)
    return Response(finalarr)



@api_view(["GET","POST"])
def videodatasync(request):
    vid = request.data["videoid"]
    did = request.data["dataid"]
    stime = request.data["starttime"]
    etime = request.data["endtime"]

    # read data from where ????????????????????
    with connection.cursor() as cursor:
        cursor.execute("select mtime,data",[vid,stime,etime])
        data=cursor.fetchall()
    #read video frames
    with connection.cursor() as cursor:
        cursor.execute("select frames,msecs,actualfps from videodetails where actualfps >=%s and actualfps<=%s",[vid,stime,etime])
        frame=cursor.fetchall()

    finalvals=[]
    k=0
    for i in frame:
        if (data[k][0] == i[1]) and (data[k+1][1] == i[1]):
            dval = round((data[k][1]+data[k+1][1]) / 2.0)
            finalvals.append({'data': dval, 'msec':i[1], 'frame':i[0]})
        else:
            finalvals.append({'data': data[k][1], 'msec': i[1], 'frame': i[0]})
        k=k+1

    return Response(finavals)






#############################============= ADMIN PANEL API's ==========================###################


@api_view(["POST"])
def newuser(request):
    uname = request.data["uname"]
    setpas = request.data["setpas"]
    uemail = request.data["uemail"]
    mno = request.data["mno"]
    rname = request.data["rname"]
    adminid=request.data["adminid"]
    print(uname, setpas, uemail, mno, rname)
    with connection.cursor() as cursor:
        # calling the procedure
        s = cursor.execute('call createuser(%s,%s,%s,%s,%s)', [uname, setpas, uemail, mno, rname])
        s1 = cursor.execute('update userz set usertype=3, adminid=%s where emailid=%s',[adminid,uemail])

    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})

#unblock or undelete user
@api_view(["POST"])
def unblockuser(request):
    uid = request.data["userid"]
    block = request.data["block"]
    print(uid)
    print(block)
    with connection.cursor() as cursor:
        s = cursor.execute('update userz set blockedstatus=%s where userid=%s', [block,uid])

    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})

# use this to reset or change password
@api_view(["POST"])
def changepaswd(request):
    uid = request.data["userid"]
    pswd = request.data["password"]
    with connection.cursor() as cursor:
        s = cursor.execute("update userz set passwd=crypt(%s, gen_salt('bf')) where userid=%s", [pswd,uid])

    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})




#############################============= END OF ADMIN PANEL API's ==========================###################


@api_view(["POST"])
def Addnewhardwaredev(request):
    maddr= request.data["macaddr"]
    with connection.cursor() as cursor:
        p = cursor.execute('INSERT INTO hardwaremake(macaddress) values(%s)', [maddr])
    if not p:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})




#############################################End##########################################################
# stride metrics as graph..
@api_view(["GET","POST"])
def strides11(request):
    stime = request.data["start"]
    ssnid = request.data["ssnid"]
    etime = request.data["end"]

    left ='L'
    right ='R'
    rpeak = []
    lpeak = []
    finalarr =[]
    with connection.cursor() as cursor:
        cursor.execute("SELECT s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s ",[stime, etime, ssnid])
        cnt = cursor.rowcount
        p=cursor.fetchall()
    print("total count:",cnt)
    print(p)
    df = pd.DataFrame(p)
    print(df)
    acc_x = df.iloc[:, 0].values
    acc_y = df.iloc[:, 1].values
    acc_z = df.iloc[:, 2].values
    print("acc x values", acc_x)
    print("acc y values", acc_y)
    print("acc z values", acc_z)
    for j in range(len(acc_x)):
         acc_x[j] = float(acc_x[j])
    for i in range(len(acc_y)):
         acc_y[i] = float(acc_y[i])
    for k in range(len(acc_z)):
         acc_z[k] = float(acc_z[k])
    print("acc x values........ after float", acc_x)
    print("acc y values........ after float", acc_y)
    print("acc z values........ after float", acc_z)
    g = 0.98
    acc_y = acc_y - g
    accleration = [acc_x, acc_y, acc_z]
    print("acceleration.............",accleration, "                       Len of acc_x: ",len(acc_x))
    dt = 0.0175  # 1/43
    t = numpy.arange(0, len(acc_x) * dt, dt)
    print("time", t)
    vel_x = cumtrapz(acc_x, t, initial=0)
    vel_y = cumtrapz(acc_y, t, initial=0)
    vel_z = cumtrapz(acc_z, t, initial=0)
    velocity = list(zip(vel_x, vel_y, vel_z))
    vel_xy = list(zip(vel_x, vel_y))
    print("vel x values",vel_x)
    vx = vel_x.astype(float)
    vy = vel_y.astype(float)
    print(vx)
    sp = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(vx, vy)]
    sp_max = np.max(sp)
    sp_avg = np.mean(sp)
    print("speed=", sp_max)
    print("avg=", sp_avg)
    #print(sp)

    #stride length calculation
    disp_x = cumtrapz(vel_x, t, initial=0)
    disp_y = cumtrapz(vel_y, t, initial=0)
    disp_z = cumtrapz(vel_z, t, initial=0)
    displacement = list(zip(disp_x, disp_y, disp_z))
    dx = disp_x.astype(float)
    dy = disp_y.astype(float)
    sl = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(dx, dy)]
    sl_max = np.max(sl)
    print("sl_max=", sl_max)
    # print(sl)
    t1 = float(12.64)
    # max_sl = max(sl)
    speed = sl_max / t1
    print("speed=", speed)
    tc = len(sl)
    ts=0
    time=[]
    # t = (etime - stime) // tc
    t = (etime - stime) // 250         # is it always 250  unit time is 250??? is that agreed??
    for s in range(0,tc):
        ts=ts+t
        time.append(ts)
    ntime=[]
    for i in range(1,tc):
         ts=abs(time[i]-time[i-1])
         ntime.append(ts)

    print("time:", ntime)
    print("sl values:",sl)
    # Calculate displacements
    displacements = [stride_length * num_steps for stride_length, num_steps in
                     zip(sl, range(1, len(time) + 1))]
    time_intervals = np.array(time)
    stride_lengths = np.array(sl)
    displacements = np.array(displacements)
    finalarr=[]
    # finalarr.append({"time": 0, "stride0": 0, "stride1":0 ,"speed": 0})
    prevleft =0
    left = 0
    right = 0
    speed =0
    timef =0
    print("tc is ",tc)
    for i in range(0,tc):
       if (i%250) ==0:
           finalarr.append({"time": timef, "stride0": prevleft, "stride1": left, "speed": right})
           prevleft =left
       else:
             left = round(sl[k],3)
             right = round(sp[k],3)
             timef = time[k]

    finalarr.append({"time": timef, "stride0": prevleft, "stride1": left, "speed": right})
    # print(finalarr)
    return Response(finalarr)




# stride metrics as graph..
@api_view(["GET","POST"])
def strides122(request):
    stime = request.data["start"]
    ssnid = request.data["ssnid"]
    etime = request.data["end"]

    left ='L'
    right ='R'
    rpeak = []
    lpeak = []
    finalarr =[]
    with connection.cursor() as cursor:
        cursor.execute("SELECT s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s ",[stime, etime, ssnid])
        cnt = cursor.rowcount
        p=cursor.fetchall()
    print("total count:",cnt)
    print(p)
    df = pd.DataFrame(p)
    print(df)
    acc_x = df.iloc[:, 0].values
    acc_y = df.iloc[:, 1].values
    acc_z = df.iloc[:, 2].values
    print("acc x values", acc_x)
    print("acc y values", acc_y)
    print("acc z values", acc_z)
    for j in range(len(acc_x)):
         acc_x[j] = float(acc_x[j])
    for i in range(len(acc_y)):
         acc_y[i] = float(acc_y[i])
    for k in range(len(acc_z)):
         acc_z[k] = float(acc_z[k])
    print("acc x values........ after float", acc_x)
    print("acc y values........ after float", acc_y)
    print("acc z values........ after float", acc_z)
    g = 0.98
    acc_y = acc_y - g
    accleration = [acc_x, acc_y, acc_z]
    print("acceleration.............",accleration, "                       Len of acc_x: ",len(acc_x))
    dt = 0.0175  # 1/43
    t = numpy.arange(0, len(acc_x) * dt, dt)
    print("time", t)
    vel_x = cumtrapz(acc_x, t, initial=0)
    vel_y = cumtrapz(acc_y, t, initial=0)
    vel_z = cumtrapz(acc_z, t, initial=0)
    velocity = list(zip(vel_x, vel_y, vel_z))
    vel_xy = list(zip(vel_x, vel_y))
    print("vel x values",vel_x)
    vx = vel_x.astype(float)
    vy = vel_y.astype(float)
    print(vx)
    sp = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(vx, vy)]
    sp_max = np.max(sp)
    sp_avg = np.mean(sp)
    print("speed=", sp_max)
    print("avg=", sp_avg)
    #print(sp)

    #stride length calculation
    disp_x = cumtrapz(vel_x, t, initial=0)
    disp_y = cumtrapz(vel_y, t, initial=0)
    disp_z = cumtrapz(vel_z, t, initial=0)
    displacement = list(zip(disp_x, disp_y, disp_z))
    dx = disp_x.astype(float)
    dy = disp_y.astype(float)
    sl = [np.sqrt(x ** 2 + y ** 2) for x, y in zip(dx, dy)]
    sl_max = np.max(sl)
    print("sl_max=", sl_max)
    # print(sl)
    t1 = float(12.64)
    # max_sl = max(sl)
    speed = sl_max / t1
    print("speed=", speed)
    tc = len(sl)
    ts=0
    time=[]
    # t = (etime - stime) // tc
    t = (etime - stime) // 250         # is it always 250  unit time is 250??? is that agreed??
    for s in range(0,tc):
        ts=ts+t
        time.append(ts)
    ntime=[]
    for i in range(1,tc):
         ts=abs(time[i]-time[i-1])
         ntime.append(ts)

    print("time:", ntime)
    print("sl values:",sl)
    time_intervals = np.array(time)
    stride_lengths = np.array(sl)

    st = time_intervals[0]
    et = time_intervals[len(time_intervals) - 1]
    nbars = round((etime - stime) / 250)
    print("no of bars", nbars)
    tp = 0
    bc = 1
    k = 0
    farr = []
    s = 0
    s1=0
    s2=0
    farr.append({'time': s, 'dist': s})
    finalarr=[]
    finalarr.append({"time": 0, "stride0": 0, "stride1": 0, "speed": 0})
    while (bc <= nbars):
        slot = bc * 250
        print("time range", tp, tp + 250)
        while (time_intervals[k] <= slot):
                s = s + stride_lengths[k]
                k = k + 1
                # print("k",k, "slot",slot, "bc",bc)


        farr.append({'time': slot, 'dist': s})
        finalarr.append({"time": slot, "stride0": s1, "stride1": (s-s2), "speed": sp[k]})
        bc = bc + 1
        s1 = 0
        s2 = s
        s=0
        #print("farr", farr, "k", k, "slot", slot, "bc", bc)
    print(farr, " final array", finalarr)
    return Response(finalarr)


#############################============= ADMIN PANEL API's ==========================###################



#add new ordinary user depending on no of licenses purchased
@api_view(["POST"])
def newuser(request):
    uname = request.data["uname"]
    setpas = request.data["setpas"]
    uemail = request.data["uemail"]
    mno = request.data["mno"]
    rname = request.data["rname"]
    adminid = request.data["adminid"]
    print(uname, setpas, uemail, mno, rname)
    with connection.cursor() as cursor:
        p=cursor.execute('select nooflicence, usedlicence from licenses where adminid=%s', [adminid])
        p1=cursor.fetchone
        s2= True
        if (p1[0] -p1[1]) > 0 :
                # calling the procedure
                s = cursor.execute('call createuser(%s,%s,%s,%s,%s)', [uname, setpas, uemail, mno, rname])
        else :
            s2= False
    if s2:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error - purchase license'})



#block or delete user
@api_view(["POST"])
def admindeleteuser(request):
    print("Entering")
    print("Entering")
    uid = request.data["userid"]
    print(uid)
    with connection.cursor() as cursor:
        s = cursor.execute('update userz set userstatus=False where emailid=%s', [uid])

    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})



# use this to reset or change password
@api_view(["POST"])
def changepaswd(request):
    uid = request.data["userid"]
    pswd = request.data["password"]
    with connection.cursor() as cursor:
        s = cursor.execute("update userz set passwd=crypt(%s, gen_salt('bf')) where userid=%s", [pswd,uid])

    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})




#############################============= END OF ADMIN PANEL API's ==========================###################


@api_view(["GET","POST"])
def getsensorxycoords(request):
    mid = request.data["insoleid"]
    with connection.cursor() as cursor:
        cursor.execute("SELECT xcoord, ycoord from insole where insoleid=%s",[mid])
        xyvals = cursor.fetchall()
    for i in xyvals:
        print("x coord: ",i[0],"   ycoord: ",i[1])
    return JsonResponse({"xyvals":xyvals})


@api_view(["POST"])
def setsensorxycoords(request):
    mid = request.data["insoleid"]
    xv = request.data["xpos"]
    yv = request.data["ypos"]
    with connection.cursor() as cursor:
        p = cursor.execute("UPDATE insole set xcoord= %s, ycoord =%s where insoleid=%s",[xv,yv,mid])

    return JsonResponse({"status":p})



#######################################################admin apis'###############################################
# get admin details
@api_view(["GET","POST"])
def admindetails(request):
        uid = request.data["userid"]
        with connection.cursor() as cursor:
            #Email, Name, ContactNo, Role, Domain, Admin Id, Date, Organization
            s = cursor.execute('select emailid, username, mobileno, rolename, domain, oname, createddate from userz where userid=%s', [uid])
            s1=cursor.fetchone()
            a = cursor.execute("select userid from userz where domain=%s and usertype=2",[s1[4]])
            adminid =cursor.fetchone()
        if not s:
            return JsonResponse({'status': 'success','Email':s1[0],'Name':s1[1], 'ContactNo':s1[2], 'rolename':s1[3], 'domain':s1[4], 'adminid': adminid[0], 'date': s1[6], 'Organization':s1[5]})
        else:
            return JsonResponse({'status': 'error'})


#block admin
@api_view(["POST"])
def adminblock(request):
    uid = request.data["userid"]
    with connection.cursor() as cursor:
        s = cursor.execute('update userz set blockedstatus=True where userid=%s', [uid])
    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})

#unblock admin
@api_view(["POST"])
def adminunblock(request):
    uid = request.data["userid"]
    with connection.cursor() as cursor:
        s = cursor.execute('update userz set blockedstatus=false where userid=%s', [uid])
    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})



# edit admin details
@api_view(["POST"])
def editadmindetails(request):
    uid = request.data["userid"]
    name = request.data["username"]
    cno = request.data["contactno"]
    role = request.data["role"]
    domain = request.data["domain"]
    oname = request.data["organization"]
    with connection.cursor() as cursor:
        # Email, Name, ContactNo, Role, Domain, Admin Id, Date, Organization
        s = cursor.execute(
            'update userz set username=%s, mobileno=%s, rolename=%s, domain=%s, oname=%s  where userid=%s',
            [name, cno, role, domain, oname, uid])
    if not s:
        return JsonResponse(
            {'status': 'success', 'Email': s1[0], 'Name': s1[1], 'ContactNo': s1[2], 'rolename': s1[3], 'domain': s1[4],
             'adminid': adminid[0], 'date': s1[6], 'Organization': s1[5]})
    else:
        return JsonResponse({'status': 'error'})

#delete admin
@api_view(["POST"])
def deleteadmin(request):
    uid = request.data["adminid"]
    with connection.cursor() as cursor:
        s = cursor.execute('update userz set userstatus=False where userid=%s', [uid])
    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


# creating new admin
@api_view(["POST"])
def newadmin(request):
    uname = request.data["uname"]
    setpas = request.data["setpas"]
    uemail = request.data["uemail"]
    cno = request.data["contactno"]
    role = request.data["role"]
    domain = request.data["domain"]
    oname = request.data["organization"]
    amail= request.data["adminmail"]
    with connection.cursor() as cursor:
            #                        0           1        2            3           4       5            6       7    8
        a = cursor.execute('select userid,  insolemean, insolepeak, toehead,stridelength,footangle, speed, cop, organizationid from userz where emailid =%s',[amail])
        b= cursor.fetchone()
        print(b[0])
        for i in b:
            print(i)
        s = cursor.execute('call createuser(%s,%s,%s,%s,%s)', [uname, setpas, uemail, cno, role])
        # Email, Name, ContactNo, Role, Domain, Admin Id, Date, Organization
        # usertype =1 (for superadmin), =2(admin) =3 for ordinary user
        s1 = cursor.execute(
            'update userz set username=%s, mobileno=%s, rolename=%s, domain=%s, oname=%s, usertype=3,organizationid=%s, adminid=%s,insolemean = %s, insolepeak = %s, toehead = %s, stridelength = %s, footangle = %s, speed = %s, cop =%s  where emailid=%s',
            [uname, cno, role, domain, oname,b[8], b[0],b[1], b[2], b[3], b[4], b[5], b[6], b[7],uemail])
        s2 = cursor.execute(
                'update userz set   organizationid=%s, adminid=%s  where emailid=%s',
                [b[8], b[0],uemail])
        print("updated oid and adminid")
    #insolemean = % s, insolepeak = % s, toehead = % s, stridelength = % s, footangle = % s, speed = % s, cop = %s, [b[1], b[2], b[3], b[4], b[5], b[6], b[7],
    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


#make an existing user as admin
@api_view(["POST"])
def makeadmin(request):
    uid = request.data["userid"]
    with connection.cursor() as cursor:
        # usertype =1 (for superadmin), =2(admin) =3 for ordinary user
        s1 = cursor.execute(
            'update userz set usertype=2  where userid=%s',[uid])
    if not s1:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


# get insole details
@api_view(["GET","POST"])
def insoledetails(request):
        inid = request.data["insoleid"]
        with connection.cursor() as cursor:
            #({Insole type, size, totalsensor, product id, date, status, x-cord, y-cord, insole id})
            s = cursor.execute('select insoletype, solesize, noofsensors, insoleaddr, registeredtime, insolestatus, xcoord, ycoord  from insole where insoleid=%s', [inid])
            s1 = cursor.fetchone
        if not s:
            return JsonResponse({'status': 'success','insoletype':s1[0],'size':s1[1], 'totalsensor':s1[2], 'productid':s1[3], 'date':s1[4], 'status': s1[5], 'x-cord': s1[6], 'y-cord':s1[7]})
        else:
            return JsonResponse({'status': 'error'})




###################################################################################admin docs api's#################################################

################################################################################

# get admin details
@api_view(["GET","POST"])
def admindetails(request):
        uid = request.data["userid"]
        with connection.cursor() as cursor:
            #Email, Name, ContactNo, Role, Domain, Admin Id, Date, Organization
            s = cursor.execute('select emailid, username, mobileno, rolename, domain, oname, createddate from userz where userid=%s', [uid])
            s1=cursor.fetchone()
            a = cursor.execute("select userid from userz where domain=%s and usertype=2",[s1[4]])
            adminid =cursor.fetchone()
        if not s:
            return JsonResponse({'status': 'success','Email':s1[0],'Name':s1[1], 'ContactNo':s1[2], 'rolename':s1[3], 'domain':s1[4], 'adminid': adminid[0], 'date': s1[6], 'Organization':s1[5]})
        else:
            return JsonResponse({'status': 'error'})

#block admin
@api_view(["POST"])
def adminblock(request):
    uid = request.data["userid"]
    with connection.cursor() as cursor:
        s = cursor.execute('update userz set blockedstatus=True where userid=%s', [uid])
    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})

#unblock admin
@api_view(["POST"])
def adminunblock(request):
    uid = request.data["userid"]
    with connection.cursor() as cursor:
        s = cursor.execute('update userz set blockedstatus=false where userid=%s', [uid])
    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


# edit admin details
@api_view(["POST"])
def editadmindetails(request):
        uid = request.data["userid"]
        name = request.data["username"]
        cno= request.data["contactno"]
        role = request.data["role"]
        domain = request.data["domain"]
        oname = request.data["organization"]
        with connection.cursor() as cursor:
            #Email, Name, ContactNo, Role, Domain, Admin Id, Date, Organization
            s = cursor.execute('update userz set username=%s, mobileno=%s, rolename=%s, domain=%s, oname=%s  where userid=%s', [name, cno, role,domain, oname, uid])

        if not s:
            return JsonResponse({'status': 'success','Email':s1[0],'Name':s1[1], 'ContactNo':s1[2], 'rolename':s1[3], 'domain':s1[4], 'adminid': adminid[0], 'date': s1[6], 'Organization':s1[5]})
        else:
            return JsonResponse({'status': 'error'})

#delete admin
@api_view(["POST"])
def deleteadmin(request):
    uid = request.data["adminid"]
    with connection.cursor() as cursor:
        s = cursor.execute('update userz set userstatus=False where userid=%s', [uid])
    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


#make an existing user as admin
@api_view(["POST"])
def makeadmin(request):
    uid = request.data["userid"]
    with connection.cursor() as cursor:
        # usertype =1 (for superadmin), =2(admin) =3 for ordinary user
        s1 = cursor.execute(
            'update userz set usertype=2  where userid=%s',[uid])
    if not s1:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})



############################################insole api for admin dashboard ####################
# get insole details
@api_view(["GET","POST"])
def insoledetails(request):
        inid = request.data["insoleid"]
        with connection.cursor() as cursor:
            #({Insole type, size, totalsensor, product id, date, status, x-cord, y-cord, insole id})
            s = cursor.execute('select insoletype, solesize, noofsensors, insoleaddr, registeredtime, insolestatus, xcoord, ycoord  from insole where insoleid=%s', [inid])
            s1 = cursor.fetchone
        if not s:
            return JsonResponse({'status': 'success','insoletype':s1[0],'size':s1[1], 'totalsensor':s1[2], 'productid':s1[3], 'date':s1[4], 'status': s1[5], 'x-cord': s1[6], 'y-cord':s1[7]})
        else:
            return JsonResponse({'status': 'error'})

# block insole of user
@api_view(["POST"])
def blockinsole(request):
        inid = request.data["insoleid"]
        eid = request.data["emailid"]
        with connection.cursor() as cursor:
            s = cursor.execute('update userdevice set blockedstatus=True where emailid=%s and leftinsoleid=%s or rightinsoleid=%s', [eid,inid,inid])
        if not s:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})

# block insole in the insole table
@api_view(["POST"])
def blockinsole(request):
        inid = request.data["insoleid"]
        #eid = request.data["emailid"]
        with connection.cursor() as cursor:
            s = cursor.execute('update insole set blockedstatus=True where insoleid=%s', [inid])
        if not s:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})





# delete insole from insole table
@api_view(["POST"])
def deleteinsole(request):
        inid = request.data["insoleid"]
        eid = request.data["emailid"]
        with connection.cursor() as cursor:
            s = cursor.execute('update insole set insolestatus=True where insoleid=%s', [inid])
        if not s:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})

# edit insole details
@api_view(["POST"])
def editinsole(request):
        inid = request.data["insoleid"]
        itype = request.data["insoletype"]
        size = request.data["insolesize"]
        totsen = request.data["totalsensors"]
        xcord = request.data["xcords"]
        ycord = request.data["ycords"]
        with connection.cursor() as cursor:
            if itype :
                s = cursor.execute('update insole set insoletype=%s where insoleid=%s', [itype,inid])
            if size :
                s = cursor.execute('update insole set solesize=%s where insoleid=%s', [size, inid])
            if totsen:
                s = cursor.execute('update insole set noofsensors=%s where insoleid=%s', [totsen, inid])
            if xcord and ycord:
                s = cursor.execute('UPDATE insole set xcoord= %s, ycoord =%s where insoleid=%s',[xcord,ycord, inid])

        if not s:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})

###########################################hardware mgmt api for admin dashboard ####################
#view hardware details
@api_view(["GET","POST"])
def viewhardwaredetails(request):
    # viewhardware /
    # API
    # retrieve
    # parameter
    # ({Macid, hardwareid, registered date})
        mid = request.data["macid"]
        with connection.cursor() as cursor:
            s = cursor.execute('select macaddress,  values(%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP(0))',[itype,size,totsen,iaddr, xcord,ycord])
        if not s:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})


# delete device(mac+insole combo) from userdevice table
@api_view(["POST"])
def deletehardware(request):
        did = request.data["deviceid"]
        eid = request.data["emailid"]
        with connection.cursor() as cursor:
            s = cursor.execute('update userdevice set devicestatus=True where emailid=%s and udevid=%s', [eid,did])
        if not s:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})

# block device(mac+insole combo) from userdevice table
@api_view(["POST"])
def blockhardware(request):
        did = request.data["deviceid"]
        eid = request.data["emailid"]
        with connection.cursor() as cursor:
            s = cursor.execute('update userdevice set blockedstatus=True where emailid=%s and udevid=%s', [eid,did])
        if not s:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})


#adding new hardware in hardwaremake table
@api_view(["POST"])
def newhardware(request):
    maddr= request.data["macaddr"]
    mname =request.data["manufacturername"]
    #r=random.randint(1, 30)
    #unr= floor(1000 + r * 8999)
    with connection.cursor() as cursor:
     #   p1 = cursor.execute('select count(*) from hardwaredetails where makeID =%s',[unr]);
        p = cursor.execute('INSERT INTO hardwaremake(macaddress,manufacturername) values(%s,%s)', [maddr,mname])
    if not p:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


###########################################licence mgmt api for admin dashboard ####################


# edit no of licences in licence table
@api_view(["POST"])
def editlicence(request):
    eid = request.data["adminemailid"]
    tot = request.data["totallicence"]
    with connection.cursor() as cursor:
        p = cursor.execute('update licences set nooflicence=%s where emailid=%s',[tot,eid])
    if not p:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


# view the details of licence from licence table
@api_view(["GET","POST"])
def viewlicence(request):
    adminid = request.data["adminid"]

    with connection.cursor() as cursor:
        p = cursor.execute('select organizationname, emailid, nooflicence from licences where adminid= %s',[adminid])
        p1 = cursor.fetchone
    if not p:
        return JsonResponse({'status': 'success', 'oname':p1[0], 'emailid':p1[1], 'totallicence':p1[2]})
    else:
        return JsonResponse({'status': 'error'})


# view the details of all admin details
@api_view(["GET","POST"])
def alladmin(request):
    arr2 = []
    with connection.cursor() as cursor:
        cursor.execute('select username,emailid,mobileno,rolename,createddate,userid,domain,oname,blockedstatus from userz where usertype= 3 and userstatus=true')
        p1 = cursor.fetchall()
    for p in p1:
        arr2.append({'status': 'success', 'name':p[0], 'emailid':p[1], 'mobileno':p[2], 'rolename':p[3], 'date':p[4], 'userid':p[5], 'domain':p[6], 'organisation':p[7], 'block':p[8]})

    if not p1:
        return JsonResponse({})
    else:
        return Response(arr2)



@api_view(["GET","POST"])
def adminlistuser(request):
    arr2 = []
    with connection.cursor() as cursor:
        cursor.execute('select username,emailid,mobileno,rolename,createddate,userid,domain,oname,blockedstatus from userz where usertype= 3 and userstatus=true order by username')
        p1 = cursor.fetchall()
    for p in p1:
        arr2.append({'status': 'success', 'name':p[0], 'emailid':p[1], 'mobileno':p[2], 'rolename':p[3], 'date':p[4], 'userid':p[5], 'domain':p[6], 'organisation':p[7], 'block':p[8]})

    if not p1:
        return JsonResponse({})
    else:
        return Response(arr2)




@api_view(["POST"])
def adminregnewpair(request):
    leftmakeid = request.data["leftmakeid"]
    rightmakeid = request.data["rightmakeid"]
    leftinsoleid = request.data["leftinsoleid"]
    rightinsoleid = request.data["rightinsoleid"]
    devicename = request.data["devicename"]
    email = request.data["email"]
    with connection.cursor() as cursor:
        p=cursor.execute("insert into userdevice(registeredtime, leftmakeid, rightmakeid, leftinsoleid, rightinsoleid, devicename,email) values(CURRENT_DATE, %s,%s,%s,%s,%s,%s)", [leftmakeid,rightmakeid,leftinsoleid,rightinsoleid,devicename,email])
    if not p:
         return  JsonResponse({'status':"success"})
    else:
        return JsonResponse({'status': "error"})


@api_view(["POST"])
def adminblockpair(request):
    prodid = request.data["productid"]
    states = request.data["states"]
    st1 = request.data["block"]
    print(st1)
    print(prodid)
    print(states)
    with connection.cursor() as cursor:
       cursor.execute("update userdevice set blockedstatus=%s where udevid=%s", [states,prodid])
       connection.commit()
       count = cursor.rowcount
       print(count, "Record Deleted successfully ")
    if count:
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})


@api_view(["POST"])
def checkpastdata(request):
    ssnid = request.data["sessionid"]

    with connection.cursor() as cursor:
        cursor.execute("select count(*) from sensordata where sessionid=%s", [ssnid])
        cnt = cursor.fetchone()
    if cnt[0] > 0:
        return JsonResponse({'status': 'success', "count": cnt[0], "rows": 1})
    else:
        return JsonResponse({'status': 'success', "count": cnt[0], "rows": 0})


@api_view(["POST"])
def deletepastdata(request):
    ssnid = request.data["sessionId"]
    print(">>>>>>>")
    with connection.cursor() as cursor:
        p = cursor.execute("delete from sensordata where sessionid=%s", [ssnid])
        rc1 = cursor.rowcount
        q = cursor.execute("delete from onlinestride where sessionid=%s", [ssnid])
        rc2 = cursor.rowcount
    if (rc1 >= 0) and (rc2 >= 0):
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})

@api_view(["GET","POST"])
def adminedit(request):
    print("here")
    email = request.data["email"]
    print(email)
    arr2 = []
    with connection.cursor() as cursor:
        cursor.execute('select username,emailid,mobileno,rolename,createddate,userid,domain,oname,blockedstatus from userz where emailid=%s',[email])
        p1 = cursor.fetchall()
    for p in p1:
        arr2.append({'status': 'success', 'name':p[0], 'emailid':p[1], 'mobileno':p[2], 'rolename':p[3], 'date':p[4], 'userid':p[5], 'domain':p[6], 'organisation':p[7], 'block':p[8]})

    if not p1:
        return JsonResponse({})
    else:
        return Response(arr2)








@api_view(["POST"])
def adminupdateuser(request):
    email = request.data["email"]
    name = request.data["name"]
    role = request.data["role"]
    contact = request.data["contact"]

    with connection.cursor() as cursor:
       cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
       cursor.execute("update userz set username=%s,rolename= %s,mobileno=%s where emailid=%s", [name,role,contact,email])
       connection.commit()
       count = cursor.rowcount
       print(count, "Record Updated successfully ")
    if count:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})



@api_view(["GET","POST"])
def infoondevicesbyid(request):
    dname = request.data["devicename"]
    with connection.cursor() as cursor:
        cursor.execute(
            "select macaddress from hardwaremake where makeid = (select leftmakeid from userdevice where udevid =%s ) UNION ALL(select macaddress from hardwaremake where makeid = (select rightmakeid from userdevice where udevid =%s ))",
            [dname, dname])
        macid = cursor.fetchall()
        print(macid)
        m = cursor.rowcount;
    if m == 1:
        lmid = macid[0][0]
        rmid = macid[0][0]
    else:
        lmid = macid[0][0]
        rmid = macid[1][0]  # next tuple's first value

    with connection.cursor() as cursor:
        cursor.execute(
            "select udevid from userdevice where udevid =%s",
            [dname])
        devid = cursor.fetchone()
        m = cursor.rowcount;

    with connection.cursor() as cursor:
        p = cursor.execute(
            "select solesize, noofsensors from insole where insoleid = (select leftinsoleid from userdevice where udevid =%s ) ",
            [dname])
        insoles = cursor.fetchall()
    solesize = insoles[0][0]
    noofsens = insoles[0][1]  # next tuple's first value
    if m:
        return JsonResponse(
            {'status': 'Success', 'leftmac': lmid, 'rightmac': rmid, 'size': solesize, 'totalsensors': str(noofsens), 'devicename':dname, 'deviceid':str(devid[0])})
    else:
        return JsonResponse({'status': 'Error'})



@api_view(["GET","POST"])
def analyticsStridebyAHRS(request):
    vv = 0
    ssnid = request.data["sid"]  # 40500
    stime = request.data["start"]  # 100
    etime = request.data["end"]  # 300
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='L'",
            [stime, etime, ssnid])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    print(p)

    # step 2 - AHRS class
    class AHRS:
        def __init__(self, *args):
            self.SamplePeriod = 1 / 33
            self.Quaternion = [1, 0, 0, 0]
            self.Kp = 2
            self.Ki = 0
            self.KpInit = 200
            self.InitPeriod = 5
            self.q = [1, 0, 0, 0]
            self.IntError = [0, 0, 0]
            self.KpRamped = None
            for i in range(0, len(args), 2):
                if args[i] == 'SamplePeriod':
                    self.SamplePeriod = args[i + 1]
                elif args[i] == 'Quaternion':
                    self.Quaternion = args[i + 1]
                    self.q = self.quaternConj(self.Quaternion)
                elif args[i] == 'Kp':
                    self.Kp = args[i + 1]
                elif args[i] == 'Ki':
                    self.Ki = args[i + 1]
                elif args[i] == 'KpInit':
                    self.KpInit = args[i + 1]
                elif args[i] == 'InitPeriod':
                    self.InitPeriod = args[i + 1]
                else:
                    raise ValueError('Invalid argument')
            self.KpRamped = self.KpInit

        def Update(self, Gyroscope, Accelerometer, Magnetometer):
            raise NotImplementedError('This method is unimplemented')

        def UpdateIMU(self, Gyroscope, Accelerometer):
            if norm(Accelerometer) == 0:
                print('Accelerometer magnitude is zero. Algorithm update aborted.')
                return
            else:
                Accelerometer = Accelerometer / norm(Accelerometer)
            v = [2 * (self.q[1] * self.q[3] - self.q[0] * self.q[2]),
                 2 * (self.q[2] * self.q[3] + self.q[0] * self.q[1]),
                 self.q[0] ** 2 - self.q[1] ** 2 - self.q[2] ** 2 + self.q[3] ** 2]
            error = np.cross(v, Accelerometer)
            self.IntError = self.IntError + error
            Ref = Gyroscope - (self.Kp * error + self.Ki * self.IntError)
            pDot = 0.5 * self.quaternProd(self.q, [0, float(Ref[0]), float(Ref[1]), float(Ref[2])])
            self.q = self.q + pDot * self.SamplePeriod
            self.q = self.q / norm(self.q)
            self.Quaternion = self.quaternConj(self.q)

        def quaternProd(self, a, b):
            # Ensure a and b are lists or arrays
            a = np.array(a)
            b = np.array(b)
            ab = np.array([
                a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
                a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
                a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
                a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]
            ])
            return ab

        def quaternConj(self, q):
            qConj = [q[0], -q[1], -q[2], -q[3]]
            return qConj

    # step3

    def quaternProd(a, b):
        ab = [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
              a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
              a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
              a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]]
        print(ab)
        return ab

    def quaternConj(q):
        qConj = [q[0], -q[1], -q[2], -q[3]]
        # print(qConj)
        return qConj

    def quaternRotate(v, q):
        row, col = v.shape
        v0XYZ = quaternProd(quaternProd(q, np.hstack((np.zeros((row, 1)), v))), quaternConj(q))
        v = np.array(v0XYZ)[:, 1:4]
        return v

    def extract_ranges(t, heel, toe, threshold=700):
        # Detect peaks using the specified method
        peaks = []
        print("heel.....................", heel)
        for i in range(1, len(heel) - 1):  # 1 to last index
            print(heel[i - 1], "  ", heel[i], "  ", heel[i + 1], "  ", threshold)
            if heel[i - 1] < heel[i] >= heel[i + 1] and int(heel[i]) > threshold:
                print(i, "   ")
                peaks.append(i)

        print("peaks...................", peaks)
        clustered_peaks = []
        current_cluster = [peaks[0]]
        for i in range(1, len(peaks)):
            if peaks[i] - peaks[i - 1] <= 3:
                current_cluster.append(peaks[i])
            else:
                # Calculate the median of the current cluster and store it
                clustered_peaks.append(int(np.median(current_cluster)))
                current_cluster = [peaks[i]]

        # Include the last cluster
        # clustered_peaks.append(int(np.median(current_cluster)))

        # Get corresponding time values for peaks
        peak_times = [t[i] for i in clustered_peaks]

        # Store first_intersection_time values in an array
        first_intersection_times = []
        samples_for_first_intersection = []
        indices_for_first_intersection = []

        # Plot the original signal and the identified peaks
        plt.plot(t, heel, label='Heel Pressure')
        plt.plot(t, toe, label='Toe Pressure')
        plt.plot(peak_times, [heel[i] for i in clustered_peaks], 'gx')

        # Plot segments between intersections
        for i in range(len(clustered_peaks)):
            if i < len(clustered_peaks) - 1:
                start_index = clustered_peaks[i]
                end_index = clustered_peaks[i + 1]

                # Find the first intersection point between 'heel' and 'toe' signals
                intersections = np.where(np.diff(np.sign(heel[start_index:end_index] - toe[start_index:end_index])))[0]

                if len(intersections) > 0:
                    # Get the time value of the first intersection
                    first_intersection_time = t[start_index:end_index][intersections[0]]
                    first_intersection_times.append(first_intersection_time)

                    # Store corresponding samples and indices
                    sample_index = start_index + intersections[0]
                    samples_for_first_intersection.append(heel[sample_index])
                    indices_for_first_intersection.append(sample_index)

                    # Plot the segment between consecutive intersections
                    plt.axvline(first_intersection_time, color='red', linestyle='--')

        # Store start time, end time, and first intersection times in a single array
        time_array = [t[0]] + first_intersection_times + [t[-1]]

        indices_for_first_intersection = [0] + indices_for_first_intersection + [len(heel) - 1]

        # Print the array of start_time, end_time, first_intersection_times, and corresponding samples and indices
        print("Stride Time:", time_array)
        print("Samples:", samples_for_first_intersection)
        print("Sample Indices:", indices_for_first_intersection)

        return indices_for_first_intersection

    # Load data from CSV file
    # aa = np.genfromtxt('13_12_fsr_L4.csv', delimiter=',')
    aa = pd.DataFrame(p)
    print(aa)
    heel = aa.iloc[:, 2]
    print("heel.....................", heel)
    toe = aa.iloc[:, 1]
    print("toe....................", toe)

    t = aa.iloc[:, 0]
    posX = 0
    # Extract ranges using the function
    ranges = extract_ranges(t, heel, toe)

    # Perform processing for each range
    for i in range(len(ranges) - 1):
        start_index = ranges[i]
        end_index = ranges[i + 1]

        # Extract data for the current range
        accX = aa[start_index:end_index, 3]
        accY = aa[start_index:end_index, 4]
        accZ = aa[start_index:end_index, 5]
        gyrX = aa[start_index:end_index, 6]
        gyrY = aa[start_index:end_index, 7]
        gyrZ = aa[start_index:end_index, 8]
        t = aa[start_index:end_index, 0]

        Fs = 36
        L1 = len(t)
        time = np.arange(L1)

        # step4

        acc_mag = np.sqrt(accX ** 2 + accY ** 2 + accZ ** 2)

        Fs = 36
        # Detect stationary periods
        sample_period = 1 / 36
        filt_cutoff = 0.0001

        # High-pass filter accelerometer data
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'high')
        acc_magFilt = filtfilt(b, a, acc_mag)
        acc_magFilt = np.abs(acc_magFilt)

        # Low-pass filter accelerometer data
        filt_cutoff = 5
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'low')
        acc_magFilt = filtfilt(b, a, acc_magFilt)

        # Threshold detection
        stationary = acc_magFilt < 0.04

        # step 5
        # Compute orientation
        quat = np.zeros((len(time), 4))
        AHRSalgorithm = AHRS('SamplePeriod', 1 / Fs, 'Kp', 1, 'KpInit', 1)

        # Initial convergence
        initPeriod = 2
        indexSel = np.arange(np.argmax(time > (time[0] + initPeriod)))
        for i in range(2000):
            AHRSalgorithm.UpdateIMU([0, 0, 0],
                                    [np.mean(accX[indexSel]), np.mean(accY[indexSel]), np.mean(accZ[indexSel])])

        # For all data
        for t in range(len(time)):
            if stationary[t]:
                AHRSalgorithm.Kp = 0.5
            else:
                AHRSalgorithm.Kp = 1
            AHRSalgorithm.UpdateIMU(np.deg2rad([gyrX[t], gyrY[t], gyrZ[t]]), [accX[t], accY[t], accZ[t]])
            quat[t, :] = AHRSalgorithm.Quaternion
            # print((quat[t,:]))

        # Compute translational accelerations
        # Rotate accelerations from sensor frame to Earth frame
        # Function to rotate vector v by quaternion q
        def quatern_conj(q):
            if q.ndim == 1:
                return np.array([q[0], -q[1], -q[2], -q[3]])
            elif q.ndim == 2:
                return np.array([q[:, 0], -q[:, 1], -q[:, 2], -q[:, 3]]).T
            else:
                raise ValueError("Invalid dimension for quaternion array")

        def quatern_rotate(v, q):
            q_conj = quatern_conj(q)
            v_quat = np.concatenate(([0], v))
            result_quat = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)
            return result_quat[1:]

        def quaternion_multiply(q1, q2):
            w1, x1, y1, z1 = q1
            w2, x2, y2, z2 = q2
            w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
            x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
            y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
            z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
            return np.array([w, x, y, z])

        # step6

        # compute transilational acceleration

        acc1 = np.column_stack((accX, accY, accZ))
        quat_conj = quatern_conj(quat)
        # print(quat_conj)

        acc2 = np.array([quatern_rotate(row, quat_conj[i, :]) for i, row in enumerate(acc1)])
        # print(acc2 )

        acc = acc2 * 9.8

        acc[:, 2] -= 9.8

        time = np.array(time)

        # step 7

        # Integrate acceleration to yield velocity
        vel = np.zeros(acc.shape)
        for t in range(1, vel.shape[0]):
            vel[t, :] = vel[t - 1, :] + acc[t, :] * sample_period
            if stationary[t] == 1:
                vel[t, :] = [0, 0, 0]  # apply ZUPT update when foot stationary

        # we consider only x and y axis
        # Plot translational velocity
        plt.figure(figsize=(9, 3))
        plt.plot(time, vel[:, 0], 'r')
        plt.plot(time, vel[:, 1], 'g')

        # plt.title('Velocity')
        # plt.xlabel('Time (ms)')
        # plt.ylabel('Velocity (m/s)')
        # plt.legend(['X', 'Y', 'Z'])
        # plt.show()

        # Compute translational position
        # Integrate velocity to yield position
        pos = np.zeros(vel.shape)
        for t in range(1, pos.shape[0]):
            pos[t, :] = pos[t - 1, :] + vel[t, :] * sample_period
        vv = 0
        # Plot translational position
        # y axis for ward, backward movement (new insole)
        # x axis for up/down
        # mahipal old data which uses x(forward/backward)

        # plt.figure(figsize=(9, 6))
        # plt.plot(time, pos[:, 0], 'r')
        # #plt.plot(time, pos[:, 1], 'g')

        # plt.title('Position')
        # plt.xlabel('Time (ms)')
        # plt.ylabel('Position (m)')
        # plt.legend(['X', 'Y', 'Z'])
        # plt.show()
        posX = np.abs(pos[:, 0])
        print(np.max(posX))
        vv = np.max(posX)
    return Response("1")


@api_view(["GET","POST"])
def stridelengthestd(request):
    ssnid = request.data["sid"]  # 40500
    stime = request.data["start"]  # 100
    etime = request.data["end"]  # 300
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='L'",
            [stime, etime, ssnid])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    print(p)

    # lambda function for finding out delta time between two consecutive samples
    find_diff = lambda x: x.iloc[1] - x.iloc[0]

    # ---------------------------------Stridewise length estimation function---------------------
    # Estimate the length stridewise
    def compute_stride_length(data_frame, start_time, end_time):
        imu_data_sub_f = data_frame.query('t>=@start_time & t<=@end_time')
        imu_data_sub_f = imu_data_sub_f.reset_index()
        # gravity
        c_g = 9.8  # if accel an integer multiple of 9.8 m/s2
        aX_raw = c_g * imu_data_sub_f["aX"]
        aY_raw = c_g * imu_data_sub_f["aY"]
        aZ_raw = c_g * imu_data_sub_f["aZ"]

        # Velocity from unfiltered data
        imu_data_sub_f["vX_raw"] = inte.cumtrapz(aX_raw, imu_data_sub_f["t"], initial=0)
        imu_data_sub_f["vY_raw"] = inte.cumtrapz(aY_raw, imu_data_sub_f["t"], initial=0)
        imu_data_sub_f["vZ_raw"] = inte.cumtrapz(aZ_raw, imu_data_sub_f["t"], initial=0)
        # ---------------------------------Position Estimation ---------------------------------------
        # cumtrapz raw
        imu_data_sub_f["pX_raw"] = inte.cumtrapz(imu_data_sub_f["vX_raw"], imu_data_sub_f["t"], initial=0)
        imu_data_sub_f["pY_raw"] = inte.cumtrapz(imu_data_sub_f["vY_raw"], imu_data_sub_f["t"], initial=0)
        imu_data_sub_f["pZ_raw"] = inte.cumtrapz(imu_data_sub_f["vZ_raw"], imu_data_sub_f["t"], initial=0)

        return imu_data_sub_f["pY_raw"].iloc[-1] - imu_data_sub_f["pY_raw"].iloc[0]

    # data_filename = "data_source/DF_SZ_10_L_M_f7_7b_a4_d2_33_70_T_1704281653349.csv" #phyphox_at_rest.csv
    # data_filename = "data_source/DF_SZ_10_L_M_f7_7b_a4_d2_33_70_T_1704281653349.csv" #phyphox_at_rest.csv
    # imu_data = pd.read_csv(data_filename)
    print("processing")
    imu_data = pd.DataFrame(p)
    imu_data['t'] = imu_data['tms'] / 1000  # For left data set testing
    imu_data['tms'] = imu_data['tms'] - imu_data['tms'][0]  # Re-adjusting the time to start from 0
    imu_data['t'] = imu_data['t'] - imu_data['t'][0]  # Re-adjusting the time to start from 0
    # Finding Heel Difference between two consecutive data points
    print("here.................")
    imu_data["Heel"] = imu_data.loc[:, ["s4", "s5"]].mean(axis=1)
    imu_data['diff_Heel'] = imu_data['Heel'].diff(-1)
    # ---------------------------------Processing----------------------------------------------------
    # First
    imu_data_step_trans_first = imu_data.groupby(["sC"])[["tms", "t"]].first()
    imu_data_step_trans_first = imu_data_step_trans_first.reset_index()
    # Last
    imu_data_step_trans_last = imu_data.groupby(["sC"])[["tms", "t"]].last()
    imu_data_step_trans_last = imu_data_step_trans_last.reset_index()
    # concatenating
    imu_data_step_trans = imu_data_step_trans_first
    imu_data_step_trans['t_l'] = imu_data_step_trans_last['t']
    # Finding length from step 2 to final
    # imu_data_step_trans['length'] = imu_data_step_trans.apply(lambda x: compute_stride_length(imu_data,x['t'],x['t_l']),axis=1)
    imu_data_step_trans['length'] = abs(
        imu_data_step_trans.apply(lambda x: compute_stride_length(imu_data, x['t'], x['t_l']), axis=1))
    # Finding length till step 2
    imu_data_t_h_tr = imu_data.query('diff_Heel < -150 & sC==0')
    imu_data_t_h_tr_gr_f = imu_data_t_h_tr.groupby("sC").first().reset_index()
    str_time = imu_data_t_h_tr_gr_f['t'].values[0]
    stp_time = imu_data_step_trans.iloc[1]['t']
    # total_length = round(imu_data_step_trans.iloc[1:-1]['length'].sum() + compute_stride_length(imu_data,str_time,stp_time),2)
    totlen = round(
        imu_data_step_trans.iloc[1:-1]['length'].sum() + abs(compute_stride_length(imu_data, str_time, stp_time)), 2)
    # printing the length
    print("Stride wise data")
    print(imu_data_step_trans)
    print("")
    print(f"Total distance except first and last = {round(imu_data_step_trans.iloc[1:-1]['length'].sum(), 2)} m")
    print(f"Total distance {totlen}")
    return JsonResponse({'stridelength_total': totlen})


##Newly Added

@api_view(["GET","POST"])
def getcoachdetails(request):
    organisationId = request.data["organisationId"]
    arr2=[]
    with connection.cursor() as cursor:
       cursor.execute("select emailid,mobileno,username,createddate,blockedstatus,userid from userz where organizationid =%s and usertype = 3", [organisationId])
       count = cursor.fetchall()
       for c in count:
           arr2.append({"email":c[0], "mobile":c[1], "name":c[2], "date":c[3], "status":c[4], "id": c[5]})
    print(" next .....",arr2)
    #time, name, age, weight, gender, uuid
    if count :
        return Response(arr2);
    else:
        return JsonResponse({'status': 'Error'})

@api_view(["GET","POST"])
def orgdevdetails(request):
        email = request.data["email"]
        arr2 = []
        with connection.cursor() as cursor:
            cursor.execute(
                "select registeredtime, udevid ,devicename, samplingrate, devactivestatus, blockedstatus, email from userdevice where orgemail=%s order by udevid asc",
                [email])
            count = cursor.fetchall()

            print(count)
        if count :
            for c in count:
                    arr2.append({"time": c[0], "deviceid": c[1], "devicename": c[2], "samplingrate": c[3], "devactivestatus": c[4], "blockedstatus": c[5], "email": c[6]         })
            return Response(arr2)

        else :
            return JsonResponse({'status': 'Error'})


@api_view(["POST"])
def orgdeviceregister(request):
    email = request.data["email"]
    prodid = request.data["productid"]

    with connection.cursor() as cursor:
       cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
       cursor.execute("update userdevice set email = %s,devactivestatus=false where udevid=%s", [email,prodid])
       connection.commit()
       count = cursor.rowcount
       print(count, "Record Updated successfully ")
    if count:
        return JsonResponse({'status': 'Success'})
    else:
        return JsonResponse({'status': 'Error'})




@api_view(["GET","POST"])
def infoondevicesupdated(request):
    dname = request.data["devicename"]
    with connection.cursor() as cursor:
        cursor.execute(
            "select macaddress from hardwaremake where makeid = (select leftmakeid from userdevice where udevid =%s ) UNION (select macaddress from hardwaremake where makeid = (select rightmakeid from userdevice where udevid =%s ))",
            [dname, dname])
        macid = cursor.fetchall()
        m = cursor.rowcount;
    if m == 1:
        lmid = macid[0][0]
        rmid = macid[0][0]
    else:
        lmid = macid[0][0]
        rmid = macid[1][0]  # next tuple's first value

    with connection.cursor() as cursor:
        cursor.execute(
            "select udevid from userdevice where udevid =%s",
            [dname])
        devid = cursor.fetchone()
        m = cursor.rowcount;

    with connection.cursor() as cursor:
        p = cursor.execute(
            "select solesize, noofsensors from insole where insoleid = (select leftinsoleid from userdevice where udevid =%s ) ",
            [dname])
        insoles = cursor.fetchall()
    solesize = insoles[0][0]
    noofsens = insoles[0][1]  # next tuple's first value
    if m:
        return JsonResponse(
            {'status': 'Success', 'leftmac': lmid, 'rightmac': rmid, 'size': solesize, 'totalsensors': str(noofsens), 'devicename':dname, 'deviceid':str(devid[0])})
    else:
        return JsonResponse({'status': 'Error'})



@api_view(["GET","POST"])
def updatedlistofdevices(request):
    email = request.data["email"]
    arr2 = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT devicename,udevid FROM USERDEVICE WHERE email =%s and devactivestatus=true and blockedstatus = false order by devicename asc",[email] )
        count1 = cursor.rowcount
        dl = cursor.fetchall()
        print(count1, "Players  there ")
    for c in dl:
            arr2.append(
                {"devicename": c[0],"deviceid": c[1]})
    if count1:
           return Response(arr2)
    else:
           return Response(arr2)




@api_view(["POST"])
def userblock(request):
    uid = request.data["userid"]
    block = request.data["block"]
    print(uid)
    print(block)
    with connection.cursor() as cursor:
        s = cursor.execute('update userz set blockedstatus=%s where userid=%s', [block,uid])

    if not s:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


@api_view(["GET","POST"])
def getactivesession(request):
    email = request.data["email"]
    arr2 = []
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT sessionid,deviceid,type from activesession WHERE email =%s and status=%s order by sid desc limit 1",[email,'0'] )
            dl = cursor.fetchone()
        except Exception as e:
            print(e)
    if dl:
           return JsonResponse({"sessionid":dl[0],"deviceid":dl[1],"type":dl[2],"status":"success"})
    else:
           return JsonResponse({"status":"error"})





@api_view(["GET","POST"])
def angleimuright(request):
    ssnid = request.data["sid"]  # 40500    ssnid 1000  reshmi
    stime = request.data["start"]  # 100    start 50000        73ms
    etime = request.data["end"]  # 300      end 53000          3003ms
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='R'",
            [stime, etime, ssnid])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    print(p)
    imu_data = pd.DataFrame(p)
    accel_x = imu_data.iloc[:, 0] # only when mahipal data is used
    accel_y = imu_data.iloc[:, 1]  # only when mahipal data is used
    accel_z = imu_data.iloc[:, 2]  # only when mahipal data is used
    gyro_x = imu_data.iloc[:, 3]   # only when mahipal data is used
    gyro_y = imu_data.iloc[:, 4]   # only when mahipal data is used
    gyro_z = imu_data.iloc[:, 5]   # only when mahipal data is used
    time = imu_data.iloc[:, 6]
    # Design filter parameters
    lowcut = 5  # Cutoff frequency for low-pass filter (Hz)
    highcut = 0.001  # Cutoff frequency for high-pass filter (Hz)
    order = 2  # Filter order
    Fs = 38  # only when mahipal data is used 57

    # Apply filters to accelerometer data
    def apply_lpf(data, cutoff, fs, order):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        print(nyquist, normal_cutoff)
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        print("b,a", b, a)
        return filtfilt(b, a, data)

    # Apply filters to gyroscope data
    def apply_hpf(data, cutoff, fs, order):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        print(nyquist, normal_cutoff)
        b, a = butter(order, normal_cutoff, btype='high', analog=False)

        return filtfilt(b, a, data)

    # Apply filters to accelerometer and gyroscope data
    filtered_accel_x = apply_lpf(accel_x, lowcut, Fs, order)
    filtered_accel_y = apply_lpf(accel_y, lowcut, Fs, order)
    filtered_accel_z = apply_lpf(accel_z, lowcut, Fs, order)

    filtered_gyro_x = apply_hpf(gyro_x, highcut, Fs, order)
    filtered_gyro_y = apply_hpf(gyro_y, highcut, Fs, order)
    filtered_gyro_z = apply_hpf(gyro_z, highcut, Fs, order)

    # Sensor fusion using complementary filter
    alpha = 0.9
    Fs = 38  #mahipal its 57
    dt = 1 / Fs

    # Initialize variables
    roll = np.zeros_like(time)
    pitch = np.zeros_like(time)
    yaw = np.zeros_like(time)
    angleout = []
    # Perform sensor fusion using complementary filter with filtered data
    for i in range(1, len(time)):
        # Calculate roll, pitch from accelerometer data and yaw from gyroscope data
        roll[i] = alpha * (roll[i - 1] + np.degrees(filtered_gyro_y[i]) * dt) + (1 - alpha) * np.degrees(
            np.arctan2(filtered_accel_z[i], filtered_accel_x[i]))
        pitch[i] = alpha * (pitch[i - 1] - np.degrees(filtered_gyro_z[i]) * dt) + (1 - alpha) * np.degrees(
            np.arctan2(-filtered_accel_y[i], np.sqrt(filtered_accel_z[i] ** 2 + filtered_accel_x[i] ** 2)))
        yaw[i] = alpha * (yaw[i - 1] + np.degrees(filtered_gyro_x[i]) * dt)
        angleout.append({"roll": roll[i], "pitch": pitch[i], "yaw": yaw[i], "time": time[i]})
    print(angleout)
    # Plot roll, pitch, yaw
    # plt.figure()
    # plt.subplot(3, 1, 1)
    # plt.plot(time, roll)
    # plt.xlabel('Time')
    # plt.ylabel('Roll (degrees)')
    # plt.subplot(3, 1, 2)
    # plt.plot(time, pitch)
    # plt.xlabel('Time')
    # plt.ylabel('Pitch (degrees)')
    # plt.subplot(3, 1, 3)
    # plt.plot(time, yaw)
    # plt.xlabel('Time')
    # plt.ylabel('Yaw (degrees)')
    # plt.show()
    # return time, roll, pitch, yaw
    return Response(angleout)


@api_view(["GET","POST"])
def angleimuleft(request):
    ssnid = request.data["sid"]  # 40500    ssnid 1000  reshmi
    stime = request.data["start"]  # 100    start 50000        73ms
    etime = request.data["end"]  # 300      end 53000          3003ms
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT s6,s7,s8,s9,s10,s11,capturedtime from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='L'",
            [stime, etime, ssnid])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    """    
    print(p)
    imu_data = pd.DataFrame(p)
    accel_x = imu_data.iloc[:, 0]  # only when mahipal data is used
    accel_y = imu_data.iloc[:, 1]  # only when mahipal data is used
    accel_z = imu_data.iloc[:, 2]  # only when mahipal data is used
    gyro_x = imu_data.iloc[:, 3]  # only when mahipal data is used
    gyro_y = imu_data.iloc[:, 4]  # only when mahipal data is used
    gyro_z = imu_data.iloc[:, 5]  # only when mahipal data is used
    time = imu_data.iloc[:, 6]
    # Design filter parameters
    lowcut = 5  # Cutoff frequency for low-pass filter (Hz)
    highcut = 0.001  # Cutoff frequency for high-pass filter (Hz)
    order = 2  # Filter order
    Fs = 38  # only when mahipal data is used 57

    # Apply filters to accelerometer data
    def apply_lpf(data, cutoff, fs, order):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        print(nyquist, normal_cutoff)
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        print("b,a", b, a)
        return filtfilt(b, a, data)

    # Apply filters to gyroscope data
    def apply_hpf(data, cutoff, fs, order):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        print(nyquist, normal_cutoff)
        b, a = butter(order, normal_cutoff, btype='high', analog=False)

        return filtfilt(b, a, data)

    # Apply filters to accelerometer and gyroscope data
    filtered_accel_x = apply_lpf(accel_x, lowcut, Fs, order)
    filtered_accel_y = apply_lpf(accel_y, lowcut, Fs, order)
    filtered_accel_z = apply_lpf(accel_z, lowcut, Fs, order)

    filtered_gyro_x = apply_hpf(gyro_x, highcut, Fs, order)
    filtered_gyro_y = apply_hpf(gyro_y, highcut, Fs, order)
    filtered_gyro_z = apply_hpf(gyro_z, highcut, Fs, order)

    # Sensor fusion using complementary filter
    alpha = 0.9
    Fs = 38 # mahipal its 57
    dt = 1 / Fs

    # Initialize variables
    roll = np.zeros_like(time)
    pitch = np.zeros_like(time)
    yaw = np.zeros_like(time)
    angleout = []
    difftime=abs(etime-stime)
    dt=0
    # Perform sensor fusion using complementary filter with filtered data
    for i in range(1, len(time)):
        # Calculate roll, pitch from accelerometer data and yaw from gyroscope data
        roll[i] = alpha * (roll[i - 1] + np.degrees(filtered_gyro_y[i]) * dt) + (1 - alpha) * np.degrees(
            np.arctan2(filtered_accel_z[i], filtered_accel_x[i]))
        pitch[i] = alpha * (pitch[i - 1] - np.degrees(filtered_gyro_z[i]) * dt) + (1 - alpha) * np.degrees(
            np.arctan2(-filtered_accel_y[i], np.sqrt(filtered_accel_z[i] ** 2 + filtered_accel_x[i] ** 2)))
        yaw[i] = alpha * (yaw[i - 1] + np.degrees(filtered_gyro_x[i]) * dt)
        dt = dt+250
        angleout.append({"roll": roll[i], "pitch": pitch[i], "yaw": yaw[i], "time": time[i]})
    print(angleout)
    # Plot roll, pitch, yaw
    # plt.figure()
    # plt.subplot(3, 1, 1)
    # plt.plot(time, roll)
    # plt.xlabel('Time')
    # plt.ylabel('Roll (degrees)')
    # plt.subplot(3, 1, 2)
    # plt.plot(time, pitch)
    # plt.xlabel('Time')
    # plt.ylabel('Pitch (degrees)')
    # plt.subplot(3, 1, 3)
    # plt.plot(time, yaw)
    # plt.xlabel('Time')
    # plt.ylabel('Yaw (degrees)')
    # plt.show()
    # return time, roll, pitch, yaw
    return Response(angleout)
    """
    print(p)
    imu_data = pd.DataFrame(p)
    accel_x = imu_data.iloc[:, 0]  # only when mahipal data is used
    accel_y = imu_data.iloc[:, 1]  # only when mahipal data is used
    accel_z = imu_data.iloc[:, 2]  # only when mahipal data is used
    gyro_x = imu_data.iloc[:, 3]  # only when mahipal data is used
    gyro_y = imu_data.iloc[:, 4]  # only when mahipal data is used
    gyro_z = imu_data.iloc[:, 5]  # only when mahipal data is used
    time = imu_data.iloc[:, 6]
    # Design filter parameters
    lowcut = 5  # Cutoff frequency for low-pass filter (Hz)
    highcut = 0.001  # Cutoff frequency for high-pass filter (Hz)
    order = 2  # Filter order
    Fs = 38  # only when mahipal data is used 57

    # Apply filters to accelerometer data
    def apply_lpf(data, cutoff, fs, order):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        print(nyquist, normal_cutoff)
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        print("b,a", b, a)
        return filtfilt(b, a, data)

    # Apply filters to gyroscope data
    def apply_hpf(data, cutoff, fs, order):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        print(nyquist, normal_cutoff)
        b, a = butter(order, normal_cutoff, btype='high', analog=False)

        return filtfilt(b, a, data)

    # Apply filters to accelerometer and gyroscope data
    filtered_accel_x = apply_lpf(accel_x, lowcut, Fs, order)
    filtered_accel_y = apply_lpf(accel_y, lowcut, Fs, order)
    filtered_accel_z = apply_lpf(accel_z, lowcut, Fs, order)

    filtered_gyro_x = apply_hpf(gyro_x, highcut, Fs, order)
    filtered_gyro_y = apply_hpf(gyro_y, highcut, Fs, order)
    filtered_gyro_z = apply_hpf(gyro_z, highcut, Fs, order)

    # Sensor fusion using complementary filter
    alpha = 0.9
    Fs = 38  # mahipal its 57
    dt = 1 / Fs

    # Initialize variables
    roll = np.zeros_like(time)
    pitch = np.zeros_like(time)
    yaw = np.zeros_like(time)
    angleout = []
    # Perform sensor fusion using complementary filter with filtered data
    for i in range(1, len(time)):
        # Calculate roll, pitch from accelerometer data and yaw from gyroscope data
        roll[i] = alpha * (roll[i - 1] + np.degrees(filtered_gyro_y[i]) * dt) + (1 - alpha) * np.degrees(
            np.arctan2(filtered_accel_z[i], filtered_accel_x[i]))
        pitch[i] = alpha * (pitch[i - 1] - np.degrees(filtered_gyro_z[i]) * dt) + (1 - alpha) * np.degrees(
            np.arctan2(-filtered_accel_y[i], np.sqrt(filtered_accel_z[i] ** 2 + filtered_accel_x[i] ** 2)))
        yaw[i] = alpha * (yaw[i - 1] + np.degrees(filtered_gyro_x[i]) * dt)
        angleout.append({"roll": roll[i], "pitch": pitch[i], "yaw": yaw[i], "time": time[i]})
    print(angleout)
    # Plot roll, pitch, yaw
    # plt.figure()
    # plt.subplot(3, 1, 1)
    # plt.plot(time, roll)
    # plt.xlabel('Time')
    # plt.ylabel('Roll (degrees)')
    # plt.subplot(3, 1, 2)
    # plt.plot(time, pitch)
    # plt.xlabel('Time')
    # plt.ylabel('Pitch (degrees)')
    # plt.subplot(3, 1, 3)
    # plt.plot(time, yaw)
    # plt.xlabel('Time')
    # plt.ylabel('Yaw (degrees)')
    # plt.show()
    # return time, roll, pitch, yaw
    return Response(angleout)


####================================================================================================##
def quaternProd(a, b):
    ab = [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
          a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
          a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
          a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]]
    # print(ab)
    return ab


def quaternConj(q):
    qConj = [q[0], -q[1], -q[2], -q[3]]
    # print(qConj)
    return qConj


def quaternRotate(v, q):
    row, col = v.shape
    v0XYZ = quaternProd(quaternProd(q, np.hstack((np.zeros((row, 1)), v))), quaternConj(q))
    v = np.array(v0XYZ)[:, 1:4]
    return v


def extract_ranges(t, heel, toe, threshold=750):
    print("len of t", len(t))
    print("len of heel", len(heel))
    print("len of toe", len(toe))
    heel = np.array(heel)
    toe = np.array(toe)
    # Detect peaks using the specified method
    peaks = []
    for i in range(1, len(heel) - 1):  # 1 to last index
        if heel[i - 1] < heel[i] >= heel[i + 1] and heel[i] > threshold:
            peaks.append(i)
            # prev value less than present it is grator than or equal to next and grater than threshould

    # Identify clusters of nearby peaks
    clustered_peaks = []
    current_cluster = [peaks[0]]
    for i in range(1, len(peaks)):
        if peaks[i] - peaks[i - 1] <= 5:
            current_cluster.append(peaks[i])
        else:
            # Calculate the median of the current cluster and store it
            clustered_peaks.append(int(np.median(current_cluster)))
            current_cluster = [peaks[i]]

    # Get corresponding time values for peaks
    peak_times = [t[i] for i in clustered_peaks]

    # Store first_intersection_time values in an array
    first_intersection_times = []
    samples_for_first_intersection = []
    indices_for_first_intersection = []

    # Plot the original signal and the identified peaks
    # plt.plot(t, heel, label='Heel Pressure')
    # plt.plot(t, toe, label='Toe Pressure')
    # plt.plot(peak_times, [heel[i] for i in clustered_peaks], 'gx')

    # Plot segments between intersections
    for i in range(len(clustered_peaks)):
        if i < len(clustered_peaks) - 1:
            start_index = clustered_peaks[i]
            end_index = clustered_peaks[i + 1]

            # Find the first intersection point between 'heel' and 'toe' signals
            # intersections = np.where(np.diff(np.sign(heel[start_index:end_index] - toe[start_index:end_index])))[0]
            heel_array = np.array(heel[start_index:end_index])
            toe_array = np.array(toe[start_index:end_index])

            intersections = np.where(np.diff(np.sign(heel_array - toe_array)))[0]

            if len(intersections) > 0:
                # Get the time value of the first intersection
                first_intersection_time = t[start_index:end_index][intersections[0]]
                first_intersection_times.append(first_intersection_time)

                # Store corresponding samples and indices
                sample_index = start_index + intersections[0]
                samples_for_first_intersection.append(heel[sample_index])
                indices_for_first_intersection.append(sample_index)

                # Plot the segment between consecutive intersections
                # plt.axvline(first_intersection_time, color='red', linestyle='--')

    # Store start time, end time, and first intersection times in a single array
    print("1st element", t[0],"last element by using len()",t[(len(t)-1)])
    # time_array = [t[0]] + first_intersection_times + [t[-1]]
    time_array = [t[0]] + first_intersection_times + [t[(len(t)-1)]]

    indices_for_first_intersection = [0] + indices_for_first_intersection + [len(heel) - 1]

    return indices_for_first_intersection

# Compute translational accelerations
# Rotate accelerations from sensor frame to Earth frame
# Function to rotate vector v by quaternion q
def quatern_conj(q):
    if q.ndim == 1:
        return np.array([q[0], -q[1], -q[2], -q[3]])
    elif q.ndim == 2:
        return np.array([q[:, 0], -q[:, 1], -q[:, 2], -q[:, 3]]).T
    else:
        raise ValueError("Invalid dimension for quaternion array")


def quatern_rotate(v, q):
    q_conj = quatern_conj(q)
    v_quat = np.concatenate(([0], v))
    result_quat = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)
    print(result_quat)
    return result_quat[1:]


def quaternion_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return np.array([w, x, y, z])


# step 2 - AHRS class
class AHRS:
    def __init__(self, *args):
        self.SamplePeriod = 1 / 33
        self.Quaternion = [1, 0, 0, 0]
        self.Kp = 2
        self.Ki = 0
        self.KpInit = 200
        self.InitPeriod = 5
        self.q = [1, 0, 0, 0]
        self.IntError = [0, 0, 0]
        self.KpRamped = None
        for i in range(0, len(args), 2):
            if args[i] == 'SamplePeriod':
                self.SamplePeriod = args[i + 1]
            elif args[i] == 'Quaternion':
                self.Quaternion = args[i + 1]
                self.q = self.quaternConj(self.Quaternion)
            elif args[i] == 'Kp':
                self.Kp = args[i + 1]
            elif args[i] == 'Ki':
                self.Ki = args[i + 1]
            elif args[i] == 'KpInit':
                self.KpInit = args[i + 1]
            elif args[i] == 'InitPeriod':
                self.InitPeriod = args[i + 1]
            else:
                raise ValueError('Invalid argument')
        self.KpRamped = self.KpInit

    def Update(self, Gyroscope, Accelerometer, Magnetometer):
        raise NotImplementedError('This method is unimplemented')

    def UpdateIMU(self, Gyroscope, Accelerometer):
        if norm(Accelerometer) == 0:
            print('Accelerometer magnitude is zero. Algorithm update aborted.')
            return
        else:
            Accelerometer = Accelerometer / norm(Accelerometer)
        v = [2 * (self.q[1] * self.q[3] - self.q[0] * self.q[2]),
             2 * (self.q[2] * self.q[3] + self.q[0] * self.q[1]),
             self.q[0] ** 2 - self.q[1] ** 2 - self.q[2] ** 2 + self.q[3] ** 2]
        error = np.cross(v, Accelerometer)
        self.IntError = self.IntError + error
        Ref = Gyroscope - (self.Kp * error + self.Ki * self.IntError)
        pDot = 0.5 * self.quaternProd(self.q, [0, float(Ref[0]), float(Ref[1]), float(Ref[2])])
        self.q = self.q + pDot * self.SamplePeriod
        self.q = self.q / norm(self.q)
        self.Quaternion = self.quaternConj(self.q)

    def quaternProd(self, a, b):
        # Ensure a and b are lists or arrays
        a = np.array(a)
        b = np.array(b)

        ab = np.array([
            a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
            a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
            a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
            a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]
        ])
        print("quaterProd.....in AHRS class",ab)
        return ab

    def quaternConj(self, q):
        qConj = [q[0], -q[1], -q[2], -q[3]]
        print("quaterConj.....in AHRS class", qConj)
        return qConj










@api_view(["GET","POST"])
def stepcount(request):
    ssnid = request.data["sid"]  # 40500    ssnid 1000  reshmi
    stime = request.data["start"]  # 100    start 50000        73ms
    etime = request.data["end"]  # 300      end 53000          3003ms
    #left leg
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT distinct(s12) from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='L'",
            [stime, etime, ssnid])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    print(p)
    arr=[]
    for i in p:
        arr.append(i[0])
    print(arr)
    # stepcnt= max(p[0]) - min(p[0])
    stepcntl=(max(arr)-min(arr))
    print("step count", stepcntl)

    #right leg
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT distinct(s12) from sensordata where capturedtime >=%s and capturedtime <=%s and sessionid =%s and soletype='R'",
            [stime, etime, ssnid])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    print(p)
    arr = []
    for i in p:
        arr.append(i[0])
    print(arr)
    # stepcnt= max(p[0]) - min(p[0])
    stepcntr = (max(arr) - min(arr))
    print("step count", stepcntr)
    return Response({"stepleft":stepcntl, "stepright":stepcntr})






################################ storing 17 fsr sensordata #####################

@api_view(["POST"])
def storearraysensordata17(request):
    ssnid = request.data["sessionid"]
    # saar should be  <sensor values from s1..s11>,solytype,capturedtime
    sarr = request.data["sensorvalues"]
    macid = 0

    with connection.cursor() as cursor:
        cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
        for sval in sarr:
            p = cursor.execute(
                "insert into sensordata17(sessionid,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,s15,s16,s17,s18,s19,s20,s21,s22,s23,s24,s25,soletype,capturedtime,macid,timelocal) "
                "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,current_timestamp)",
                [ssnid, sval[0], sval[1], sval[2], sval[3], sval[4], sval[5], sval[6], sval[7], sval[8], sval[9],
                 sval[10], sval[11], sval[12], sval[13], sval[15], sval[16], sval[17], sval[18], sval[19], sval[20],
                 sval[21], sval[22], sval[23], sval[24], sval[25], sval[26], macid])

            if not p:
                done = 1
            else:
                done = 0

    if done == 1:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


######################## retrieving 17 sensor data ######################
@api_view(["GET","POST"])
def readarraysensordata17(request):
    ssnid = request.data["sessionid"]
    stime = request.data["start"]
    etime = request.data["end"]
    stype = request.data["soletype"]

    with connection.cursor() as cursor:
        p = cursor.execute(
            "select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,s15,s16,s17,s18,s19,s20,s21,s22,s23,s24,s25,soletype,capturedtime from sensordata17 where sessionid=%s and capturedtime>=%s and capturedtime <=%s and soletype=%s",
            [ssnid, stime, etime, stype])

        if not p:
            done = 1
        else:
            done = 0


    if done == 1:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


#######################################################################################


class AHRS:
    def __init__(self, *args):
        self.SamplePeriod = 1 / 33
        self.Quaternion = [1, 0, 0, 0]
        self.Kp = 2
        self.Ki = 0
        self.KpInit = 200
        self.InitPeriod = 5
        self.q = [1, 0, 0, 0]
        self.IntError = [0, 0, 0]
        self.KpRamped = None
        for i in range(0, len(args), 2):
            if args[i] == 'SamplePeriod':
                self.SamplePeriod = args[i + 1]
            elif args[i] == 'Quaternion':
                self.Quaternion = args[i + 1]
                self.q = self.quaternConj(self.Quaternion)
            elif args[i] == 'Kp':
                self.Kp = args[i + 1]
            elif args[i] == 'Ki':
                self.Ki = args[i + 1]
            elif args[i] == 'KpInit':
                self.KpInit = args[i + 1]
            elif args[i] == 'InitPeriod':
                self.InitPeriod = args[i + 1]
            else:
                raise ValueError('Invalid argument')
        self.KpRamped = self.KpInit

    def Update(self, Gyroscope, Accelerometer, Magnetometer):
        raise NotImplementedError('This method is unimplemented')

    def UpdateIMU(self, Gyroscope, Accelerometer):
        if norm(Accelerometer) == 0:
            print('Accelerometer magnitude is zero. Algorithm update aborted.')
            return
        else:
            Accelerometer = Accelerometer / norm(Accelerometer)
        v = [2 * (self.q[1] * self.q[3] - self.q[0] * self.q[2]),
             2 * (self.q[2] * self.q[3] + self.q[0] * self.q[1]),
             self.q[0] ** 2 - self.q[1] ** 2 - self.q[2] ** 2 + self.q[3] ** 2]
        error = np.cross(v, Accelerometer)
        self.IntError = self.IntError + error
        Ref = Gyroscope - (self.Kp * error + self.Ki * self.IntError)
        pDot = 0.5 * self.quaternProd(self.q, [0, float(Ref[0]), float(Ref[1]), float(Ref[2])])
        self.q = self.q + pDot * self.SamplePeriod
        self.q = self.q / norm(self.q)
        self.Quaternion = self.quaternConj(self.q)

    def quaternProd(self, a, b):
        # Ensure a and b are lists or arrays
        a = np.array(a)
        b = np.array(b)

        ab = np.array([
            a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
            a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
            a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
            a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]
        ])
        return ab

    def quaternConj(self, q):
        qConj = [q[0], -q[1], -q[2], -q[3]]
        return qConj

################end of class###########################
def quaternProd(a, b):
        ab = [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
              a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
              a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
              a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]]
        # print(ab)
        return ab

def quaternConj(q):
        qConj = [q[0], -q[1], -q[2], -q[3]]
        # print(qConj)
        return qConj

def quaternRotate(v, q):
        row, col = v.shape
        v0XYZ = quaternProd(quaternProd(q, np.hstack((np.zeros((row, 1)), v))), quaternConj(q))
        v = np.array(v0XYZ)[:, 1:4]
        return v

def extract_ranges(t, heel, toe, threshold=650):
    # Detect peaks using the specified method
    peaks = []
    for i in range(1, len(heel) - 1):  # 1 to last index
        if heel[i - 1] < heel[i] >= heel[i + 1] and heel[i] > threshold:
            peaks.append(i)

    # Identify clusters of nearby peaks
    clustered_peaks = []
    current_cluster = [peaks[0]]
    for i in range(1, len(peaks)):
        if peaks[i] - peaks[i - 1] <= 5:
            current_cluster.append(peaks[i])
        else:
            # Calculate the median of the current cluster and store it
            clustered_peaks.append(int(np.median(current_cluster)))
            current_cluster = [peaks[i]]


    # Get corresponding time values for peaks
    peak_times = [t[i] for i in clustered_peaks]

    # Store first_intersection_time values in an array
    first_intersection_times = []
    samples_for_first_intersection = []
    indices_for_first_intersection = []


    # Plot segments between intersections
    for i in range(len(clustered_peaks)):

        if (i < (len(clustered_peaks) - 1)):
            start_index = clustered_peaks[i]
            end_index = clustered_peaks[i + 1]
            # Find the first intersection point between 'heel' and 'toe' signals
            heel_array = np.array(heel[start_index:end_index])
            toe_array = np.array(toe[start_index:end_index])
            intersections = np.where(np.diff(np.sign(heel_array - toe_array)))[0]
            if len(intersections) > 0 :
                    t_list = t.tolist()
                    first_intersection_time = t_list[start_index:end_index][intersections[0]]
                    first_intersection_times.append(first_intersection_time)
                    sample_index = start_index + intersections[0]
                    samples_for_first_intersection.append(heel[sample_index])
                    indices_for_first_intersection.append(sample_index)
        else :
              break
    time_array = [t[0]] + first_intersection_times + [t[(len(t)-1)]]
    ta = time_array
    indices_for_first_intersection = [0] + indices_for_first_intersection + [len(heel) - 1]

    return indices_for_first_intersection
########################################################################################################
# Compute translational accelerations
# Rotate accelerations from sensor frame to Earth frame
# Function to rotate vector v by quaternion q
def quatern_conj(q):
            if q.ndim == 1:
                return np.array([q[0], -q[1], -q[2], -q[3]])
            elif q.ndim == 2:
                return np.array([q[:, 0], -q[:, 1], -q[:, 2], -q[:, 3]]).T
            else:
                raise ValueError("Invalid dimension for quaternion array")

def quatern_rotate(v, q):
            q_conj = quatern_conj(q)
            v_quat = np.concatenate(([0], v))
            result_quat = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)
            return result_quat[1:]

def quaternion_multiply(q1, q2):
            w1, x1, y1, z1 = q1
            w2, x2, y2, z2 = q2
            w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
            x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
            y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
            z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
            return np.array([w, x, y, z])
###################################################################################################

def stridelenestimate(s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,t12):
    print("in stridelenestimate()..................................")
    toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]
    heel = [sum(x) / len(x) for x in zip(s4, s5)]
    t=t12
    print("toe: ",toe)
    print("heel: ",heel)
    Fs = 40                  # change this if data is at different frequency
    # Extract ranges using the function
    ranges = extract_ranges(t, heel, toe)
    tim_array = []
    for ty in range(0, len(ranges)):

        tim_array.append(int(t[ranges[ty]]))

    # Initialize an empty list to store all position values values
    print("ranges", ranges)
    # print("time values", tim_array)

    max_pos_values = []
    if len(ranges) <= 0:
        return []
    print("len of ranges", len(ranges))
    #Perform processing for each range
    for i in range(len(ranges) - 1):
        start_index = ranges[i]
        end_index = ranges[i + 1]
        accX = s6[start_index:end_index] / 9.8
        accY = s7[start_index:end_index] / 9.8
        accZ = s8[start_index:end_index] / 9.8
        gyrX = s9[start_index:end_index] * 57.29
        gyrY = s10[start_index:end_index] * 57.29
        gyrZ = s11[start_index:end_index] * 57.29
        t = t12[start_index:end_index]
        t11 = t
        L1 = len(t)
        time = np.arange(L1)
        # step4

        acc_mag = np.sqrt(accX ** 2 + accY ** 2 + accZ ** 2)
        # Detect stationary periods
        sample_period = 1 / Fs
        filt_cutoff = 0.0001

        # High-pass filter accelerometer data
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'high')
        acc_magFilt = filtfilt(b, a, acc_mag)
        acc_magFilt = np.abs(acc_magFilt)

        # Low-pass filter accelerometer data
        filt_cutoff = 5
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'low')
        acc_magFilt = filtfilt(b, a, acc_magFilt)

        # Threshold detection
        stationary = acc_magFilt < (0.03)

        # step 5
        # Compute orientation
        quat = np.zeros((len(time), 4))
        AHRSalgorithm = AHRS('SamplePeriod', 1 / Fs, 'Kp', 1, 'KpInit', 1)
        # Initial convergence
        initPeriod = 0.5
        indexSel = np.arange(np.argmax(time > (time[0] + initPeriod)))
        adjusted_indexSel = [i + start_index for i in indexSel]

        # Use adjusted_indexSel to access values in accX
        selected_values = accX[adjusted_indexSel]

        # print(selected_values)
        indexSel=adjusted_indexSel
        for j in range(500):
            AHRSalgorithm.UpdateIMU([0, 0, 0], [np.mean(accX[indexSel]), np.mean(accY[indexSel]), np.mean(accZ[indexSel])])
        # For all data
        for t in range(len(time)):
            if stationary[t]:
                AHRSalgorithm.Kp = 0.01
            else:
                AHRSalgorithm.Kp = 0.01
            try :
               AHRSalgorithm.UpdateIMU(np.deg2rad([gyrX[t], gyrY[t], gyrZ[t]]), [accX[t], accY[t], accZ[t]])
            except ValueError as ve:
                # Handle the ValueError (e.g., if the user enters a non-integer)
                # print(f"Error: {ve}. Please enter valid integers.")
                uk=1
            except ZeroDivisionError:
                # Handle the ZeroDivisionError (e.g., if the user enters 0 as the second number)
                # print("Error: Cannot divide by zero.")
                uk=1
            except Exception as e:
                # Handle other exceptions
                # print(f"An unexpected error occurred: {e}")
                uk=1
            # AHRSalgorithm.UpdateIMU(np.deg2rad([gyrX[t], gyrY[t], gyrZ[t]]), [accX[t], accY[t], accZ[t]])
            quat[t, :] = AHRSalgorithm.Quaternion


        # step6

        # compute transilational acceleration

        acc1 = np.column_stack((accX, accY, accZ))
        quat_conj = quatern_conj(quat)
        # print(quat_conj)

        acc2 = np.array([quatern_rotate(row, quat_conj[i, :]) for i, row in enumerate(acc1)])
        # print(acc2 )

        acc = acc2 * 9.8

        acc[:, 2] -= 9.8

        time = np.array(time)

        # step 7
        # Integrate acceleration to yield velocity
        vel = np.zeros(acc.shape)
        for t in range(1, vel.shape[0]):
            vel[t, :] = vel[t - 1, :] + acc[t, :] * sample_period
            if stationary[t] == 1:
                vel[t, :] = [0, 0, 0]  # apply ZUPT update when foot stationary

        # plt.figure()
        # plt.plot(vel)
        # plt.show()

        # Compute integral drift during non-stationary periods
        velDrift = np.zeros(vel.shape)
        stationaryStart = np.where(np.diff(stationary) == 1)[0]
        stationaryEnd = np.where(np.diff(stationary) == -1)[0]
        for i in range(len(stationaryEnd)):
            driftRate = vel[stationaryStart[i] - 1, :] / (stationaryStart[i] - stationaryEnd[i])
            enum = np.arange(1, stationaryStart[i] - stationaryEnd[i] + 1)
            drift = np.column_stack((enum * driftRate[0], enum * driftRate[1], enum * driftRate[2]))
            velDrift[stationaryEnd[i]:stationaryStart[i] - 1, :] = drift

        # Remove integral drift
        vel = vel - velDrift

        # Compute translational position

        # Integrate velocity to yield position
        pos = np.zeros(vel.shape)
        for t in range(1, pos.shape[0]):
            pos[t, :] = pos[t - 1, :] + vel[t, :] * sample_period


        posX = np.abs(pos[:, 1])
        # print(np.max(posX))
        max_pos = np.max(posX)

        max_pos_values.append(max_pos)
        # print("max_pos_values", max_pos_values)
        print("sum of distance:", np.sum(max_pos_values))
        tsum=np.sum(max_pos_values)
        max_pos_array = np.array(max_pos_values)
    print("finally strides............", max_pos_values)
    print("finally time ..............", tim_array)
    timestart = tim_array[1]
    sc = 1
    leftstride = []
    tsum = 0
    print(len(max_pos_values))
    # if (len(max_pos_values) >= len(tim_array)):
    for ts in range(1, len(max_pos_values)):
        print(ts, tim_array[ts], max_pos_values[ts])
        tt = tim_array[ts] - timestart
        if tt <= 0:
            vf = 0
        else:
            vf = max_pos_values[ts] / float(tt * 0.001)
        leftstride.append({"strideno": sc, "dist": max_pos_values[ts], "time": tim_array[ts],"velocity": vf})
        timestart = tim_array[ts]
        tsum = tsum + max_pos_values[ts]
        sc = sc + 1
    # tsum= np.sum(max_pos_values)

    print("finally stride :", leftstride)
    print("total distance using tsum :", tsum, "m/s2")


    return leftstride

###################################################################################################
@api_view(["POST"])
def onlinestridecompute(request):      #online stride computation using AHRS

        ssnid = request.data["sessionid"]
        # sarr should be  <sensor values from s1..s11>,<s12 and s13 for step size >solytype,capturedtime
        sarr = request.data["sensorvalues"]
        print("inside onlinestridecompute()..............")
        stimez = min(sublist[14] for sublist in sarr)
        etimez = max(sublist[14] for sublist in sarr)
        print("starttime is ", stimez, "endtime is:", etimez)

        # # delete existing data  for sessionid in onlinestride for both soletypes
        # with connection.cursor() as cursor:
        #     p = cursor.execute(
        #         "DELETE from onlinestride where sessionid =%s", [ssnid])

        print("ssnid and sarr values........................................", ssnid, sarr)
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
            for sval in sarr:
                print("row..", sval)
                p = cursor.execute(
                    "insert into sensordata(sessionid,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,timelocal) "
                    "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,current_timestamp)",
                    [ssnid, sval[0], sval[1], sval[2], sval[3], sval[4], sval[5], sval[6], sval[7], sval[8], sval[9],
                     sval[10], sval[11], sval[12], sval[13], sval[14]])

                if not p:
                    done = 1
                else:
                    done = 0

        if done == 1:
            # for right leg data
            sval = [sublist for sublist in sarr if 'R' in sublist]
            rdone=0
            totaldist=0.0

            # for right leg data
            print("total right rows:...............", sval)
            if (len(sval) > 0) :
                aa = pd.DataFrame(sval)
                s1 = aa.iloc[:, 0]
                s2 = aa.iloc[:, 1]
                s3 = aa.iloc[:, 2]
                s4 = aa.iloc[:, 3]
                s5 = aa.iloc[:, 4]
                s6 = aa.iloc[:, 5]
                s7 = aa.iloc[:, 6]
                s8 = aa.iloc[:, 7]
                s9 = aa.iloc[:, 8]
                s10 = aa.iloc[:, 9]
                s11 = aa.iloc[:, 10]
                t12 = aa.iloc[:, 14]
                print("right calling strideestimate()...............")
                try:
                    rsl = stridelenestimate(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, t12)
                    print("ls is ...........", rsl, "len", len(rsl),"start time:", min(t12))
                    stype = 'R'
                    if (len(rsl) > 0):
                        totaldist = 0.0
                        rc=0
                        with connection.cursor() as cursor:
                            # data in rsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                            for r in rsl:
                                sessionid = int(ssnid)
                                strideno = int(r["strideno"])
                                dist = float(r["dist"])
                                velocity = float(r["velocity"])
                                stz = r["time"]
                                if (rc < len(rsl)-1):
                                      etz =int((rsl[rc+1]["time"])-1)
                                else:
                                      etz = int(etimez)
                                print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                      "strideno", strideno, "dist", dist, "velocity", velocity)
                                try:
                                    p = cursor.execute(
                                        "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                        [sessionid, stz, etz, stype, strideno, dist, velocity])
                                except Exception as e:
                                    # Handle any other unexpected exceptions
                                    print(f"An unexpected error occurred: {e}")

                                if not p:
                                    totaldist = totaldist + dist
                                    rc=rc+1
                                    rdone = 1  # write into onlinestride  successful
                                else:
                                    rdone = 0  # it failed to write
                except Exception as e:
                            # Handle any other unexpected exceptions
                            print(f"An unexpected error occurred when Right calling stridelenstimate(): {e}")
                            rdone = 0  # failed
                            return JsonResponse({'status': 'error'})
            else:
                rdone = 1  # rsl length is zero so no strides detected and written into table
                totaldist=0.0


            print("right leg total distance:", totaldist)


            # for left leg data
            sval = [sublist for sublist in sarr if 'L' in sublist]


            # for left leg data
            print("total LEFT  rows:...............", sval)
            ldone=0
            totdist=0.0
            if (len(sval) > 0):
                aa = pd.DataFrame(sval)
                print("aa............", aa)
                s1 = aa.iloc[:, 0]
                s2 = aa.iloc[:, 1]
                s3 = aa.iloc[:, 2]
                s4 = aa.iloc[:, 3]
                s5 = aa.iloc[:, 4]
                s6 = aa.iloc[:, 5]
                s7 = aa.iloc[:, 6]
                s8 = aa.iloc[:, 7]
                s9 = aa.iloc[:, 8]
                s10 = aa.iloc[:, 9]
                s11 = aa.iloc[:, 10]
                t12 = aa.iloc[:, 14]

                print("left calling strideestimate()...............")
                try:
                    lsl = stridelenestimate(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, t12)
                    print("ls is ...........", lsl, "len", len(lsl), "start time:", min(t12))
                    stype = 'L'
                    if (len(lsl) > 0):
                        totdist = 0.0
                        rc=0
                        with connection.cursor() as cursor:
                            # data in lsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                            for l in lsl:
                                sessionid = int(ssnid)
                                strideno = int(l["strideno"])
                                dist = float(l["dist"])
                                velocity = float(l["velocity"])
                                stz = l["time"]
                                if (rc < len(lsl) - 1):
                                    etz = int((lsl[rc + 1]["time"]) - 1)
                                else:
                                    etz = int(etimez)
                                print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                      "strideno", strideno, "dist", dist, "velocity", velocity)
                                try:
                                    p = cursor.execute(
                                        "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                        [sessionid, stz, etz, stype, strideno, dist, velocity])
                                except Exception as e:
                                    # Handle any other unexpected exceptions
                                    print(f"An unexpected error occurred: {e}")

                                if not p:
                                    totdist = totdist + dist
                                    rc=rc+1
                                    ldone = 1  # its successful
                                else:
                                    ldone = 0  # it failed

                except Exception as e:
                    # Handle any other unexpected exceptions
                    print(f"An unexpected error occurred when left calling stridelenstimate(): {e}")
                    ldone = 0  # failed
                    return JsonResponse({'status': 'error'})
            else:
                ldone = 1  # lsl length is zero so no strides detected and written into table
                totdist = 0.0


            print("left leg total distance:", totaldist)

            if (rdone == 1) and (ldone == 1):
                print("total total distance:", (totaldist+totdist))
                return JsonResponse({'status': 'success'})
            elif ((rdone == 1) and (ldone == 0)) or ((rdone == 0) and (ldone == 1)):
                print("total distance:", (totaldist+totdist), "right distance:", totaldist, "left distance: ",totdist)
                return JsonResponse({'status': 'success'})
            else :
                return JsonResponse({'status': 'error'})


        else:
            return JsonResponse({'status': 'error'})  #### if done ==0 ie., data writing into table has failed!!


##############################################################################
#modified stridelenestimate() for every new sensor data inserted computes strides and writes a running strideno into onlinestride for that sessionid

@api_view(["POST"])
def onlinestridecompute11(request):      #online stride computation using AHRS

        ssnid = request.data["sessionid"]
        # sarr should be  <sensor values from s1..s11>,<s12 and s13 for step size >solytype,capturedtime
        sarr = request.data["sensorvalues"]
        print("inside onlinestridecompute()..............")
        try:
            stimez = min(sublist[14] for sublist in sarr)
            etimez = max(sublist[14] for sublist in sarr)
        except Exception as e:
            print(sarr)
            print(e)
        print("starttime is ", stimez, "endtime is:", etimez)

        print("ssnid and sarr values........................................", ssnid, sarr)
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
            for sval in sarr:
                print("row..", sval)
                p = cursor.execute(
                    "insert into sensordata(sessionid,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,timelocal) "
                    "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,current_timestamp)",
                    [ssnid, sval[0], sval[1], sval[2], sval[3], sval[4], sval[5], sval[6], sval[7], sval[8], sval[9],
                     sval[10], sval[11], sval[12], sval[13], sval[14]])

                if not p:
                    done = 1
                else:
                    done = 0

        # get last strideno stored for both left and right  for sessionid in onlinestride for both soletypes
        with connection.cursor() as cursor:
            p = cursor.execute(
                "select max(strideno) from onlinestride where sessionid =%s and soletype='L'", [ssnid])
            lsnos = cursor.fetchone()
            print("rows from LEFT onlinestride.................................", lsnos)
        if (lsnos[0] == None):
            lsno=1
        elif (lsnos[0] >= 0):
            lsno = lsnos[0] + 1
        else:
            lsno = 1
        print("last write 's lsno", lsno)
        with connection.cursor() as cursor:
            p = cursor.execute(
                "select max(strideno) from onlinestride where sessionid =%s and soletype='R'", [ssnid])
            rsnos = cursor.fetchone()
            print("rows from RIGHT onlinestride.................................",rsnos)

        if (rsnos[0] == None):
            rsno = 1
        elif (rsnos[0] >= 0):
            rsno = rsnos[0] + 1
        else:
            rsno = 1
        print("last write's rsno", rsno)
        # lsno=lsno+1
        # rsno=rsno+1
        print("new insert value for lsno: ",lsno, "rsno: ",rsno)
        if done == 1:
            # for right leg data
            sval = [sublist for sublist in sarr if 'R' in sublist]
            rdone=0
            totaldist=0.0

            # for right leg data
            print("total right rows:...............", sval)
            if (len(sval) > 0) :
                aa = pd.DataFrame(sval)
                s1 = aa.iloc[:, 0]
                s2 = aa.iloc[:, 1]
                s3 = aa.iloc[:, 2]
                s4 = aa.iloc[:, 3]
                s5 = aa.iloc[:, 4]
                s6 = aa.iloc[:, 5]
                s7 = aa.iloc[:, 6]
                s8 = aa.iloc[:, 7]
                s9 = aa.iloc[:, 8]
                s10 = aa.iloc[:, 9]
                s11 = aa.iloc[:, 10]
                t12 = aa.iloc[:, 14]
                print("right calling strideestimate()...............")
                try:
                    rsl = stridelenestimate(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, t12)
                    print("ls is ...........", rsl, "len", len(rsl),"start time:", min(t12))
                    stype = 'R'
                    if (len(rsl) > 0):
                        totaldist = 0.0
                        rc=0
                        with connection.cursor() as cursor:
                            # data in rsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                            for r in rsl:
                                sessionid = int(ssnid)
                                # strideno = int(r["strideno"])
                                strideno = int(rsno)
                                dist = float(r["dist"])
                                velocity = float(r["velocity"])
                                stz = r["time"]
                                if (rc < len(rsl)-1):
                                      etz =int((rsl[rc+1]["time"])-1)
                                else:
                                      etz = int(etimez)
                                print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                      "strideno", strideno, "dist", dist, "velocity", velocity)
                                try:
                                    p = cursor.execute(
                                        "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                        [sessionid, stz, etz, stype, strideno, dist, velocity])
                                except Exception as e:
                                    # Handle any other unexpected exceptions
                                    print(f"An unexpected error occurred: {e}")

                                if not p:
                                    totaldist = totaldist + dist
                                    rc=rc+1
                                    rsno=rsno+1
                                    rdone = 1  # write into onlinestride  successful
                                else:
                                    rdone = 0  # it failed to write
                except Exception as e:
                            # Handle any other unexpected exceptions
                            print(f"An unexpected error occurred when Right calling stridelenstimate(): {e}")
                            rdone = 0  # failed
                            return JsonResponse({'status': 'error'})
            else:
                rdone = 1  # rsl length is zero so no strides detected and written into table
                totaldist=0.0


            print("right leg total distance:", totaldist)


            # for left leg data
            sval = [sublist for sublist in sarr if 'L' in sublist]


            # for left leg data
            print("total LEFT  rows:...............", sval)
            ldone=0
            totdist=0.0
            if (len(sval) > 0):
                aa = pd.DataFrame(sval)
                print("aa............", aa)
                s1 = aa.iloc[:, 0]
                s2 = aa.iloc[:, 1]
                s3 = aa.iloc[:, 2]
                s4 = aa.iloc[:, 3]
                s5 = aa.iloc[:, 4]
                s6 = aa.iloc[:, 5]
                s7 = aa.iloc[:, 6]
                s8 = aa.iloc[:, 7]
                s9 = aa.iloc[:, 8]
                s10 = aa.iloc[:, 9]
                s11 = aa.iloc[:, 10]
                t12 = aa.iloc[:, 14]

                print("left calling strideestimate()...............")
                try:
                    lsl = stridelenestimate(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, t12)
                    print("ls is ...........", lsl, "len", len(lsl), "start time:", min(t12))
                    stype = 'L'
                    if (len(lsl) > 0):
                        totdist = 0.0
                        rc=0
                        with connection.cursor() as cursor:
                            # data in lsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                            for l in lsl:
                                sessionid = int(ssnid)
                                # strideno = int(l["strideno"])
                                strideno =int(lsno)
                                dist = float(l["dist"])
                                velocity = float(l["velocity"])
                                stz = l["time"]
                                if (rc < len(lsl) - 1):
                                    etz = int((lsl[rc + 1]["time"]) - 1)
                                else:
                                    etz = int(etimez)
                                print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                      "strideno", strideno, "dist", dist, "velocity", velocity)
                                try:
                                    p = cursor.execute(
                                        "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                        [sessionid, stz, etz, stype, strideno, dist, velocity])
                                except Exception as e:
                                    # Handle any other unexpected exceptions
                                    print(f"An unexpected error occurred: {e}")

                                if not p:
                                    totdist = totdist + dist
                                    rc=rc+1
                                    lsno=lsno+1
                                    ldone = 1  # its successful
                                else:
                                    ldone = 0  # it failed

                except Exception as e:
                    # Handle any other unexpected exceptions
                    print(f"An unexpected error occurred when left calling stridelenstimate(): {e}")
                    ldone = 0  # failed
                    return JsonResponse({'status': 'error'})
            else:
                ldone = 1  # lsl length is zero so no strides detected and written into table
                totdist = 0.0


            print("left leg total distance:", totaldist)

            if (rdone == 1) and (ldone == 1):
                print("total total distance:", (totaldist+totdist))
                return JsonResponse({'status': 'success'})
            elif ((rdone == 1) and (ldone == 0)) or ((rdone == 0) and (ldone == 1)):
                print("total distance:", (totaldist+totdist), "right distance:", totaldist, "left distance: ",totdist)
                return JsonResponse({'status': 'success'})
            else :
                return JsonResponse({'status': 'error'})


        else:
            return JsonResponse({'status': 'error'})  #### if done ==0 ie., data writing into table has failed!!







################################################################################

@api_view(["GET","POST"])
def onlinestrideinfo(request):           # online stride  reading  OLD CODE.........................................................
     ssnid = request.data["sid"]
     print(ssnid)

     try:
        with connection.cursor() as cursor:
            p = cursor.execute("select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by starttime desc limit 11",[ssnid])
            rcnt = cursor.rowcount
            rstride =cursor.fetchall()
        print("right stride :", rstride)
        with connection.cursor() as cursor:
            p = cursor.execute("select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by starttime desc limit 11",[ssnid])
            lcnt = cursor.rowcount
            lstride = cursor.fetchall()
        print("left stride:",lstride)

        finarr = []
        for r1 in range(min(lcnt, rcnt)):
            finarr.append({
                "leftstrideno": lstride[r1][0],
                "rightstrideno": rstride[r1][0],
                "leftdistance": lstride[r1][1],
                "rightdistance": rstride[r1][1],
                "leftstridevel": lstride[r1][2],
                "rightstridevel": rstride[r1][2]
            })

        if lcnt == 0 and rcnt > 0:
            for r1 in range(rcnt):
                finarr.append({
                    "leftstrideno": None,                                 ##################### this None is the problem when it goes to graph so needs to change
                    "rightstrideno": rstride[r1][0],
                    "leftdistance": None,                                 ##################### this None is the problem when it goes to graph so needs to change
                    "rightdistance": rstride[r1][1],
                    "leftstridevel": None,                                 ##################### this None is the problem when it goes to graph so needs to change
                    "rightstridevel": rstride[r1][2]
                })
        elif rcnt == 0  and lcnt >0:
               for i in range(lcnt):
                        finarr.append({
                            "leftstrideno": lstride[i][0],
                            "rightstrideno": None,                                 ##################### this None is the problem when it goes to graph so needs to change
                            "leftdistance": lstride[i][1],
                            "rightdistance": None,                                 ##################### this None is the problem when it goes to graph so needs to change
                            "leftstridevel": lstride[i][2],
                            "rightstridevel": None                                 ##################### this None is the problem when it goes to graph so needs to change
                        })
        elif (rcnt - lcnt) > 0 :
               for r1 in range(lcnt+1,rcnt+1):
                    finarr.append({
                        "leftstrideno": None,                                 ##################### this None is the problem when it goes to graph so needs to change
                        "rightstrideno": rstride[r1][0],
                        "leftdistance": None,                                 ##################### this None is the problem when it goes to graph so needs to change
                        "rightdistance": rstride[r1][1],
                        "leftstridevel": None,                                 ##################### this None is the problem when it goes to graph so needs to change
                        "rightstridevel": rstride[r1][2]
                    })
        elif (lcnt - rcnt) > 0:
              for i in range(rcnt + 1, lcnt+1):
                    finarr.append({
                        "leftstrideno": lstride[i][0],
                        "rightstrideno": None,                                 ##################### this None is the problem when it goes to graph so needs to change
                        "leftdistance": lstride[i][1],
                        "rightdistance": None,                                 ##################### this None is the problem when it goes to graph so needs to change
                        "leftstridevel": lstride[i][2],
                        "rightstridevel": None                                 ##################### this None is the problem when it goes to graph so needs to change
                    })

        print(finarr)


     except Exception as e:
         print(e)
     return Response(finarr)




# modified code of onlinestrideinfo()  and here None is replaced by 0's..........................................................................
@api_view(["GET","POST"])
def onlinestrideinfo11(request):
     print("**********************************")# online stride  reading NONE are replaced by 0.......................................................
     ssnid = request.data["sid"]
     print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
     print(ssnid)

     try:
        with connection.cursor() as cursor:
            # p = cursor.execute("select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by starttime limit 11",[ssnid])
            p = cursor.execute("select * from(select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by strideno desc limit 11) as foo order by strideno asc",[ssnid])
            rcnt = cursor.rowcount
            rstride =cursor.fetchall()
        print("right stride :", rstride)
        with connection.cursor() as cursor:
            # p = cursor.execute("select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by starttime desc limit 11",[ssnid])
            p = cursor.execute(
                "select * from(select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by strideno desc limit 11) as foo order by strideno asc",
                [ssnid])
            lcnt = cursor.rowcount
            lstride = cursor.fetchall()
        print("left stride:",lstride)

        finarr = []
        for r1 in range(min(lcnt, rcnt)):
            finarr.append({
                "leftstrideno": lstride[r1][0],
                "rightstrideno": rstride[r1][0],
                "leftdistance": lstride[r1][1],
                "rightdistance": rstride[r1][1],
                "leftstridevel": lstride[r1][2],
                "rightstridevel": rstride[r1][2]
            })

        if lcnt == 0 and rcnt > 0:
            for r1 in range(rcnt):
                finarr.append({
                    "leftstrideno": 0,
                    "rightstrideno": rstride[r1][0],
                    "leftdistance": 0,
                    "rightdistance": rstride[r1][1],
                    "leftstridevel": 0,
                    "rightstridevel": rstride[r1][2]
                })
        elif rcnt == 0  and lcnt >0:
             for r1 in range(lcnt):
                finarr.append({
                    "leftstrideno": lstride[r1][0],
                    "rightstrideno": 0,
                    "leftdistance": lstride[r1][1],
                    "rightdistance": 0,
                    "leftstridevel": lstride[r1][2],
                    "rightstridevel": 0
                })
        elif (rcnt - lcnt) > 0 :
            for r1 in range(lcnt+1,rcnt):
                finarr.append({
                    "leftstrideno": 0,
                    "rightstrideno": rstride[r1][0],
                    "leftdistance": 0,
                    "rightdistance": rstride[r1][1],
                    "leftstridevel": 0,
                    "rightstridevel": rstride[r1][2]
                })
        elif (lcnt - rcnt) > 0:
            for r1 in range(rcnt + 1, lcnt):
                finarr.append({
                    "leftstrideno": lstride[r1][0],
                    "rightstrideno": 0,
                    "leftdistance": lstride[r1][1],
                    "rightdistance": 0,
                    "leftstridevel": lstride[r1][2],
                    "rightstridevel": 0
                })

        print(finarr)


     except Exception as e:
         print(e)
     return Response(finarr)

#######################################################################################################################
@api_view(["GET","POST"])
def strideinfo1121(request):           # online stride  reading
     ssnid = request.data["sid"]
     print(ssnid)
     finarr=[]
     with connection.cursor() as cursor:
         p = cursor.execute(
             "select starttime from onlinestride where sessionid =%s and soletype='R' order by starttime", [ssnid])
         rstart = cursor.fetchall()
     print("rows from RIGHT onlinestride.................................", rstart)
     with connection.cursor() as cursor:
         sno = 1
         for r in rstart:
             p = cursor.execute(
                 "update  onlinestride set strideno= %s where sessionid = %s and soletype = 'R' and starttime =%s",
                 [sno, ssnid, r[0]])
             sno = sno + 1

     with connection.cursor() as cursor:
         p = cursor.execute(
             "select starttime from onlinestride where sessionid =%s and soletype='L' order by starttime", [ssnid])
         lstart = cursor.fetchall()
     print("rows from LEFT onlinestride.................................", lstart)
     with connection.cursor() as cursor:
         sno = 1
         for l in lstart:
             print(l[0])
             p = cursor.execute(
                 "update  onlinestride set strideno= %s where sessionid = %s and soletype = 'L' and starttime =%s",
                 [sno, ssnid, l[0]])
             sno = sno + 1

     try:
        with connection.cursor() as cursor:
            # p = cursor.execute("select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by starttime limit 11",[ssnid])
            p = cursor.execute("select strideno, distance,velocity from (select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by strideno asc limit 11) as tbl order by strideno asc",[ssnid])
            rcnt = cursor.rowcount
            rstride =cursor.fetchall()
        print("right stride :", rstride)
        with connection.cursor() as cursor:
            p = cursor.execute("select strideno, distance,velocity from (select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by starttime desc limit 11) as tbl order by strideno asc",[ssnid])
            # p = cursor.execute(
            #     "select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by strideno asc limit 11",
            #     [ssnid])
            lcnt = cursor.rowcount
            lstride = cursor.fetchall()
        print("left stride:",lstride)

        finarr = []
        for r1 in range(min(lcnt, rcnt)):
            finarr.append({
                "leftstrideno": lstride[r1][0],
                "rightstrideno": rstride[r1][0],
                "leftdistance": lstride[r1][1],
                "rightdistance": rstride[r1][1],
                "leftstridevel": lstride[r1][2],
                "rightstridevel": rstride[r1][2]
            })

        if lcnt == 0 and rcnt > 0:
            for r1 in range(rcnt):
                finarr.append({
                    "leftstrideno": 0,
                    "rightstrideno": rstride[r1][0],
                    "leftdistance": 0,
                    "rightdistance": rstride[r1][1],
                    "leftstridevel": 0,
                    "rightstridevel": rstride[r1][2]
                })
        elif rcnt == 0  and lcnt >0:
             for r1 in range(lcnt):
                finarr.append({
                    "leftstrideno": lstride[r1][0],
                    "rightstrideno": 0,
                    "leftdistance": lstride[r1][1],
                    "rightdistance": 0,
                    "leftstridevel": lstride[r1][2],
                    "rightstridevel": 0
                })
        elif (rcnt - lcnt) > 0 :
            for r1 in range(lcnt+1,rcnt):
                finarr.append({
                    "leftstrideno": 0,
                    "rightstrideno": rstride[r1][0],
                    "leftdistance": 0,
                    "rightdistance": rstride[r1][1],
                    "leftstridevel": 0,
                    "rightstridevel": rstride[r1][2]
                })
        elif (lcnt - rcnt) > 0:
            for r1 in range(rcnt + 1, lcnt):
                finarr.append({
                    "leftstrideno": lstride[r1][0],
                    "rightstrideno": 0,
                    "leftdistance": lstride[r1][1],
                    "rightdistance": 0,
                    "leftstridevel": lstride[r1][2],
                    "rightstridevel": 0
                })

        print(finarr)
     except Exception as e:
         print(e)
     return Response(finarr)

#######################################################################################################################



@api_view(["GET","POST"])
def svleft(request):

        # offine stride computation using AHRS
        ssnid = request.data["sid"]
        lstime = request.data["start"]
        letime = request.data["end"]
        print("LEFT OFFLINE STRIDE .......................",ssnid, lstime, letime)

        ################################################# for left leg data
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,capturedtime from sensordata where sessionid =%s and capturedtime >=%s and capturedtime <=%s  and  soletype='L' order by capturedtime asc",
                [ssnid, lstime, letime])
            cnt = cursor.rowcount
            p = cursor.fetchall()
        print("total left rows:...............", cnt)
        # print(p)
        aa = pd.DataFrame(p)
        s1 = aa.iloc[:, 0]
        s2 = aa.iloc[:, 1]
        s3 = aa.iloc[:, 2]
        s4 = aa.iloc[:, 3]
        s5 = aa.iloc[:, 4]
        s6 = aa.iloc[:, 5]
        s7 = aa.iloc[:, 6]
        s8 = aa.iloc[:, 7]
        s9 = aa.iloc[:, 8]
        s10 = aa.iloc[:, 9]
        s11 = aa.iloc[:, 10]
        t12 = aa.iloc[:, 11]
        print("left calling strideestimate()...............")
        try:
            lsl = stridelenestimate(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, t12)
            print("LEFT ls is computed as ...........", lsl)
            if (len(lsl) > 0):
                rc = 0
                stype='L'
                # write into onlinestride table
                with connection.cursor() as cursor:
                    # data in lsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                    for l in lsl:
                        sessionid = int(ssnid)
                        strideno = int(l["strideno"])
                        dist = float(l["dist"])
                        velocity = float(l["velocity"])
                        stz = l["time"]
                        if (rc < len(lsl) - 1):
                            etz = int((lsl[rc + 1]["time"]) - 1)
                        else:
                            etz = int(letime)
                        print(".................sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype",stype,"strideno", strideno, "dist", dist, "velocity", velocity)
                        try:
                            p = cursor.execute(
                                "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                [sessionid, stz, etz, stype, strideno, dist, velocity])
                        except Exception as e:
                            # Handle any other unexpected exceptions
                            print(f"An unexpected error occurred: {e}")
                            return JsonResponse({'status': 'error'})
                        ldone = 1
                        rc = rc + 1
            else:
                ldone = 1  # no strides detected.
                print("no strides for left detected.....")
        except Exception as e:
            # Handle any other unexpected exceptions
            print(f"An unexpected error occurred: {e}")
            return JsonResponse({'status': 'error'})



@api_view(["GET","POST"])
def svright(request):
    # offine stride computation using AHRS
    ssnid = request.data["sid"]
    rstime = request.data["start"]
    retime = request.data["end"]
    print("RIGHT OFFLINE STRIDE .......................", ssnid, rstime, retime)
    ######################################################
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,capturedtime from sensordata where sessionid =%s and capturedtime >=%s and capturedtime <=%s  and  soletype='R' order by capturedtime asc",
            [ssnid, rstime, retime])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    print("total right rows:...............", cnt)
    # print(p)
    aa = pd.DataFrame(p)
    s1 = aa.iloc[:, 0]
    s2 = aa.iloc[:, 1]
    s3 = aa.iloc[:, 2]
    s4 = aa.iloc[:, 3]
    s5 = aa.iloc[:, 4]
    s6 = aa.iloc[:, 5]
    s7 = aa.iloc[:, 6]
    s8 = aa.iloc[:, 7]
    s9 = aa.iloc[:, 8]
    s10 = aa.iloc[:, 9]
    s11 = aa.iloc[:, 10]
    t12 = aa.iloc[:, 11]
    print("right calling strideestimate()...............")
    try:
        rsl = stridelenestimate(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, t12)
        print("right ls is  ...........", rsl)
        print("len of rsl :",len(rsl))
        # write into onlinestride table
        if (len(rsl) > 0):
            rc = 0
            stype='R'
            with connection.cursor() as cursor:
                # data in rsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                for r in rsl:
                    sessionid = int(ssnid)
                    strideno = int(r["strideno"])
                    dist = float(r["dist"])
                    velocity = float(r["velocity"])
                    stz = r["time"]
                    if (rc < len(rsl) - 1):
                        etz = int((rsl[rc + 1]["time"]) - 1)
                    else:
                        etz = int(retime)

                    print(".................sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                          "strideno", strideno, "dist", dist, "velocity", velocity)
                    try:
                        p = cursor.execute(
                            "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                            [sessionid, stz, etz, stype, strideno, dist, velocity])
                    except Exception as e:
                        # Handle any other unexpected exceptions
                        print(f"An unexpected error occurred: {e}")
                        return JsonResponse({'status': 'error'})
                    rdone = 1
                    rc = rc + 1
        else:
            rdone = 1  # no strides detected
            print("no strides detected for right..........")

    except Exception as e:
        # Handle any other unexpected exceptions
        print(f"An unexpected error occurred: {e}")
        return JsonResponse({'status': 'error'})

#########################################################################################################

@api_view(["GET","POST"])
def strideinfo1121L(request):           # online stride  reading
     # offine stride retrieval from onlinestride table for LEFT DATA
     ssnid = request.data["sid"]
     lstime = request.data["start"]
     letime = request.data["end"]
     lstime = lstime - 3000
     letime = letime + 3000
     print(ssnid)
     with connection.cursor() as cursor:
         p = cursor.execute(
             "select starttime from onlinestride where sessionid =%s and soletype='L' order by starttime", [ssnid])
         lstart = cursor.fetchall()
     print("rows from LEFT onlinestride.................................", lstart)
     with connection.cursor() as cursor:
         sno = 1
         for l in lstart:
             p = cursor.execute(
                 "update  onlinestride set strideno= %s where sessionid = %s and soletype = 'L' and starttime =%s",
                 [sno, ssnid, l[0]])
             sno = sno + 1

     try:
        with connection.cursor() as cursor:
            p = cursor.execute("select strideno, distance,velocity from (select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' and starttime >=%s and endtime <=%s  order by starttime desc limit 11) as tbl order by strideno asc",[ssnid,lstime,letime])
            # p = cursor.execute(
            #     "select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by strideno asc limit 11",
            #     [ssnid])
            lcnt = cursor.rowcount
            lstride = cursor.fetchall()
        print("left stride:",lstride)

        finarr = []
        sno =1
        for l1 in range(lcnt):
            finarr.append({
                "leftstrideno": sno,
                "leftdistance": lstride[l1][1],
                "leftstridevel": lstride[l1][2]
            })
            sn=sno+1
        print(finarr)


     except Exception as e:
         print(e)
     return Response(finarr)

@api_view(["GET","POST"])
def strideinfo1121R(request):           # online stride  reading
     # offine stride retrieval from onlinestride table for RIGHT DATA
     ssnid = request.data["sid"]
     rstime = request.data["start"]
     retime = request.data["end"]
     rstime = rstime - 3000
     retime = retime + 3000
     print(ssnid)
     with connection.cursor() as cursor:
         p = cursor.execute(
             "select starttime from onlinestride where sessionid =%s and soletype='R' order by starttime", [ssnid])
         rstart = cursor.fetchall()
     print("rows from RIGHT onlinestride.................................", rstart)
     with connection.cursor() as cursor:
         sno = 1
         for r in rstart:
             p = cursor.execute(
                 "update  onlinestride set strideno= %s where sessionid = %s and soletype = 'R' and starttime =%s",
                 [sno, ssnid, r[0]])
             sno = sno + 1

     try:
        with connection.cursor() as cursor:
            p = cursor.execute("select strideno, distance,velocity from (select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' and starttime >= %s and endtime <= %s order by starttime desc limit 11) as tbl order by strideno asc",[ssnid,rstime,retime])
            rcnt = cursor.rowcount
            rstride = cursor.fetchall()
        print("right stride:",rstride)

        finarr = []
        sno=1
        for r1 in range(rcnt):
            finarr.append({
                "rightstrideno": sno,
                "rightdistance": rstride[r1][1],
                "rightstridevel": rstride[r1][2]
            })
        print(finarr)


     except Exception as e:
         print(e)
     return Response(finarr)



#########################################################################################################


#########################################################################################################

def strideahrs(svalues):
        # step 2 - AHRS class
        class AHRS:
            def __init__(self, *args):
                self.SamplePeriod = 1 / 33
                self.Quaternion = [1, 0, 0, 0]
                self.Kp = 2
                self.Ki = 0
                self.KpInit = 200
                self.InitPeriod = 5
                self.q = [1, 0, 0, 0]
                self.IntError = [0, 0, 0]
                self.KpRamped = None
                for i in range(0, len(args), 2):
                    if args[i] == 'SamplePeriod':
                        self.SamplePeriod = args[i + 1]
                    elif args[i] == 'Quaternion':
                        self.Quaternion = args[i + 1]
                        self.q = self.quaternConj(self.Quaternion)
                    elif args[i] == 'Kp':
                        self.Kp = args[i + 1]
                    elif args[i] == 'Ki':
                        self.Ki = args[i + 1]
                    elif args[i] == 'KpInit':
                        self.KpInit = args[i + 1]
                    elif args[i] == 'InitPeriod':
                        self.InitPeriod = args[i + 1]
                    else:
                        raise ValueError('Invalid argument')
                self.KpRamped = self.KpInit

            def Update(self, Gyroscope, Accelerometer, Magnetometer):
                raise NotImplementedError('This method is unimplemented')

            def UpdateIMU(self, Gyroscope, Accelerometer):
                if norm(Accelerometer) == 0:
                    print('Accelerometer magnitude is zero. Algorithm update aborted.')
                    return
                else:
                    Accelerometer = Accelerometer / norm(Accelerometer)
                v = [2 * (self.q[1] * self.q[3] - self.q[0] * self.q[2]),
                     2 * (self.q[2] * self.q[3] + self.q[0] * self.q[1]),
                     self.q[0] ** 2 - self.q[1] ** 2 - self.q[2] ** 2 + self.q[3] ** 2]
                error = np.cross(v, Accelerometer)
                self.IntError = self.IntError + error
                Ref = Gyroscope - (self.Kp * error + self.Ki * self.IntError)
                pDot = 0.5 * self.quaternProd(self.q, [0, float(Ref[0]), float(Ref[1]), float(Ref[2])])
                self.q = self.q + pDot * self.SamplePeriod
                self.q = self.q / norm(self.q)
                self.Quaternion = self.quaternConj(self.q)

            def quaternProd(self, a, b):
                # Ensure a and b are lists or arrays
                a = np.array(a)
                b = np.array(b)

                ab = np.array([
                    a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
                    a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
                    a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
                    a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]
                ])
                return ab

            def quaternConj(self, q):
                qConj = [q[0], -q[1], -q[2], -q[3]]
                return qConj


        # step3

        def quaternProd(a, b):
            ab = [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
                  a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
                  a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
                  a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]]
            # print(ab)
            return ab


        def quaternConj(q):
            qConj = [q[0], -q[1], -q[2], -q[3]]
            # print(qConj)
            return qConj


        def quaternRotate(v, q):
            row, col = v.shape
            v0XYZ = quaternProd(quaternProd(q, np.hstack((np.zeros((row, 1)), v))), quaternConj(q))
            v = np.array(v0XYZ)[:, 1:4]
            return v


        def extract_ranges(t, heel, toe, threshold=650):
            # Detect peaks using the specified method
            peaks = []
            for i in range(1, len(heel) - 1):  # 1 to last index
                if heel[i - 1] < heel[i] >= heel[i + 1] and heel[i] > threshold:
                    peaks.append(i)
                    # prev value less than present it is grator than or equal to next and grater than threshould
            # if not peaks:  # Check if the list is empty
            #     print("peak list is empty. Cannot extract ranges.")
            #     return []
            # Identify clusters of nearby peaks
            clustered_peaks = []
            current_cluster = [peaks[0]]
            for i in range(1, len(peaks)):
                if peaks[i] - peaks[i - 1] <= 5:
                    current_cluster.append(peaks[i])
                else:
                    # Calculate the median of the current cluster and store it
                    clustered_peaks.append(int(np.median(current_cluster)))
                    current_cluster = [peaks[i]]

            # Include the last cluster
            # clustered_peaks.append(int(np.median(current_cluster)))

            # Get corresponding time values for peaks
            peak_times = [t[i] for i in clustered_peaks]

            # Store first_intersection_time values in an array
            first_intersection_times = []
            samples_for_first_intersection = []
            indices_for_first_intersection = []

            # Plot the original signal and the identified peaks
            # plt.plot(t, heel, label='Heel Pressure')
            # plt.plot(t, toe, label='Toe Pressure')
            #plt.plot(peak_times, [heel[i] for i in clustered_peaks], 'gx')

            # Plot segments between intersections
            for i in range(len(clustered_peaks)):
                if i < len(clustered_peaks) - 1:
                    start_index = clustered_peaks[i]
                    end_index = clustered_peaks[i + 1]

                    # Find the first intersection point between 'heel' and 'toe' signals
                    # intersections = np.where(np.diff(np.sign(heel[start_index:end_index] - toe[start_index:end_index])))[0]
                    heel_array = np.array(heel[start_index:end_index])
                    toe_array = np.array(toe[start_index:end_index])

                    intersections = np.where(np.diff(np.sign(heel_array - toe_array)))[0]

                    if len(intersections) > 0:
                        # Get the time value of the first intersection
                        first_intersection_time = t[start_index:end_index][intersections[0]]
                        first_intersection_times.append(first_intersection_time)

                        # Store corresponding samples and indices
                        sample_index = start_index + intersections[0]
                        samples_for_first_intersection.append(heel[sample_index])
                        indices_for_first_intersection.append(sample_index)

                        # Plot the segment between consecutive intersections
                        # plt.axvline(first_intersection_time, color='red', linestyle='--')

            # Store start time, end time, and first intersection times in a single array
            time_array = [t[0]] + first_intersection_times + [t[-1]]
            ta = time_array
            # print(time_array)
            indices_for_first_intersection = [0] + indices_for_first_intersection + [len(heel) - 1]

            # Print the array of start_time, end_time, first_intersection_times, and corresponding samples and indices
            #     print("Stride Time:", time_array)
            #     print("Samples:", samples_for_first_intersection)
            #     print("Sample Indices:", indices_for_first_intersection)

            return indices_for_first_intersection

        columns = list(zip(*svalues))

        # Unpack the columns into separate variables
        s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, t12 = columns


        # toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]
        toe = [sum(x) / len(x) for x in zip(s1, s2)]
        # print("toe.....................",toe)
        heel = [sum(x) / len(x) for x in zip(s4, s5)]
        # print("heel.....................",heel)


        # print("time..............",t12)

        Fs = 40
        # Extract ranges using the function
        ranges = extract_ranges(t12, heel, toe)
        # rts= extract_ranges(t,heel,toe)
        # ranges,tim=rts
        # ranges = [int(x) for x in franges]
        tim_array = []
        for ty in range(0, len(ranges)):
            # print(t[ranges[ty]],end=" ")
            tim_array.append(int(t12[ranges[ty]]))
        # Initialize an empty list to store all position values values
        print("times",tim_array)
        print("ranges",ranges)
        # print("time values",tim_array)

        max_pos_values = []
        max_pos_time = []
        # print("len of ranges",len(ranges))
        # Perform processing for each range
        for i in range(len(ranges) - 1):
            # print("ï th value.........................................................", i)
            start_index = ranges[i]
            end_index = ranges[i + 1]
            axt = s6[start_index:end_index]
            accX = [float(value) / 9.8 for value in axt]

            ayt = s7[start_index:end_index]
            accY = [float(value) / 9.8 for value in ayt]

            azt = s8[start_index:end_index]
            accZ = [float(value) / 9.8 for value in azt]

            gxt = s9[start_index:end_index]
            gyrX = [float(value) * 57.29 for value in gxt]

            gyt = s10[start_index:end_index]
            gyrY = [float(value) * 57.29 for value in gyt]

            gzt = s11[start_index:end_index]
            gyrZ = [float(value) * 57.29 for value in gzt]

            t = t12[start_index:end_index]

            # print("here...............345...............")
            t11 = t
            L1 = len(t)
            time = np.arange(L1)
            # print("time is ..............",t)
            # step4

            # acc_mag = np.sqrt(accX ** 2 + accY ** 2 + accZ ** 2)
            # Convert lists to NumPy arrays
            accX_array = np.array(accX)
            accY_array = np.array(accY)
            accZ_array = np.array(accZ)

            # Calculate the magnitude of acceleration
            acc_mag = np.sqrt(accX_array ** 2 + accY_array ** 2 + accZ_array ** 2)
            # print("acc_mag",acc_mag)
            # Detect stationary periods
            sample_period = 1 / Fs
            filt_cutoff = 0.0001

            # High-pass filter accelerometer data
            b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'high')
            acc_magFilt = filtfilt(b, a, acc_mag)
            acc_magFilt = np.abs(acc_magFilt)

            # Low-pass filter accelerometer data
            filt_cutoff = 5
            b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'low')
            acc_magFilt = filtfilt(b, a, acc_magFilt)

            # Threshold detection
            stationary = acc_magFilt < (0.03)

            # step 5
            # Compute orientation
            quat = np.zeros((len(time), 4))
            AHRSalgorithm = AHRS('SamplePeriod', 1 / Fs, 'Kp', 1, 'KpInit', 1)

            # Initial convergence
            initPeriod = 2
            indexSel = np.arange(np.argmax(time > (time[0] + initPeriod)))
            for i in range(500):
                # print("11111111111111111111111111111111")
                # AHRSalgorithm.UpdateIMU([0, 0, 0], [np.mean(accX[indexSel]), np.mean(accY[indexSel]), np.mean(accZ[indexSel])])
                AHRSalgorithm.UpdateIMU([0, 0, 0],
                                        [np.mean(accX_array[indexSel]), np.mean(accY_array[indexSel]), np.mean(accZ_array[indexSel])])
                # print("111111111111111222222222222222222222")
            # For all data
            for t in range(len(time)):
                if stationary[t]:
                    AHRSalgorithm.Kp = 0.01
                else:
                    AHRSalgorithm.Kp = 0.01
                AHRSalgorithm.UpdateIMU(np.deg2rad([gyrX[t], gyrY[t], gyrZ[t]]), [accX[t], accY[t], accZ[t]])
                quat[t, :] = AHRSalgorithm.Quaternion
                # print((quat[t,:]))


            # Compute translational accelerations
            # Rotate accelerations from sensor frame to Earth frame
            # Function to rotate vector v by quaternion q
            def quatern_conj(q):
                if q.ndim == 1:
                    return np.array([q[0], -q[1], -q[2], -q[3]])
                elif q.ndim == 2:
                    return np.array([q[:, 0], -q[:, 1], -q[:, 2], -q[:, 3]]).T
                else:
                    raise ValueError("Invalid dimension for quaternion array")


            def quatern_rotate(v, q):
                q_conj = quatern_conj(q)
                v_quat = np.concatenate(([0], v))
                result_quat = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)
                return result_quat[1:]


            def quaternion_multiply(q1, q2):
                w1, x1, y1, z1 = q1
                w2, x2, y2, z2 = q2
                w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
                x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
                y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
                z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
                return np.array([w, x, y, z])


            # step6

            # compute transilational acceleration

            acc1 = np.column_stack((accX, accY, accZ))
            quat_conj = quatern_conj(quat)
            # print(quat_conj)

            acc2 = np.array([quatern_rotate(row, quat_conj[i, :]) for i, row in enumerate(acc1)])
            # print(acc2 )

            acc = acc2 * 9.8

            acc[:, 2] -= 9.8

            # plt.figure(figsize=(9, 3))
            # plt.plot(time, acc[:, 0], 'r', label='X')
            # plt.plot(time, acc[:, 1], 'g', label='Y')
            # plt.plot(time, acc[:, 2], 'b', label='Z')
            # plt.title('Acceleration')
            # plt.xlabel('Time (s)')
            # plt.ylabel('Acceleration (m/s/s)')
            # plt.legend()
            # # plt.show()

            time = np.array(time)

            # step 7
            # Integrate acceleration to yield velocity
            vel = np.zeros(acc.shape)
            for t in range(1, vel.shape[0]):
                vel[t, :] = vel[t - 1, :] + acc[t, :] * sample_period
                if stationary[t] == 1:
                    vel[t, :] = [0, 0, 0]  # apply ZUPT update when foot stationary

            # plt.figure()
            # plt.plot(vel)
            # plt.show()

            # Compute integral drift during non-stationary periods
            velDrift = np.zeros(vel.shape)
            stationaryStart = np.where(np.diff(stationary) == 1)[0]
            stationaryEnd = np.where(np.diff(stationary) == -1)[0]
            for i in range(len(stationaryEnd)):
                driftRate = vel[stationaryStart[i] - 1, :] / (stationaryStart[i] - stationaryEnd[i])
                enum = np.arange(1, stationaryStart[i] - stationaryEnd[i] + 1)
                drift = np.column_stack((enum * driftRate[0], enum * driftRate[1], enum * driftRate[2]))
                velDrift[stationaryEnd[i]:stationaryStart[i] - 1, :] = drift

            # Remove integral drift
            vel = vel - velDrift

            # Compute translational position

            # Integrate velocity to yield position
            pos = np.zeros(vel.shape)
            for t in range(1, pos.shape[0]):
                pos[t, :] = pos[t - 1, :] + vel[t, :] * sample_period

            # Plot translational position
            # y axis for ward, backward movement (new insole)
            # x axis for up/down
            # mahipal old data which uses x(forward/backward)

            # plt.figure(figsize=(9, 6))
            # # plt.plot(time, pos[:, 0], 'r')
            # plt.plot(time, pos[:, 1], 'g')
            #
            # plt.title('Position')
            # plt.xlabel('samples')
            # plt.ylabel('Position (m)')
            # plt.legend(['X', 'Y', 'Z'])
            # plt.show()
            posX = np.abs(pos[:, 1])
            # pos[:,0] means x axis(old insole(mahipal data)). pos[:,1] for new insole(yaxis is x here)
            # print("posX values...",posX)
            print("Max value of position...",np.max(posX))
            max_pos = np.max(posX)
            # print("t11 is ",t11, time)
            #
            # # Find the index of the maximum value in sl
            # max_index = np.argmax(posX1)
            #
            # # Get the corresponding time from tm
            # # max_time = t11[max_index]
            # max_time = t11[max_index]
            # # Get the maximum value in sl
            # max_pos = np.max(posX1)

            max_pos_values.append(max_pos)
            # print("max_pos_values", max_pos_values)
            # print("sum of distance:", np.sum(max_pos_values))
            # max_pos_time.append(max_time)
            # print(np.sum(max_pos_values))
            # print("last",posX1[len(posX1)- 1])

            # a = (max_pos + posX1[len(posX1)- 1])/2
            # print("a=",a)
            # print(np.mean(posX1[len(posX1)- 1]))
            # max_pos_array = np.array(max_pos_values)
        print("computed positions............", max_pos_values)
        print("computed times ..............", tim_array)
        # # print("finally time............",max_pos_time)
        #
        #
        if (len(ranges) >0):
                timestart = tim_array[0]
                sc = 1
                stride = []
                tsum = 0
                print(len(max_pos_values))
                for ts in range(1, (len(max_pos_values) )):
                    print(ts, tim_array[ts], max_pos_values[ts])
                    tt = tim_array[ts] - timestart
                    # stride.append({"strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),
                    #                    "velocity": (max_pos_values[ts] / float(tt * 0.001))})
                    stride.append({"strideno": sc, "dist": max_pos_values[ts], "time": tim_array[ts],
                                   "velocity": (max_pos_values[ts] / float(tt * 0.001))})
                    timestart = tim_array[ts]
                    sc = sc + 1
                    tsum = tsum + max_pos_values[ts]

                print("strides  :", stride)
                print("total distance :", tsum, "m/s2")
                return stride
        else:
             print("No strides detected.........................")
             return []



##########################################################################################################

def strideahrs16(s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,t12,s14,s15,s16,s17,s18):
    # toe = s2.toDouble() + s3.toDouble() + s4.toDouble()+ s5.toDouble()
    # heal = s8.toDouble() + s9.toDouble()+ s10.toDouble()
    # step 2 - AHRS class
    class AHRS:
        def __init__(self, *args):
            self.SamplePeriod = 1 / 33
            self.Quaternion = [1, 0, 0, 0]
            self.Kp = 2
            self.Ki = 0
            self.KpInit = 200
            self.InitPeriod = 5
            self.q = [1, 0, 0, 0]
            self.IntError = [0, 0, 0]
            self.KpRamped = None
            for i in range(0, len(args), 2):
                if args[i] == 'SamplePeriod':
                    self.SamplePeriod = args[i + 1]
                elif args[i] == 'Quaternion':
                    self.Quaternion = args[i + 1]
                    self.q = self.quaternConj(self.Quaternion)
                elif args[i] == 'Kp':
                    self.Kp = args[i + 1]
                elif args[i] == 'Ki':
                    self.Ki = args[i + 1]
                elif args[i] == 'KpInit':
                    self.KpInit = args[i + 1]
                elif args[i] == 'InitPeriod':
                    self.InitPeriod = args[i + 1]
                else:
                    raise ValueError('Invalid argument')
            self.KpRamped = self.KpInit

        def Update(self, Gyroscope, Accelerometer, Magnetometer):
            raise NotImplementedError('This method is unimplemented')

        def UpdateIMU(self, Gyroscope, Accelerometer):
            if norm(Accelerometer) == 0:
                print('Accelerometer magnitude is zero. Algorithm update aborted.')
                return
            else:
                Accelerometer = Accelerometer / norm(Accelerometer)
            v = [2 * (self.q[1] * self.q[3] - self.q[0] * self.q[2]),
                 2 * (self.q[2] * self.q[3] + self.q[0] * self.q[1]),
                 self.q[0] ** 2 - self.q[1] ** 2 - self.q[2] ** 2 + self.q[3] ** 2]
            error = np.cross(v, Accelerometer)
            self.IntError = self.IntError + error
            Ref = Gyroscope - (self.Kp * error + self.Ki * self.IntError)
            pDot = 0.5 * self.quaternProd(self.q, [0, float(Ref[0]), float(Ref[1]), float(Ref[2])])
            self.q = self.q + pDot * self.SamplePeriod
            self.q = self.q / norm(self.q)
            self.Quaternion = self.quaternConj(self.q)

        def quaternProd(self, a, b):
            # Ensure a and b are lists or arrays
            a = np.array(a)
            b = np.array(b)

            ab = np.array([
                a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
                a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
                a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
                a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]
            ])
            return ab

        def quaternConj(self, q):
            qConj = [q[0], -q[1], -q[2], -q[3]]
            return qConj

    # step3

    def quaternProd(a, b):
        ab = [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
              a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
              a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
              a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]]
        # print(ab)
        return ab

    def quaternConj(q):
        qConj = [q[0], -q[1], -q[2], -q[3]]
        # print(qConj)
        return qConj

    def quaternRotate(v, q):
        row, col = v.shape
        v0XYZ = quaternProd(quaternProd(q, np.hstack((np.zeros((row, 1)), v))), quaternConj(q))
        v = np.array(v0XYZ)[:, 1:4]
        return v

    def extract_ranges(t, heel, toe, threshold=650):
        # Detect peaks using the specified method
        peaks = []
        for i in range(1, len(heel) - 1):  # 1 to last index
            if heel[i - 1] < heel[i] >= heel[i + 1] and heel[i] > threshold:
                peaks.append(i)
                # prev value less than present it is grator than or equal to next and grater than threshould
        # if not peaks:  # Check if the list is empty
        #     print("peak list is empty. Cannot extract ranges.")
        #     return []
        # Identify clusters of nearby peaks
        clustered_peaks = []
        current_cluster = [peaks[0]]
        for i in range(1, len(peaks)):
            if peaks[i] - peaks[i - 1] <= 5:
                current_cluster.append(peaks[i])
            else:
                # Calculate the median of the current cluster and store it
                clustered_peaks.append(int(np.median(current_cluster)))
                current_cluster = [peaks[i]]

        # Include the last cluster
        # clustered_peaks.append(int(np.median(current_cluster)))

        # Get corresponding time values for peaks
        peak_times = [t[i] for i in clustered_peaks]

        # Store first_intersection_time values in an array
        first_intersection_times = []
        samples_for_first_intersection = []
        indices_for_first_intersection = []

        # Plot the original signal and the identified peaks
        # plt.plot(t, heel, label='Heel Pressure')
        # plt.plot(t, toe, label='Toe Pressure')
        # plt.plot(peak_times, [heel[i] for i in clustered_peaks], 'gx')

        # Plot segments between intersections
        for i in range(len(clustered_peaks)):
            if i < len(clustered_peaks) - 1:
                start_index = clustered_peaks[i]
                end_index = clustered_peaks[i + 1]

                # Find the first intersection point between 'heel' and 'toe' signals
                # intersections = np.where(np.diff(np.sign(heel[start_index:end_index] - toe[start_index:end_index])))[0]
                heel_array = np.array(heel[start_index:end_index])
                toe_array = np.array(toe[start_index:end_index])

                intersections = np.where(np.diff(np.sign(heel_array - toe_array)))[0]

                if len(intersections) > 0:
                    # Get the time value of the first intersection
                    first_intersection_time = t[start_index:end_index][intersections[0]]
                    first_intersection_times.append(first_intersection_time)

                    # Store corresponding samples and indices
                    sample_index = start_index + intersections[0]
                    samples_for_first_intersection.append(heel[sample_index])
                    indices_for_first_intersection.append(sample_index)

                    # Plot the segment between consecutive intersections
                    # plt.axvline(first_intersection_time, color='red', linestyle='--')

        # Store start time, end time, and first intersection times in a single array
        time_array = [t[0]] + first_intersection_times + [t[-1]]
        ta = time_array
        # print(time_array)
        indices_for_first_intersection = [0] + indices_for_first_intersection + [len(heel) - 1]

        # Print the array of start_time, end_time, first_intersection_times, and corresponding samples and indices
        #     print("Stride Time:", time_array)
        #     print("Samples:", samples_for_first_intersection)
        #     print("Sample Indices:", indices_for_first_intersection)

        return indices_for_first_intersection

    columns = list(zip(*svalues))

    # Unpack the columns into separate variables
    # s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, t12 = columns

    # toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]
    toe = [sum(x) / len(x) for x in zip(s2,s3,s4,s5)]
    # print("toe.....................",toe)
    heel = [sum(x) / len(x) for x in zip(s8,s9,s10)]
    # print("heel.....................",heel)

    # print("time..............",t12)

    Fs = 40
    # Extract ranges using the function
    ranges = extract_ranges(t12, heel, toe)
    # rts= extract_ranges(t,heel,toe)
    # ranges,tim=rts
    # ranges = [int(x) for x in franges]
    tim_array = []
    for ty in range(0, len(ranges)):
        # print(t[ranges[ty]],end=" ")
        tim_array.append(int(t12[ranges[ty]]))
    # Initialize an empty list to store all position values values
    print("times", tim_array)
    print("ranges", ranges)
    # print("time values",tim_array)

    max_pos_values = []
    max_pos_time = []
    # print("len of ranges",len(ranges))
    # Perform processing for each range
    for i in range(len(ranges) - 1):
        # print("ï th value.........................................................", i)
        start_index = ranges[i]
        end_index = ranges[i + 1]
        axt = s6[start_index:end_index]
        accX = [float(value) / 9.8 for value in axt]

        ayt = s7[start_index:end_index]
        accY = [float(value) / 9.8 for value in ayt]

        azt = s8[start_index:end_index]
        accZ = [float(value) / 9.8 for value in azt]

        gxt = s9[start_index:end_index]
        gyrX = [float(value) * 57.29 for value in gxt]

        gyt = s10[start_index:end_index]
        gyrY = [float(value) * 57.29 for value in gyt]

        gzt = s11[start_index:end_index]
        gyrZ = [float(value) * 57.29 for value in gzt]

        t = t12[start_index:end_index]

        # print("here...............345...............")
        t11 = t
        L1 = len(t)
        time = np.arange(L1)
        # print("time is ..............",t)
        # step4

        # acc_mag = np.sqrt(accX ** 2 + accY ** 2 + accZ ** 2)
        # Convert lists to NumPy arrays
        accX_array = np.array(accX)
        accY_array = np.array(accY)
        accZ_array = np.array(accZ)

        # Calculate the magnitude of acceleration
        acc_mag = np.sqrt(accX_array ** 2 + accY_array ** 2 + accZ_array ** 2)
        # print("acc_mag",acc_mag)
        # Detect stationary periods
        sample_period = 1 / Fs
        filt_cutoff = 0.0001

        # High-pass filter accelerometer data
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'high')
        acc_magFilt = filtfilt(b, a, acc_mag)
        acc_magFilt = np.abs(acc_magFilt)

        # Low-pass filter accelerometer data
        filt_cutoff = 5
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'low')
        acc_magFilt = filtfilt(b, a, acc_magFilt)

        # Threshold detection
        stationary = acc_magFilt < (0.03)

        # step 5
        # Compute orientation
        quat = np.zeros((len(time), 4))
        AHRSalgorithm = AHRS('SamplePeriod', 1 / Fs, 'Kp', 1, 'KpInit', 1)

        # Initial convergence
        initPeriod = 2
        indexSel = np.arange(np.argmax(time > (time[0] + initPeriod)))
        for i in range(500):
            # print("11111111111111111111111111111111")
            # AHRSalgorithm.UpdateIMU([0, 0, 0], [np.mean(accX[indexSel]), np.mean(accY[indexSel]), np.mean(accZ[indexSel])])
            AHRSalgorithm.UpdateIMU([0, 0, 0],
                                    [np.mean(accX_array[indexSel]), np.mean(accY_array[indexSel]),
                                     np.mean(accZ_array[indexSel])])
            # print("111111111111111222222222222222222222")
        # For all data
        for t in range(len(time)):
            if stationary[t]:
                AHRSalgorithm.Kp = 0.01
            else:
                AHRSalgorithm.Kp = 0.01
            AHRSalgorithm.UpdateIMU(np.deg2rad([gyrX[t], gyrY[t], gyrZ[t]]), [accX[t], accY[t], accZ[t]])
            quat[t, :] = AHRSalgorithm.Quaternion
            # print((quat[t,:]))

        # Compute translational accelerations
        # Rotate accelerations from sensor frame to Earth frame
        # Function to rotate vector v by quaternion q
        def quatern_conj(q):
            if q.ndim == 1:
                return np.array([q[0], -q[1], -q[2], -q[3]])
            elif q.ndim == 2:
                return np.array([q[:, 0], -q[:, 1], -q[:, 2], -q[:, 3]]).T
            else:
                raise ValueError("Invalid dimension for quaternion array")

        def quatern_rotate(v, q):
            q_conj = quatern_conj(q)
            v_quat = np.concatenate(([0], v))
            result_quat = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)
            return result_quat[1:]

        def quaternion_multiply(q1, q2):
            w1, x1, y1, z1 = q1
            w2, x2, y2, z2 = q2
            w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
            x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
            y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
            z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
            return np.array([w, x, y, z])

        # step6

        # compute transilational acceleration

        acc1 = np.column_stack((accX, accY, accZ))
        quat_conj = quatern_conj(quat)
        # print(quat_conj)

        acc2 = np.array([quatern_rotate(row, quat_conj[i, :]) for i, row in enumerate(acc1)])
        # print(acc2 )

        acc = acc2 * 9.8

        acc[:, 2] -= 9.8

        # plt.figure(figsize=(9, 3))
        # plt.plot(time, acc[:, 0], 'r', label='X')
        # plt.plot(time, acc[:, 1], 'g', label='Y')
        # plt.plot(time, acc[:, 2], 'b', label='Z')
        # plt.title('Acceleration')
        # plt.xlabel('Time (s)')
        # plt.ylabel('Acceleration (m/s/s)')
        # plt.legend()
        # # plt.show()

        time = np.array(time)

        # step 7
        # Integrate acceleration to yield velocity
        vel = np.zeros(acc.shape)
        for t in range(1, vel.shape[0]):
            vel[t, :] = vel[t - 1, :] + acc[t, :] * sample_period
            if stationary[t] == 1:
                vel[t, :] = [0, 0, 0]  # apply ZUPT update when foot stationary

        # plt.figure()
        # plt.plot(vel)
        # plt.show()

        # Compute integral drift during non-stationary periods
        velDrift = np.zeros(vel.shape)
        stationaryStart = np.where(np.diff(stationary) == 1)[0]
        stationaryEnd = np.where(np.diff(stationary) == -1)[0]
        for i in range(len(stationaryEnd)):
            driftRate = vel[stationaryStart[i] - 1, :] / (stationaryStart[i] - stationaryEnd[i])
            enum = np.arange(1, stationaryStart[i] - stationaryEnd[i] + 1)
            drift = np.column_stack((enum * driftRate[0], enum * driftRate[1], enum * driftRate[2]))
            velDrift[stationaryEnd[i]:stationaryStart[i] - 1, :] = drift

        # Remove integral drift
        vel = vel - velDrift

        # Compute translational position

        # Integrate velocity to yield position
        pos = np.zeros(vel.shape)
        for t in range(1, pos.shape[0]):
            pos[t, :] = pos[t - 1, :] + vel[t, :] * sample_period

        # Plot translational position
        # y axis for ward, backward movement (new insole)
        # x axis for up/down
        # mahipal old data which uses x(forward/backward)

        # plt.figure(figsize=(9, 6))
        # # plt.plot(time, pos[:, 0], 'r')
        # plt.plot(time, pos[:, 1], 'g')
        #
        # plt.title('Position')
        # plt.xlabel('samples')
        # plt.ylabel('Position (m)')
        # plt.legend(['X', 'Y', 'Z'])
        # plt.show()
        posX = np.abs(pos[:, 1])
        # pos[:,0] means x axis(old insole(mahipal data)). pos[:,1] for new insole(yaxis is x here)
        # print("posX values...",posX)
        print("Max value of position...", np.max(posX))
        max_pos = np.max(posX)
        # print("t11 is ",t11, time)
        #
        # # Find the index of the maximum value in sl
        # max_index = np.argmax(posX1)
        #
        # # Get the corresponding time from tm
        # # max_time = t11[max_index]
        # max_time = t11[max_index]
        # # Get the maximum value in sl
        # max_pos = np.max(posX1)

        max_pos_values.append(max_pos)
        # print("max_pos_values", max_pos_values)
        # print("sum of distance:", np.sum(max_pos_values))
        # max_pos_time.append(max_time)
        # print(np.sum(max_pos_values))
        # print("last",posX1[len(posX1)- 1])

        # a = (max_pos + posX1[len(posX1)- 1])/2
        # print("a=",a)
        # print(np.mean(posX1[len(posX1)- 1]))
        # max_pos_array = np.array(max_pos_values)
    print("computed positions............", max_pos_values)
    print("computed times ..............", tim_array)
    # # print("finally time............",max_pos_time)
    #
    #
    if (len(ranges) > 0):
        timestart = tim_array[0]
        sc = 1
        stride = []
        tsum = 0
        print(len(max_pos_values))
        for ts in range(1, (len(max_pos_values))):
            print(ts, tim_array[ts], max_pos_values[ts])
            tt = tim_array[ts] - timestart
            # stride.append({"strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),
            #                    "velocity": (max_pos_values[ts] / float(tt * 0.001))})
            stride.append({"strideno": sc, "dist": max_pos_values[ts], "time": tim_array[ts],
                           "velocity": (max_pos_values[ts] / float(tt * 0.001))})
            timestart = tim_array[ts]
            sc = sc + 1
            tsum = tsum + max_pos_values[ts]

        print("strides  :", stride)
        print("total distance :", tsum, "m/s2")
        return stride
    else:
        print("No strides detected.........................")
        return []


##########################################################################################################
#########################################################################################################


def strideahrsmod(svalues, nos):
        print("nos is", nos)
        print("len of svals in strideahrsmod() ",len(svalues))
        # step 2 - AHRS class
        class AHRS:
            def __init__(self, *args):
                self.SamplePeriod = 1 / 33
                self.Quaternion = [1, 0, 0, 0]
                self.Kp = 2
                self.Ki = 0
                self.KpInit = 200
                self.InitPeriod = 5
                self.q = [1, 0, 0, 0]
                self.IntError = [0, 0, 0]
                self.KpRamped = None
                for i in range(0, len(args), 2):
                    if args[i] == 'SamplePeriod':
                        self.SamplePeriod = args[i + 1]
                    elif args[i] == 'Quaternion':
                        self.Quaternion = args[i + 1]
                        self.q = self.quaternConj(self.Quaternion)
                    elif args[i] == 'Kp':
                        self.Kp = args[i + 1]
                    elif args[i] == 'Ki':
                        self.Ki = args[i + 1]
                    elif args[i] == 'KpInit':
                        self.KpInit = args[i + 1]
                    elif args[i] == 'InitPeriod':
                        self.InitPeriod = args[i + 1]
                    else:
                        raise ValueError('Invalid argument')
                self.KpRamped = self.KpInit

            def Update(self, Gyroscope, Accelerometer, Magnetometer):
                raise NotImplementedError('This method is unimplemented')

            def UpdateIMU(self, Gyroscope, Accelerometer):
                if norm(Accelerometer) == 0:
                    print('Accelerometer magnitude is zero. Algorithm update aborted.')
                    return
                else:
                    Accelerometer = Accelerometer / norm(Accelerometer)
                v = [2 * (self.q[1] * self.q[3] - self.q[0] * self.q[2]),
                     2 * (self.q[2] * self.q[3] + self.q[0] * self.q[1]),
                     self.q[0] ** 2 - self.q[1] ** 2 - self.q[2] ** 2 + self.q[3] ** 2]
                error = np.cross(v, Accelerometer)
                self.IntError = self.IntError + error
                Ref = Gyroscope - (self.Kp * error + self.Ki * self.IntError)
                pDot = 0.5 * self.quaternProd(self.q, [0, float(Ref[0]), float(Ref[1]), float(Ref[2])])
                self.q = self.q + pDot * self.SamplePeriod
                self.q = self.q / norm(self.q)
                self.Quaternion = self.quaternConj(self.q)

            def quaternProd(self, a, b):
                # Ensure a and b are lists or arrays
                a = np.array(a)
                b = np.array(b)

                ab = np.array([
                    a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
                    a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
                    a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
                    a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]
                ])
                return ab

            def quaternConj(self, q):
                qConj = [q[0], -q[1], -q[2], -q[3]]
                return qConj


        # step3

        def quaternProd(a, b):
            ab = [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
                  a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
                  a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
                  a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]]
            # print(ab)
            return ab


        def quaternConj(q):
            qConj = [q[0], -q[1], -q[2], -q[3]]
            # print(qConj)
            return qConj


        def quaternRotate(v, q):
            row, col = v.shape
            v0XYZ = quaternProd(quaternProd(q, np.hstack((np.zeros((row, 1)), v))), quaternConj(q))
            v = np.array(v0XYZ)[:, 1:4]
            return v


        def extract_ranges(t, heel, toe, threshold=650):
            print("in_extract_ranges()................")
            # Detect peaks using the specified method
            peaks = []
            for i in range(1, len(heel) - 1):  # 1 to last index
                if heel[i - 1] < heel[i] >= heel[i + 1] and heel[i] > threshold:
                    peaks.append(i)
                    # prev value less than present it is grator than or equal to next and grater than threshould
            # if not peaks:  # Check if the list is empty
            #     print("peak list is empty. Cannot extract ranges.")
            #     return []
            # Identify clusters of nearby peaks
            if peaks == [] :
                return []
            clustered_peaks = []
            current_cluster = [peaks[0]]
            for i in range(1, len(peaks)):
                if peaks[i] - peaks[i - 1] <= 5:
                    current_cluster.append(peaks[i])
                else:
                    # Calculate the median of the current cluster and store it
                    clustered_peaks.append(int(np.median(current_cluster)))
                    current_cluster = [peaks[i]]

            # Include the last cluster
            # clustered_peaks.append(int(np.median(current_cluster)))

            # Get corresponding time values for peaks
            peak_times = [t[i] for i in clustered_peaks]

            # Store first_intersection_time values in an array
            first_intersection_times = []
            samples_for_first_intersection = []
            indices_for_first_intersection = []

            # Plot the original signal and the identified peaks
            # plt.plot(t, heel, label='Heel Pressure')
            # plt.plot(t, toe, label='Toe Pressure')
            #plt.plot(peak_times, [heel[i] for i in clustered_peaks], 'gx')

            # Plot segments between intersections
            for i in range(len(clustered_peaks)):
                if i < len(clustered_peaks) - 1:
                    start_index = clustered_peaks[i]
                    end_index = clustered_peaks[i + 1]

                    # Find the first intersection point between 'heel' and 'toe' signals
                    # intersections = np.where(np.diff(np.sign(heel[start_index:end_index] - toe[start_index:end_index])))[0]
                    heel_array = np.array(heel[start_index:end_index])
                    toe_array = np.array(toe[start_index:end_index])

                    intersections = np.where(np.diff(np.sign(heel_array - toe_array)))[0]

                    if len(intersections) > 0:
                        # Get the time value of the first intersection
                        first_intersection_time = t[start_index:end_index][intersections[0]]
                        first_intersection_times.append(first_intersection_time)

                        # Store corresponding samples and indices
                        sample_index = start_index + intersections[0]
                        samples_for_first_intersection.append(heel[sample_index])
                        indices_for_first_intersection.append(sample_index)

                        # Plot the segment between consecutive intersections
                        # plt.axvline(first_intersection_time, color='red', linestyle='--')

            # Store start time, end time, and first intersection times in a single array
            time_array = [t[0]] + first_intersection_times + [t[-1]]
            ta = time_array
            # print(time_array)
            indices_for_first_intersection = [0] + indices_for_first_intersection + [len(heel) - 1]

            # Print the array of start_time, end_time, first_intersection_times, and corresponding samples and indices
            #     print("Stride Time:", time_array)
            #     print("Samples:", samples_for_first_intersection)
            #     print("Sample Indices:", indices_for_first_intersection)
            print("in extract_ranges()...........", indices_for_first_intersection)
            return indices_for_first_intersection

        columns = list(zip(*svalues))

        if (nos == "11") :
            # Unpack the columns into separate variables-----------'L/R'
            s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, t12 = columns
            print("in 11 sensor data  extracted...................................")
            # For Toe: s1,s2,s3 and for Heel: s4,s5.
            toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]
            heel = [sum(x) / len(x) for x in zip(s4, s5)]
            print("toe and heel computed .................")

        else :
            # Unpack the columns into separate variables-----------'L/R'
            #<---5 fsr  -->|<---imu----------->|stepcount|                      |<-2nd part  5 FSR->|
            #s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11  s12 s13   soletype capturedtime s14 15 s16 s17 s18
            s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, stype, t12, s14, s15, s16, s17, s18 = columns
            #For Toe: s3,s4,s5,s6 and for Heel: s8,s9,s10.
            toe = [sum(x) / len(x) for x in zip(s3, s4, s5, s14)]
            heel = [sum(x) / len(x) for x in zip(s16, s17, s18)]

        Fs = 40
        ranges=[]
        # Extract ranges using the function
        ranges = extract_ranges(t12, heel, toe)
        tim_array = []
        if len(ranges) == 0 :
            print("no ranges detected .............")
            return []
        for ty in range(0, len(ranges)):
            tim_array.append(int(t12[ranges[ty]]))

        # Initialize an empty list to store all position values values
        print("times",tim_array)
        print("ranges",ranges)

        max_pos_values = []
        max_pos_time = []
        # Perform processing for each range
        for i in range(len(ranges) - 1):
            # print("ï th value.........................................................", i)
            start_index = ranges[i]
            end_index = ranges[i + 1]
            axt = s6[start_index:end_index]
            accX = [float(value) / 9.8 for value in axt]

            ayt = s7[start_index:end_index]
            accY = [float(value) / 9.8 for value in ayt]

            azt = s8[start_index:end_index]
            accZ = [float(value) / 9.8 for value in azt]

            gxt = s9[start_index:end_index]
            gyrX = [float(value) * 57.29 for value in gxt]

            gyt = s10[start_index:end_index]
            gyrY = [float(value) * 57.29 for value in gyt]

            gzt = s11[start_index:end_index]
            gyrZ = [float(value) * 57.29 for value in gzt]

            t = t12[start_index:end_index]

            t11 = t
            L1 = len(t)
            time = np.arange(L1)
            # step4

            # acc_mag = np.sqrt(accX ** 2 + accY ** 2 + accZ ** 2)
            # Convert lists to NumPy arrays
            accX_array = np.array(accX)
            accY_array = np.array(accY)
            accZ_array = np.array(accZ)

            # Calculate the magnitude of acceleration
            acc_mag = np.sqrt(accX_array ** 2 + accY_array ** 2 + accZ_array ** 2)
            # print("acc_mag",acc_mag)
            # Detect stationary periods
            sample_period = 1 / Fs
            filt_cutoff = 0.0001

            # High-pass filter accelerometer data
            b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'high')
            acc_magFilt = filtfilt(b, a, acc_mag)
            acc_magFilt = np.abs(acc_magFilt)

            # Low-pass filter accelerometer data
            filt_cutoff = 5
            b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'low')
            acc_magFilt = filtfilt(b, a, acc_magFilt)
            # For  left insole  Stationary = 0.03, Kp1 = 0.01, Kp2 = 0.01.
            # For right  insole  Stationary = 0.05, Kp1 = 0.5, Kp2 = 0.4
            # Threshold detection
            stationary = acc_magFilt < (0.03)
            # step 5
            # Compute orientation
            quat = np.zeros((len(time), 4))
            AHRSalgorithm = AHRS('SamplePeriod', 1 / Fs, 'Kp', 1, 'KpInit', 1)

            # Initial convergence
            initPeriod = 2
            indexSel = np.arange(np.argmax(time > (time[0] + initPeriod)))
            for i in range(500):
                # print("11111111111111111111111111111111")
                # AHRSalgorithm.UpdateIMU([0, 0, 0], [np.mean(accX[indexSel]), np.mean(accY[indexSel]), np.mean(accZ[indexSel])])
                AHRSalgorithm.UpdateIMU([0, 0, 0],
                                        [np.mean(accX_array[indexSel]), np.mean(accY_array[indexSel]), np.mean(accZ_array[indexSel])])
                # print("111111111111111222222222222222222222")
            # For all data
            for t in range(len(time)):
                # For  left insole  Stationary = 0.03, Kp1 = 0.01, Kp2 = 0.01.
                # For right  insole  Stationary = 0.05, Kp1 = 0.5, Kp2 = 0.4
                if stationary[t]:
                        AHRSalgorithm.Kp = 0.01
                        #AHRSalgorithm.Kp = kval1
                else:
                        AHRSalgorithm.Kp = 0.01
                        #AHRSalgorithm.Kp = kval2
                AHRSalgorithm.UpdateIMU(np.deg2rad([gyrX[t], gyrY[t], gyrZ[t]]), [accX[t], accY[t], accZ[t]])
                quat[t, :] = AHRSalgorithm.Quaternion
                # print((quat[t,:]))


            # Compute translational accelerations
            # Rotate accelerations from sensor frame to E````````````````````````````````````````arth frame
            # Function to rotate vector v by quaternion q
            def quatern_conj(q):
                if q.ndim == 1:
                    return np.array([q[0], -q[1], -q[2], -q[3]])
                elif q.ndim == 2:
                    return np.array([q[:, 0], -q[:, 1], -q[:, 2], -q[:, 3]]).T
                else:
                    raise ValueError("Invalid dimension for quaternion array")


            def quatern_rotate(v, q):
                q_conj = quatern_conj(q)
                v_quat = np.concatenate(([0], v))
                result_quat = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)
                return result_quat[1:]


            def quaternion_multiply(q1, q2):
                w1, x1, y1, z1 = q1
                w2, x2, y2, z2 = q2
                w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
                x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
                y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
                z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
                return np.array([w, x, y, z])


            # step6

            # compute transilational acceleration

            acc1 = np.column_stack((accX, accY, accZ))
            quat_conj = quatern_conj(quat)
            # print(quat_conj)

            acc2 = np.array([quatern_rotate(row, quat_conj[i, :]) for i, row in enumerate(acc1)])
            # print(acc2 )

            acc = acc2 * 9.8

            acc[:, 2] -= 9.8

            time = np.array(time)

            # step 7
            # Integrate acceleration to yield velocity
            vel = np.zeros(acc.shape)
            for t in range(1, vel.shape[0]):
                vel[t, :] = vel[t - 1, :] + acc[t, :] * sample_period
                if stationary[t] == 1:
                    vel[t, :] = [0, 0, 0]  # apply ZUPT update when foot stationary

            # Compute integral drift during non-stationary periods
            velDrift = np.zeros(vel.shape)
            stationaryStart = np.where(np.diff(stationary) == 1)[0]
            stationaryEnd = np.where(np.diff(stationary) == -1)[0]
            for i in range(len(stationaryEnd)):
                driftRate = vel[stationaryStart[i] - 1, :] / (stationaryStart[i] - stationaryEnd[i])
                enum = np.arange(1, stationaryStart[i] - stationaryEnd[i] + 1)
                drift = np.column_stack((enum * driftRate[0], enum * driftRate[1], enum * driftRate[2]))
                velDrift[stationaryEnd[i]:stationaryStart[i] - 1, :] = drift

            # Remove integral drift
            vel = vel - velDrift

            # Compute translational position

            # Integrate velocity to yield position
            pos = np.zeros(vel.shape)
            for t in range(1, pos.shape[0]):
                pos[t, :] = pos[t - 1, :] + vel[t, :] * sample_period

            posX = np.abs(pos[:, 1])
            print("Max value of position...",np.max(posX))
            max_pos = np.max(posX)
            max_pos_values.append(max_pos)

        print("computed positions............", max_pos_values)
        print("computed times ..............", tim_array)
        if (len(ranges) >0):
                timestart = tim_array[0]
                sc = 1
                stride = []
                tsum = 0
                print(len(max_pos_values))
                for ts in range(1, (len(max_pos_values) )):
                    tt = ((tim_array[ts + 1] - 1) - tim_array[ts]) *0.001
                    print(ts, tim_array[ts], max_pos_values[ts], tt, (max_pos_values[ts] /tt))
                    stride.append({"strideno": sc, "dist": max_pos_values[ts], "time": tim_array[ts],
                                   "velocity": (max_pos_values[ts] /tt)})
                    sc = sc + 1
                    tsum = tsum + max_pos_values[ts]

                print("strides  :", stride)
                print("total distance :", tsum, "m/s2")
                return stride
        else:
             print("No strides detected.........................")
             return []






##########################################################################################################
#modified stridelenestimate() for every new sensor data inserted computes strides and writes a running strideno into onlinestride for that sessionid
###Adding new one 16 sensors

@api_view(["POST"])
def onlinestridecompute112(request):      #online stride computation using AHRS

        ssnid = request.data["sessionid"]
        # sarr should be  <sensor values from s1..s11>,<s12 and s13 for step size >solytype,capturedtime
        sarr = request.data["sensorvalues"]
        nos =request.data["totalsensor"]
        print("inside onlinestridecompute()..............")
        stimez = min(sublist[14] for sublist in sarr)
        etimez = max(sublist[14] for sublist in sarr)
        print("starttime is ", stimez, "endtime is:", etimez)
        print("total sensors.",nos)
        print("ssnid and sarr values........................................", ssnid, len(sarr))
        if int(nos) == 11:
            rr=0
            with connection.cursor() as cursor:
                cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
                for sval in sarr:
                    # print("row..", sval)
                    p = cursor.execute( "insert into sensordata(sessionid,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,timelocal) "
                                        "values(%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s, %s,%s, %s,%s,current_timestamp)",
                                        [ssnid, sval[0], sval[1], sval[2], sval[3], sval[4],  sval[5], sval[6], sval[7], sval[8], sval[9],
                                         sval[10],  sval[11], sval[12],  sval[13], sval[14]])
                    if p:
                        done = 1
                    else:
                        done = 0
                    rr=rr+1
            print("total right rows written:", rr)
        else :
            print("writting 16 sensor data....")
            ll=0
            # sarr should be  <sensor values from s1..s11>,<s12 and s13> for stepcount, <s14..s18> for 5 more fsr's ,solytype,capturedtime
            with connection.cursor() as cursor:
                    cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
                    for sval in sarr:
                            p = cursor.execute(
                                "insert into sensordata(sessionid,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,s14,s15,s16,s17,s18,timelocal) "
                                "values(%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s, %s,%s, %s,%s, %s,%s,%s,%s,%s,current_timestamp)",
                                [ssnid, sval[0], sval[1], sval[2], sval[3], sval[4],  sval[5], sval[6], sval[7], sval[8],sval[9],sval[10], sval[11], sval[12],  sval[13], sval[14], sval[15], sval[16], sval[17], sval[18],sval[19]])

                            if p:
                                done = 1
                            else:
                                done = 0
                            ll=ll+1
            print("total left rows written:",ll)
        #get last strideno  stored for both left and right  for sessionid in onlinestride for both soletypes
        with connection.cursor() as cursor:
            p = cursor.execute(
                "select max(strideno) from onlinestride where sessionid =%s and soletype='L'", [ssnid])
            lsnos = cursor.fetchone()
            print("rows from LEFT onlinestride.................................", lsnos)

        if (lsnos[0] == None):
            lsno = 1
        elif (lsnos[0] >= 0):
            lsno = lsnos[0] + 1
        else:
            lsno = 1
        print("last write 's lsno", lsno)
        with connection.cursor() as cursor:
            p = cursor.execute(
                "select max(strideno) from onlinestride where sessionid =%s and soletype='R'", [ssnid])
            rsnos = cursor.fetchone()
            print("rows from RIGHT onlinestride.................................", rsnos)

        if (rsnos[0] == None):
            rsno = 1
        elif (rsnos[0] >= 0):
            rsno = rsnos[0] + 1
        else:
            rsno = 1
        print("last write's rsno", rsno)

        # lsno=lsno+1
        # rsno=rsno+1
        print("new insert value for lsno: ", lsno, "rsno: ", rsno)
        if done == 1:
            # for right leg data
            sval = [sublist for sublist in sarr if 'R' in sublist]
            rdone=0
            totaldist=0.0
            drn = 'R'
            # for right leg data
            print("total right rows:...............", len(sval))
            if (len(sval) > 0) :
                aa = pd.DataFrame(sval)
                print("right calling strideestimate()...............")
                try:
                    print("for right sval", len(sval), "nos",nos, "drn", drn)
                    rsl = strideahrsmod(sval,nos,drn)
                    print("ls is ...........", rsl, "len", len(rsl))
                    stype = 'R'
                    if (len(rsl) > 0):
                        totaldist = 0.0
                        rc=0


                        with connection.cursor() as cursor:
                            # data in rsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                            for r in rsl:
                                sessionid = int(ssnid)
                                # strideno = int(r["strideno"])
                                strideno = int(rsno)
                                dist = float(r["dist"])
                                velocity = float(r["velocity"])
                                stz = r["time"]
                                if (rc < len(rsl) - 1):
                                    etz = int((rsl[rc + 1]["time"]) - 1)
                                else:
                                    etz = int(etimez)

                                print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                      "strideno", strideno, "dist", dist, "velocity", velocity)
                                try:
                                    p = cursor.execute(
                                        "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                        [sessionid, stz, etz, stype, strideno, dist, velocity])
                                except Exception as e:
                                    # Handle any other unexpected exceptions
                                    print(f"An unexpected error occurred: {e}")

                                if not p:
                                    totaldist = totaldist + dist
                                    rc = rc+1
                                    rsno = rsno+1
                                    rdone = 1  # write into onlinestride  successful
                                else:
                                    rdone = 0  # it failed to write
                except Exception as e:
                            # Handle any other unexpected exceptions
                            print(f"An unexpected error occurred when Right calling stridelenstimate(): {e}")
                            rdone = 0  # failed
                            return JsonResponse({'status': 'error'})
            else:
                rdone = 1  # rsl length is zero so no strides detected and written into table
                totaldist=0.0


            print("right leg total distance:", totaldist)


            # for left leg data
            sval = [sublist for sublist in sarr if 'L' in sublist]


            # for left leg data
            print("total LEFT  rows:...............", sval)
            ldone=0
            totdist=0.0
            if (len(sval) > 0):
                aa = pd.DataFrame(sval)

                print("aa............", aa)
                print("left calling strideestimate()...............")
                drn = 'L'
                try:
                    # lsl = strideahrs(sval)
                    # lsl = strideahrs16(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, t12, s14, s15, s16, s17, s18)
                    print("for left sval", len(sval), "nos", nos, "drn", drn)
                    lsl = strideahrsmod(sval,nos,drn)
                    print("ls is ...........", lsl, "len", len(lsl))
                    stype = 'L'
                    if (len(lsl) > 0):
                        totdist = 0.0
                        rc=0

                        with connection.cursor() as cursor:
                            # data in lsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                            for l in lsl:
                                sessionid = int(ssnid)
                                # strideno = int(l["strideno"])
                                strideno =int(lsno)
                                dist = float(l["dist"])
                                velocity = float(l["velocity"])
                                stz = l["time"]
                                if (rc < len(lsl) - 1):
                                    etz = int((lsl[rc + 1]["time"]) - 1)
                                else:
                                    etz = int(etimez)
                                print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                      "strideno", strideno, "dist", dist, "velocity", velocity)
                                try:
                                    p = cursor.execute(
                                        "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                        [sessionid, stz, etz, stype, strideno, dist, velocity])
                                except Exception as e:
                                    # Handle any other unexpected exceptions
                                    print(f"An unexpected error occurred: {e}")

                                if not p:
                                    totdist = totdist + dist
                                    rc=rc+1
                                    lsno=lsno+1
                                    ldone = 1  # its successful
                                else:
                                    ldone = 0  # it failed
                        print("left leg total distance:", totdist)
                except Exception as e:
                    # Handle any other unexpected exceptions
                    print(f"An unexpected error occurred when left calling stridelenstimate(): {e}")
                    ldone = 0  # failed
                    return JsonResponse({'status': 'error'})
            else:
                ldone = 1  # lsl length is zero so no strides detected and written into table
                totdist = 0.0




            if (rdone == 1) and (ldone == 1):
                print("total total distance:     left =",totdist, "   right =",totaldist," L+R=" ,(totaldist+totdist))
                return JsonResponse({'status': 'success'})
            elif ((rdone == 1) and (ldone == 0)) or ((rdone == 0) and (ldone == 1)):
                print("total distance:", (totaldist+totdist), "right distance:", totaldist, "left distance: ",totdist)
                return JsonResponse({'status': 'success'})
            else :
                return JsonResponse({'status': 'error'})


        else:
            return JsonResponse({'status': 'error'})  #### if done ==0 ie., data writing into table has failed!!







##########################################################################

############################################################################################################
# modified stridelenestimate() for every new sensor data inserted computes strides and writes a running strideno into onlinestride for that sessionid
###Adding new one 16 sensors


@api_view(["POST"])
def onlinestridecompute1121(request):  # online stride computation using AHRS
    print("here....................................")
    ssnid = request.data["sessionid"]
    # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data,<s12 and s13 for step size >,solytype,capturedtime  ===> 5 FSR
    # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data ,,<s12 and s13 for step size >,solytype,capturedtime,<s14,s15,s16,s17,s18> which are 2nd part of FSR  ie., 1st part FSR(s1,s2,s3,s4,s5) + 2nd part FSR (s14,s15,s16,s17,s18)  ===>10 FSR(s1,s2,s3,s4,s5,s14,s15,s16,s17,s18)
    sarr = request.data["SensorValues"]
    nos = request.data["totalsensor"]
    print(ssnid, sarr, nos)
    print("inside onlinestridecompute().............")


    stimez = min(sublist[14] for sublist in sarr)
    etimez = max(sublist[14] for sublist in sarr)
    print("starttime is ", stimez, "endtime is:", etimez)
    print("total sensors.", nos)
    print("ssnid and sarr values........................................", ssnid, len(sarr))
    if (nos == "11"):
        rr = 0
        print("....11 sensor data writing in to db started.......")
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
            for sval in sarr:
                # print("row..", sval)
                p = cursor.execute(
                    "insert into sensordata(sessionid,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,timelocal) "
                    "values(%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s, %s,%s, %s,%s,current_timestamp)",
                    [ssnid, sval[0], sval[1], sval[2], sval[3], sval[4], sval[5], sval[6], sval[7], sval[8], sval[9],
                     sval[10], sval[11], sval[12], sval[13], sval[14]])
                if p:
                    done = 1
                else:
                    done = 0
                rr = rr + 1
        print(".......total 11 sensor data rows written:", rr)
    else:
        print("writting 16 sensor data....")
        ll = 0
        # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data ,,<s12 and s13 for step size >,solytype,capturedtime,<s14,s15,s16,s17,s18> which are 2nd part of FSR  ie., 1st part FSR(s1,s2,s3,s4,s5) + 2nd part FSR (s14,s15,s16,s17,s18)  ===>10 FSR(s1,s2,s3,s4,s5,s14,s15,s16,s17,s18)
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Kolkata'")
            for sval in sarr:
                p = cursor.execute(
                    "insert into sensordata(sessionid,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,s14,s15,s16,s17,s18,timelocal) "
                    "values(%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s, %s,%s, %s,%s, %s,%s,%s,%s,%s,current_timestamp)",
                    [ssnid, sval[0], sval[1], sval[2], sval[3], sval[4], sval[5], sval[6], sval[7], sval[8], sval[9],
                     sval[10], sval[11], sval[12], sval[13], sval[14], sval[15], sval[16], sval[17], sval[18],
                     sval[19]])

                if  p:
                    done = 1
                else:
                    done = 0
                ll = ll + 1
        print(".............total 16 SENSOR rows written:", ll)

    if done == 1:
        # for right leg data
        sval = [sublist for sublist in sarr if 'R' in sublist]
        rdone = 0
        totaldist = 0.0

        #--------------------------- for right leg data
        print("total right rows:...............", len(sval))
        if (len(sval) > 0):
            aa = pd.DataFrame(sval)
            print("right calling strideahrsmod()...............")
            try:
                print("for right sval", len(sval), "nos", nos)
                rsl = strideahrsmod(sval, nos)
                print("ls is ...........", rsl, "len", len(rsl))
                stype = 'R'
                if (len(rsl) > 0):
                    totaldist = 0.0
                    rc = 0
                    with connection.cursor() as cursor:
                        # data in rsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                        for r in rsl:
                            sessionid = int(ssnid)
                            # strideno = int(r["strideno"])
                            strideno = 0
                            dist = float(r["dist"])
                            velocity = float(r["velocity"])
                            stz = r["time"]
                            if (rc < len(rsl) - 1):
                                etz = int((rsl[rc + 1]["time"]) - 1)
                            else:
                                etz = int(etimez)

                            print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                  "strideno", strideno, "dist", dist, "velocity", velocity)
                            try:
                                p = cursor.execute(
                                    "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                    [sessionid, stz, etz, stype, strideno, dist, velocity])
                            except Exception as e:
                                # Handle any other unexpected exceptions
                                print(f"An unexpected error occurred: {e}")

                            if not p:
                                totaldist = totaldist + dist
                                rc = rc + 1

                                rdone = 1  # write into onlinestride  successful
                            else:
                                rdone = 0  # it failed to write

            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"An unexpected error occurred when Right calling strideahrsmod(): {e}")
                rdone = 0  # failed
                return JsonResponse({'status': 'error'})


        else:
            rdone = 1  # rsl length is zero so no strides detected and written into table
            totaldist = 0.0

        print("right leg total distance:", totaldist)

        # for left leg data
        sval = [sublist for sublist in sarr if 'L' in sublist]

        # for left leg data
        print("total LEFT  rows:...............", sval)
        ldone = 0
        totdist = 0.0
        if (len(sval) > 0):
            aa = pd.DataFrame(sval)

            print("aa............", aa)
            print("left calling strideahrsmod()...............")

            try:
                # lsl = strideahrs(sval)
                # lsl = strideahrs16(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, t12, s14, s15, s16, s17, s18)
                print("for left sval", len(sval), "nos", nos)
                lsl = strideahrsmod(sval, nos)
                print("ls is ...........", lsl, "len", len(lsl))
                stype = 'L'
                if (len(lsl) > 0):
                    totdist = 0.0
                    rc = 0
                    with connection.cursor() as cursor:
                        # data in lsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                        for l in lsl:
                            sessionid = int(ssnid)
                            # strideno = int(l["strideno"])
                            strideno = 0
                            dist = float(l["dist"])
                            velocity = float(l["velocity"])
                            stz = l["time"]
                            if (rc < len(lsl) - 1):
                                etz = int((lsl[rc + 1]["time"]) - 1)
                            else:
                                etz = int(etimez)

                            print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                  "strideno", strideno, "dist", dist, "velocity", velocity)
                            try:
                                p = cursor.execute(
                                    "insert into onlinestride(sessionid,starttime,endtime,soletype, distance, velocity)   values(%s,%s,%s,%s,%s,%s)",
                                    [sessionid, stz, etz, stype, dist, velocity])
                            except Exception as e:
                                # Handle any other unexpected exceptions
                                print(f"An unexpected error occurred: {e}")

                            if not p:
                                totdist = totdist + dist
                                rc = rc + 1
                                ldone = 1  # its successful
                            else:
                                ldone = 0  # it failed
                    print("left leg total distance:", totdist)

            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"An unexpected error occurred when left calling stridelenstimate(): {e}")
                ldone = 0  # failed
                return JsonResponse({'status': 'error'})


        else:
            ldone = 1  # lsl length is zero so no strides detected and written into table
            totdist = 0.0

        if (rdone == 1) and (ldone == 1):

            print("total total distance:     left =", totdist, "   right =", totaldist, " L+R=", (totaldist + totdist))
            return JsonResponse({'status': 'success'})
        elif ((rdone == 1) and (ldone == 0)) or ((rdone == 0) and (ldone == 1)):
            print("total distance:", (totaldist + totdist), "right distance:", totaldist, "left distance: ", totdist)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})


    else:
        return JsonResponse({'status': 'error'})  #### if done ==0 ie., data writing into table has failed!!



##########################################################################


@api_view(["GET","POST"])
def strideinfo1121(request):  # online stride  reading
    ssnid = request.data["sid"]
    print(ssnid)
    with connection.cursor() as cursor:
        p = cursor.execute(
            "select starttime from onlinestride where sessionid =%s and soletype='R' order by starttime", [ssnid])
        rstart = cursor.fetchall()
    print("rows from RIGHT onlinestride.................................", rstart)
    with connection.cursor() as cursor:
        sno = 1
        for r in rstart:
            p = cursor.execute(
                "update  onlinestride set strideno= %s where sessionid = %s and soletype = 'R' and starttime =%s",
                [sno, ssnid, r[0]])
            sno = sno + 1

    with connection.cursor() as cursor:
        p = cursor.execute(
            "select starttime from onlinestride where sessionid =%s and soletype='L' order by starttime", [ssnid])
        lstart = cursor.fetchall()
    print("rows from LEFT onlinestride.................................", lstart)
    with connection.cursor() as cursor:
        sno = 1
        for l in lstart:
            print(l[0])
            p = cursor.execute(
                "update  onlinestride set strideno= %s where sessionid = %s and soletype = 'L' and starttime =%s",
                [sno, ssnid, l[0]])
            sno = sno + 1

    try:
        with connection.cursor() as cursor:
            # p = cursor.execute("select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by starttime limit 11",[ssnid])
            p = cursor.execute(
                "select strideno, distance,velocity from (select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by strideno asc limit 11) as tbl order by strideno asc",
                [ssnid])
            rcnt = cursor.rowcount
            rstride = cursor.fetchall()
        print("right stride :", rstride)
        with connection.cursor() as cursor:
            p = cursor.execute(
                "select strideno, distance,velocity from (select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by starttime desc limit 11) as tbl order by strideno asc",
                [ssnid])
            # p = cursor.execute(
            #     "select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by strideno asc limit 11",
            #     [ssnid])
            lcnt = cursor.rowcount
            lstride = cursor.fetchall()
        print("left stride:", lstride)

        finarr = []
        for r1 in range(min(lcnt, rcnt)):
            finarr.append({
                "lefttime": 0,
                "righttime": 0,
                "leftstrideno": lstride[r1][0],
                "rightstrideno": rstride[r1][0],
                "leftdistance": lstride[r1][1],
                "rightdistance": rstride[r1][1],
                "leftstridevel": lstride[r1][2],
                "rightstridevel": rstride[r1][2]
            })

        if lcnt == 0 and rcnt > 0:
            for r1 in range(rcnt):
                finarr.append({
                    "lefttime":0,
                    "righttime":0,
                    "leftstrideno": 0,
                    "rightstrideno": rstride[r1][0],
                    "leftdistance": 0,
                    "rightdistance": rstride[r1][1],
                    "leftstridevel": 0,
                    "rightstridevel": rstride[r1][2]
                })
        elif rcnt == 0 and lcnt > 0:
            for r1 in range(lcnt):
                finarr.append({
                    "lefttime":0,
                    "righttime":0,
                    "leftstrideno": lstride[r1][0],
                    "rightstrideno": 0,
                    "leftdistance": lstride[r1][1],
                    "rightdistance": 0,
                    "leftstridevel": lstride[r1][2],
                    "rightstridevel": 0
                })
        elif (rcnt - lcnt) > 0:
            for r1 in range(lcnt + 1, rcnt):
                finarr.append({
                    "lefttime":0,
                    "righttime":0,
                    "leftstrideno": 0,
                    "rightstrideno": rstride[r1][0],
                    "leftdistance": 0,
                    "rightdistance": rstride[r1][1],
                    "leftstridevel": 0,
                    "rightstridevel": rstride[r1][2]
                })
        elif (lcnt - rcnt) > 0:
            for r1 in range(rcnt + 1, lcnt):
                finarr.append({
                    "lefttime":0,
                    "righttime":0,
                    "leftstrideno": lstride[r1][0],
                    "rightstrideno": 0,
                    "leftdistance": lstride[r1][1],
                    "rightdistance": 0,
                    "leftstridevel": lstride[r1][2],
                    "rightstridevel": 0
                })

        print(finarr)


    except Exception as e:
        print(e)
    return Response(finarr)


##################################################################################################


@api_view(["GET","POST"])
def svleft(request):
    # offine stride retrieval from onlinestride table
    ssnid = request.data["sid"]
    lstime = request.data["start"]
    letime = request.data["end"]
    # nos = request.data["totalsensor"]
    lstime = lstime - 3000
    letime = letime + 3000
    with connection.cursor() as cursor:
        p = cursor.execute(
            "select starttime from onlinestride where sessionid =%s and soletype='L'", [ssnid])
        lstart = cursor.fetchall()
        print("rows from LEFT onlinestride.................................", lstart)
    with connection.cursor() as cursor:
        sno = 1
        for l in lstart:
            p = cursor.execute(
                "update  onlinestride set strideno= %s where sessionid = %s and soletype = 'L' and starttime =%s",
                [sno, ssnid, l[0]])
            sno = sno + 1

    try:

        with connection.cursor() as cursor:
            p = cursor.execute(
                "select * from(select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='L' order by strideno desc limit 11) as foo order by strideno asc",
                [ssnid])
            lcnt = cursor.rowcount
            lstride = cursor.fetchall()
        print("retrieved left stride:", lstride)

        finarr = []
        for l1 in lstride:
            finarr.append({
                "leftstrideno": l1[0],
                "leftdistance": l1[1],
                "leftstridevel": l1[2]
            })

        print(finarr)


    except Exception as e:
        print(e)
    return Response(finarr)


@api_view(["GET","POST"])
def svright(request):
    # offine stride retrieval from onlinestride table
    ssnid = request.data["sid"]
    # nos = request.data["totalsensor"]
    rstime = rstime - 3000
    retime = retime + 3000
    with connection.cursor() as cursor:
        p = cursor.execute(
            "select starttime from onlinestride where sessionid =%s and soletype='R'", [ssnid])
        rstart = cursor.fetchall()
        print("rows from RIGHT onlinestride.................................", rstart)
    with connection.cursor() as cursor:
        sno = 1
        for r in rstart:
            p = cursor.execute(
                "update  onlinestride set strideno= %s where sessionid = %s and soletype = 'R' and starttime =%s",[sno, ssnid, r[0]])
            sno = sno + 1

    try:
        with connection.cursor() as cursor:
            # p = cursor.execute("select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by starttime limit 11",[ssnid])
            p = cursor.execute(
                "select * from(select strideno, distance, velocity from onlinestride where sessionid=%s and soletype='R' order by strideno desc limit 11) as foo order by strideno asc",
                [ssnid])
            rcnt = cursor.rowcount
            rstride = cursor.fetchall()
        print("right stride :", rstride)

        finarr = []
        for r1 in rstride:
            finarr.append({
                "rightstrideno": r1[0],
                "rightdistance": r1[1],
                "rightstridevel": r1[2]
            })

        print(finarr)


    except Exception as e:
        print(e)
    return Response(finarr)


#########################################################################################################

@api_view(["GET","POST"])
def getvideometadatamodified(request):
    vid = request.data["videourl"]
    tstat = request.data["togglestatus"]

    arr2 = []
    video_url = vid
    command = ['C:\\Users\\UM\\Downloads\\ffmpeg-6.0-essentials_build\\bin\\ffprobe.exe', '-v', 'quiet',
               '-print_format', 'json', '-show_format', '-show_streams', video_url]
    output = subprocess.check_output(command).decode('utf-8')
    metadata = json.loads(output)
    print(json.dumps(metadata, indent=4))

    # cdt1 = metadata['streams']
    # print(cdt1)
    cdt = metadata['streams'][0]['tags']['creation_time']

    # arr2.append({"createddate": cdt})
    duration = metadata['streams'][0]['duration']
    print("Video duration:", duration, " seconds")
    d = duration
    dmsecs = int((float(duration) * 10))
    print(d, dmsecs, "msecs")
    if (int(tstat)) == 1:
         arr2.append({"createddate": cdt, "stime": cdt})
    else:
        v = int(cdt) - dmsecs
        arr2.append({"createddate": cdt, "stime": v})
    return Response(arr2)

#################swing stance #########################

def swingstancemod(toe,heel,t):
    # Calculate automatic threshold for toe and heel using Otsu's method
    toe = np.array(toe)
    heel = np.array(heel)
    t = np.array(t)

    threshold_toe = threshold_otsu(toe)
    threshold_heel = threshold_otsu(heel)

    # Classify each time point as stance, swing, or no phase
    stance_phase = (toe > threshold_toe) & (heel > threshold_heel)
    swing_phase = (toe <= threshold_toe) & (heel <= threshold_heel)
    no_phase = ~(stance_phase | swing_phase)

    # Merge "no phase" data with stance phase
    stance_phase = stance_phase | no_phase

    # Identify transitions and calculate durations
    stance_durations = []
    swing_durations = []

    # Initialize current phase based on the first data point
    if stance_phase[0]:
        current_phase = 'stance'
    elif swing_phase[0]:
        current_phase = 'swing'
    else:
        current_phase = 'no phase'

    start_time = t[0]

    for i in range(1, len(t)):
        if stance_phase[i]:
            if current_phase != 'stance':
                if current_phase == 'swing' and start_time != t[i - 1]:
                    swing_durations.append(t[i - 1] - start_time)
                elif current_phase == 'no phase' and start_time != t[i - 1]:
                    stance_durations.append(t[i - 1] - start_time)
                current_phase = 'stance'
                start_time = t[i]
        elif swing_phase[i]:
            if current_phase != 'swing':
                if current_phase == 'stance' and start_time != t[i - 1]:
                    stance_durations.append(t[i - 1] - start_time)
                elif current_phase == 'no phase' and start_time != t[i - 1]:
                    swing_durations.append(t[i - 1] - start_time)
                current_phase = 'swing'
                start_time = t[i]
        else:
            if current_phase != 'no phase':
                if current_phase == 'stance':
                    stance_durations.append(t[i - 1] - start_time)
                elif current_phase == 'swing':
                    swing_durations.append(t[i - 1] - start_time)
                current_phase = 'no phase'
                start_time = t[i]

    # Append the last phase duration if it ends at the last data point
    if current_phase == 'stance':
        stance_durations.append(t[-1] - start_time)
    elif current_phase == 'swing':
        swing_durations.append(t[-1] - start_time)

    # Convert durations to milliseconds (assuming t is in seconds)
    stance_durations = np.array(stance_durations)
    swing_durations = np.array(swing_durations)

    # Print durations
    print('Stance Phase Durations:')
    print(stance_durations)
    print('Swing Phase Durations:')
    print(swing_durations)
    return (swing_durations,stance_durations)

@api_view(["GET","POST"])
def swingstance(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]
    nos = request.data["totalsensors"]
    print(stime, ssnid, etime)

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value
    left='L'
    right ='R'
    finarr=[]
    if (nos == 11):
            ###################################### for 11 sensor data LEFT insole ############## LEFT INSOLE
            with connection.cursor() as cursor:
                cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid', [left, ssnid,stime,etime])
                slval = cursor.fetchall()
                lcount = cursor.rowcount

                # Extract relevant columns
                t = slval[:, 5]
                s1 = slval[:, 0]
                s2 = slval[:, 1]
                s3 = slval[:, 2]
                s4 = slval[:, 3]
                s5 = slval[:, 4]
                toes = (s1 + s2 + s3) / 3
                heels = (s4 + s5) / 2
                swl, stl = swingstancemod(toes, heels, t)
                print(swl,stl)
            ###################################### for 11 sensor data LEFT insole ############## LEFT INSOLE
            with connection.cursor() as cursor:
                    cursor.execute(
                        'select s1,s2,s3,s4,s5,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid',
                        [right, ssnid, stime, etime])
                    srval = cursor.fetchall()
                    rcount = cursor.rowcount

                    # Extract relevant columns
                    t = srval[:, 5]
                    s1 = srval[:, 0]
                    s2 = srval[:, 1]
                    s3 = srval[:, 2]
                    s4 = srval[:, 3]
                    s5 = srval[:, 4]
                    toes = (s1 + s2 + s3) / 3
                    heels = (s4 + s5) / 2
                    swr, str = swingstancemod(toes, heels, t)
                    print(swr, str)

    else :
            ###################################### for 16 sensor data LEFT insole ############## LEFT INSOLE
            with connection.cursor() as cursor:
                cursor.execute(
                    'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid',
                    [left, ssnid, stime, etime])
                slval = cursor.fetchall()
                lcount = cursor.rowcount

                # Extract relevant columns
                # for 10 fsr  toe : s16,s17,s18 and for heel : s3,s4,s5,s14
                t = slval[:,10]
                s1 = slval[:, 2]
                s2 = slval[:, 3]
                s3 = slval[:, 4]
                s4 = slval[:, 5]
                s5 = slval[:, 7]
                s6 = slval[:, 8]
                s7 = slval[:, 9]
                # Calculate toe and heel values
                toes = (s1 + s2 + s3 + s4) / 4
                heels = (s5 + s6 + s7) / 3
                swl, stl = swingstancemod(toes, heels, t)
                print(swl, stl)
            ###################################### for 11 sensor data LEFT insole ############## LEFT INSOLE
            with connection.cursor() as cursor:
                cursor.execute(
                    "select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by sensordataid"
                    ,[right, ssnid, stime, etime])
                srval = cursor.fetchall()
                rcount = cursor.rowcount

                # Extract relevant columns
                # for 10 fsr  toe : s16,s17,s18 and for heel : s3,s4,s5,s14
                t = srval[:,10]
                s1 = srval[:, 2]
                s2 = srval[:, 3]
                s3 = srval[:, 4]
                s4 = srval[:, 5]
                s5 = srval[:, 7]
                s6 = srval[:, 8]
                s7 = srval[:, 9]
                # Calculate toe and heel values
                toes = (s1 + s2 + s3 + s4) / 4
                heels = (s5 + s6 + s7) / 3
                swr, str = swingstancemod(toes, heels, t)
                print(swr, str)

    if lcount > rcount : # no of rows in left is more than right  rows
        for i in range(rcount) :
            finarr.append({"leftswing": swl[i], ["rightswing"]: swr[i],
                           "leftstance": stl[i], ["rightstance"]: str[i]})
        for j in range((lcount-rcount)):
            finarr.append({"leftswing": swl[j], ["rightswing"]: 0,
                           "leftstance": stl[j], ["rightstance"]: 0})
    elif  lcount < rcount : # no of rows in right is more than left rows
        for i in range(lcount) :
            finarr.append({"leftswing": swl[i], ["rightswing"]: swr[i],
                           "leftstance": stl[i], ["rightstance"]: str[i]})
        for j in range((rcount-lcount)):
            finarr.append({"leftswing": 0, ["rightswing"]: swr[j],
                           "leftstance": 0, ["rightstance"]: swr[j]})
    elif abs(lcount-rcount) == 0: # both left and right has equal rows
        for i in range(rcount):
            finarr.append({"leftswing": swl[i], ["rightswing"]: swr[i],
                           "leftstance": stl[i], ["rightstance"]: str[i]})

    return Response(finarr)

################################## end of code##################################

###############################################################################################################

@api_view(["GET","POST"])
def finalcentreofpressuremodifiedz1(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]
    nos = request.data["totalsensor"]

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value

    left = 'L'
    right = 'R'
    lcopx = []
    lcopy = []
    ltime = []
    rtime = []
    rcopx = []
    rcopy = []
    finalarr = []
    lcount = 0
    rcount = 0
    print("in cop()")
    print(ssnid,stime,etime,nos)
    print(type(nos))
    if (nos == 11):
        print("Processing 11 sensor data Left......................")
        ###################################### for 11 sensor  data  ############## LEFT INSOLE
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime',
                [left, ssnid, stime, etime])
            slval = cursor.fetchall()
            for p in slval:
                xcop = (p[0] * 27.16) + (p[1] * 57.84) + (p[2] * 53.21) + (p[3] * 43.37) +(p[4] * 0.53)
                ptot = (p[0] + p[1] + p[2] + p[3] + p[4])
                if ptot > 0:
                    xcopf = xcop / ptot
                else:
                    xcopf = 0
                ycop = (p[0] * 187.80) + (p[1] * 167.39) + (p[2] * 117.70) + (p[3] * 54.69) + (p[4] * 33.84)
                if ptot > 0:
                    ycopf = ycop / ptot
                else:
                    ycopf = 0

                xcopf = int(xcopf)
                ycopf = int(ycopf)
                lcopx.append(xcopf)
                lcopy.append(ycopf)
                mapped_value = map_range(p[5], stime, etime, 0, 3000)
                mapped_value = round(mapped_value, 0)
                ltime.append(mapped_value)
                lcount = lcount + 1
            # print(lcount)

        ###################################### for 11 sensor data  ############## RIGHT INSOLE ################
        print("Processing 11 sensor data Right......................")
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime',
                [right, ssnid, stime, etime])
            rlval = cursor.fetchall()
            for c in rlval:
                xcop1 = (c[0] * 27.16) + (c[1] * 57.84) + (c[2] * 53.21) + (c[3] * 43.37 ) + (c[4] * 30.53)
                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
                if ptot1 >0:
                    xcopf1 = xcop1 / ptot1
                else :
                    xcopf1 = 0
                ycop1 = (c[0] * 187.80) + (c[1] * 167.39) + (c[2] * 117.70) + (c[3] * 54.69) + (c[4] * 33.84)
                if ptot1 >0:
                    ycopf1 = ycop1 / ptot1
                else :
                    ycopf1 = 0

                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                mapped_value1 = map_range(c[5], stime, etime, 0, 3000)
                mapped_value1 = round(mapped_value1, 0)
                rtime.append(mapped_value1)
                rcount = rcount + 1
            # print(rcount)
    else:
        print("here in 16 sensor data processing Left.................")
        ################## for 16 sensor data  ################# LEFT INSOLE  ##############
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime',
                [left, ssnid, stime, etime]);
            slval = cursor.fetchall()
        for p in slval:
            xcop= ((p[0] * 56.76) + (p[1] * 63.65) + (p[2] * 64.28) + (p[3] * 48.52) + (p[4] * 21.60) + (p[5] * 25.60) + (p[6] * 35.91) + (p[7] * 28.84) + (p[8] * 30.78) + (p[9] * 48.60))
            ptot = (p[0] + p[1] + p[2] + p[3] + p[4] + p[5] + p[6] + p[7] + p[8] + p[9])
            if ptot > 0:
                xcopf = xcop / ptot
            else:
                xcopf = 0
            ycop = (p[0] * 118.15) + (p[1] * 149.59) + (p[2] * 186.54) + (p[3] * 196.57) + (p[4] * 233.08) + (
                        p[5] * 184.71) + (p[6] * 146.40) + (p[7] * 59.73) + (p[8] * 25.07) + (p[9] * 59.73)
            if ptot > 0:
                ycopf = ycop / ptot
            else:
                ycopf = 0
            xcopf = int(xcopf)
            ycopf = int(ycopf)
            lcopx.append(xcopf)
            lcopy.append(ycopf)
            mapped_value = map_range(p[10], stime, etime, 0, 3000)
            mapped_value = round(mapped_value, 0)
            ltime.append(mapped_value)
            lcount = lcount + 1
            # print(lcount)

        #################### for 16 sensor data  ################# RIGHT INSOLE  ##############
        print("here in 16 sensor data processing Right.................")
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime',
                [right, ssnid, stime, etime])
            rlval = cursor.fetchall()
            for c in rlval:
                xcop1 = ((c[0] * 31.41) + (c[1] * 27.97) + (c[2] * 26.42) + (c[3] * 40.28) + (c[4] * 63.91) + (c[5] * 56.91) + (c[6] * 51.36) + (c[7] * 60.27) + (c[8] * 50.72) + (c[9] * 38.41))
                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4] + c[5] + c[6] + c[7] + c[8] + c[9])
                if ptot1 >0:
                    xcopf1 = xcop1 / ptot1
                else :
                    xcopf1= 0

                ycop1 = (c[0] * 113.15) + (c[1] * 133.59) + (c[2] * 180.27) + (c[3] * 207.57) + (c[4] * 240.87) + (c[5] * 189.71) + (c[6] * 151.40) + (c[7] * 64.73) + (c[8] * 30.07) + (c[9] * 64.73)
                if ptot1 >0 :
                    ycopf1 = ycop1 / ptot1
                else:
                    ycopf1 = 0
                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                mapped_value1 = map_range(c[10], stime, etime, 0, 3000)
                mapped_value1 = round(mapped_value1, 0)
                rtime.append(mapped_value1)
                rcount = rcount + 1
                # print(rcount)

    tc = min(lcount, rcount)
    if (lcount < rcount):
        # print("Left Minimum")
        lcopx = lcopx[:len(rcopx)]
        lcopy = lcopy[:len(rcopy)]
        ltime = ltime[:len(rtime)]

    else:
        # print("Right Minimum")
        rcopx = rcopx[:len(lcopx)]
        rcopy = rcopy[:len(lcopy)]
        rtime = rtime[:len(ltime)]

    for i in range(tc):
        fleftcopx = lcopx[i]
        fleftcopy = lcopy[i]
        frightcopx = rcopx[i]
        frightcopy = rcopy[i]
        ftime = rtime[i]
        finalarr.append({"leftcopx": fleftcopx, "leftcopy": fleftcopy, "time": ftime, "rightcopx": frightcopx,
                         "rightcopy": frightcopy})

    return Response(finalarr)




######################################################################################################################


##############################################swing stance MODIFIED #########################

def swingstancemodified(toe,heel,t):
    # Calculate automatic threshold for toe and heel using Otsu's method
    toes = np.array(toe)
    heels = np.array(heel)
    ts = np.array(t)
    print(" in swingstancemod()..........")
    print(toe, toes)
    threshold_toe = threshold_otsu(toes)
    threshold_heel = threshold_otsu(heels)

    # Classify each time point as stance, swing, or no phase
    stance_phase = (toes > threshold_toe) & (heels > threshold_heel)
    swing_phase = (toes <= threshold_toe) & (heels <= threshold_heel)
    no_phase = ~(stance_phase | swing_phase)

    # Merge "no phase" data with stance phase
    stance_phase = stance_phase | no_phase

    # Identify transitions and calculate durations
    stance_durations = []
    swing_durations = []

    # Initialize current phase based on the first data point
    if stance_phase[0]:
        current_phase = 'stance'
    elif swing_phase[0]:
        current_phase = 'swing'
    else:
        current_phase = 'no phase'

    start_time = ts[0]

    for i in range(1, len(ts)):
        if stance_phase[i]:
            if current_phase != 'stance':
                if current_phase == 'swing' and start_time != ts[i - 1]:
                    swing_durations.append(ts[i - 1] - start_time)
                elif current_phase == 'no phase' and start_time != ts[i - 1]:
                    stance_durations.append(ts[i - 1] - start_time)
                current_phase = 'stance'
                start_time = ts[i]
        elif swing_phase[i]:
            if current_phase != 'swing':
                if current_phase == 'stance' and start_time != ts[i - 1]:
                    stance_durations.append(ts[i - 1] - start_time)
                elif current_phase == 'no phase' and start_time != t[i - 1]:
                    swing_durations.append(ts[i - 1] - start_time)
                current_phase = 'swing'
                start_time = ts[i]
        else:
            if current_phase != 'no phase':
                if current_phase == 'stance':
                    stance_durations.append(ts[i - 1] - start_time)
                elif current_phase == 'swing':
                    swing_durations.append(ts[i - 1] - start_time)
                current_phase = 'no phase'
                start_time = ts[i]

    # Append the last phase duration if it ends at the last data point
    if current_phase == 'stance':
        stance_durations.append(ts[-1] - start_time)
    elif current_phase == 'swing':
        swing_durations.append(ts[-1] - start_time)

    # Convert durations to milliseconds (assuming t is in seconds)
    stance_durations = np.array(stance_durations)
    swing_durations = np.array(swing_durations)

    # Print durations
    print('Stance Phase Durations:')
    print(stance_durations)
    print('Swing Phase Durations:')
    print(swing_durations)
    return (swing_durations,stance_durations)

@api_view(["GET","POST"])
def swingstancemodifiedz1(request):
    stime = request.data["stime"]
    ssnid = request.data["ssnid"]
    etime = request.data["etime"]
    nos = request.data["totalsensor"]
    print(stime, ssnid, etime)

    def map_range(value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled_value = float(value - from_min) / float(from_range)
        mapped_value = to_min + (scaled_value * to_range)
        return mapped_value
    left='L'
    right ='R'
    finarr=[]
    swl=[]
    swr=[]
    stl=[]
    str1=[]
    if (nos == 11):
            print("computing 11 sensor data swingstance......................")
            ###################################### for 11 sensor data LEFT insole ##############
            print("computing swingstance for left ......................")
            with connection.cursor() as cursor:
                cursor.execute('select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime', [left, ssnid,stime,etime])
                slval = cursor.fetchall()
                # print(slval)
                lcount = cursor.rowcount
                print("lcount:",lcount)
                aa = pd.DataFrame(slval)
                # print(aa)
                # Extract relevant columns
                t = aa[5]
                s1 = aa[0] #toe
                s2 = aa[1]
                s3 =aa[2]
                s4 = aa[3] #heel
                s5 = aa[4]
                # print(t,s1,s2,s3,s4,s5)
                # toes = (s1 + s2 + s3) / 3
                # heels = (s4 + s5) / 2
                toes = [sum(x) / len(x) for x in zip(s1, s2, s3)]
                heels = [sum(x) / len(x) for x in zip(s4, s5)]
                swl, stl = swingstancemodified(toes, heels, t)
                print("returned  results (left):")
                print(swl,stl)
            ###################################### for 11 sensor data RIGHT insole ##############
            print("computing swingstance for right ......................")
            with connection.cursor() as cursor:
                    cursor.execute(
                        'select s1,s2,s3,s4,s5,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime',
                        [right, ssnid, stime, etime])
                    srval = cursor.fetchall()
                    rcount = cursor.rowcount
                    aa = pd.DataFrame(srval)
                    # Extract relevant columns
                    t = aa[5]
                    s1 = aa[0] #toe
                    s2 = aa[1]
                    s3 = aa[2]
                    s4 = aa[3] #heel
                    s5 = aa[4]
                    # toes = (s1 + s2 + s3) / 3
                    # heels = (s4 + s5) / 2
                    toes = [sum(x) / len(x) for x in zip(s1, s2, s3)]
                    heels = [sum(x) / len(x) for x in zip(s4, s5)]
                    swr, str1 = swingstancemodified(toes, heels, t)
                    print("returned  results (right):")
                    print(swr, str1)

    else :
            print("computing 16 sensor data swingstance......................")
            ###################################### for 16 sensor data LEFT insole ##############
            print("computing swingstance for left ......................")
            with connection.cursor() as cursor:
                cursor.execute(
                    'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime',
                    [left, ssnid, stime, etime])
                slval = cursor.fetchall()
                lcount = cursor.rowcount
                aa = pd.DataFrame(slval)
                # print(aa)
                # Extract relevant columns
                # for 10 fsr  heel : s16,s17,s18 and for toe : s3,s4,s5,s14
                t = aa[10]
                s1 = aa[2]  # toe
                s2 = aa[3]
                s3 = aa[4]
                s4 = aa[5]
                s5 = aa[7]  # heel
                s6 = aa[8]
                s7 = aa[9]
                # Calculate toe and heel values
                # toes = (s1 + s2 + s3 + s4) / 4
                # heels = (s5 + s6 + s7) / 3
                toes = [sum(x) / len(x) for x in zip(s1, s2, s3, s4)]
                heels = [sum(x) / len(x) for x in zip(s5, s6, s7)]
                swl, stl = swingstancemodified(toes, heels, t)
                print("returned  results (left):")
                print(swl, stl)
            ###################################### for 16 sensor data RIGHT insole ##############
            print("computing swingstance for right ......................")
            with connection.cursor() as cursor:
                cursor.execute(
                    "select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime"
                    ,[right, ssnid, stime, etime])
                srval = cursor.fetchall()
                rcount = cursor.rowcount
                aa = pd.DataFrame(srval)
                print(aa)
                # Extract relevant columns
                # for 10 fsr  heel : s16,s17,s18 and for toe : s3,s4,s5,s14
                t = aa[10]
                s1 = aa[2] #toe
                s2 = aa[3]
                s3 = aa[4]
                s4 = aa[5]
                s5 = aa[7] #heel
                s6 = aa[8]
                s7 = aa[9]
                # Calculate toe and heel values
                # toes = (s1 + s2 + s3 + s4) / 4
                # heels = (s5 + s6 + s7) / 3
                toes = [sum(x) / len(x) for x in zip(s1, s2, s3, s4)]
                heels = [sum(x) / len(x) for x in zip(s5, s6, s7)]
                swr, str1 = swingstancemodified(toes, heels, t)
                print("returned  results (right):")
                print(swr, str1)

    # if lcount > rcount : # no of rows in left is more than right  rows
    #     for i in range(rcount) :
    #         finarr.append({"leftswing": swl[i], ["rightswing"]: swr[i],
    #                        "leftstance": stl[i], ["rightstance"]: str[i]})
    #     for j in range((lcount-rcount)):
    #         finarr.append({"leftswing": swl[j], ["rightswing"]: 0,
    #                        "leftstance": stl[j], ["rightstance"]: 0})
    # elif  lcount < rcount : # no of rows in right is more than left rows
    #     for i in range(lcount) :
    #         finarr.append({"leftswing": swl[i], ["rightswing"]: swr[i],
    #                        "leftstance": stl[i], ["rightstance"]: str[i]})
    #     for j in range((rcount-lcount)):
    #         finarr.append({"leftswing": 0, ["rightswing"]: swr[j],
    #                        "leftstance": 0, ["rightstance"]: swr[j]})
    # elif abs(lcount-rcount) == 0: # both left and right has equal rows
    #     for i in range(rcount):
    #         finarr.append({"leftswing": swl[i], ["rightswing"]: swr[i],
    #                        "leftstance": stl[i], ["rightstance"]: str[i]})
    finarr.append({"swing left":swl, "swing right":swr, "stance left":stl, "stance right":str1})
    return Response(finarr)

########################################   caddence #################################################
def cadencemod(steps):
    # Generate synthetic pedometer data parameters
    sampling_frequency = 40  # in Hz
    print("inside cadencez()............")
    total_samples = len(steps)
    print("total_samples",total_samples)

    # Parameters
    samples_per_minute = sampling_frequency * 60
    print("samples_per_minute",samples_per_minute)
    # Compute cadence in steps per minute
    num_samples = len(steps)
    print("num_samples", num_samples)
    num_minutes = num_samples // samples_per_minute
    print("num_minutes",num_minutes)
    cadence = []

    for i in range(num_minutes):
        start_index = i * samples_per_minute
        end_index = (i + 1) * samples_per_minute
        steps_in_minute = len(steps[start_index:end_index].unique()) - 1
        cadence.append(steps_in_minute)
    print("cadence.",cadence)
    # Time vector (in minutes)
    time_vector = np.arange(1, num_minutes + 1)
    return (time_vector, cadence)


@api_view(["GET","POST"])
def cadencez1(request):
    ssnid = request.data["ssnid"]
    nos = request.data["totalsensor"]
    stime = request.data["stime"]
    etime = request.data["etime"]
    print(ssnid, nos)


    left='L'
    right ='R'
    finarr=[]
    print(type(nos), type(etime), type(stime))
    cadr=[]
    cadl=[]
    timel=[]
    timer=[]

    if (nos == 11):
            ###################################### for 11 sensor data LEFT insole ##############
            print("here reading data for 11 sensor LEFT ...................")
            with connection.cursor() as cursor:
                cursor.execute('select s12, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime', [left, ssnid,stime,etime])
                slval = cursor.fetchall()
                lcount = cursor.rowcount
                print(lcount, slval)
                # Extract relevant columns
                dd = pd.DataFrame(slval)
                stepz = dd[0]
                print("stepsss...............",stepz)
                timel, cadl = cadencemod(stepz)
                print("outcomes for cadence 11 sensor data left....", timel, cadl)
            ###################################### for 11 sensor data RIGHT insole ##############
            print("here reading data for 11 sensor RIGHT ...................")
            with connection.cursor() as cursor:
                    cursor.execute(
                        'select s12 ,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime',
                        [right, ssnid, stime, etime])
                    srval = cursor.fetchall()
                    rcount = cursor.rowcount
                    ddr = pd.DataFrame(srval)
                    stepz = ddr[0]
                    # Extract relevant columns
                    print("stepsss...............", stepz)
                    timer, cadr = cadencemod(stepz)
                    print("outcomes for cadence 11 sensor data right.....",timer, cadr)

    else :
            ###################################### for 16 sensor data LEFT insole ##############
            print("here reading data for 16 sensor left ...................")
            with connection.cursor() as cursor:
                cursor.execute(
                    'select s12, capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime',
                    [left, ssnid, stime, etime])
                slval = cursor.fetchall()
                lcount = cursor.rowcount

                # Extract relevant columns
                dd = pd.DataFrame(slval)
                stepz = dd[0]
                print("stepsss...............", stepz)
                timel, cadl = cadencemod(stepz)
                print("outcomes for cadence 16 sensor data left....", timel, cadl)
            ###################################### for 16 sensor data RIGHT insole ##############
            print("here reading data for 16 sensor right ...................")
            with connection.cursor() as cursor:
                cursor.execute(
                    'select s12 ,capturedtime from sensordata where  soletype = %s and sessionid=%s  and capturedtime >= %s and capturedtime <= %s order by capturedtime',
                    [right, ssnid, stime, etime])
                srval = cursor.fetchall()
                rcount = cursor.rowcount

                # Extract relevant columns
                ddr = pd.DataFrame(srval)
                stepz = ddr[0]
                print("stepsss...............", stepz)
                timer, cadr = cadencemod(stepz)
                print("outcomes for cadence 16 sensor data right.....",timer, cadr)

    # if lcount > rcount : # no of rows in left is more than right  rows
    #     for i in range(rcount) :
    #         finarr.append({"lefttime": timel[i], ["righttime"]: timer[i],
    #                        "leftcad": cadl[i], ["rightcad"]: cadr[i]})
    #     for j in range((lcount-rcount)):
    #         finarr.append({"lefttime": timel[j], ["righttime"]: 0,
    #                        "leftcad": cadl[j], ["rightcad"]: 0})
    # elif  lcount < rcount : # no of rows in right is more than left rows
    #     for i in range(lcount) :
    #         finarr.append({"lefttime": timel[i], ["righttimeg"]: timer[i],
    #                        "leftcad": cadl[i], ["rightcad"]: cadr[i]})
    #     for j in range((rcount-lcount)):
    #         finarr.append({"lefttime": 0, ["righttime"]: timer[j],
    #                        "leftcad": 0, ["rightcad"]: cadr[j]})
    # elif abs(lcount-rcount) == 0: # both left and right has equal rows
    #     for i in range(rcount):
    #         finarr.append({"lefttime": timel[i], ["righttime"]: timer[i],
    #                        "leftcad": cadl[i], ["rightcad"]: cadr[i]})
    finarr.append({"lefttime":timel, "leftcadence":cadl, "righttime":timer, "rightcadence":cadr})
    return Response(finarr)


################################### end  of  code ############################################
##################################         REPORT   GENERATOR       ###########################

def computethminmaxavg(ssnid, nos, th):
    print("computing toe heel max/min/avg pressures.........")
    left = 'L'
    right = 'R'
    lptoe=[]
    rptoe=[]
    lpheel=[]
    rpheel=[]
    if (nos == 11):
        ###################################### for 11 sensor data ############## LEFT INSOLE
        print("11 sensors ..............left")
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5 from sensordata where  soletype = %s and sessionid=%s  group by s1,s2,s3,s4,s5,capturedtime order by capturedtime',[left, ssnid])
            slval = cursor.fetchall()
            lrcount = cursor.rowcount
        print("total left rows...", lrcount)
        for p in slval:
            if (th == 4 ) :
                ptot2 = p[0] + p[1]
                ptot2 = round(ptot2 / 2, 2)  # toe
            elif (th == 5):
                ptot2 = p[0] + p[2]
                ptot2 = round(ptot2 / 2, 2)  # toe
            else :
                ptot2 = p[0] + p[1] + p[2]
                ptot2 = round(ptot2 / 3, 2)  # toe
            if ptot2 >= 778:
                ptot2 = (0.1439 * ptot2) - 109.31
            elif 778 > ptot2 > 18:
                ptot2 = (0.0035 * ptot2) - 0.063
            elif ptot2 <= 18:
                ptot2 = 0
            lptoe.append(ptot2)

            if (th == 4) :
                ptot3 = p[3]
            elif (th == 5):
                ptot3 = p[4]
            else:
                ptot3 = p[3] + p[4]
                ptot3 = round(ptot3 / 2, 2)  # heel
            if ptot3 >= 778:
                ptot3 = (0.1439 * ptot3) - 109.31
            elif 778 > ptot3 > 18:
                ptot3 = (0.0035 * ptot3) - 0.063
            elif ptot3 <= 18:
                ptot3 = 0
            lpheel.append(ptot3)

        # Find the max, min.avg of toe
        ltoemax = max(lptoe)
        ltoemin = min(lptoe)
        ltoeavg = sum(lptoe) / len(lptoe)
        # Find the max, min.avg of  heel
        lheelmax = max(lpheel)
        lheelmin = min(lpheel)
        lheelavg = sum(lpheel) / len(lpheel)

        ###################################### for 11 sensor data  ############## RIGHT INSOLE ################
        print("11 sensors ..............right")
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5 from sensordata where  soletype = %s and sessionid=%s  group by s1,s2,s3,s4,s5,capturedtime order by capturedtime',[right, ssnid])
            rlval = cursor.fetchall()
            rrcount = cursor.rowcount
        print("total right rows...", rrcount)
        for q in rlval:
            if (th == 4) :
                qtot2 = q[0] + q[1]
                qtot2 = round(qtot2 / 2, 2)  # toe
            elif (th == 5):
                qtot2 = q[0] + q[2]
                qtot2 = round(qtot2 / 2, 2)  # toe
            else :
                qtot2 = q[0] + q[1] + q[2]
                qtot2 = round(qtot2 / 3, 2)  # toe

            if qtot2 >= 778:
                qtot2 = (0.1439 * qtot2) - 109.31
            elif 778 > qtot2 > 18:
                qtot2 = (0.0035 * qtot2) - 0.063
            elif qtot2 <= 18:
                qtot2 = 0
            rptoe.append(qtot2)

            if (th == 4) :
                qtot3 = q[3]
            elif (th == 5):
                qtot3 = q[4]
            else :
                qtot3 = q[3] + q[4]
                qtot3 = round(qtot3 / 2, 2)  # heel
            if qtot3 >= 778:
                qtot3 = (0.1439 * qtot3) - 109.31
            elif 778 > qtot3 > 18:
                qtot3 = (0.0035 * qtot3) - 0.063
            elif qtot3 <= 18:
                qtot3 = 0
            rpheel.append(qtot3)

        # Find the max/min/avg values of toe
        rtoemax = max(rptoe)
        rtoemin = min(rptoe)
        rtoeavg = sum(rptoe) / len(rptoe)
        # Find the max/min/avg values of heel
        rheelmax = max(rpheel)
        rheelmin = min(rpheel)
        rheelavg = sum(rpheel) / len(rpheel)
    else :
        ###################################### for 16 sensor data ############## LEFT INSOLE
        print("reading 16 sensor data LEFT from db  ............................")
        with connection.cursor() as cursor:
           cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18 from sensordata where  soletype = %s and sessionid=%s  order by capturedtime',[left, ssnid])
           slval = cursor.fetchall()
           lrcount = cursor.rowcount
        print("total rows on left...",lrcount)
        for p in slval:
            # s3,s4,s5,s6 for toe on both leg and  s8,s9,s10 for heel on both legs
            ptot2 = (p[2] + p[3] + p[4] + p[5])
            ptot2 = round((ptot2 / 4), 2)  # toe
            if ptot2 >= 778:
                ptot2 = (0.1439 * ptot2) - 109.31
            elif 778 > ptot2 > 18:
                ptot2 = (0.0035 * ptot2) - 0.063
            elif ptot2 <= 18:
                ptot2 = 0
            lptoe.append(ptot2)

            ptot3 = (p[7] + p[8] + p[9])
            ptot3 = round((ptot3 / 3), 2)  # heel
            if ptot3 >= 778:
                ptot3 = (0.1439 * ptot3) - 109.31
            elif 778 > ptot3 > 18:
                ptot3 = (0.0035 * ptot3) - 0.063
            elif ptot3 <= 18:
                ptot3 = 0
            lpheel.append(ptot3)

        # Find the max, min.avg of toe
        ltoemax = max(lptoe)
        ltoemin = min(lptoe)
        ltoeavg = sum(lptoe) / len(lptoe)
        # Find the max, min.avg of  heel
        lheelmax = max(lpheel)
        lheelmin = min(lpheel)
        lheelavg = sum(lpheel) / len(lpheel)

        ###################################### for 16 sensor data   ############## RIGHT INSOLE ################
        print("Reading 16 sensor data RIGHT from db  ............................")
        with connection.cursor() as cursor:
            cursor.execute(
                "select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18 from sensordata where  soletype = %s and sessionid=%s  order by capturedtime",[right, ssnid])
            rlval = cursor.fetchall()
            rrcount = cursor.rowcount
        print("total rows on right....",rrcount)
        for q in rlval:
            # s3,s4,s5,s6 for toe on both leg and  s8,s9,s10 for heel on both legs
            qtot2 = (q[2] + q[3] + q[4] + q[5])
            qtot2 = round((qtot2 / 4), 2)  # toe
            if qtot2 >= 778:
                qtot2 = (0.1439 * qtot2) - 109.31
            elif 778 > qtot2 > 18:
                qtot2 = (0.0035 * qtot2) - 0.063
            elif qtot2 <= 18:
                qtot2 = 0
            rptoe.append(qtot2)

            qtot3 = (q[7] + q[8] + q[9])
            qtot3 = round((qtot3 / 3), 2)  # heel
            if qtot3 >= 778:
                qtot3 = (0.1439 * qtot3) - 109.31
            elif 778 > qtot3 > 18:
                qtot3 = (0.0035 * qtot3) - 0.063
            elif qtot3 <= 18:
                qtot3 = 0
            rpheel.append(qtot3)

        # Find the max/min/avg values of toe
        rtoemax = max(rptoe)
        rtoemin = min(rptoe)
        rtoeavg = sum(rptoe) / len(rptoe)
        # Find the max/min/avg values of heel
        rheelmax = max(rpheel)
        rheelmin = min(rpheel)
        rheelavg = sum(rpheel) / len(rpheel)

    # write to db
    print(ssnid,rtoemax,rheelmax,ltoemax,lheelmax,rtoemin,rheelmin,ltoemin,lheelmin,rtoeavg,rheelavg,ltoeavg,lheelavg)
    with connection.cursor() as cursor:
        cursor.execute("insert into reportdatastore(sessionid, rmaxtoe, rmaxheel, lmaxtoe, lmaxheel, rmintoe, rminheel, lmintoe, lminheel, ravgtoe, ravgheel, lavgtoe, lavgheel) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                ,[ssnid,rtoemax,rheelmax,ltoemax,lheelmax,rtoemin,rheelmin,ltoemin,lheelmin,rtoeavg,rheelavg,ltoeavg,lheelavg])
        rc = cursor.rowcount
    if rc > 0:
         return 1
    else :
         return 0


def computecop(ssnid, nos,th):
    xyvals = []
    left = 'L'
    right = 'R'
    lcopx = []
    lcopy = []
    ltime = []
    rtime = []
    rcopx = []
    rcopy = []
    finalarr = []
    lcount = 0
    rcount = 0
    xcoords=[]
    ycoords=[]

    if (nos == 11):
        print("in 11 sensor data processing.......................")
        print("in 11 sensor ... getting xy coords... for LEFT")
        with connection.cursor() as cursor:
            cursor.execute(
                "select xcoord, ycoord from insole where insoleid = (select leftinsoleid from userdevice where udevid = (select udevid from sessionactivity where sessionid=%s))",
                [ssnid])
            xyvals = cursor.fetchall()
        x=y=[]
        for a in xyvals:
            print("x: ", a[0], "y: ", a[1])
            x=a[0]
            y=a[1]
        print(x,y)
        ###################################### for 11 sensor  data  ############## LEFT INSOLE
        print("in 11 sensor ... getting sendor data... for LEFT")
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5 from sensordata where  soletype = %s and sessionid=%s group by s1,s2,s3,s4,s5,capturedtime order by capturedtime asc',[left, ssnid])
            slval = cursor.fetchall()
            print(len(slval))

            for p in slval:
                if (th == 4):
                    xcop = (p[0] * x[0]) + (p[1] * x[1]) + (p[2] * x[2]) + (p[3] * x[3])
                    ptot = (p[0] + p[1] + p[2] + p[3])
                    if ptot > 0:
                        xcopf = xcop / ptot
                    else:
                        xcopf = 0
                    ycop = (p[0] * y[0]) + (p[1] * y[1]) + (p[2] * y[2]) + (p[3] * y[3])
                    if ptot > 0:
                        ycopf = ycop / ptot
                    else:
                        ycopf = 0
                else :
                    xcop = (p[0] * x[0]) + (p[1] * x[1]) + (p[2] * x[2]) + (p[3] * x[3]) + (
                                p[4] * x[4])

                    ptot = (p[0] + p[1] + p[2] + p[3] + p[4])
                    if ptot > 0:
                        xcopf = xcop / ptot
                    else:
                        xcopf = 0
                    ycop = (p[0] * y[0]) + (p[1] * y[1]) + (p[2] * y[2]) + (p[3] * y[3]) + (
                                p[4] * y[4])
                    if ptot > 0:
                        ycopf = ycop / ptot
                    else:
                        ycopf = 0

                xcopf = int(xcopf)
                ycopf = int(ycopf)
                lcopx.append(xcopf)
                lcopy.append(ycopf)
                lcount = lcount + 1
            print("total left rows..............",lcount)

        ###################################### for 11 sensor data  ############## RIGHT INSOLE ################
        print("in 11 sensor ... getting xy coords... for RIGHT")
        with connection.cursor() as cursor:
            cursor.execute(
                "select xcoord, ycoord from insole where insoleid = (select rightinsoleid from userdevice where udevid = (select udevid from sessionactivity where sessionid=%s))",
                [ssnid])
            xyvals = cursor.fetchall()
        # Separate xcoords and ycoords into separate lists
        x = y = []
        for a in xyvals:
            print("x: ", a[0], "y: ", a[1])
            x = a[0]
            y = a[1]
        print(x, y)
        print("in 11 sensor ... getting sensor data... for RIGHT")
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5 from sensordata where  soletype = %s and sessionid=%s group by s1,s2,s3,s4,s5,capturedtime order by capturedtime asc',[right, ssnid])
            rlval = cursor.fetchall()
            for c in rlval:
                if (th == 4):
                    xcop1 = (c[0] * x[0]) + (c[1] * x[1]) + (c[2] * x[2]) + (c[3] * x[3])
                    ptot1 = (c[0] + c[1] + c[2] + c[3])
                    if ptot1 > 0:
                        xcopf1 = xcop1 / ptot1
                    else:
                        xcopf1 = 0
                    ycop1 = (c[0] * y[0]) + (c[1] * y[1]) + (c[2] * y[2]) + (c[3] * y[3])
                    if ptot1 > 0:
                        ycopf1 = ycop1 / ptot1
                    else:
                        ycopf1 = 0
                else :

                    xcop1 = (c[0] * x[0]) + (c[1] * x[1]) + (c[2] * x[2]) + (
                                c[3] * x[3]) + (c[4] * x[4])
                    ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4])
                    if ptot1 > 0:
                        xcopf1 = xcop1 / ptot1
                    else:
                        xcopf1 = 0
                    ycop1 = (c[0] * y[0]) + (c[1] * y[1]) + (c[2] * y[2]) + (
                                c[3] * y[3]) + (c[4] * y[4])
                    if ptot1 > 0:
                        ycopf1 = ycop1 / ptot1
                    else:
                        ycopf1 = 0

                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                rcount = rcount + 1
            print("total right rows ...........",rcount)
    else:
        print("here in 16 sensor data processing.................")
        ################## for 16 sensor data  ################# LEFT INSOLE  ##############
        print("in 16 sensor ... getting xy coords... for LEFT")
        with connection.cursor() as cursor:
            cursor.execute(
                "select xcoord, ycoord from insole where insoleid = (select leftinsoleid from userdevice where udevid = (select udevid from sessionactivity where sessionid=%s))",
                [ssnid])
            xyvals = cursor.fetchall()
        for a in xyvals:
            print("x: ", a[0], "y: ", a[1])
        # Separate xcoords and ycoords into separate lists
        x = y = []
        for a in xyvals:
            print("x: ", a[0], "y: ", a[1])
            x = a[0]
            y = a[1]
        print(x, y)
        print("in 16 sensor ... getting sensordata ... for LEFT")
        with connection.cursor() as cursor:
            cursor.execute(
                'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18 from sensordata where  soletype = %s and sessionid=%s order by capturedtime asc',[left, ssnid])
            slval = cursor.fetchall()
            print(slval)
        for p in slval:
            xcop = ((p[0] * x[0]) + (p[1] * x[1]) + (p[2] * x[2]) + (p[3] * x[3]) + (
                        p[4] * x[4]) + (p[5] * x[5]) + (p[6] * x[6]) + (p[7] * x[7]) + (
                                p[8] * x[8]) + (p[9] * x[9]))
            ptot = (p[0] + p[1] + p[2] + p[3] + p[4] + p[5] + p[6] + p[7] + p[8] + p[9])
            if ptot > 0:
                xcopf = xcop / ptot
            else:
                xcopf = 0
            ycop = (p[0] * y[0]) + (p[1] * y[1]) + (p[2] * y[2]) + (p[3] * y[3]) + (
                    p[4] * y[4]) + (p[5] * y[5]) + (p[6] * y[6]) + (p[7] * y[7]) + (
                           p[8] * y[8]) + (p[9] * y[9])
            if ptot > 0:
                ycopf = ycop / ptot
            else:
                ycopf = 0
            xcopf = int(xcopf)
            ycopf = int(ycopf)
            lcopx.append(xcopf)
            lcopy.append(ycopf)
            lcount = lcount + 1
        print("total rows..........",lcount)

        #################### for 16 sensor data  ################# RIGHT INSOLE  ##############
        print("in 16 sensor ... getting xy coords... for RIGHT")
        with connection.cursor() as cursor:
            cursor.execute(
                "select xcoord, ycoord from insole where insoleid = (select rightinsoleid from userdevice where udevid = (select udevid from sessionactivity where sessionid=%s))",
                [ssnid])
            xyvals = cursor.fetchall()
        for a in xyvals:
            print("x: ", a[0], "y: ", a[1])
        # Separate xcoords and ycoords into separate lists
        x = y = []
        for a in xyvals:
            print("x: ", a[0], "y: ", a[1])
            x = a[0]
            y = a[1]
        print(x, y)
        print("in 16 sensor ... getting sensordata  ... for RIGHT")
        with connection.cursor() as cursor:
            query1 = 'select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18 from sensordata where  soletype = %s and sessionid=%s order by capturedtime asc'
            cursor.execute(query1 ,[right, ssnid])
            rlval = cursor.fetchall()
            for c in rlval:
                xcop1 = ((c[0] * x[0]) + (c[1] * x[1]) + (c[2] * x[2]) + (
                            c[3] * x[3]) + (c[4] * x[4]) + (c[5] * x[5]) + (
                                     c[6] * x[6]) + (c[7] * x[7]) + (c[8] * x[8]) + (
                                     c[9] * x[9]))
                ptot1 = (c[0] + c[1] + c[2] + c[3] + c[4] + c[5] + c[6] + c[7] + c[8] + c[9])
                if ptot1 > 0:
                    xcopf1 = xcop1 / ptot1
                else:
                    xcopf1 = 0
                ycop1 = (c[0] * y[0]) + (c[1] * y[1]) + (c[2] * y[2]) + (
                            c[3] * y[3]) + (c[4] * y[4]) + (c[5] * y[5]) + (
                                    c[6] * y[6]) + (c[7] * y[7]) + (c[8] * y[8]) + (
                                    c[9] * y[9])
                if ptot1 > 0:
                    ycopf1 = ycop1 / ptot1
                else:
                    ycopf1 = 0
                xcopf1 = int(xcopf1)
                ycopf1 = int(ycopf1)
                rcopx.append(xcopf1)
                rcopy.append(ycopf1)
                rcount = rcount + 1
            print("total rows .........",rcount)
    # Calculate mean for rcopx and lcopx
    print("computing .............mn values of right and left for xvals")
    meanrcopx = sum(rcopx) / len(rcopx) if rcopx else None
    meanlcopx = sum(lcopx) / len(lcopx) if lcopx else None
    print(meanrcopx)
    print(meanlcopx)

    # Calculate mean for rcopy and lcopy
    print("computing .............mn values of right and left yvals")
    meanrcopy = sum(rcopy) / len(rcopy) if rcopy else None
    meanlcopy = sum(lcopy) / len(lcopy) if lcopy else None
    print(meanrcopy)
    print(meanlcopy)
    with connection.cursor() as cursor:
        cursor.execute("update reportdatastore set rmeancopx=%s, rmeancopy=%s , lmeancopx=%s, lmeancopy=%s where sessionid=%s",[meanrcopx, meanrcopy, meanlcopx, meanlcopy, ssnid])
        rc=cursor.rowcount
    if rc >0:
         return 1
    else :
         return 0


def computestepcnt(ssnid):
    # read left leg count
    queryl = "SELECT distinct(s12) from sensordata where sessionid =%s and soletype='L'"
    with connection.cursor() as cursor:
        cursor.execute( queryl,[ssnid])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    print(p)
    arr = []
    for i in p:
        arr.append(i[0])
    print(arr)
    stepcntl = max(arr)
    print("left step count", stepcntl)

    # right leg
    queryr = "SELECT distinct(s12) from sensordata where sessionid =%s and soletype='R'"
    with connection.cursor() as cursor:
        cursor.execute(queryr,[ssnid])
        cnt = cursor.rowcount
        p = cursor.fetchall()
    print(p)
    arr = []
    for i in p:
        arr.append(i[0])
    print(arr)
    stepcntr = max(arr)
    print("right step count", stepcntr)
    with connection.cursor() as cursor:
        cursor.execute(
            "update reportdatastore set lstepcnt=%s, rstepcnt=%s , totalstepcnt=%s where sessionid=%s",[stepcntl,stepcntr,(stepcntl+stepcntr),ssnid])
        rc = cursor.rowcount
    if rc > 0:
        return 1
    else:
        return 0

def cadencecal(steps):
    print("computing cadence()..................")
    # Sampling frequency
    fs = 40  # 40 Hz
    farr = []
    # Calculate time per sample
    time_per_sample = 1 / fs

    # Calculate total duration in seconds
    total_duration = len(steps) * time_per_sample

    # Initialize variables
    current_time = 0
    block_number = 1

    # Process data in blocks
    while current_time < total_duration:
        # Determine the end of the current block (either 1 minute or the remaining duration)
        if current_time + 60 <= total_duration:
            block_duration = 60  # 1 minute
        else:
            block_duration = total_duration - current_time

        # Determine the number of samples in the current block
        num_samples = round(block_duration / time_per_sample)

        # Extract the current block data
        current_block_data = steps[:num_samples]

        # Calculate step count in the current block
        step_count = max(current_block_data) - min(current_block_data)

        # Print the results
        print(f'Block {block_number}: Duration = {block_duration:.2f} seconds, Step Count = {step_count}')
        farr.append({"block": block_number, "duration": block_duration, "stepcount": step_count})
        # Update variables
        current_time += block_duration
        step_count_data = steps[num_samples:]
        block_number += 1

    # Separate arrays for block, duration, and stepcount
    block_array = [item["block"] for item in farr]
    duration_array = [item["duration"] for item in farr]
    stepcount_array = [item["stepcount"] for item in farr]
    print(duration_array, stepcount_array)
    return duration_array,stepcount_array


def computecadence(ssnid):
    ###################################### for 11/16 sensor data LEFT insole ##############
    print("here reading data for 11/16 sensor LEFT ...................")
    with connection.cursor() as cursor:
        cursor.execute("select s12, capturedtime from sensordata where  soletype = 'L' and sessionid=%s group by s12,capturedtime order by capturedtime asc",[ssnid])
        slval = cursor.fetchall()
        lcount = cursor.rowcount
        print(lcount, slval)
        # Extract relevant columns
        dd = pd.DataFrame(slval)
        stepz = dd[0]
        print("values from table...............",stepz)
        timel, cadl = cadencecal(stepz)
        print("outcomes for cadence 11 sensor data left....", timel, cadl)
    ###################################### for 11/16 sensor data RIGHT insole ##############
    print("here reading data for 11 sensor RIGHT ...................")
    with connection.cursor() as cursor:
        cursor.execute("select s12 ,capturedtime from sensordata where  soletype = 'R' and sessionid=%s group by s12, capturedtime order by capturedtime asc",[ssnid])
        srval = cursor.fetchall()
        rc=cursor.rowcount
        print(rc)
        print(srval)
        rcount = cursor.rowcount
        ddr = pd.DataFrame(srval)
        stepz = ddr[0]
        print(len(stepz))
        # Extract relevant columns
        timer, cadr = cadencecal(stepz)
        print("outcomes for cadence 11 sensor data right.....",timer, cadr)
    with connection.cursor() as cursor:
        cursor.execute(
            "update reportdatastore set lcadence=%s, ltime=%s , rcadence=%s, rtime=%s where sessionid=%s",[cadl,timel,cadr,timer,ssnid])
        rc = cursor.rowcount
    if rc > 0:
        return 1
    else:
        return 0

# Calculate Stride Length Variability (Coefficient of Variation)
def stride_length_variability(strides):
    mean_stride_length = np.mean(strides)
    std_dev_stride_length = np.std(strides)
    cv = (std_dev_stride_length / mean_stride_length) * 100
    return cv

# Calculate Stride Length Asymmetry (Symmetry Index)
def stride_length_asymmetry(right_leg_strides, left_leg_strides):
    mean_right_leg = np.mean(right_leg_strides)
    mean_left_leg = np.mean(left_leg_strides)
    si = ((mean_right_leg - mean_left_leg) / (mean_right_leg + mean_left_leg)) * 100
    return si

def swingstancecal(toe,heel,t):
    # Calculate automatic threshold for toe and heel using Otsu's method
    toes = np.array(toe)
    heels = np.array(heel)
    ts = np.array(t)
    print(" in swingstancecal()..........")
    # print(toe, toes)
    threshold_toe = threshold_otsu(toes)
    threshold_heel = threshold_otsu(heels)

    # Classify each time point as stance, swing, or no phase
    stance_phase = (toes > threshold_toe) & (heels > threshold_heel)
    swing_phase = (toes <= threshold_toe) & (heels <= threshold_heel)
    no_phase = ~(stance_phase | swing_phase)

    # Merge "no phase" data with stance phase
    stance_phase = stance_phase | no_phase

    # Identify transitions and calculate durations
    stance_durations = []
    swing_durations = []

    # Initialize current phase based on the first data point
    if stance_phase[0]:
        current_phase = 'stance'
    elif swing_phase[0]:
        current_phase = 'swing'
    else:
        current_phase = 'no phase'

    start_time = ts[0]

    for i in range(1, len(ts)):
        if stance_phase[i]:
            if current_phase != 'stance':
                if current_phase == 'swing' and start_time != ts[i - 1]:
                    swing_durations.append(ts[i - 1] - start_time)
                elif current_phase == 'no phase' and start_time != ts[i - 1]:
                    stance_durations.append(ts[i - 1] - start_time)
                current_phase = 'stance'
                start_time = ts[i]
        elif swing_phase[i]:
            if current_phase != 'swing':
                if current_phase == 'stance' and start_time != ts[i - 1]:
                    stance_durations.append(ts[i - 1] - start_time)
                elif current_phase == 'no phase' and start_time != t[i - 1]:
                    swing_durations.append(ts[i - 1] - start_time)
                current_phase = 'swing'
                start_time = ts[i]
        else:
            if current_phase != 'no phase':
                if current_phase == 'stance':
                    stance_durations.append(ts[i - 1] - start_time)
                elif current_phase == 'swing':
                    swing_durations.append(ts[i - 1] - start_time)
                current_phase = 'no phase'
                start_time = ts[i]

    # Append the last phase duration if it ends at the last data point
    if current_phase == 'stance':
        stance_durations.append(ts[-1] - start_time)
    elif current_phase == 'swing':
        swing_durations.append(ts[-1] - start_time)

    # Convert durations to milliseconds (assuming t is in seconds)
    stance_durations = np.array(stance_durations)
    swing_durations = np.array(swing_durations)
    return swing_durations,stance_durations

def computeswingstancevrasym(ssnid,nos,th):
    if (nos == 11):
        print("computing 11 sensor data swingstance......................")
        ###################################### for 11 sensor data LEFT insole ############## LEFT INSOLE
        print("computing swingstance for left ......................")
        with connection.cursor() as cursor:
            cursor.execute("select s1,s2,s3,s4,s5, capturedtime from sensordata where  soletype = 'L' and sessionid=%s group by s1,s2,s3,s4,s5,capturedtime order by capturedtime asc", [ssnid])
            slval = cursor.fetchall()
            lcount = cursor.rowcount
            print("computeswingstancevarsym() values fetched from db............", len(slval))
            aa = pd.DataFrame(slval)
            # print(aa)
            # toe ==> s1,s2,s3 and heel ==> s4,s5
            t = aa[5]
            s1 = aa[0] #toe
            s2 = aa[1]
            s3 =aa[2]
            s4 = aa[3] #heel
            s5 = aa[4]
            if (th == 4):
                toe = [sum(x) / len(x) for x in zip(s1, s2)]
                heel = s4
            elif (th == 5):
                toe = [sum(x) / len(x) for x in zip(s1, s3)]
                heel = s5
            elif (th == 0):
                toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]
                heel = s5
            else :
                toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]
                heel = [sum(x) / len(x) for x in zip(s4, s5)]
            swl, stl = swingstancecal(toe, heel, t)
            print("left :",swl, stl)
            # Calculate the average
            avgswl = sum(swl) / len(swl)
            avgstl = sum(stl) / len(stl)
            lswvar = stride_length_variability(swl)
            lstvar = stride_length_variability(stl)
            print("left variablibity :",lswvar, lstvar)
        ###################################### for 11 sensor data LEFT insole ############## LEFT INSOLE
        print("computing swingstance for right ......................")
        with connection.cursor() as cursor:
                cursor.execute("select s1,s2,s3,s4,s5,capturedtime from sensordata where  soletype ='R' and sessionid=%s group by s1,s2,s3,s4,s5,capturedtime order by capturedtime asc",[ssnid])
                srval = cursor.fetchall()
                rcount = cursor.rowcount
                print("computeswingstancevarsym() values fetched from db............")
                aa = pd.DataFrame(srval)
                # Extract relevant columns
                # toe ==> s1,s2,s3 and heel ==> s4,s5
                t = aa[5]
                s1 = aa[0] #toe
                s2 = aa[1]
                s3 = aa[2]
                s4 = aa[3] #heel
                s5 = aa[4]
                if (th == 4):
                    toe = [sum(x) / len(x) for x in zip(s1, s2)]
                    heel = s4
                elif (th == 5):
                    toe = [sum(x) / len(x) for x in zip(s1, s3)]
                    heel = s5
                elif (th == 0):
                    toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]
                    heel = s5
                else:
                    toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]
                    heel = [sum(x) / len(x) for x in zip(s4, s5)]
                swr, str1 = swingstancecal(toe, heel, t)
                print("right :", swr, str1)
                # Calculate the average
                avgswr = sum(swr) / len(swr)
                avgstr1 = sum(str1) / len(str1)
                rswvar = stride_length_variability(swr)
                rstvar = stride_length_variability(str1)
                swasym = stride_length_asymmetry(swl, swr)
                stasym = stride_length_asymmetry(stl,str1)
                print("right variablibity :", rswvar, rstvar, "asym swing",swasym, " stance",stasym)
    else:
        print("computing 16 sensor data swingstance......................")
        ###################################### for 16 sensor data LEFT insole ############## LEFT INSOLE
        print("computing swingstance for left ......................")
        with connection.cursor() as cursor:
            cursor.execute("select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18, capturedtime from sensordata where  soletype = 'L' and sessionid=%s order by capturedtime asc",[ssnid])
            slval = cursor.fetchall()
            lcount = cursor.rowcount
            print("computeswingstancevarsym() values fetched from db............")
            aa = pd.DataFrame(slval)
            # Extract relevant columns
            # for 10 fsr  heel : s16,s17,s18 and for toe : s3,s4,s5,s14
            t = aa[10]
            s1 = aa[2]  # toe
            s2 = aa[3]
            s3 = aa[4]
            s4 = aa[5]
            s5 = aa[7]  # heel
            s6 = aa[8]
            s7 = aa[9]
            # Calculate toe and heel values
            toe = [sum(x) / len(x) for x in zip(s1, s2, s3, s4)]
            heel = [sum(x) / len(x) for x in zip(s5, s6, s7)]
            swl, stl = swingstancecal(toe, heel, t)
            # print("left :", swl, stl)
            # Calculate the average
            avgswl = sum(swl) / len(swl)
            avgstl = sum(stl) / len(stl)
            lswvar = stride_length_variability(swl)
            lstvar = stride_length_variability(stl)
            print("left variablibity :", lswvar, lstvar)
        ###################################### for 16 sensor data LEFT insole ############## RIGHT INSOLE
        print("computing swingstance for right ......................")
        with connection.cursor() as cursor:
            cursor.execute("select s1,s2,s3,s4,s5,s14,s15,s16,s17,s18, capturedtime from sensordata where  soletype = 'R' and sessionid=%s  order by capturedtime asc", [ssnid])
            srval = cursor.fetchall()
            rcount = cursor.rowcount
            print("computeswingstancevarsym() values fetched from db............")
            aa = pd.DataFrame(srval)
            # print(aa)
            # Extract relevant columns
            # for 10 fsr  heel : s16,s17,s18 and for toe : s3,s4,s5,s14
            t = aa[10]
            s1 = aa[2]  # toe
            s2 = aa[3]
            s3 = aa[4]
            s4 = aa[5]
            s5 = aa[7]  # heel
            s6 = aa[8]
            s7 = aa[9]
            toe = [sum(x) / len(x) for x in zip(s1, s2, s3, s4)]
            heel = [sum(x) / len(x) for x in zip(s5, s6, s7)]
            swr, str1 = swingstancecal(toe, heel, t)
            # print("right :", swr, str1)
            # Calculate the average
            avgswr = sum(swr) / len(swr)
            avgstr1 = sum(str1) / len(str1)
            rswvar = stride_length_variability(swr)
            rstvar = stride_length_variability(str1)
            swasym = stride_length_asymmetry(swl, swr)
            stasym = stride_length_asymmetry(stl, str1)
            print("right variablibity :", rswvar, rstvar, "asym swing", swasym, " stance", stasym)
    # Convert the swl array to a PostgreSQL array string format
    swlstr = '{' + ','.join(map(str, swl)) + '}'
    swrstr = '{' + ','.join(map(str, swr)) + '}'
    str1str = '{' + ','.join(map(str, str1)) + '}'
    stlstr = '{' + ','.join(map(str, stl)) + '}'


    with connection.cursor() as cursor:
        cursor.execute(
            "update reportdatastore set rswingtime=%s, lswingtime=%s, rstancetime=%s, lstancetime=%s , rswingtimevar=%s ,lswingtimevar=%s ,rstancetimevar=%s, lstancetimevar=%s, swingasym=%s, stanceasym=%s, lavgswing=%s, lavgstance=%s, ravgswing=%s, ravgstance=%s where sessionid=%s",
            [ swrstr,swlstr,str1str,stlstr,rswvar,lswvar, rstvar,lstvar, swasym, stasym, avgswl,avgstl,avgswr,avgstr1, ssnid])

        rc = cursor.rowcount
    if rc > 0:
        return 1
    else:
        return 0

def strideahrsmodz(svalues, nos,th):
    print("nos is", nos)
    print("len of svals in strideahrsmodz() ", len(svalues))

    # step 2 - AHRS class
    class AHRS:
        def __init__(self, *args):
            self.SamplePeriod = 1 / 33
            self.Quaternion = [1, 0, 0, 0]
            self.Kp = 2
            self.Ki = 0
            self.KpInit = 200
            self.InitPeriod = 5
            self.q = [1, 0, 0, 0]
            self.IntError = [0, 0, 0]
            self.KpRamped = None
            for i in range(0, len(args), 2):
                if args[i] == 'SamplePeriod':
                    self.SamplePeriod = args[i + 1]
                elif args[i] == 'Quaternion':
                    self.Quaternion = args[i + 1]
                    self.q = self.quaternConj(self.Quaternion)
                elif args[i] == 'Kp':
                    self.Kp = args[i + 1]
                elif args[i] == 'Ki':
                    self.Ki = args[i + 1]
                elif args[i] == 'KpInit':
                    self.KpInit = args[i + 1]
                elif args[i] == 'InitPeriod':
                    self.InitPeriod = args[i + 1]
                else:
                    raise ValueError('Invalid argument')
            self.KpRamped = self.KpInit

        def Update(self, Gyroscope, Accelerometer, Magnetometer):
            raise NotImplementedError('This method is unimplemented')

        def UpdateIMU(self, Gyroscope, Accelerometer):
            if norm(Accelerometer) == 0:
                print('Accelerometer magnitude is zero. Algorithm update aborted.')
                return
            else:
                Accelerometer = Accelerometer / norm(Accelerometer)
            v = [2 * (self.q[1] * self.q[3] - self.q[0] * self.q[2]),
                 2 * (self.q[2] * self.q[3] + self.q[0] * self.q[1]),
                 self.q[0] ** 2 - self.q[1] ** 2 - self.q[2] ** 2 + self.q[3] ** 2]
            error = np.cross(v, Accelerometer)
            self.IntError = self.IntError + error
            Ref = Gyroscope - (self.Kp * error + self.Ki * self.IntError)
            pDot = 0.5 * self.quaternProd(self.q, [0, float(Ref[0]), float(Ref[1]), float(Ref[2])])
            self.q = self.q + pDot * self.SamplePeriod
            self.q = self.q / norm(self.q)
            self.Quaternion = self.quaternConj(self.q)

        def quaternProd(self, a, b):
            # Ensure a and b are lists or arrays
            a = np.array(a)
            b = np.array(b)

            ab = np.array([
                a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
                a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
                a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
                a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]
            ])
            return ab

        def quaternConj(self, q):
            qConj = [q[0], -q[1], -q[2], -q[3]]
            return qConj

    # step3

    def quaternProd(a, b):
        ab = [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
              a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
              a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
              a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]]
        # print(ab)
        return ab

    def quaternConj(q):
        qConj = [q[0], -q[1], -q[2], -q[3]]
        # print(qConj)
        return qConj

    def quaternRotate(v, q):
        row, col = v.shape
        v0XYZ = quaternProd(quaternProd(q, np.hstack((np.zeros((row, 1)), v))), quaternConj(q))
        v = np.array(v0XYZ)[:, 1:4]
        return v

    def extract_ranges(t, heel, toe, threshold=500):
        print("in_extract_ranges()................")
        # Detect peaks using the specified method
        peaks = []
        for i in range(1, len(heel) - 1):  # 1 to last index
            if heel[i - 1] < heel[i] >= heel[i + 1] and heel[i] > threshold:
                peaks.append(i)
                # prev value less than present it is grator than or equal to next and grater than threshould
        # if not peaks:  # Check if the list is empty
        #     print("peak list is empty. Cannot extract ranges.")
        #     return []
        # Identify clusters of nearby peaks
        if peaks == []:
            return []
        clustered_peaks = []
        current_cluster = [peaks[0]]
        for i in range(1, len(peaks)):
            if peaks[i] - peaks[i - 1] <= 5:
                current_cluster.append(peaks[i])
            else:
                # Calculate the median of the current cluster and store it
                clustered_peaks.append(int(np.median(current_cluster)))
                current_cluster = [peaks[i]]

        # Include the last cluster
        # clustered_peaks.append(int(np.median(current_cluster)))

        # Get corresponding time values for peaks
        peak_times = [t[i] for i in clustered_peaks]

        # Store first_intersection_time values in an array
        first_intersection_times = []
        samples_for_first_intersection = []
        indices_for_first_intersection = []

        # Plot the original signal and the identified peaks
        # plt.plot(t, heel, label='Heel Pressure')
        # plt.plot(t, toe, label='Toe Pressure')
        # plt.plot(peak_times, [heel[i] for i in clustered_peaks], 'gx')

        # Plot segments between intersections
        for i in range(len(clustered_peaks)):
            if i < len(clustered_peaks) - 1:
                start_index = clustered_peaks[i]
                end_index = clustered_peaks[i + 1]

                # Find the first intersection point between 'heel' and 'toe' signals
                # intersections = np.where(np.diff(np.sign(heel[start_index:end_index] - toe[start_index:end_index])))[0]
                heel_array = np.array(heel[start_index:end_index])
                toe_array = np.array(toe[start_index:end_index])

                intersections = np.where(np.diff(np.sign(heel_array - toe_array)))[0]

                if len(intersections) > 0:
                    # Get the time value of the first intersection
                    first_intersection_time = t[start_index:end_index][intersections[0]]
                    first_intersection_times.append(first_intersection_time)

                    # Store corresponding samples and indices
                    sample_index = start_index + intersections[0]
                    samples_for_first_intersection.append(heel[sample_index])
                    indices_for_first_intersection.append(sample_index)

                    # Plot the segment between consecutive intersections
                    # plt.axvline(first_intersection_time, color='red', linestyle='--')

        # Store start time, end time, and first intersection times in a single array
        time_array = [t[0]] + first_intersection_times + [t[-1]]
        ta = time_array
        # print(time_array)
        indices_for_first_intersection = [0] + indices_for_first_intersection + [len(heel) - 1]

        # Print the array of start_time, end_time, first_intersection_times, and corresponding samples and indices
        #     print("Stride Time:", time_array)
        #     print("Samples:", samples_for_first_intersection)
        #     print("Sample Indices:", indices_for_first_intersection)
        print("in extract_ranges()...........", indices_for_first_intersection)
        return indices_for_first_intersection

    columns = list(zip(*svalues))
    a1=[]
    b1=[]
    if (nos == 11):
        # Unpack the columns into separate variables-----------s14 is 'L/R' ie., soletype
        s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, t12 = columns
        print("in 11 sensor data  extracted...................................")
        # For Toe: s1,s2,s3 and for Heel: s4,s5.
        if (th == 4):
            toe = [sum(x) / len(x) for x in zip(s1, s2)]
            heel = s5
        elif (th == 5):
            toe = [sum(x) / len(x) for x in zip(s1, s3)]
            heel = s5
        elif (th == 0):
            toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]
            heel = s5
        else:
            toe = [sum(x) / len(x) for x in zip(s1, s2, s3)]
            heel = [sum(x) / len(x) for x in zip(s4, s5)]

        print("toe and heel computed .................")

    else:
        # Unpack the columns into separate variables-----------'L/R'
        # <---5 fsr  -->|<---imu----------->|stepcount|                      |<-2nd part  5 FSR->|
        # s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11  s12 s13   soletype capturedtime s14 15 s16 s17 s18
        s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, stype, t12, s14, s15, s16, s17, s18 = columns
        # For Toe: s3,s4,s5,s6 and for Heel: s8,s9,s10.
        toe = [sum(x) / len(x) for x in zip(s3, s4, s5, s14)]
        heel = [sum(x) / len(x) for x in zip(s16, s17, s18)]

    Fs = 40
    ranges = []
    # Extract ranges using the function
    ranges = extract_ranges(t12, heel, toe)
    tim_array = []
    if len(ranges) == 0:
        print("no ranges detected .............")
        return []
    for ty in range(0, len(ranges)):
        tim_array.append(int(t12[ranges[ty]]))

    # Initialize an empty list to store all position values values
    print("times", tim_array)
    print("ranges", ranges)

    max_pos_values = []
    max_pos_time = []
    # Perform processing for each range
    for i in range(len(ranges) - 1):
        # print("ï th value.........................................................", i)
        start_index = ranges[i]
        end_index = ranges[i + 1]
        axt = s6[start_index:end_index]
        accX = [float(value) / 9.8 for value in axt]

        ayt = s7[start_index:end_index]
        accY = [float(value) / 9.8 for value in ayt]

        azt = s8[start_index:end_index]
        accZ = [float(value) / 9.8 for value in azt]

        gxt = s9[start_index:end_index]
        gyrX = [float(value) * 57.29 for value in gxt]

        gyt = s10[start_index:end_index]
        gyrY = [float(value) * 57.29 for value in gyt]

        gzt = s11[start_index:end_index]
        gyrZ = [float(value) * 57.29 for value in gzt]

        t = t12[start_index:end_index]

        t11 = t
        L1 = len(t)
        time = np.arange(L1)
        # step4

        # acc_mag = np.sqrt(accX ** 2 + accY ** 2 + accZ ** 2)
        # Convert lists to NumPy arrays
        accX_array = np.array(accX)
        accY_array = np.array(accY)
        accZ_array = np.array(accZ)

        # Calculate the magnitude of acceleration
        acc_mag = np.sqrt(accX_array ** 2 + accY_array ** 2 + accZ_array ** 2)
        # print("acc_mag",acc_mag)
        # Detect stationary periods
        sample_period = 1 / Fs
        filt_cutoff = 0.0001

        # High-pass filter accelerometer data
        b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'high')
        try :
            acc_magFilt = filtfilt(b, a, acc_mag)
            acc_magFilt = np.abs(acc_magFilt)

            # Low-pass filter accelerometer data
            filt_cutoff = 5
            b, a = butter(1, (2 * filt_cutoff) / (1 / sample_period), 'low')
            acc_magFilt = filtfilt(b, a, acc_magFilt)
        except Exception as e:
            print("here............",e)
        # For  left insole  Stationary = 0.03, Kp1 = 0.01, Kp2 = 0.01.
        # For right  insole  Stationary = 0.05, Kp1 = 0.5, Kp2 = 0.4
        # Threshold detection
        stationary = acc_magFilt < (0.03)
        # step 5
        # Compute orientation
        quat = np.zeros((len(time), 4))
        AHRSalgorithm = AHRS('SamplePeriod', 1 / Fs, 'Kp', 1, 'KpInit', 1)

        # Initial convergence
        initPeriod = 2
        indexSel = np.arange(np.argmax(time > (time[0] + initPeriod)))
        for i in range(500):
            # print("11111111111111111111111111111111")
            # AHRSalgorithm.UpdateIMU([0, 0, 0], [np.mean(accX[indexSel]), np.mean(accY[indexSel]), np.mean(accZ[indexSel])])
            AHRSalgorithm.UpdateIMU([0, 0, 0],
                                    [np.mean(accX_array[indexSel]), np.mean(accY_array[indexSel]),
                                     np.mean(accZ_array[indexSel])])
            # print("111111111111111222222222222222222222")
        # For all data
        for t in range(len(time)):
            # For  left insole  Stationary = 0.03, Kp1 = 0.01, Kp2 = 0.01.
            # For right  insole  Stationary = 0.05, Kp1 = 0.5, Kp2 = 0.4
            if stationary[t]:
                AHRSalgorithm.Kp = 0.01
                # AHRSalgorithm.Kp = kval1
            else:
                AHRSalgorithm.Kp = 0.01
                # AHRSalgorithm.Kp = kval2
            AHRSalgorithm.UpdateIMU(np.deg2rad([gyrX[t], gyrY[t], gyrZ[t]]), [accX[t], accY[t], accZ[t]])
            quat[t, :] = AHRSalgorithm.Quaternion
            # print((quat[t,:]))

        # Compute translational accelerations
        # Rotate accelerations from sensor frame to E````````````````````````````````````````arth frame
        # Function to rotate vector v by quaternion q
        def quatern_conj(q):
            if q.ndim == 1:
                return np.array([q[0], -q[1], -q[2], -q[3]])
            elif q.ndim == 2:
                return np.array([q[:, 0], -q[:, 1], -q[:, 2], -q[:, 3]]).T
            else:
                raise ValueError("Invalid dimension for quaternion array")

        def quatern_rotate(v, q):
            q_conj = quatern_conj(q)
            v_quat = np.concatenate(([0], v))
            result_quat = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)
            return result_quat[1:]

        def quaternion_multiply(q1, q2):
            w1, x1, y1, z1 = q1
            w2, x2, y2, z2 = q2
            w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
            x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
            y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
            z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
            return np.array([w, x, y, z])

        # step6

        # compute transilational acceleration

        acc1 = np.column_stack((accX, accY, accZ))
        quat_conj = quatern_conj(quat)
        # print(quat_conj)

        acc2 = np.array([quatern_rotate(row, quat_conj[i, :]) for i, row in enumerate(acc1)])
        # print(acc2 )

        acc = acc2 * 9.8

        acc[:, 2] -= 9.8

        time = np.array(time)

        # step 7
        # Integrate acceleration to yield velocity
        vel = np.zeros(acc.shape)
        for t in range(1, vel.shape[0]):
            vel[t, :] = vel[t - 1, :] + acc[t, :] * sample_period
            if stationary[t] == 1:
                vel[t, :] = [0, 0, 0]  # apply ZUPT update when foot stationary

        # Compute integral drift during non-stationary periods
        velDrift = np.zeros(vel.shape)
        stationaryStart = np.where(np.diff(stationary) == 1)[0]
        stationaryEnd = np.where(np.diff(stationary) == -1)[0]
        for i in range(len(stationaryEnd)):
            driftRate = vel[stationaryStart[i] - 1, :] / (stationaryStart[i] - stationaryEnd[i])
            enum = np.arange(1, stationaryStart[i] - stationaryEnd[i] + 1)
            drift = np.column_stack((enum * driftRate[0], enum * driftRate[1], enum * driftRate[2]))
            velDrift[stationaryEnd[i]:stationaryStart[i] - 1, :] = drift

        # Remove integral drift
        vel = vel - velDrift

        # Compute translational position
        print("aaaaaaaaaaa.............")
        # Integrate velocity to yield position
        pos = np.zeros(vel.shape)
        for t in range(1, pos.shape[0]):
            pos[t, :] = pos[t - 1, :] + vel[t, :] * sample_period
        print("bbbbbbbbbbb.............")
        posX = np.abs(pos[:, 1])
        print("Max value of position...", np.max(posX))

        max_pos = np.max(posX)
        max_pos_values.append(max_pos)
        print("ccccccccccc.............")
    try :
        print("computed positions............", max_pos_values)
        print("computed times ..............", tim_array)
        a1= max_pos_values
        b1=tim_array
    except Exception as e:
        print(f"Unexpected {err=}, {type(err)=}")
        max_pos_values=a1
        tim_array=b1
    if (len(ranges) > 0):
        timestart = tim_array[0]
        sc = 1
        stride = []
        tsum = 0
        print("len is ...",len(max_pos_values))
        for ts in range(1, (len(max_pos_values))):
            tt = ((tim_array[ts + 1] - 1) - tim_array[ts]) * 0.001
            print(ts, tim_array[ts], max_pos_values[ts], tt, (max_pos_values[ts] / tt))
            if ((max_pos_values[ts]>=0.6) and (max_pos_values[ts]<=1.5)):
                stride.append({"strideno": sc, "dist": max_pos_values[ts], "time": tim_array[ts],
                           "velocity": (max_pos_values[ts] / tt)})
                sc = sc + 1
                tsum = tsum + max_pos_values[ts]

        print("strides  :", stride)
        print("total distance :", tsum, "m/s2")
        return stride
    else:
        print("No strides detected.........................")
        return []


##########################################################################################################


def computestrides(ssnid,nos,th):  # online stride computation using AHRS
        if (nos == 11):
            # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data,<s12 and s13 for step size >,solytype,capturedtime  ===> 5 FSR
            # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data ,,<s12 and s13 for step size >,solytype,capturedtime,<s14,s15,s16,s17,s18>
            # which are 2nd part of FSR  ie., 1st part FSR(s1,s2,s3,s4,s5) + 2nd part FSR (s14,s15,s16,s17,s18)  ===>10 FSR(s1,s2,s3,s4,s5,s14,s15,s16,s17,s18)
            # for right leg data
            with connection.cursor() as cursor:
                cursor.execute("select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime from sensordata where sessionid =%s and soletype='R'  group by s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime order by capturedtime asc", [ssnid])
                sval = cursor.fetchall()
                rcnt = cursor.rowcount
            print("11 sensor right leg total rows .............",len(sval))
        else :
            # for right leg data
            with connection.cursor() as cursor:
                cursor.execute(
                    "select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,s14,s15,s16,s17,s18 from sensordata where sessionid =%s and soletype='R' order by capturedtime asc",
                    [ssnid])
                sval = cursor.fetchall()
                rcnt = cursor.rowcount
            print("16 sensor right leg total rows .............", len(sval))
        with connection.cursor() as cursor:
            cursor.execute("select min(capturedtime), max(capturedtime) from sensordata where sessionid =%s and soletype='R'",[ssnid])
            tim = cursor.fetchall()

        stimez = tim[0][0]
        etimez = tim[0][1]
        print("starttime:",stimez," endtime:", etimez)
        rdone = 0
        totaldist = 0.0
        # for right leg data
        print("total right rows:...............", len(sval))
        if (len(sval) > 0):
            print("right calling strideahrsmodz()...............")
            try:
                print("for right sval", len(sval), "nos", nos,"th:",th)
                rsl = strideahrsmodz(sval, nos, th)
                print("Right stride length is ...........", rsl, "len", len(rsl))
                stype = 'R'
                if (len(rsl) > 0):
                    totaldist = 0.0
                    rc = 0
                    with connection.cursor() as cursor:
                        # data in rsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                        for r in rsl:
                            print(r)
                            if (r["dist"] >=0.5) and (r["dist"] <=1.5):
                                sessionid = int(ssnid)
                                # strideno = int(r["strideno"])
                                strideno = 0
                                dist = float(r["dist"])
                                velocity = float(r["velocity"])
                                stz = r["time"]
                                if (rc < len(rsl) - 1):
                                    print("value is................",((rsl[rpc + 1]["time"]) - 1))
                                    etz = int((rsl[rc + 1]["time"]) - 1)
                                else:
                                    etz = int(etimez)

                                print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                      "strideno", strideno, "dist", dist, "velocity", velocity)
                                try:
                                    p = cursor.execute(
                                        "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                        [sessionid, stz, etz, stype, strideno, dist, velocity])
                                except Exception as e:
                                    # Handle any other unexpected exceptions
                                    print(f"An unexpected error occurred: {e}")

                                if not p:
                                    totaldist = totaldist + dist
                                    rc = rc + 1

                                    rdone = 1  # write into onlinestride  successful
                                else:
                                    rdone = 0  # it failed to write
                            else :
                                rpc = rpc+1
            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"An unexpected error occurred when Right calling strideahrsmodz(): {e}")
                rdone = 0  # failed
                # return JsonResponse({'status': 'error'})
                return 0


        else:
            rdone = 1  # rsl length is zero so no strides detected and written into table
            totaldist = 0.0

        print("right leg total distance:", totaldist)

        # for left leg data
        if (nos == 11):
            print("LEFT LEG DATA PROCESSING ....................................")
            # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data,<s12 and s13 for step size >,solytype,capturedtime  ===> 5 FSR
            # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data ,,<s12 and s13 for step size >,solytype,capturedtime,<s14,s15,s16,s17,s18>
            # which are 2nd part of FSR  ie., 1st part FSR(s1,s2,s3,s4,s5) + 2nd part FSR (s14,s15,s16,s17,s18)  ===>10 FSR(s1,s2,s3,s4,s5,s14,s15,s16,s17,s18)
            # for right leg data
            with connection.cursor() as cursor:
                cursor.execute(
                    "select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime from sensordata where sessionid =%s and soletype='L' group by s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime order by capturedtime asc",
                    [ssnid])
                sval = cursor.fetchall()
                rcnt = cursor.rowcount
            print("11 sensor left leg total rows .............",len(sval))
        else:
            # for right leg data 16 sensor
            with connection.cursor() as cursor:
                cursor.execute(
                    "select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,s14,s15,s16,s17,s18 from sensordata where sessionid =%s and soletype='L' order by capturedtime asc",
                    [ssnid])
                sval = cursor.fetchall()
                rcnt = cursor.rowcount
            print("16 sensor left leg total rows .............", len(sval))
        with connection.cursor() as cursor:
            cursor.execute(
                "select min(capturedtime), max(capturedtime) from sensordata where sessionid =%s and soletype='R'",
                [ssnid])
            tim = cursor.fetchall()
        stimez = tim[0][0]
        etimez = tim[0][1]
        print("starttime:",stimez," endtime:", etimez)
        # for left leg data
        print("total LEFT  rows:...............", len(sval))
        ldone = 0
        totdist = 0.0
        if (len(sval) > 0):
            print("left calling strideahrsmodz()...............")
            try:
                # lsl = strideahrs(sval)
                # lsl = strideahrs16(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, t12, s14, s15, s16, s17, s18)
                print("for left sval", len(sval), "nos", nos, "th ", th)
                lsl = strideahrsmodz(sval, nos, th)
                print("Left stride length is ...........", lsl, "len", len(lsl))
                stype = 'L'
                if (len(lsl) > 0):
                    totdist = 0.0
                    rc = 0
                    with connection.cursor() as cursor:
                        # data in lsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                        for l in lsl:
                            if ((l["dist"]>=0.5) and (l["dist"]<=1.5)):
                                sessionid = int(ssnid)
                                # strideno = int(l["strideno"])
                                strideno = 0
                                sno=0
                                dist = float(l["dist"])
                                velocity = float(l["velocity"])
                                stz = l["time"]
                                if (rc < len(lsl) - 1):
                                    etz = int((lsl[rc + 1]["time"]) - 1)
                                else:
                                    etz = int(etimez)

                                print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                      "strideno", strideno, "dist", dist, "velocity", velocity)
                                try:
                                    p = cursor.execute(
                                        "insert into onlinestride(sessionid,starttime,endtime,soletype, distance, velocity)   values(%s,%s,%s,%s,%s,%s)",
                                        [sessionid,stz, etz, stype, dist, velocity])
                                except Exception as e:
                                    # Handle any other unexpected exceptions
                                    print(f"An unexpected error occurred: {e}")

                                if not p:
                                    totdist = totdist + dist
                                    rc = rc + 1
                                    ldone = 1  # its successful
                                else:
                                    ldone = 0  # it failed
                        print("left leg total distance:", totdist)

            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"An unexpected error occurred when left calling strideahrsmodz(): {e}")
                ldone = 0  # failed
                # return JsonResponse({'status': 'error'})
                return 0


        else:
            ldone = 1  # lsl length is zero so no strides detected and written into table
            totdist = 0.0

        if (rdone == 1) and (ldone == 1):

            print("total total distance:     left =", totdist, "   right =", totaldist, " L+R=",
                  (totaldist + totdist))
            # return JsonResponse({'status': 'success'})
            return 1
        elif ((rdone == 1) and (ldone == 0)) or ((rdone == 0) and (ldone == 1)):
            print("total distance:", (totaldist + totdist), "right distance:", totaldist, "left distance: ",
                  totdist)
            # return JsonResponse({'status': 'success'})
            return 1
        else:
            # return JsonResponse({'status': 'error'})
            return 0


def computestridesmod(ssnid, nos, th):  # online stride computation using AHRS
    if (nos == 11):
        # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data,<s12 and s13 for step size >,solytype,capturedtime  ===> 5 FSR
        # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data ,,<s12 and s13 for step size >,solytype,capturedtime,<s14,s15,s16,s17,s18>
        # which are 2nd part of FSR  ie., 1st part FSR(s1,s2,s3,s4,s5) + 2nd part FSR (s14,s15,s16,s17,s18)  ===>10 FSR(s1,s2,s3,s4,s5,s14,s15,s16,s17,s18)
        # for right leg data
        with connection.cursor() as cursor:
            cursor.execute(
                "select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime from sensordata where sessionid =%s and soletype='R'  group by s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime order by capturedtime asc",
                [ssnid])
            sval = cursor.fetchall()
            rcnt = cursor.rowcount
        print("11 sensor right leg total rows .............", len(sval))
    else:
        # for right leg data
        with connection.cursor() as cursor:
            cursor.execute(
                "select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,s14,s15,s16,s17,s18 from sensordata where sessionid =%s and soletype='R' order by capturedtime asc",
                [ssnid])
            sval = cursor.fetchall()
            rcnt = cursor.rowcount
        print("16 sensor right leg total rows .............", len(sval))
    with connection.cursor() as cursor:
        cursor.execute(
            "select min(capturedtime), max(capturedtime) from sensordata where sessionid =%s and soletype='R'", [ssnid])
        tim = cursor.fetchall()

    stimez = tim[0][0]
    etimez = tim[0][1]
    print("starttime:", stimez, " endtime:", etimez)
    rdone = 0
    totaldist = 0.0
    # for right leg data
    print("total right rows:...............", len(sval))
    if (len(sval) > 0):
        print("right calling strideahrsmodz()...............")
        try:
            print("for right sval", len(sval), "nos", nos, "th:", th)
            rsl = strideahrsmodz(sval, nos, th)
            print("Right stride length is ...........", rsl, "len", len(rsl))
            stype = 'R'
            if (len(rsl) > 0):
                totaldist = 0.0
                rc = 0
                with connection.cursor() as cursor:
                    # data in rsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                    for r in rsl:
                            sessionid = int(ssnid)
                            strideno = int(r["strideno"])
                            dist = float(r["dist"])
                            velocity = float(r["velocity"])
                            stz = r["time"]
                            if (rc < len(rsl) - 1):
                                print("value is................", int((rsl[rc + 1]["time"]) - 1))
                                etz = int((rsl[rc + 1]["time"]) - 1)
                            else:
                                etz = int(etimez)

                            print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                  "strideno", strideno, "dist", dist, "velocity", velocity)
                            try:
                                p = cursor.execute(
                                    "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                    [sessionid, stz, etz, stype, strideno, dist, velocity])
                            except Exception as e:
                                # Handle any other unexpected exceptions
                                print(f"An unexpected error occurred: {e}")

                            if not p:
                                totaldist = totaldist + dist
                                rc = rc + 1

                                rdone = 1  # write into onlinestride  successful
                            else:
                                rdone = 0  # it failed to write

        except Exception as e:
            # Handle any other unexpected exceptions
            print(f"An unexpected error occurred when Right calling strideahrsmodz(): {e}")
            rdone = 0  # failed
            # return JsonResponse({'status': 'error'})
            return 0


    else:
        rdone = 1  # rsl length is zero so no strides detected and written into table
        totaldist = 0.0

    print("right leg total distance:", totaldist)

    # for left leg data
    if (nos == 11):
        print("LEFT LEG DATA PROCESSING ....................................")
        # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data,<s12 and s13 for step size >,solytype,capturedtime  ===> 5 FSR
        # sarr should be  <sensor values from s1..s5> which are 1st part FSR , <s6..s11> which is imu data ,,<s12 and s13 for step size >,solytype,capturedtime,<s14,s15,s16,s17,s18>
        # which are 2nd part of FSR  ie., 1st part FSR(s1,s2,s3,s4,s5) + 2nd part FSR (s14,s15,s16,s17,s18)  ===>10 FSR(s1,s2,s3,s4,s5,s14,s15,s16,s17,s18)
        # for right leg data
        with connection.cursor() as cursor:
            cursor.execute(
                "select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime from sensordata where sessionid =%s and soletype='L' group by s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime order by capturedtime asc",
                [ssnid])
            sval = cursor.fetchall()
            rcnt = cursor.rowcount
        print("11 sensor left leg total rows .............", len(sval))
    else:
        # for right leg data 16 sensor
        with connection.cursor() as cursor:
            cursor.execute(
                "select s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,soletype,capturedtime,s14,s15,s16,s17,s18 from sensordata where sessionid =%s and soletype='L' order by capturedtime asc",
                [ssnid])
            sval = cursor.fetchall()
            rcnt = cursor.rowcount
        print("16 sensor left leg total rows .............", len(sval))
    with connection.cursor() as cursor:
        cursor.execute(
            "select min(capturedtime), max(capturedtime) from sensordata where sessionid =%s and soletype='R'",
            [ssnid])
        tim = cursor.fetchall()
    stimez = tim[0][0]
    etimez = tim[0][1]
    print("starttime:", stimez, " endtime:", etimez)
    # for left leg data
    print("total LEFT  rows:...............", len(sval))
    ldone = 0
    totdist = 0.0
    if (len(sval) > 0):
        print("left calling strideahrsmodz()...............")
        try:
            # lsl = strideahrs(sval)
            # lsl = strideahrs16(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, t12, s14, s15, s16, s17, s18)
            print("for left sval", len(sval), "nos", nos, "th ", th)
            lsl = strideahrsmodz(sval, nos, th)
            print("Left stride length is ...........", lsl, "len", len(lsl))
            stype = 'L'
            if (len(lsl) > 0):
                totdist = 0.0
                rc = 0
                with connection.cursor() as cursor:
                    # data in lsl is :   "strideno": sc, "dist": max_pos_values[ts], "time": (tt * 0.001),"velocity": vl
                    for l in lsl:
                            sessionid = int(ssnid)
                            strideno = int(l["strideno"])
                            dist = float(l["dist"])
                            velocity = float(l["velocity"])
                            stz = l["time"]
                            if (rc < len(lsl) - 1):
                                etz = int((lsl[rc + 1]["time"]) - 1)
                            else:
                                etz = int(etimez)

                            print("sessionid", sessionid, "starttime", stz, "endtime", etz, "soletype", stype,
                                  "strideno", strideno, "dist", dist, "velocity", velocity)
                            try:
                                p = cursor.execute(
                                    "insert into onlinestride(sessionid,starttime,endtime,soletype,strideno, distance, velocity)   values(%s,%s,%s,%s,%s,%s,%s)",
                                    [sessionid, stz, etz, stype, strideno, dist, velocity])
                            except Exception as e:
                                # Handle any other unexpected exceptions
                                print(f"An unexpected error occurred: {e}")

                            if not p:
                                totdist = totdist + dist
                                rc = rc + 1
                                ldone = 1  # its successful
                            else:
                                ldone = 0  # it failed
                    print("left leg total distance:", totdist)

        except Exception as e:
            # Handle any other unexpected exceptions
            print(f"An unexpected error occurred when left calling strideahrsmodz(): {e}")
            ldone = 0  # failed
            # return JsonResponse({'status': 'error'})
            return 0


    else:
        ldone = 1  # lsl length is zero so no strides detected and written into table
        totdist = 0.0

    if (rdone == 1) and (ldone == 1):

        print("total total distance:     left =", totdist, "   right =", totaldist, " L+R=",
              (totaldist + totdist))
        # return JsonResponse({'status': 'success'})
        return 1
    elif ((rdone == 1) and (ldone == 0)) or ((rdone == 0) and (ldone == 1)):
        print("total distance:", (totaldist + totdist), "right distance:", totaldist, "left distance: ",
              totdist)
        # return JsonResponse({'status': 'success'})
        return 1
    else:
        # return JsonResponse({'status': 'error'})
        return 0


def computestridevarasym(ssnid):
    print("here............")
    # Example stride lengths for right and left legs
    with connection.cursor() as cursor:
        cursor.execute("select distance from onlinestride where soletype ='R' and sessionid=%s order by starttime asc",[ssnid])
        rstrds= cursor.fetchall()
        print("rstrides fetched...............",rstrds)
        rc = cursor.rowcount
    print("................right", rc)
    rstrides=rstrds
    with connection.cursor() as cursor:
        cursor.execute("select distance from onlinestride where soletype ='L' and sessionid=%s order by starttime asc",[ssnid])
        lstrides = cursor.fetchall()
        print("lstrides fetched...............", lstrides)
        lc = cursor.rowcount
    print(".................left:",lc)
    if rc > lc:
        right_leg_strides = np.array(rstrides[:lc])
        left_leg_strides = np.array(lstrides)
    elif lc> rc:
        right_leg_strides = np.array(rstrides)
        left_leg_strides = np.array(lstrides[:rc])
    else:
        right_leg_strides = np.array(rstrides)
        left_leg_strides = np.array(lstrides)

    right_leg_cv = stride_length_variability(right_leg_strides)
    left_leg_cv = stride_length_variability(left_leg_strides)

    si = stride_length_asymmetry(right_leg_strides, left_leg_strides)
    print("results to be in table ",right_leg_cv,left_leg_cv,si,ssnid)

    with connection.cursor() as cursor:
        cursor.execute(
            "update reportdatastore set rslvar=%s, lslvar=%s, slasym=%s where sessionid=%s",[right_leg_cv,left_leg_cv,si,ssnid])
        rc = cursor.rowcount
    if rc > 0:
        return 1
    else:
        return 0




def computestridevelovarasym(ssnid):
    # Example stride lengths for right and left legs
    print("inside ..........computestridevelovarasym()..........")
    with connection.cursor() as cursor:
        cursor.execute("select velocity from onlinestride where soletype ='R' and sessionid=%s order by starttime asc",[ssnid])
        rstrds =cursor.fetchall()
        print("rstrides fetched...............", rstrds)
        rc = cursor.rowcount
    print("................right", rc)
    rstrides =rstrds
    with connection.cursor() as cursor:
        cursor.execute(
            "select velocity from onlinestride where soletype ='L' and sessionid=%s order by starttime asc",[ssnid])
        lstrides=cursor.fetchall()
        print("lstrides fetched...............", lstrides)
        lc = cursor.rowcount
    print(".................left:", lc)
    if rc > lc:
        right_leg_strides = np.array(rstrides[:lc])
        left_leg_strides = np.array(lstrides)
    elif lc> rc:
        right_leg_strides = np.array(rstrides)
        left_leg_strides = np.array(lstrides[:rc])
    else:
        right_leg_strides = np.array(rstrides)
        left_leg_strides = np.array(lstrides)

    right_leg_cv = stride_length_variability(right_leg_strides)
    left_leg_cv = stride_length_variability(left_leg_strides)

    si = stride_length_asymmetry(right_leg_strides, left_leg_strides)
    print("stride velo varasym............",right_leg_cv,left_leg_cv,si,ssnid)
    with connection.cursor() as cursor:
        cursor.execute(
            "update reportdatastore set rsvvar=%s, lsvvar=%s, svasym=%s where sessionid=%s",[right_leg_cv,left_leg_cv,si,ssnid])
        rc = cursor.rowcount
    if rc > 0:
        return 1
    else:
        return 0

def computeflatfoot(ssnid,th):
    # Example stride lengths for right and left legs
    print("in ..........computeflatfoot()..........")
    with connection.cursor() as cursor:
        cursor.execute("select s3,s4 from sensordata where soletype ='R' and sessionid=%s order by capturedtime asc",[ssnid])
        rffval =cursor.fetchall()

        print("rflatfoot fetched...............", len(rffval))
        rc = cursor.rowcount
    ddr = pd.DataFrame(rffval)
    ra1 = ddr[0]
    ra2 = ddr[1]
    print("................right", rc)
    with connection.cursor() as cursor:
        cursor.execute("select s3,s4 from sensordata where soletype ='L' and sessionid=%s order by capturedtime asc",[ssnid])
        lffval = cursor.fetchall()
        print("lflatfoot fetched...............", len(lffval))
        lc = cursor.rowcount
    ddl = pd.DataFrame(lffval)
    la1 = ddl[0]
    la2 = ddl[1]
    print(".................left:", lc)
    if th == 4 :            # for 4 sensor , flatfoot is computed using s3 values
        meanrff = np.mean(ra1)
        meanlff = np.mean(la1)
    else:                   # for 5 sensor , flatfoot is computed using s4 values
        meanrff = np.mean(ra2)
        meanlff = np.mean(la2)
    print("flat foot values computed :  for R =",meanrff, " for L= ",meanlff)
    with connection.cursor() as cursor:
        cursor.execute("update reportdatastore set rflatfoot=%s, lflatfoot=%s where sessionid=%s",[meanrff,meanlff,ssnid])
        rc = cursor.rowcount
    if rc > 0:
        return 1
    else:
        return 0



@api_view(["GET"])
def genreport(request):
    ssnid = request.data["ssnid"]
    nos = request.data["totalsensor"]
    th  = request.data["th"] # 4 or 5 sensors
    print(ssnid,nos)
    with connection.cursor() as cursor:
        cursor.execute("select count(*) from reportdatastore where sessionid=%s",[ssnid])
        rc = cursor.fetchone()
    print(rc[0])

    if rc[0] == 0:
        toeheelstat = computethminmaxavg(ssnid, nos, th)
        print("===========================> minmaxavg of presuures ................................... completed")
        copstat = computecop(ssnid, nos, th)
        print("===========================> meancops ................................ completed")
        stepcntstat = computestepcnt(ssnid)
        print("===========================> stepcnts ..................................... completed")
        computestridesmod(ssnid, nos, th)      #th needed for toe and heel
        print("===========================> Each Strides detected with dist,velocity ,start and end times generation ............................................ completed")

        stridevarsymstat= computestridevarasym(ssnid)
        print("===========================> stride distance variablility and asymmetry ........................................ completed")
        stridevelostat = computestridevelovarasym(ssnid)
        print("===========================> stride velocity  variablility and asymmetry  ........................ completed")
        cadstat = computecadence(ssnid)
        print("===========================> cadence ........... completed")
        swingstancestat = computeswingstancevrasym(ssnid,nos,th) # th needed for toe and heel
        print("===========================> Swing Stance, its variablility and asymmetry  .................................... completed")
        flatfootstat = computeflatfoot(ssnid,th)  # th needed for toe and heel
        print("===========================> Flat foot  ..................................... completed")

        if toeheelstat ==1 and copstat ==1 and stepcntstat ==1 and cadstat ==1 and stridevarsymstat == 1 and swingstancestat ==1 and stridevelostat ==1 and flatfootstat==1:
            return JsonResponse({"status": "success"})
        else :
            return JsonResponse({"status": "error"})
    else:  # read report values
        print("report is table..................")
        farr1 = []
        farr2 = []
        farr3 = []
        farr4 = []
        farr5 = []
        farr6 = []
        farr7 = []
        ff = []
        with connection.cursor() as cursor:
            cursor.execute(reportminmaxavgPresQuery, [ssnid])
            val = cursor.fetchone()
        farr1.append(
            {"rmaxtoe": val[0], "rmaxheel": val[1], "lmaxtoe": val[2], "lmaxheel": val[3], "rmintoe": val[4], "lmintoe": val[5],
             "lminheel": val[6], "ravgtoe": val[7], "ravgheel": val[8], "lavgtoe": val[9], "lavgheel": val[10]})
        print(farr1)
        with connection.cursor() as cursor:
            cursor.execute(reportcopstepsQuery, [ssnid])
            val = cursor.fetchone()
        #     rmeancopx,rmeancopy ,lmeancopx, lmeancopy, lstepcnt, rstepcnt,totalstepcnt
        farr2.append({"rmeancopx": val[0], "rmeancopy": val[1], "lmeancopx": val[2], "lmeancopy": val[3], "lstepcnt": val[4],
                      "rstepcnt": val[5], "totalstepcnt": val[6]})
        print(farr2)
        with connection.cursor() as cursor:
            cursor.execute(reportswingQuery, [ssnid])
            val = cursor.fetchone()
        # lswingtime,rswingtime ,lswingtimevar, rswingtimevar, swingasym
        farr3.append(
            {"lswingtime": val[0], "rswingtime": val[1], "lswingtimevar": val[2], "rswingtimevar": val[3], "swingasym": val[4]})
        print(farr3)
        with connection.cursor() as cursor:
            cursor.execute(reportstanceQuery, [ssnid])
            val = cursor.fetchone()
        # lstancetime,rstancetime ,lstancetimevar, rstancetimevar, stanceasym
        farr4.append({"lstancetime": val[0], "rstancetime": val[1], "lstancetimevar": val[2], "rstancetimevar": val[3],
                      "stanceasym": val[4]})
        print(farr4)
        with connection.cursor() as cursor:
            cursor.execute(reportstrideQuery, [ssnid])
            val = cursor.fetchone()
        # rslvar,lslvar ,slasym,rsvvar,lsvvar,svasym
        farr5.append(
            {"rslvar": val[0], "lslvar": val[1], "slasym": val[2], "rsvvar": val[3], "lsvvar": val[4], "svasym": val[5]})
        print(farr5)
        with connection.cursor() as cursor:
            cursor.execute(reportcadQuery, [ssnid])
            val = cursor.fetchone()
        # lcadence, ltime, rcadence, rtime
        farr6.append({"lcadence": val[0], "ltime": val[1], "rcadence": val[2], "rtime": val[3]})
        print(farr6)
        with connection.cursor() as cursor:
            cursor.execute(reportstridelenvelQuery, [ssnid])
            val = cursor.fetchone()
        if val:
            #     distance, velocity
            farr7.append({"distance": val[0], "velocity": val[1]})
            print(farr7)
        else:
            print("[]")

        ff.append(
            {"pressure": farr1, "copandstepcount": farr2, "swing": farr3, "stance": farr4, "stridevar": farr5, "cadence": farr6,
             "stridedisvelo": farr7})
        return Response(ff)
