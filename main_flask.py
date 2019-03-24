from flask import Flask, render_template, request, send_file, jsonify, Response
import os
import time
import calendar
import csv
import ast
from multiprocessing import Process
import sys
from onvif import ONVIFCamera
import zeep
from WSDiscovery import WSDiscovery
from engine import test
from ast import literal_eval
from datetime import datetime
import importlib

class Config(object):      
    def __init__(self, IP, on = False):   
        self.IP = IP
        self.dct =  {
            'IP': self.IP,\
            'on': on,\
        }
               
    def write_to_file(self):
        cfgPath = os.getcwd() + '/engine/utils/config.py'
        f = open(cfgPath, 'w')
        f.write(str(self.dct))
        f.close()
        print('Write to file!')
        
    def get_dct(self):
        return self.dct
    
def tracking_on(id):
    # starts testing
    import settings
    importlib.reload(settings)
    from settings import ids, cameras
    intd = int(id)
    camera = cameras[intd][0] + ':' + settings.cameras[intd][1]
    conf.dct['IP'] = camera
    conf.dct['on'] = True
    conf.write_to_file()
    testClass = test.Tester()
    testClass.main()
    return 'OK!  def tracking_on'

def tracking_off(id):
    try:
        import settings
        conf.dct['IP'] = str(camera)
        conf.dct['on'] = False
        conf.write_to_file()
    except:
        return 'unable to kill - no proccess'
    return 'OK!  def tracking_off'

def quicksummary(id):
    id = int(id)
    info = []
    import settings
    importlib.reload(settings)
    from settings import ids, cameras
    fname = str(cameras[id][0]) + '.csv'
    if os.path.isfile(os.getcwd() + '/engine/reports/' + fname):
        with open(os.getcwd() + '/engine/reports/' + fname) as report:
            reader = csv.reader(report)
            sum = [row for idx, row in enumerate(reader) if idx in range(1,11)]
        info = info + [sum]
    else:
        info = info + [[None]]
    return info

def crDict():
    global conf
    conf = Config(IP = None)
    print('config dict created')
    

def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


def discover():
    # discovery method
    try:
        cameras = []
        ports = []
        count = -1
        id = []
        wsd = WSDiscovery()
        wsd.start()
        ret = wsd.searchServices()
        print('discovered ', len(ret), ' services!')
        for service in ret:
            if 'onvif' in service.getXAddrs()[0]:
                ip = service.getXAddrs()[0]
                #print(ip)
                ip = ip.split('/')
                buf = ip[2].split(':')
                ip = buf[0]
                if len(buf)>1:
                    port = buf[1]
                else:
                    port = '80'
                cameras = cameras + [[ip, port]]
                #print(cameras)
        cameras.sort()
        for each in cameras:
            count = count + 1
            id = id + [count]
        print("cameras: ", cameras)
        print("ids: ", id)
        set = open(os.getcwd() + '/settings.py', 'w')
        set.write('cameras = ' + repr(cameras) + '\n')
        set.write('ids = ' + repr(id))
        set.close()
        wsd.stop()
    except:
        return 'failed to discover services'
    return 'succ'

app = Flask(__name__)
@app.before_first_request
def startup():
    global t
    t = None

@app.route('/')
def homepage():
    info = []
    crDict()
    if calendar.timegm(time.gmtime()) - os.path.getmtime(os.getcwd() + '/settings.py') >= 600:
        discover()
    import settings
    importlib.reload(settings)
    from settings import ids, cameras
    for idd in ids:
        fname = str(settings.cameras[idd][0]) + '.csv'
        print(fname)
        if os.path.isfile(os.getcwd() + '/engine/reports/' + fname):
            with open(os.getcwd() + '/engine/reports/' + fname) as report:
                reader = csv.reader(report)
                sum = [row for idx, row in enumerate(reader) if idx in range(1,11)]
            info = info + [sum]
        else:
            info = info + [[None]]
    return render_template('index.html', ids = ids, cameras = cameras, N = len(cameras), summary = info)

@app.route('/discover')
def refresh():
    discover()
    return jsonify(dict(status='finished'))

@app.route('/getsummary')
def getsummary():
    infor = ''
    info = quicksummary(request.args['id'])
    if info[0][6][1] == 'True':
        infor = 'Supported'
    else:
        infor = 'Not Supported'
    html = "<table class='table table-bordered'><tr><td>Continuous Move</td><td>{}</td></tr><tr><td>Absolute Move</td><td>{}</td></tr><tr><td>Video Encoding</td><td>{}</td></tr><tr><td>Video Resolutions</td><td><pre>{}</pre></td></tr><tr><td>Audio Encoding</td><td>{}</td></tr><tr><td>Relay Support</td><td>{}</td></tr></table>".format(info[0][1][1], info[0][2][1], info[0][3][1], info[0][4][1], info[0][5][1], infor)
    return jsonify(dict(status=html))

@app.route('/set_on')
def set_on():
    global t
    t = Process(target=tracking_on, args=(request.args['id'], ))
    t.start()
    #time.sleep(0.5)
    return jsonify(dict(status="finished"))
    
@app.route('/set_off')
def set_off():
    try:
        file = open(os.getcwd() + '/engine/status.log', 'w')
        file.write('cancelled')
        file.close()
        t.terminate()
        t.join()
        print('terminated sucessfully')
    except:
        print('error terminating process')
    return jsonify(dict(status="finished"))
    
@app.route('/status')
def getstatus():
    statusR = None
    status2 = None
    file = open(os.getcwd() + '/engine/status.log', 'r')
    statusR = file.read()
    file2 = open(os.getcwd() + '/engine/status2.log', 'r')
    status2 = file2.read()
    return jsonify(dict(status=statusR, status2=status2))

@app.route('/clearreports')
def delreports():
    folder = os.getcwd() + '/engine/reports'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except:
            print("couldn't delete file")
    return jsonify(dict(status='finished'))

@app.route('/viewfull/<id>')
def view_full(id):
    import settings
    importlib.reload(settings)
    from settings import ids, cameras
    idd = ast.literal_eval(id)
    fname = str(cameras[idd][0]) + '.csv'
    fname2 = '/engine/reports/' + str(cameras[idd][0]) + '.csv'
    fpath = os.getcwd() + '/engine/reports/' + str(cameras[idd][0]) + '.csv'
    with open(fpath) as csv_file:
        data = list(csv.reader(csv_file))
        for idx, item in enumerate(data):
            if '\n' in item[1]:
                data[idx][1] = data[idx][1].replace('\n', '<br/>')
    return render_template('report.html', data=data, id=idd)
    
@app.route('/download/<id>')
def download(id):
    import settings
    importlib.reload(settings)
    from settings import ids, cameras
    idd = ast.literal_eval(id)
    fname = str(cameras[idd][0]) + '.csv'
    fname2 = '/engine/reports/' + str(cameras[idd][0]) + '.csv'
    fpath = os.getcwd() + '/engine/reports/' + str(cameras[idd][0]) + '.csv'
    return send_file(fpath, as_attachment=True)
    
@app.route('/log')
def dllog():
    fpath = os.getcwd() + '/tester.log'
    with open(fpath) as log_file:
        data = log_file.read()
        data = data.replace('\n', '<br/>')
        log_file.close()
    dateB = os.path.getmtime(os.getcwd() + '/tester.log')
    date = datetime.fromtimestamp(dateB).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('log.html', data=data, date=date)
   
if __name__ == '__main__':
    #app.run(host='127.0.0.1')
    app.run(host='192.168.11.211', debug=False)