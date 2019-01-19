from onvif import ONVIFCamera
from time import sleep
from ast import literal_eval
import math
import zeep
import os
import csv
import datetime


class Tester:

    # bandaid fix for broken zeep module
    
    # алармы нужны, птз абсолют мув, имеджинг (фокус важный момент, режим + возвращаемое значение), на аналитику забить, стриминг, профили медиа (на аудио обратить внимание, поддержка аас), нетворк (дхцп и все такое, но возможность менять не проверять)

    def zeep_pythonvalue(self, xmlvalue):
        return xmlvalue

    def main(self):
        
        
        # reading config
        
        path = os.getcwd() + '/engine/utils/config.py'
        try:
            d = open(path, 'r')
            print('opening config successful')
        except IOError:
            print('error while opening config, loading default config')
            d = open(os.getcwd() + '/engine/utils/defaultConfig.py', 'r')
        dconfig = d.read()
        config = literal_eval(dconfig)
        
        # dont touch this
        
        zeep.xsd.simple.AnySimpleType.pythonvalue = self.zeep_pythonvalue
        
        # getting ip
        
        ip = config.get('IP')
        ip = ip.split(':')
        ip = ip[0]
        port = 80
        login = 'admin'
        password = 'Supervisor'
        
        
        mycam = ONVIFCamera(ip, port, login, password)
        
        # trying out different services
        
        try:
            media = mycam.create_media_service()
            mediaF = True
        except:
            mediaF = False
        try:
            dmgmt = mycam.create_devicemgmt_service()
            dmgmtF = True
        except:
            dmgmtF = False
        try:
            dio = mycam.create_deviceio_service()
            dioF = True
        except:
            dioF = False
        try:
            events = mycam.create_events_service()
            eventsF = True
        except:
            eventsF = False
        try:
            analyt = mycam.create_analytics_service()
            analytF = True
        except:
            analytF = False
        try:
            ptz = mycam.create_ptz_service()
            ptzF = True
        except:
            ptzF = False
        
        ####################################
        # testing deviceMGMT service block #
        ####################################
        
        if dmgmtF:
            dmgmtResult = None
            try:
                testBuffer = str(dmgmt.GetDeviceInformation())
            except:
                testBuffer = "Not Supported"
            dmgmtResult = [['GetDeviceInformation', testBuffer]]
            
            try:
                testBuffer = str(dmgmt.GetSystemLog())
            except:
                testBuffer = "Not Supported Or Empty"
            dmgmtResult = [['GetSystemLog', testBuffer]]
            
            try:
                testBuffer = str(dmgmt.GetRemoteDiscoveryMode())
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetRemoteDiscoveryMode', testBuffer]]         
        
            try:
                testBuffer = str(dmgmt.GetEndpointReference())
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetEndpointReference', testBuffer]]    

            try:
                testBuffer = str(dmgmt.GetSystemDateAndTime())
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetSystemDateAndTime', testBuffer]]              

            try:
                testBuffer = str(dmgmt.GetDiscoveryMode())
                testBuffer2 = testBuffer
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetDiscoveryMode', testBuffer]]

            if testBuffer == 'Discoverable':
                dmgmt.SetDiscoveryMode('NonDiscoverable')
                testBuffer = str(dmgmt.GetDiscoveryMode())
                if testBuffer == 'NonDiscoverable':
                    dmgmtResult = dmgmtResult + [['SetDiscoveryMode', 'Supported']]
                    dmgmt.SetDiscoveryMode(testBuffer2)
            elif testBuffer == 'NonDiscoverable':
                dmgmt.SetDiscoveryMode('Discoverable')
                testBuffer = str(dmgmt.GetDiscoveryMode())
                if testBuffer == 'Discoverable':
                    dmgmtResult = dmgmtResult + [['SetDiscoveryMode', 'Supported']]
                    dmgmt.SetDiscoveryMode(testBuffer2)
            
            try:
                testBuffer = str(dmgmt.GetRemoteDiscoveryMode())
                testBuffer2 = testBuffer
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetRemoteDiscoveryMode', testBuffer]]

            if testBuffer2 == 'Discoverable':
                dmgmt.SetRemoteDiscoveryMode('NonDiscoverable')
                testBuffer = str(dmgmt.GetRemoteDiscoveryMode())
                if testBuffer == 'NonDiscoverable':
                    dmgmtResult = dmgmtResult + [['SetRemoteDiscoveryMode', 'Supported']]
                    dmgmt.SetRemoteDiscoveryMode(testBuffer2)
            elif testBuffer2 == 'NonDiscoverable':
                dmgmt.SetRemoteDiscoveryMode('Discoverable')
                testBuffer = str(dmgmt.GetRemoteDiscoveryMode())
                if testBuffer == 'Discoverable':
                    dmgmtResult = dmgmtResult + [['SetRemoteDiscoveryMode', 'Supported']]
                    dmgmt.SetRemoteDiscoveryMode(testBuffer2)
            else:
                dmgmtResult = dmgmtResult + [['SetRemoteDiscoveryMode', 'Not Supported']]
            
            try:
                testBuffer = str(dmgmt.GetUsers())
                testBuffer2 = dmgmt.GetUsers()
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetUsers', testBuffer]]
            
            if "Not Supported" not in testBuffer:
                try:
                    NewUser = dmgmt.GetUsers()[0]
                    NewUser.Username = 'O1N2V3IFTester'
                    NewUser.Password = 'Tester4444'
                    NewUser.UserLevel = 'User'
                    dmgmt.CreateUsers(NewUser)
                    testBuffer2 = dmgmt.GetUsers()[len(dmgmt.GetUsers())-1]
                    if testBuffer2.Username == 'O1N2V3IFTester':
                        testBuffer = 'Supported'
                        dmgmtResult = dmgmtResult + [['CreateUsers', testBuffer]]
                    else:
                        testBuffer = "Not Supported"
                        dmgmtResult = dmgmtResult + [['CreateUsers', testBuffer]] 
                except:
                    testBuffer = "Not Supported"
                    dmgmtResult = dmgmtResult + [['CreateUsers', testBuffer]] 
                
                if testBuffer == 'Supported':
                    try:
                        NewUser.UserLevel = 'Operator'
                        dmgmt.SetUser(NewUser)
                        testBuffer2 = dmgmt.GetUsers()[len(dmgmt.GetUsers())-1]
                        if testBuffer2.UserLevel == 'Operator':
                            testBuffer = 'Supported'
                            dmgmtResult = dmgmtResult + [['SetUser', testBuffer]]
                        else:
                            testBuffer = "Not Supported"
                            dmgmtResult = dmgmtResult + [['SetUser', testBuffer]] 
                    except:
                        testBuffer = "Not Supported"
                        dmgmtResult = dmgmtResult + [['SetUser', testBuffer]] 
                
                    try:
                        dmgmt.DeleteUsers('O1N2V3IFTester')
                        testBuffer2 = dmgmt.GetUsers()[len(dmgmt.GetUsers())-1]
                        if testBuffer2.Username != 'O1N2V3IFTester':
                            testBuffer = 'Supported'
                            dmgmtResult = dmgmtResult + [['DeleteUsers', testBuffer]]
                        else:
                            testBuffer = "Not Supported"
                            dmgmtResult = dmgmtResult + [['DeleteUsers', testBuffer]] 
                    except:
                        testBuffer = "Not Supported"
                        dmgmtResult = dmgmtResult + [['DeleteUsers', testBuffer]]
                else:
                    dmgmtResult = dmgmtResult + [['SetUser', 'Unable to test due to unavailability of CreateUsers() method']] 
                    dmgmtResult = dmgmtResult + [['DeleteUsers', 'Unable to test due to unavailability of CreateUsers() method']] 
            else:
                dmgmtResult = dmgmtResult + [['SetUser', 'Unable to test due to unavailability of GetUsers() method']] 
                dmgmtResult = dmgmtResult + [['DeleteUsers', 'Unable to test due to unavailability of GetUsers() method']] 
                
        ####################################
        #   testing events service block   #
        ####################################  
        
        if eventsF:
            eventResult = None
            try:
                testBuffer = str(events.GetServiceCapabilities())
            except:
                testBuffer = "Not Supported"
            eventResult = [['GetServiceCapabilities', testBuffer]]
            
            try:
                testBuffer = str(events.CreatePullPointSubscription())
            except:
                testBuffer = "Not Supported"
            eventResult = eventResult + [['CreatePullPointSubscription', testBuffer]]
            
            try:
                testBuffer = str(events.PullMessages())
            except AttributeError:
                testBuffer = "Not Supported - Therefore Events Module Not Supported (PullMessages Is A Mandatory Method)"
            eventResult = eventResult + [['PullMessages', testBuffer]]
            
            if "Not Supported" not in testBuffer:
                try:
                    testBuffer = str(events.GetEventProperties())
                except:
                    testBuffer = "Not Supported"
                eventResult = eventResult + [['GetEventProperties', testBuffer]]
            else:
                eventsF = False
        
        date = str(datetime.datetime.now())
        date = date.split('.')
        header = [['Device IP', ip], ['Test Performed', date[0]]]
        header2 = [['Method Tested', 'Test Result']]
        summary = [['DeviceMgmt', str(dmgmtF)], ['DeviceIO', str(dioF)], ['Events', str(eventsF)], ['Analytics', str(analytF)], ['PTZ', str(ptzF)], ['Media', str(mediaF)]]
        spacer = [['', ''], ['', '']]
        reportn = os.getcwd() + '/engine/reports/' + ip + '.csv'
        with open(reportn, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(header)
            writer.writerows(summary)
            writer.writerows(spacer)
            #writer.writerows(header2)
            writer.writerows(dmgmtResult)
            writer.writerows(spacer)
            writer.writerows(eventResult)
        csvFile.close()    