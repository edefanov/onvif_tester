from flask import Flask, render_template, request, send_file, jsonify
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
    # starts tracking
    import settings
    global trackingMain
    intd = int(id)
    camera = settings.cameras[intd][0] + ':' + settings.cameras[intd][1]
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
                print(ip)
                ip = ip.split('/')
                buf = ip[2].split(':')
                ip = buf[0]
                if len(buf)>1:
                    port = buf[1]
                else:
                    port = '80'
                cameras = cameras + [[ip, port]]
                print(cameras)
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
    global trackingMain
    trackingMain = None

@app.route('/')
def homepage():
    info = []
    crDict()
    if calendar.timegm(time.gmtime()) - os.path.getmtime(os.getcwd() + '/settings.py') >= 300:
        discover()
    import settings
    for idd in settings.ids:
        fname = str(settings.cameras[idd][0]) + '.csv'
        if os.path.isfile(os.getcwd() + '/engine/reports/' + fname):
            with open(os.getcwd() + '/engine/reports/' + fname) as report:
                reader = csv.reader(report)
                sum = [row for idx, row in enumerate(reader) if idx in range(1,8)]
            info = info + [sum]
        else:
            info = info + [[None]]
    return render_template('index.html', ids = settings.ids, cameras = settings.cameras, N = len(settings.cameras), summary = info)

@app.route('/discover', methods=['POST'])
def refresh():
    info = []
    crDict()
    discover()
    import settings
    for idd in settings.ids:
        fname = str(settings.cameras[idd][0]) + '.csv'
        if os.path.isfile(os.getcwd() + '/engine/reports/' + fname):
            with open(os.getcwd() + '/engine/reports/' + fname) as report:
                reader = csv.reader(report)
                sum = [row for idx, row in enumerate(reader) if idx in range(1,8)]
            info = info + [sum]
        else:
            info = info + [[None]]
    return render_template('index.html', ids = settings.ids, cameras = settings.cameras, N = len(settings.cameras), summary = info)


@app.route('/set_on')
def set_on():
    print(tracking_on(request.args['id']))
    return jsonify(dict(status='finished'))

@app.route('/set_off')
def set_off():
    print(tracking_off(request.args['id']))
    return ' '

@app.route('/viewfull/<id>')
def view_full(id):
    import settings
    idd = ast.literal_eval(id)
    fname = str(settings.cameras[idd][0]) + '.csv'
    fname2 = '/engine/reports/' + str(settings.cameras[idd][0]) + '.csv'
    fpath = os.getcwd() + '/engine/reports/' + str(settings.cameras[idd][0]) + '.csv'
    with open(fpath) as csv_file:
        data = list(csv.reader(csv_file))
    return render_template('report.html', data=data, id=idd)
    
@app.route('/download/<id>')
def download(id):
    import settings
    idd = ast.literal_eval(id)
    fname = str(settings.cameras[idd][0]) + '.csv'
    fname2 = '/engine/reports/' + str(settings.cameras[idd][0]) + '.csv'
    fpath = os.getcwd() + '/engine/reports/' + str(settings.cameras[idd][0]) + '.csv'
    return send_file(fpath, as_attachment=True)
   
if __name__ == '__main__':
    app.run(host='127.0.0.1')
    #app.run(host='192.168.11.104')