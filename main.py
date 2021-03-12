# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import json
import time
import os
import datetime

authUrl = "https://erp.ephor.online/api/1.0/Auth.php"
auditUrl = "https://erp.ephor.online/api/1.0/audit/Audit.php"
automatUrl = "https://erp.ephor.online/api/1.0/automat/Automat.php"
authAction = { "action" : "Login", "_dc": time.time() }
listAutomatAction = { "action" : "ReadAutomatDetail" }

secret = '[{ "login" : "master175", "password" : "123123" }]'

#Login and save cookies
loginResponse = requests.post(authUrl, params = authAction, data = secret)
Cookie = loginResponse.headers["Set-Cookie"].split(';')[0]

#Get and save VMC list
automatResponse = requests.get(automatUrl, params = listAutomatAction, headers={"Cookie": Cookie})
        #Save to file
with open("automatList.json", 'w') as automatListFile:
    json.dump(automatResponse.json(), automatListFile)
automats = {}
automatlist = json.loads(automatResponse.text)
for automat in automatlist["data"]:
    automats[automat["id"]] = automat["number"]


def getLastAudit(automatId):
    folder = str(automatId)
    audits = {}
    listAuditAction = {"action": "ReadAudit",
                       "filter": '[{"property":"automat_id","value":"' + str(automatId) + '"}]'}
    auditListResponse = requests.get(auditUrl,
                                     params=listAuditAction,
                                     headers={"Cookie": Cookie})
    auditList = json.loads(auditListResponse.text)
    if auditList["success"] == True:
        if auditList["total"] != 0:
            if os.path.exists(folder) == False:
                os.mkdir(folder)
                with open( str(automatId) + "/lastAudit.txt", "w" ) as lastAuditFile:
                    lastAuditFile.write( "1970-01-01 00:01:01" )

            for audit in auditList["data"]:
                audits[audit["id"]] = audit["date"]
                with open( str(automatId) + "/lastAudit.txt", "r" ) as lastAuditFile:
                    lastAuditDate = datetime.datetime.strptime(lastAuditFile.read(), "%Y-%m-%d %H:%M:%S")
                    currentAuditDate = datetime.datetime.strptime(audit["date"], "%Y-%m-%d %H:%M:%S")
                    if currentAuditDate > lastAuditDate:
                        getAuditAction = { "action": "ReadTextAudit",
                                           "filter":'[{"property":"id","value":"'+ str(audit["id"]) + '"}]'}
                        getAuditResponse = requests.get(auditUrl,
                                                        params=getAuditAction,
                                                        headers={"Cookie": Cookie})
                        with open(str(automatId) + "/audit" + str(audit["id"]) + "_" + audit["date"], "w") as auditFile:
                            auditFile.write(getAuditResponse.text)
                        with open(str(automatId) + "/lastAudit.txt", "w") as lastAuditFile:
                            lastAuditFile.write(audit["date"])
        else:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  +" - Автомат: " + str(automatId)
                  + " - статистик нет " )
    else:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              + " - Ошибка получения списка уадитов: "
              + auditList)


for automat in automats:
    getLastAudit(automat)

