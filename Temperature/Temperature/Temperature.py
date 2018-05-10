import paramiko
import cryptography
import re
import pypyodbc


# TODO
#send qm start as user temperature




def shutdownvm(vmid):
    stdin, stdout, stderr = sshclient.exec_command('qm stop '+str(vmid))
    print(stderr.read())

def filter(start, end, text):
    st = re.search(start, text, re.IGNORECASE).end()+2
    if end == "Core4":
        return text[st:]
    else:
        en = re.search(end, text, re.IGNORECASE).start()-1
        return text[st:en]

#open password file
pw_file = open("pw.cfg", "r")
sshpw = pw_file.readline()
sqlpw = pw_file.readline()

#set order of VM shutdown by ID
idfirst = ['104','105','103']
idsecond = ['106','100','101','102']

#connect to Hypervisor and send ssh command
sshclient = paramiko.SSHClient()
sshclient.load_system_host_keys()
sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sshclient.connect('192.168.2.5', username='temperature', password=sshpw)
stdin, stdout, stderr = sshclient.exec_command('sensors')

#convert und filter returned data
text = stdout.read().decode("utf-8")
text = text.replace(" ", "")
text = text.replace(u"°C", "")
text = text.replace(u"(high=+105.0,crit=+105.0)", "")

st = re.search('Core0:', text, re.IGNORECASE).start()
text = text[st:]

#get temperature for each Core
Core = ["","","",""]
for x in range(0, 4):
    Core[x] = filter("Core"+str(x), "Core"+str(x+1), text)
    print(Core[x])

#create connection to SQL server
sqlconnection = pypyodbc.connect('Driver={SQL Server};Server=192.168.2.107;Database=Temperature;uid=temperature;pwd='+str(sqlpw))


#check for heat
maxheat = float(max(Core))
print(maxheat)
if maxheat > 60.0:
    print("Be careful temperature exceeds 60 Degrees")
    for x in range(0, len(idfirst)):
        shutdownvm(idfirst[x])
elif maxheat > 75.0:
    print("Be careful temperature exceeds 75 Degrees")
    for x in range(0, len(idsecond)):
        shutdownvm(idsecond[x])


sshclient.close()