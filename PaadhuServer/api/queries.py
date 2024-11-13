#report related
reportminmaxavgPresQuery = "select  rmaxtoe, rmaxheel,lmaxtoe,lmaxheel,rmintoe, rminheel,lmintoe,lminheel,ravgtoe,ravgheel,lavgtoe,lavgheel  from reportdatastore where sessionid=%s"
reportcopstepsQuery = "select rmeancopx,rmeancopy ,lmeancopx, lmeancopy, lstepcnt, rstepcnt,totalstepcnt  from reportdatastore where sessionid=%s"
reportswingQuery = "select lswingtime,rswingtime ,lswingtimevar, rswingtimevar, swingasym  from reportdatastore where sessionid=%s"
reportstanceQuery = "select lstancetime,rstancetime ,lstancetimevar, rstancetimevar, stanceasym  from reportdatastore where sessionid=%s"
reportstrideQuery = "select rslvar,lslvar ,slasym,rsvvar,lsvvar,svasym from reportdatastore where sessionid=%s"
reportcadQuery = "select lcadence,ltime ,rcadence, rtime from reportdatastore where sessionid=%s"
reportstridelenvelQuery = "select distance, velocity from onlinestride where sessionid =%s order by starttime asc"


