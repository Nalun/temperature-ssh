import paramiko
import cryptography
import re

#open password file
pw_file = open("pw.cfg", "r")
pw = pw_file.readline()

#set order of VM shutdown by ID
idfirst = ['104','105','103']
idsecond = ['106','100','101','102']

def shutdownvm(vmid):
    stdin, stdout, stderr = client.exec_command('qm stop '+str(vmid))
    print(stdout.read())
    print(stderr.read())

def filter( start, end, text):
    st = re.search(start, text, re.IGNORECASE).end()+2
    if end == "Core4":
        return text[st:]
    else:
        en = re.search(end, text, re.IGNORECASE).start()-1
        return text[st:en]

#connect to Hypervisor and send ssh command
client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.2.5', username='temperature', password=pw)
stdin, stdout, stderr = client.exec_command('sensors')

#convert und filter returned data
text = stdout.read().decode("utf-8")
text = text.replace(" ", "")
text = text.replace(u"(high=+105.0°C,crit=+105.0°C)", "")
text = text.replace(u"°C", "")
st = re.search('Core0:', text, re.IGNORECASE).start()
text = text[st:]

#get temperature for each Core
Core = ["","","",""]
for x in range(0, 4):
    Core[x] = filter("Core"+str(x), "Core"+str(x+1), text)
    print(Core[x])

#check for heat
maxheat = float(max(Core))
print(maxheat)

if maxheat > 40.0:
    print("Be careful temperature exceeds 60 Degrees")
    for x in range(0, len(idfirst)):
        shutdownvm(idfirst[x])
elif maxheat > 75.0:
    print("Be careful temperature exceeds 75 Degrees")
    for x in range(0, len(idsecond)):
        shutdownvm(idsecond[x])


client.close()