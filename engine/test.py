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
        port = ip[1]
        ip = ip[0]
        print(' ')
        print(' ')
        print(' ip = ', ip)
        print(' PORT =  ', port)
        print(' ')
        print(' ')
        #port = 80
        login = 'admin'
        password = 'Supervisor'
        
        
        mycam = ONVIFCamera(ip, port, login, password)
        
        # variables
        
        getStatusF = None
        GetProfilesF = True
        vSourceToken = None
        
        
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
                
            try:
                testBuffer = str(dmgmt2.GetHostname())
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetHostname', testBuffer]]
            
            try:
                testBuffer = str(dmgmt2.GetDNS())
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetDNS', testBuffer]]
            
            try:
                testBuffer = str(dmgmt2.GetDynamicDNS())
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetDynamicDNS', testBuffer]]
            
            try:
                testBuffer = str(dmgmt2.GetNetworkProtocols())
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetNetworkProtocols', testBuffer]]
            
            try:
                testBuffer = str(dmgmt2.GetNetworkInterfaces())
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetNetworkInterfaces', testBuffer]]
            
            try:
                testBuffer = str(dmgmt2.GetNTP())
            except:
                testBuffer = "Not Supported"
            dmgmtResult = dmgmtResult + [['GetNTP', testBuffer]]
                
        
        
        ####################################
        #   testing media service block    #
        #################################### 
        
        if mediaF:
            mediaResult = None
            try:
                testBuffer = media.GetVideoSources()
                testBuffer2 = str(testBuffer2)
                vSourceToken = testBuffer[0].token
            except:
                testBuffer = "Not Supported"
            dmgmtResult = [['GetVideoSources', testBuffer2]]
            
            try:
                
        
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
                
        
        ####################################
        #    testing ptz service block     #
        ####################################
        
        if ptzF:
            ptzResult = None
            GetNodesF = False
            try:
                testBuffer = str(ptz.GetNodes())
                GetNodesF = True
            except:
                testBuffer = "Not Supported"
            ptzResult = [['GetNodes', testBuffer]]
        
            if testBuffer == "Not Supported":
                testBuffer = "Not Supported Due To GetNodes() Unavailability"
            else:
                testBuffer = ptz.GetNodes()
                testBuffer2 = ptz.GetNode(testBuffer[0].token)
                if testBuffer2 == testBuffer[0]:
                    testBuffer = "Supported"
                else:
                    testBuffer = "Not Supported"
            ptzResult = ptzResult + [['GetNode', testBuffer]]
            
            try:
                testBuffer = str(ptz.GetConfigurations())
            except:
                testBuffer = "Not Supported"
            ptzResult = ptzResult + [['GetConfigurations', testBuffer]]
        
            if testBuffer == "Not Supported":
                testBuffer = "Unable to test due to unavailability of GetConfigurations() method"
            else:
                testBuffer = ptz.GetConfigurations()
                testBuffer2 = ptz.GetConfiguration(testBuffer[0].token)
                if testBuffer2 == testBuffer[0]:
                    testBuffer = "Supported"
                else:
                    testBuffer = "Not Supported"
            ptzResult = ptzResult + [['GetConfiguration', testBuffer]]
            
            if GetNodesF:
                try:
                    if GetProfilesF:
                        mediaToken = media.GetProfiles()[0].token
                        statusInit = ptz.GetStatus(mediaToken)
                        if statusInit.MoveStatus:
                            statusBefore = statusInit.MoveStatus
                            req = {'Timeout': None, 'Velocity': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': 0.1, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                            ptz.ContinuousMove(req)
                            sleep(2)
                            statusDuring1 = ptz.GetStatus(mediaToken)
                            ptz.Stop(mediaToken)
                            req.Velocity.PanTilt.x = -0.1
                            sleep(2.5)
                            ptz.ContinuousMove(req)
                            statusDuring2 = ptz.GetStatus(mediaToken)
                            ptz.Stop(mediaToken)
                            if statusBefore == statusDuring1.MoveStatus and statusBefore == statusDuring2.MoveStatus:
                                testBuffer = "MoveStatus property not functioning correctly; "
                                getStatusF = [0]
                            else:
                                testBuffer = "MoveStatus property supported and functions correctly; "
                                getStatusF = [1]
                        else:
                            testBuffer = "MoveStatus property not supported; "
                            getStatusF = [0]
                        if statusInit.Position:
                            statusBefore = statusInit.Position
                            req = {'Timeout': None, 'Velocity': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': 0.1, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                            ptz.ContinuousMove(req)
                            sleep(2)
                            statusDuring1 = ptz.GetStatus(mediaToken)
                            ptz.Stop(mediaToken)
                            req.Velocity.PanTilt.x = -0.1
                            ptz.ContinuousMove(req)
                            sleep(2.5)
                            statusDuring2 = ptz.GetStatus(mediaToken)
                            ptz.Stop(mediaToken)
                            if statusBefore == statusDuring1.Position and statusBefore == statusDuring2.Position:
                                testBuffer = testBuffer + "Position property not functioning correctly; "
                                getStatusF = getStatusF + [0]
                            else:
                                testBuffer = testBuffer + "Position property supported and functions correctly; "
                                getStatusF = getStatusF + [1]
                        else:
                            testBuffer = testBuffer + "Position property not supported; "
                            getStatusF = getStatusF + [0]
                    else:
                        testBuffer = "Unable to test due to unavailability of GetProfiles() method"
                        getStatusF = [0, 0]
                except:
                    testBuffer = "Not Supported"
                    getStatusF = [0, 0]
                ptzResult = ptzResult + [['GetStatus', testBuffer]]
            else:
                testBuffer = "Unable to test due to unavailability of GetNodes() method"
                getStatusF = [0, 0]
                ptzResult = ptzResult + [['GetStatus', testBuffer]]
                
            if getStatusF == [0, 0]:
                testBuffer = 'Unable to test due to unavailability of GetStatus() method'
                ptzResult = ptzResult + [['ContinuousMove', testBuffer]]
                ptzResult = ptzResult + [['AbsoluteMove', testBuffer]]
                ptzResult = ptzResult + [['RelativeMove', testBuffer]]
            #elif getStatusF == [0, 1]:   
        
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
            writer.writerows(spacer)
            writer.writerows(ptzResult)
        csvFile.close()    