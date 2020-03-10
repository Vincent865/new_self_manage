'''Common helper module'''
import os

__author__ = 'Chris'

def get_ps_result():
    ''' get process status '''
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    ps_result = []
    for pid in pids:
        try:
            ps_result.append(pid + ' ' + \
                open(os.path.join('/proc', pid, 'cmdline'), 'rb').read())
        except IOError: # proc has already terminated
            continue
    return ps_result

def process_already_running(cmdline):
    ''' check process is running! '''
    count = 0
    result = get_ps_result()
    for line in result:
        if line.find(cmdline) != -1:
            #print line
            count += 1
    #print count
    if count > 1:
        return True
    else:
        return False

def ports_to_engine(ports):
    ''' get port about DPI engine '''
    #print ports
    dpi = ""
    dpi += str(ports[0])
    ports = ports[1:]
    for port in ports:
        dpi += '-'+str(port)
    return dpi.lower()
