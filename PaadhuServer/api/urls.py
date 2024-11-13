from django.urls import path
from . import views
urlpatterns = [
   # path('', views.ApiOverview, name='home'),
    path('login/', views.login, name='login'),
    ####################################################### admin panel /user related##################################
    path('createuser/',views.newuser, name='createuser'),
    path('adminuserdelete/',views.admindeleteuser, name='admindeleteuser'),
    path('userundelete/',views.unblockuser, name='userundelete'),
    path('changepswd/',views.changepaswd, name='changepswd'),
    path('Addnewhwdev/', views.Addnewhardwaredev, name="Addnewhwdev"),
    path('adminlist/', views.alladmin, name="adminlist"),
    path('createadmin/', views.newadmin, name="createadmin"),
    path('getadmindevicedetails/', views.getadmindevdetails, name='getdevicedetails'),
    path('admindeletehardware/',views.deletehardwaremac,name='deletehardwaremac'),
    path('adminpairdevicedetails/', views.admingetpairdetails, name='admingetpairdetails'),
    path('adminmaclist/', views.macadminlist, name='macadminlist'),
    path('adminuserlist/', views.adminlistuser, name="adminlistuser"),
    path('adminpairreg/', views.adminregnewpair, name="adminregnewpair"),
    path('adminpairblock/', views.adminblockpair, name="adminblockpair"),
    path('adminedits/', views.adminedit, name="adminedit"),
    path('adminuserupdate/', views.adminupdateuser, name="adminupdateuser"),

    path('checksensordata/', views.checksensorvalues, name='checksensordata'),
    path('deviceinfobyid/', views.infoondevicesbyid, name='deviceinfobyid'),

    ############################################## end of admin panel / user related##################################
    ####################################################### hardware/device relaed##################################
    path('productcheck/', views.checksproduct, name='productcheck'),
    path('productdetails/', views.getproddetails, name='productdetails'),
    path('finalnewdeviceregister/', views.deviceregister, name='finalnewdeviceregister'),
    path('checkregistereddevice/', views.checkifregistered, name='checkregistereddevice'),
    path('getdevicedetails/',views.getdevdetails,name='getdevicedetails'),
    path('deletedevice/',views.devdelete,name='deletedevice'),
    path('newplayer/', views.playeradd, name='newplayer'),
    path('checkplayerstatus/', views.checkplayer, name='checkplayerstatus'),
    path('checksessionstatus/', views.checksession, name='checksessionstatus'),
    path('playerdetails/', views.getplayerdetails, name='playerdetails'),
    ############################################## end of hardware/device related##################################
    ####################################################### Analytics related##################################
    path('peakvalue/', views.peakvalues, name='peakvalue'),
    path('meanvalue/', views.meanvalues, name='meanvalue'),
    path('lcopvalue/', views.lcopvalues, name='lcopvalue'),
    path('rcopvalue/', views.rcopvalues, name='rcopvalue'),
    path('footvalue/', views.footvalues, name='footvalue'),
    path('updatevideos/', views.updatevideo, name='updatevideos'),
    path('getvideoids/', views.getvideoid, name='getvideoids'),
    path('sessiondetails/', views.getsessiondetails, name='sessiondetails'),
    path('playerdetailsid/', views.getplayerdetailsid, name='playerdetailsid'),
    path('sessiondetailsview/', views.getsession, name='sessiondetailsview'),
    path('deleteplayer/', views.playerdelete, name='deleteplayer'),
    path('deletehistory/', views.historydelete, name='deletehistory'),
    path('playertrainingstatus/', views.trainingplayerstatus, name='playertrainingstatus'),
    path('playertraininghistory/', views.trainingplayerhistory, name='playertraininghistory'),
    path('devicelist/',views.listofdevices, name='devicelist'),
    path('userlist/',views.listofplayers, name='userlist'),
    path('deviceinfo/',views.infoondevices, name='deviceinfo'),
    path('newactivityregistration/',views.startsession, name='newactivityregistration'),
    path('sensordatainsert/',views.storesensordat, name='sensordatainsert'),
    path('readsensordata/',views.getsensorvalues, name='readsensordata'),
    path('endsession/',views.sessionend, name='endsession'),
    path('preprocessvisual/',views.datavisualprocess,name='preprocessvisual'),
    path('newsubactivity/', views.startsubact, name='newsubactivity'),
    path('videoinserts/', views.videoinsert, name='videoinserts'),
    path('subsessiondeletes/', views.subsessiondelete, name='subsessiondeletes'),
    path('endsubactivity/', views.endsubact, name='endsubactivity'),
    path('getsubactdata/', views.getsubactivitydata, name='getsubactdata'),
    path('getmaxvalue/', views.getmaxvaluestatus, name='getmaxvalue'),
    path('getmaxtime/', views.getmaxtimestatus, name='getmaxtime'),
    path('datafromvidsmean/', views.datafromvidmeans, name='datafromvidsmean'),
    path('datafromvidspeak/', views.datafromvidpeaks, name='datafromvidspeak'),
    path('datafromvidswalk/', views.datafromvidwalks, name='datafromvidswalk'),
    path('datafromvidfoot/', views.datafromvidfoots, name='datafromvidfoot'),
    path('stride/', views.strides, name='stride'),
    path('footheal/', views.datafromvidfoottrans, name='footheal'),
    path('finalmeans/', views.finalmean, name='finalmeans'),
    # path('finalpeaks/', views.finalpeak, name='finalpeaks'),
    path('finalpeaks/', views.finalpkmntoeheel, name='finalpeaks'),
    path('finalimus/', views.finalimumetrics, name='finalimu'),
    path('finalhealtoe/', views.finalhealtoes, name='finalhealtoe'),
    #path('finalcentreofpressures/', views.finalcentreofpressure, name='finalcentreofpressures'),
    #path('finalcentreofpressures/', views.finalcentreofpressure, name='finalcentreofpressures'),
    path('finalcops/', views.finalcentreofpressuremodifiedz1, name='finalcentreofpressures'),
    path('finalcentreofpressures/', views.finalcentreofpressuremodifiedz1, name='fin'),
    path('finalfsrmetrics/',views.finalpkmntoeheel, name="finalfsrmetrics"),
    path('finalfsrgraphs/', views.finalpkmntoeheelmod, name="finalfsrmetrics"),
    ############################################### offline metrics#################################################
    path('finalstrides/offline/', views.strideinfo, name="finalimumetrics"),
    path('finalcops/offline/', views.finalcentreofpressuremodifiedz1, name='finalcentreofpressures'),
    path('finalfsrgraphs/offline/', views.finalpkmntoeheelmodified, name='finalcentreofpressures'),
    
    ######################################################################
    path('angleMetric/', views.angleMetrics, name='angleMetric'),
    path('frames/', views.getallsecondsframes, name='frames'),
    path('framemsec/', views.geteachframemsec, name='framemesc'),
    path('getframes/', views.get25framemsec, name='framemesc'),
    path('videometa/', views.getvideometadata, name='videometa'),
    path('subactframes/', views.getsubactivityframes, name='subactframes'),
    path('subactvideoframes/', views.subactvideoandframemsecs, name='subactvideoframes'),
    path('strides1f/', views.strides1, name='strides1f'),

    path("getxycoords/",views.getsensorxycoords, name="getxycoords"),
    path("setxycoords/",views.setsensorxycoords, name="setxycoords"),
    path("setanalyticsflagss/", views.setanalyticsflags, name="setanalyticsflagss"),
    path("getanalyticsflagss/", views.getanalyticsflags, name="getanalyticsflagss"),
    path('gethealth/', views.getsensorhealth, name='gethealth'),
    path('sethealth/', views.setsensorhealth, name='sethealth'),
    path("getframemsecs/", views.getframemsec, name="getframemsecs"),
    path('videoedit/',views.videoedit, name='videoedit'),  #will delete videoid rows from videodetails table, add new rows of frame details , change videostatus to true.
    path('storesensorarray/',views.storearraysensordat, name='storesensorarray'),   # for storing array of sensor into table
    path('checkpastdata/',views.checkpastdata, name='checkpastdata'),   # check count of past data rows for given sessionid if morethan zero it returns 1 else returns 0
    path('deletepastdata/',views.deletepastdata, name='deletepastdata'),   # deletes tha past data for the given sessionid.
    path("ADC/", views.ADCcalibrate, name="ADC"),
    path('gethealth/', views.getsensorhealth, name='gethealth'),
    path('sethealth/', views.setsensorhealth, name='sethealth'),
    path('frame/', views.getframenoformsec, name='frame'),
    path('frametime/', views.frameactualtime, name='frametime'),
    path('sl21/', views.strides21, name='sl21'),
    ##################################################new strides calculation  ################################################
    path('strides11/', views.strides11, name='strides1f'),
    path('strides1222/', views.strides122, name='strides1222'),

    path('analyticsStridebyAHRS/',views.analyticsStridebyAHRS,name='analyticsStridebyAHRS'),
    path('writelog/',views.storelogreport, name='writelogfile'),

    path('imu/angle/left/',views.angleimuleft, name='angleimuleft'),
    path('imu/angle/right/',views.angleimuright, name='angleimuright'),

    path('imu/stepcount/',views.stepcount, name='stepcount'),

    #################################NEW API###############################################

    path('activesession/', views.getactivesession, name='getactivesession'),
    path('coachdetails/', views.getcoachdetails, name='coachdetails'),
    path('orggetdevicedetails/', views.orgdevdetails, name='orgdevicedetails'),
    path('orgdeviceassign/', views.orgdeviceregister, name='orgdeviceregister'),
    path('deviceinfoupdated/', views.infoondevicesupdated, name='infoondevicesupdated'),
    path('devicelistupdated/', views.updatedlistofdevices, name='updateddevicelist'),
    path('blockuser/', views.userblock, name='userblock'),
    ################################################  stride computation   ################################################################################
    # path('dummydata/', views.dummy, name='dummy'), # for offline stride computataion
    # path('onlinestridezinfo/',views.onlinestrideinfo, name='onlinestridestore'), # it reads stride no, dist and velocity from onlinestride table from db this can be used by offline and onlin to read stride info
    path('onlinestridezinfo/',views.strideinfo1121, name='onlinestrideread'),
    path('onlinestrideinfo/', views.onlinestrideinfo, name='onlinestridestore'),
    # path('onlinestride/compute/',views.onlinestridecompute, name='onlinestridestorencompute'), # itfor online stride computation
    path('onlinestride/compute/',views.onlinestridecompute1121, name='onlinestridestorencompute'), # itfor online stride computation
    #path('imu/sv/lty/', views.svleft, name='leftstrideoffline'),
    #path('imu/sv/rty/', views.svright, name='rightstrideoffline'),
    path('imu/sv/lty/', views.strideinfo1121L, name='leftstrideoffline'),
    path('imu/sv/rty/', views.strideinfo1121R, name='rightstrideoffline'),
    path('finalcop/', views.finalcentreofpressuremod, name='rightstrideoffline'),  # this api will do for both 10and 16 sensors  cop metrics.
    path('finalcopsmodified/', views.finalcentreofpressuremodifiedz1, name='finalcentreofpressures'), # NEW MODIFIED it reads coords from insole table
    path('onlinestride/computes/', views.onlinestridecompute1121, name='onlinestridestorencomputes'),
    path('finalstrides/offonline/', views.strideinfo1121, name="finalimumetrics"),
    path('swingstance/', views.swingstancemodifiedz1, name='swingstance'),
    path('cadence/', views.cadencez1, name='cadence'),
    path('report/',views.genreport, name='reportgeneration'),
]
