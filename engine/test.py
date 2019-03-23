from onvif import ONVIFCamera
from time import sleep
from ast import literal_eval
import math
import zeep
import os
import csv
import datetime
import logging
import sys


class Tester:

    # bandaid fix for broken zeep module
    
    # птз абсолют мув, имеджинг (фокус важный момент, режим + возвращаемое значение), на аналитику забить, стриминг, профили медиа (на аудио обратить внимание, поддержка аас), нетворк (дхцп и все такое, но возможность менять не проверять)

    def zeep_pythonvalue(self, xmlvalue):
        return xmlvalue

    def main(self):
        file = open(os.getcwd() + '/engine/status.log', 'w')
        file.write('starting')
        file.close()
        
        # setting up logging
        
        
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        logging.basicConfig(filename='tester.log', filemode='w', level=logging.INFO)
        
        logging.info('test log')
        
        
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
        
        # variables
        
        getStatusF = None
        getiStatusF = None
        GetProfilesF = False
        vSourceToken = None
        rToken = None
        relayF = False
        contMove = 'Not Supported'
        absMove = 'Not Supported'
        vCodecs = 'None'
        aCodecs = 'None'
        vResolutions = 'None'
        testBuffer = None
        testBuffer2 = None
        testBuffer3 = None
        connected = False
        
        
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
        
        try:
            mycam = ONVIFCamera(ip, port, login, password)
            connected = True
            file = open(os.getcwd() + '/engine/status.log', 'w')
            file.write('connected')
            file.close()
        except:
            logging.exception("couldn't connect")
            file = open(os.getcwd() + '/engine/status.log', 'w')
            file.write('retrying')
            file.close()
            sleep(5)
            try:
                mycam = ONVIFCamera(ip, port, login, password)
                file = open(os.getcwd() + '/engine/status.log', 'w')
                file.write('connected')
                file.close()
            except:
                file = open(os.getcwd() + '/engine/status.log', 'w')
                file.write('notconnected')
                file.close()
                return
            connected = False
        
        
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
        try:
            imaging = mycam.create_imaging_service()
            imagingF = True
        except:
            imagingF = False
        
        ####################################
        # testing deviceMGMT service block #
        ####################################
        
        if dmgmtF:
            logging.info(' ')
            logging.info('testing devicemgmt')
            logging.info(' ')
            dmgmtResult = None
            file = open(os.getcwd() + '/engine/status.log', 'w')
            file.write('dmgmt')
            file.close()
            try:
                testBuffer = str(dmgmt.GetDeviceInformation())
            except:
                testBuffer = "Not Supported"
                logging.exception('getdeviceinformation')
            dmgmtResult = [['GetDeviceInformation', testBuffer]]
            
            sleep(0.5)
            
            # try:
                # testBuffer = str(dmgmt.GetDeviceCapabilities())
            # except:
                # testBuffer = "Not Supported"
                # logging.exception('getdevicecapabilities')
            # dmgmtResult = dmgmtResult + [['GetDeviceCapabilities', testBuffer]]
            
            # sleep(0.5)
            
            try:
                testBuffer = str(dmgmt.GetRemoteDiscoveryMode())
            except:
                testBuffer = "Not Supported"
                logging.exception('getremotediscoverymode')
            dmgmtResult = dmgmtResult + [['GetRemoteDiscoveryMode', testBuffer]]         
            
            sleep(0.5)
            
            try:
                testBuffer = str(dmgmt.GetEndpointReference())
            except:
                testBuffer = "Not Supported"
                logging.exception('getendpointreference')
            dmgmtResult = dmgmtResult + [['GetEndpointReference', testBuffer]]    
            
            sleep(0.5)
            
            try:
                testBuffer = str(dmgmt.GetSystemDateAndTime())
            except:
                testBuffer = "Not Supported"
                logging.exception('getsystemdateandtime')
            dmgmtResult = dmgmtResult + [['GetSystemDateAndTime', testBuffer]]              
            
            sleep(0.5)
            
            try:
                testBuffer = str(dmgmt.GetDiscoveryMode())
                testBuffer2 = testBuffer
            except:
                testBuffer = "Not Supported"
                logging.exception('getdiscoverymode')
            dmgmtResult = dmgmtResult + [['GetDiscoveryMode', testBuffer]]
            
            sleep(0.5)
            
            if testBuffer == 'Discoverable':
                try:
                    dmgmt.SetDiscoveryMode('NonDiscoverable')
                    testBuffer = str(dmgmt.GetDiscoveryMode())
                    if testBuffer == 'NonDiscoverable':
                        testBuffer3 = 'Supported'
                        dmgmt.SetDiscoveryMode(testBuffer2)
                except:
                    testBuffer3 = 'Not Supported'
                    logging.exception('setdiscoverymode')
                dmgmtResult = dmgmtResult + [['SetDiscoveryMode', testBuffer3]]
            elif testBuffer == 'NonDiscoverable':
                try:
                    dmgmt.SetDiscoveryMode('Discoverable')
                    testBuffer = str(dmgmt.GetDiscoveryMode())
                    if testBuffer == 'Discoverable':
                        testBuffer3 = 'Supported'
                        dmgmt.SetDiscoveryMode(testBuffer2)
                except:
                    testBuffer3 = 'Not Supported'
                    logging.exception('setdiscoverymode')
                dmgmtResult = dmgmtResult + [['SetDiscoveryMode', testBuffer3]]
            
            sleep(0.5)
            
            try:
                testBuffer = str(dmgmt.GetRemoteDiscoveryMode())
                testBuffer2 = testBuffer
            except:
                testBuffer = "Not Supported"
                logging.exception(' ')
            dmgmtResult = dmgmtResult + [['GetRemoteDiscoveryMode', testBuffer]]

            if testBuffer2 == 'Discoverable':
                try:
                    dmgmt.SetRemoteDiscoveryMode('NonDiscoverable')
                    testBuffer = str(dmgmt.GetRemoteDiscoveryMode())
                    if testBuffer == 'NonDiscoverable':
                        dmgmtResult = dmgmtResult + [['SetRemoteDiscoveryMode', 'Supported']]
                        dmgmt.SetRemoteDiscoveryMode(testBuffer2)
                except:
                    dmgmtResult = dmgmtResult + [['SetRemoteDiscoveryMode', 'Not Supported']]
                    logging.exception(' ')
            elif testBuffer2 == 'NonDiscoverable':
                try:
                    dmgmt.SetRemoteDiscoveryMode('Discoverable')
                    testBuffer = str(dmgmt.GetRemoteDiscoveryMode())
                    if testBuffer == 'Discoverable':
                        dmgmtResult = dmgmtResult + [['SetRemoteDiscoveryMode', 'Supported']]
                        dmgmt.SetRemoteDiscoveryMode(testBuffer2)
                except:
                    dmgmtResult = dmgmtResult + [['SetRemoteDiscoveryMode', 'Not Supported']]
                    logging.exception(' ')
            else:
                dmgmtResult = dmgmtResult + [['SetRemoteDiscoveryMode', 'Not Supported']]
            
            try:
                dmgmt.DeleteUsers('O1N2V3IFTester')
            except:
                logging.info('no onviftester')
            
            sleep(0.5)
            try:
                dmgmt = mycam.create_devicemgmt_service()
            except:
                logging.exception(' ')
            
            try:
                testBuffer2 = dmgmt.GetUsers()
                try:
                    testBuffer = str(testBuffer2)
                except:
                    logging.exception('could not convert get users to string!')
                    testBuffer = 'Supported'
            except zeep.exceptions.Fault:
                testBuffer = "Supported"
                logging.exception('get users2')
            except:
                testBuffer = "Not Supported"
                logging.exception('get users')
            dmgmtResult = dmgmtResult + [['GetUsers', testBuffer]]
            
            sleep(1)
            
            '''testBuffer2 = dmgmt.GetUsers()
            NewUser = testBuffer2[0]
            NewUser.Username = 'O1N2V3IFTester'
            NewUser.Password = 'Tester4444'
            NewUser.UserLevel = 'User'
            dmgmt.CreateUsers(NewUser)
            sleep(1)
            testBuffer2 = dmgmt.GetUsers()[len(dmgmt.GetUsers())-1]
            print('new userino test    ', str(testBuffer2))'''
            
            if "Not Supported" not in testBuffer:
                try:
                
                    #testBuffer2 = dmgmt.GetUsers()
                    #NewUser = testBuffer2[0]
                    #NewUser.Username = 'O1N2V3IFTester'
                    #NewUser.Password = 'Tester4444'
                    #NewUser.UserLevel = 'User'
                    NewUser = {'Username': 'O1N2V3IFTester', 'Password':'Tester4444', 'UserLevel': 'User'}
                    print(NewUser)
                    dmgmt.CreateUsers(NewUser)
                    sleep(2)
                    testBuffer2 = dmgmt.GetUsers()[len(dmgmt.GetUsers())-1]
                    print(testBuffer2)
                    if testBuffer2.Username == 'O1N2V3IFTester':
                        testBuffer = 'Supported'
                        dmgmtResult = dmgmtResult + [['CreateUsers', testBuffer]]
                    else:
                        testBuffer = "Not Supported"
                        dmgmtResult = dmgmtResult + [['CreateUsers', testBuffer]] 
                except zeep.exceptions.Fault:
                    testBuffer = "Supported"
                except:
                    testBuffer = "Not Supported"
                    logging.exception('create user')
                    dmgmtResult = dmgmtResult + [['CreateUsers', testBuffer]] 
                
                sleep(1)
                
                if testBuffer == 'Supported':
                    try:
                        NewUser['UserLevel'] = 'Operator'
                        dmgmt.SetUser(NewUser)
                        sleep(2)
                        testBuffer2 = dmgmt.GetUsers()[len(dmgmt.GetUsers())-1]
                        if testBuffer2.UserLevel == 'Operator':
                            testBuffer = 'Supported'
                            dmgmtResult = dmgmtResult + [['SetUser', testBuffer]]
                        else:
                            testBuffer = "Not Supported"
                            dmgmtResult = dmgmtResult + [['SetUser', testBuffer]]
                    except zeep.exceptions.Fault:
                        testBuffer = "Supported"
                        logging.exception(' ')
                    except:
                        testBuffer = "Not Supported"
                        logging.exception('set user')
                        dmgmtResult = dmgmtResult + [['SetUser', testBuffer]] 
                    
                    sleep(1)
                    
                    try:
                        dmgmt.DeleteUsers('O1N2V3IFTester')
                        sleep(2)
                        testBuffer2 = dmgmt.GetUsers()[len(dmgmt.GetUsers())-1]
                        if testBuffer2.Username != 'O1N2V3IFTester':
                            testBuffer = 'Supported'
                            dmgmtResult = dmgmtResult + [['DeleteUsers', testBuffer]]
                        else:
                            testBuffer = "Not Supported"
                            dmgmtResult = dmgmtResult + [['DeleteUsers', testBuffer]] 
                    except zeep.exceptions.Fault:
                        testBuffer = "Supported"
                        logging.exception(' ')
                    except:
                        testBuffer = "Not Supported"
                        logging.exception('delete users')
                        dmgmtResult = dmgmtResult + [['DeleteUsers', testBuffer]]
                else:
                    dmgmtResult = dmgmtResult + [['SetUser', 'Unable to test due to unavailability of CreateUsers() method']] 
                    dmgmtResult = dmgmtResult + [['DeleteUsers', 'Unable to test due to unavailability of CreateUsers() method']] 
            else:
                dmgmtResult = dmgmtResult + [['SetUser', 'Unable to test due to unavailability of GetUsers() method']] 
                dmgmtResult = dmgmtResult + [['DeleteUsers', 'Unable to test due to unavailability of GetUsers() method']] 
            
            sleep(0.5)
            
            try:
                testBuffer2 = dmgmt.GetHostname()
                testBuffer = str(testBuffer2)
            except:
                testBuffer = "Not Supported"
                logging.exception('gethostname')
            dmgmtResult = dmgmtResult + [['GetHostname', testBuffer]]
            
            sleep(0.5)
            
            try:
                testBuffer = str(dmgmt.GetDNS())
            except:
                testBuffer = "Not Supported"
                logging.exception(' ')
            dmgmtResult = dmgmtResult + [['GetDNS', testBuffer]]
            
            try:
                testBuffer = str(dmgmt.GetDynamicDNS())
            except:
                testBuffer = "Not Supported"
                logging.exception(' ')
            dmgmtResult = dmgmtResult + [['GetDynamicDNS', testBuffer]]
            
            try:
                testBuffer = str(dmgmt.GetNetworkProtocols())
            except:
                testBuffer = "Not Supported"
                logging.exception(' ')
            dmgmtResult = dmgmtResult + [['GetNetworkProtocols', testBuffer]]
            
            try:
                testBuffer = str(dmgmt.GetNetworkInterfaces())
            except:
                testBuffer = "Not Supported"
                logging.exception(' ')
            dmgmtResult = dmgmtResult + [['GetNetworkInterfaces', testBuffer]]
            
            try:
                testBuffer = str(dmgmt.GetNTP())
            except:
                testBuffer = "Not Supported"
                logging.exception(' ')
            dmgmtResult = dmgmtResult + [['GetNTP', testBuffer]]
            
            sleep(0.5)
            
            try:
                testBuffer = dmgmt.GetRelayOutputs()
                testBuffer2 = str(testBuffer)
                if len(testBuffer)>0:
                    relayF = True
            except:
                testBuffer2 = "Not Supported"
                logging.exception('get relay outputs')
            dmgmtResult = dmgmtResult + [['GetRelayOutputs', testBuffer2]]
            
            if relayF:
                try:
                    rToken = dmgmt.GetRelayOutputs()[0].token
                    rState = {'RelayOutputToken': rToken, 'LogicalState': 'active'}
                    testBuffer = dmgmt.SetRelayOutputState(rState)
                    testBuffer = "Supported"
                except:
                    testBuffer = "Not Supported"
                    logging.exception('set relay output state')
                dmgmtResult = dmgmtResult + [['SetRelayOutputState', testBuffer]]
                
                try:
                    rToken = dmgmt.GetRelayOutputs()[0].token
                    rIS = dmgmt.GetRelayOutputs()[0].Properties.IdleState
                    if rIS == 'closed':
                        rSettings = {'RelayOutputToken': rToken, 'Properties': {'Mode': 'Bistable', 'DelayTime': dmgmt.GetRelayOutputs()[0].Properties.DelayTime, 'IdleState': 'open'}}
                        dmgmt.SetRelayOutputSettings(rSettings)
                        sleep(0.5)
                        if dmgmt.GetRelayOutputs()[0].Properties.IdleState == 'open':
                            testBuffer = "Supported"
                        else:
                            testBuffer = "Not Supported"
                    elif rIS == 'open':
                        rSettings = {'RelayOutputToken': rToken, 'Properties': {'Mode': 'Bistable', 'DelayTime': dmgmt.GetRelayOutputs()[0].Properties.DelayTime, 'IdleState': 'closed'}}
                        dmgmt.SetRelayOutputSettings(rSettings)
                        sleep(0.5)
                        if dmgmt.GetRelayOutputs()[0].Properties.IdleState == 'closed':
                            testBuffer = "Supported"
                        else:
                            testBuffer = "Not Supported"
                except:
                    testBuffer = "Not Supported"
                    logging.exception('set relay output settings')
                dmgmtResult = dmgmtResult + [['SetRelayOutputSettings', testBuffer]]
                
            sleep(2)
            
        ####################################
        #   testing media service block    #
        #################################### 
        
        if mediaF:
            logging.info(' ')
            logging.info('testing media')
            logging.info(' ')
            mediaResult = None
            file = open(os.getcwd() + '/engine/status.log', 'w')
            file.write('media')
            file.close()
            try:
                testBuffer = media.GetVideoSources()
                testBuffer2 = str(testBuffer)
                vSourceToken = testBuffer[0].token
            except:
                testBuffer2 = "Not Supported"
                logging.exception(' ')
            mediaResult = [['GetVideoSources', testBuffer2]]
            
            try:
                testBuffer = media.GetAudioSources()
                testBuffer2 = str(testBuffer)
            except:
                testBuffer2 = "Not Supported"
                logging.exception(' ')
            mediaResult = mediaResult + [['GetAudioSources', testBuffer2]]
            
            try:
                testBuffer = media.GetAudioEncoderConfigurationOptions()
                
                # compiling a list of available codecs for summary
                
                aCodecs = ''
                try:
                    for x in testBuffer.Options:
                        if aCodecs == '':
                            aCodecs = str(x.Encoding)
                        else:
                            aCodecs = aCodecs + ', ' + str(x.Encoding)
                except:
                    logging.exception('couldnt find any audio codecs')
                if not aCodecs:
                    aCodecs = 'None'
                
                testBuffer2 = str(testBuffer)
            except:
                testBuffer2 = "Not Supported"
                logging.exception('get audio encoder options')
            mediaResult = mediaResult + [['GetAudioEncoderConfigurationOptions', testBuffer2]]
            
            try:
                testBuffer = media.GetVideoEncoderConfigurationOptions()
                
                # compiling a list of available codecs for summary
                
                try:
                    if len(testBuffer.MPEG4):
                        vCodecs = 'MPEG4'
                except:
                    vCodecs = ''
                try:
                    if len(testBuffer.H264):
                        if vCodecs:
                            vCodecs = vCodecs + ', H264'
                        else:
                            vCodecs = 'H264'
                except:
                    vCodecs = vCodecs + ''
                try:
                    if len(testBuffer.JPEG):
                        if vCodecs:
                            vCodecs = vCodecs + ', JPEG'
                        else:
                            vCodecs = 'JPEG'
                except:
                    vCodecs = vCodecs + ''
                if not vCodecs:
                    vCodecs = 'None'
                
                # compiling a list of available resolutions for summary
                
                vResolutions = ''
                try:
                    for x in testBuffer.MPEG4.ResolutionsAvailable:
                        if not vResolutions:
                            vResolutions = 'MPEG4: ' + str(x.Width) + 'x' + str(x.Height)
                        else:
                            vResolutions = vResolutions + ', ' + str(x.Width) + 'x' + str(x.Height)
                except:
                    logging.exception('couldnt find resolutions for mpeg4')
                if vResolutions:
                    vResolutions = vResolutions + '\n'
                try:
                    for x in testBuffer.H264.ResolutionsAvailable:
                        if not vResolutions:
                            vResolutions = 'H264: ' + str(x.Width) + 'x' + str(x.Height)
                        else:
                            if 'H264:' in vResolutions:
                                vResolutions = vResolutions + ', ' + str(x.Width) + 'x' + str(x.Height)
                            else:
                                vResolutions = vResolutions + 'H264: ' + str(x.Width) + 'x' + str(x.Height)
                except:
                    logging.exception('couldnt find resolutions for h264')
                if vResolutions:
                    vResolutions = vResolutions + '\n'
                try:
                    for x in testBuffer.JPEG.ResolutionsAvailable:
                        if not vResolutions:
                            vResolutions = 'JPEG: ' + str(x.Width) + 'x' + str(x.Height)
                        else:
                            if 'JPEG:' in vResolutions:
                                vResolutions = vResolutions + ', ' + str(x.Width) + 'x' + str(x.Height)
                            else:
                                vResolutions = vResolutions + 'JPEG: ' + str(x.Width) + 'x' + str(x.Height)
                except:
                    logging.exception('couldnt find resolutions for jpeg')
                if not vResolutions:
                    vResolutions = 'None'
                testBuffer2 = str(testBuffer)
            except:
                testBuffer2 = "Not Supported"
                logging.exception('get video encoder options')
            mediaResult = mediaResult + [['GetVideoEncoderConfigurationOptions', testBuffer2]]
            
            try:
                profileToken = media.GetProfiles()[0].token
                testBuffer2 = media.GetProfiles()
                testBuffer2 = str(testBuffer2)
                if len(testBuffer2) > 67256:
                    testBuffer2 = (testBuffer2[:67256] + '..') if len(testBuffer2) > 67258 else testBuffer2
                GetProfilesF = True
            except:
                testBuffer2 = "Not Supported"
                logging.exception('media get profiles')
            mediaResult = mediaResult + [['GetProfiles', testBuffer2]]
            
            try:
                testBuffer2 = str(media.GetStreamUri({'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': 'UDP'}, 'ProfileToken': profileToken}))
            except:
                testBuffer2 = "Not Supported"
                logging.exception('stream uri')
            mediaResult = mediaResult + [['GetStreamUri', testBuffer2]]
            
            sleep(2)
        
        ####################################
        #   testing imaging service block  #
        ####################################
        
        if imagingF:
            logging.info(' ')
            logging.info('testing imaging')
            logging.info(' ')
            imagingResult = None
            file = open(os.getcwd() + '/engine/status.log', 'w')
            file.write('imaging')
            file.close()
            try:
                iOptions = imaging.GetOptions(vSourceToken)
                testBuffer = str(iOptions)
            except:
                logging.exception('getoptions')
                testBuffer = "Not Supported"
            imagingResult = [['GetOptions', testBuffer]]
            
            try:
                testBuffer = str(imaging.GetImagingSettings(vSourceToken))
            except:
                logging.exception('getimagingsettings')
                testBuffer = "Not Supported"
            imagingResult = imagingResult + [['GetImagingSettings', testBuffer]]
            
            if 'MANUAL' in iOptions.Focus.AutoFocusModes:
                try:
                    iset = {'VideoSourceToken': vSourceToken, 'ImagingSettings': {'Focus': {'AutoFocusMode': 'MANUAL'}}}
                    imaging.SetImagingSettings(iset)
                    if imaging.GetImagingSettings(vSourceToken).Focus.AutoFocusMode == 'MANUAL':
                        testBuffer = 'Supported'
                except:
                    testBuffer = "Not Supported"
                    logging.exception('set imaging settings')
                imagingResult = imagingResult + [['SetImagingSettings', testBuffer]]
            
            try:
                testBuffer = str(imaging.GetMoveOptions(vSourceToken))
            except:
                logging.exception('getmoveoptions')
                testBuffer = "Not Supported"
            imagingResult = imagingResult + [['GetMoveOptions', testBuffer]]
            
            try:
                testBuffer = imaging.GetStatus(vSourceToken)
                testBuffer2 = str(testBuffer)
                if testBuffer.FocusStatus20.MoveStatus == 'UNKNOWN':
                    getiStatusF = [0]
                else:
                    getiStatusF = [1]
            except:
                logging.exception('getstatus')
                testBuffer2 = "Not Supported"
            imagingResult = imagingResult + [['GetStatus', testBuffer2]]
            
            if 'MANUAL' in iOptions.Focus.AutoFocusModes:    
                try:
                    moveSet = {'VideoSourceToken': vSourceToken, 'Focus': {'Continuous': {'Speed': 1.0}}}
                    imaging.Move(moveSet)
                    sleep(1.5)
                    testBuffer = str(imaging.GetStatus(vSourceToken))
                    imaging.Stop(vSourceToken)
                except:
                    logging.exception('manual focus move')
                    testBuffer = "Couldn't get GetStatus response"
                imagingResult = imagingResult + [['GetStatus (after manually moving focus forward)', testBuffer]]
                
                try:
                    moveSet = {'VideoSourceToken': vSourceToken, 'Focus': {'Continuous': {'Speed': -1.0}}}
                    imaging.Move(moveSet)
                    sleep(1.5)
                    testBuffer = str(imaging.GetStatus(vSourceToken))
                    imaging.Stop(vSourceToken)
                except:
                    logging.exception('manual focus move')
                    testBuffer = "Couldn't get GetStatus response"
                imagingResult = imagingResult + [['GetStatus (after manually moving focus backwards)', testBuffer]]
                    
            try:
                iset = {'VideoSourceToken': vSourceToken, 'ImagingSettings': {'Focus': {'AutoFocusMode': 'AUTO'}}}
                imaging.SetImagingSettings(iset)
            except:
                logging.exception('set autofocus back')   

            sleep(2)
        
        ####################################
        #   testing events service block   #
        ####################################  
        
        if eventsF:
            logging.info(' ')
            logging.info('testing events')
            logging.info(' ')
            eventResult = None
            file = open(os.getcwd() + '/engine/status.log', 'w')
            file.write('events')
            file.close()
            try:
                testBuffer = str(events.GetServiceCapabilities())
            except:
                testBuffer = "Not Supported"
                logging.exception(' ')
            eventResult = [['GetServiceCapabilities', testBuffer]]
            
            try:
                testBuffer = str(events.CreatePullPointSubscription())
            except:
                testBuffer = "Not Supported"
                logging.exception(' ')
            eventResult = eventResult + [['CreatePullPointSubscription', testBuffer]]
            
            try:
                testBuffer = str(events.PullMessages())
            except AttributeError:
                testBuffer = "Not Supported - Therefore Events Module Not Supported (PullMessages Is A Mandatory Method)"
                logging.exception(' ')
            eventResult = eventResult + [['PullMessages', testBuffer]]
            
            if "Not Supported" not in testBuffer:
                try:
                    testBuffer = str(events.GetEventProperties())
                except:
                    testBuffer = "Not Supported"
                    logging.exception(' ')
                eventResult = eventResult + [['GetEventProperties', testBuffer]]
            else:
                eventsF = False
            
            sleep(2)
        
        ####################################
        #    testing ptz service block     #
        ####################################
        
        if ptzF:
            logging.info(' ')
            logging.info('testing ptz')
            logging.info(' ')
            ptzResult = None
            GetNodesF = False
            file = open(os.getcwd() + '/engine/status.log', 'w')
            file.write('ptz')
            file.close()
            try:
                testBuffer = str(ptz.GetNodes())
                GetNodesF = True
            except:
                testBuffer = "Not Supported"
                logging.exception('getnodes')
            ptzResult = [['GetNodes', testBuffer]]
        
            if testBuffer == "Not Supported":
                testBuffer = "Not Supported Due To GetNodes() Unavailability"
            else:
                try:
                    testBuffer = ptz.GetNodes()
                    testBuffer2 = ptz.GetNode(testBuffer[0].token)
                    if testBuffer2 == testBuffer[0]:
                        testBuffer = "Supported"
                    else:
                        testBuffer = "Not Supported"
                except:
                    testBuffer = "Not Supported"
                    logging.exception('getnode')
            ptzResult = ptzResult + [['GetNode', testBuffer]]
            
            try:
                testBuffer = str(ptz.GetConfigurations())
            except:
                testBuffer = "Not Supported"
                logging.exception('getconfigurations')
            ptzResult = ptzResult + [['GetConfigurations', testBuffer]]
        
            if testBuffer == "Not Supported":
                testBuffer = "Unable to test due to unavailability of GetConfigurations() method"
            else:
                try:
                    testBuffer = ptz.GetConfigurations()
                    testBuffer2 = ptz.GetConfiguration(testBuffer[0].token)
                    if testBuffer2 == testBuffer[0]:
                        testBuffer = "Supported"
                    else:
                        testBuffer = "Not Supported"
                except:
                    testBuffer = "Not Supported"
                    logging.exception('getconfiguration')
            ptzResult = ptzResult + [['GetConfiguration', testBuffer]]
            
            sleep(1)
            
            try:
                mediaToken = media.GetProfiles()[0].token
                statusInit = ptz.GetStatus(mediaToken)
                print(str(statusInit))
            except:
                logging.exception(' ')
            
            
            if GetNodesF:
                try:
                    if GetProfilesF:
                        mediaToken = media.GetProfiles()[0].token
                        statusInit = ptz.GetStatus(mediaToken)
                        if statusInit.MoveStatus:
                            statusBefore = statusInit.MoveStatus
                            req = {'Timeout': None, 'Velocity': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': 0.1, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                            ptz.ContinuousMove(req)
                            sleep(1)
                            statusDuring1 = ptz.GetStatus(mediaToken)
                            ptz.Stop(mediaToken)
                            req['Velocity']['PanTilt']['x'] = -0.1
                            sleep(1.5)
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
                            sleep(1)
                            statusDuring1 = ptz.GetStatus(mediaToken)
                            ptz.Stop(mediaToken)
                            req['Velocity']['PanTilt']['x'] = -0.1
                            ptz.ContinuousMove(req)
                            sleep(1.5)
                            statusDuring2 = ptz.GetStatus(mediaToken)
                            ptz.Stop(mediaToken)
                            if statusBefore == statusDuring1.Position and statusBefore == statusDuring2.Position:
                                testBuffer = testBuffer + "Position property not functioning correctly"
                                getStatusF = getStatusF + [0]
                            else:
                                testBuffer = testBuffer + "Position property supported and functions correctly"
                                getStatusF = getStatusF + [1]
                        else:
                            testBuffer = testBuffer + "Position property not supported"
                            getStatusF = getStatusF + [0]
                    else:
                        testBuffer = "Unable to test due to unavailability of GetProfiles() method"
                        getStatusF = [0, 0]
                except:
                    testBuffer = "Not Supported"
                    getStatusF = [0, 0]
                    logging.exception('getstatus')
                ptzResult = ptzResult + [['GetStatus', testBuffer]]
            else:
                testBuffer = "Unable to test due to unavailability of GetNodes() method"
                getStatusF = [0, 0]
                ptzResult = ptzResult + [['GetStatus', testBuffer]]
                
            if getStatusF == [0, 0]:
                testBuffer = 'Unable to test due to unavailability of GetStatus() method'
                contMove = testBuffer
                absMove = testBuffer
                ptzResult = ptzResult + [['ContinuousMove', testBuffer]]
                ptzResult = ptzResult + [['AbsoluteMove', testBuffer]]
                ptzResult = ptzResult + [['RelativeMove', testBuffer]]
            elif getStatusF == [0, 1]:
                # continuous move test if only position is available
                try:
                    mediaToken = media.GetProfiles()[0].token
                    req = {'Timeout': None, 'Velocity': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': 0.2, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                    statusInit = ptz.GetStatus(mediaToken)
                    ptz.ContinuousMove(req)
                    sleep(1.5)
                    statusDuring1 = ptz.GetStatus(mediaToken)
                    ptz.Stop(mediaToken)
                    req = {'Timeout': None, 'Velocity': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': -0.1, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                    ptz.ContinuousMove(req)
                    sleep(1.5)
                    statusDuring2 = ptz.GetStatus(mediaToken)
                    ptz.Stop(mediaToken)
                    if statusInit.Position == statusDuring1.Position and statusInit.Position == statusDuring2.Position:
                        testBuffer = "Not Supported - coordinates didn't change after moving"
                    else:
                        testBuffer = "Supported"
                    contMove = testBuffer
                except:
                    testBuffer = "Not Supported"
                    contMove = testBuffer
                    logging.exception('cont move pos')
                ptzResult = ptzResult + [['ContinuousMove', testBuffer]]
                
                # absolute move test if only position is available
                try:
                    mediaToken = media.GetProfiles()[0].token
                    statusInit = ptz.GetStatus(mediaToken)
                    req = {'Position': {'Zoom': {'x': '0'}, 'PanTilt': {'x': 1, 'y': 0}}, 'ProfileToken': mediaToken}
                    ptz.AbsoluteMove(req)
                    sleep(2)
                    statusDuring1 = ptz.GetStatus(mediaToken)
                    req = {'Position': {'Zoom': {'x': '0'}, 'PanTilt': {'x': 0.5, 'y': -1}}, 'ProfileToken': mediaToken}
                    ptz.AbsoluteMove(req)
                    sleep(2)
                    statusDuring2 = ptz.GetStatus(mediaToken)
                    ptz.Stop(mediaToken)
                    if statusInit.Position == statusDuring1.Position and statusInit.Position == statusDuring2.Position:
                        testBuffer = "Not Supported - coordinates didn't change after moving"
                    else:
                        testBuffer = "Supported"
                    absMove = testBuffer
                except:
                    testBuffer = "Not Supported"
                    absMove = testBuffer
                    logging.exception('abs move pos')
                ptzResult = ptzResult + [['AbsoluteMove', testBuffer]]
            elif getStatusF == [1, 0]:
                
                # continuous move test if only status is available
                try:
                    mediaToken = media.GetProfiles()[0].token
                    req = {'Timeout': None, 'Velocity': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': 0.2, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                    statusInit = ptz.GetStatus(mediaToken)
                    ptz.ContinuousMove(req)
                    sleep(1.5)
                    statusDuring1 = ptz.GetStatus(mediaToken)
                    ptz.Stop(mediaToken)
                    req = {'Timeout': None, 'Velocity': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': -0.1, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                    ptz.ContinuousMove(req)
                    sleep(1.5)
                    statusDuring2 = ptz.GetStatus(mediaToken)
                    ptz.Stop(mediaToken)
                    if statusInit.MoveStatus == statusDuring1.MoveStatus and statusInit.MoveStatus == statusDuring2.MoveStatus:
                        testBuffer = "Not Supported - move status didn't change while moving"
                    else:
                        testBuffer = "Supported"
                    contMove = testBuffer
                except:
                    testBuffer = "Not Supported"
                    contMove = testBuffer
                    logging.exception('cont move status')
                ptzResult = ptzResult + [['ContinuousMove', testBuffer]]
                
                # absolute move test if only move status is available
                try:
                    mediaToken = media.GetProfiles()[0].token
                    statusInit = ptz.GetStatus(mediaToken)
                    req = {'Position': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': 1, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                    ptz.AbsoluteMove(req)
                    sleep(1)
                    statusDuring1 = ptz.GetStatus(mediaToken)
                    req = {'Position': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': 0.5, 'space': '', 'y': -1}}, 'ProfileToken': mediaToken}
                    ptz.AbsoluteMove(req)
                    sleep(1)
                    statusDuring2 = ptz.GetStatus(mediaToken)
                    ptz.Stop(mediaToken)
                    if statusInit.MoveStatus == statusDuring1.MoveStatus and statusInit.MoveStatus == statusDuring2.MoveStatus:
                        testBuffer = "Not Supported - move status didn't change while moving"
                    else:
                        testBuffer = "Supported"
                    absMove = testBuffer
                except:
                    testBuffer = "Not Supported"
                    absMove = testBuffer
                    logging.exception('abs move status')
                ptzResult = ptzResult + [['AbsoluteMove', testBuffer]]
            elif getStatusF == [1, 1]:
                
                ''' if both position and movestatus are supported '''
                
                # continuous move test using move status
                try:
                    mediaToken = media.GetProfiles()[0].token
                    req = {'Timeout': None, 'Velocity': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': 0.2, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                    statusInit = ptz.GetStatus(mediaToken)
                    ptz.ContinuousMove(req)
                    sleep(1.5)
                    statusDuring1 = ptz.GetStatus(mediaToken)
                    ptz.Stop(mediaToken)
                    req = {'Timeout': None, 'Velocity': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': -0.1, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                    ptz.ContinuousMove(req)
                    sleep(1.5)
                    statusDuring2 = ptz.GetStatus(mediaToken)
                    ptz.Stop(mediaToken)
                    if statusInit.MoveStatus == statusDuring1.MoveStatus and statusInit.MoveStatus == statusDuring2.MoveStatus:
                        testBuffer = "Not Supported - move status didn't change while moving"
                    else:
                        testBuffer = "Supported"
                    contMove = testBuffer
                except:
                    testBuffer = "Not Supported"
                    contMove = testBuffer
                    logging.exception('cont move getstatus')
                ptzResult = ptzResult + [['ContinuousMove', testBuffer]]
                
                # absolute move test using position
                try:
                    mediaToken = media.GetProfiles()[0].token
                    statusInit = ptz.GetStatus(mediaToken)
                    req = {'Position': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': 1, 'space': '', 'y': 0}}, 'ProfileToken': mediaToken}
                    ptz.AbsoluteMove(req)
                    sleep(2)
                    statusDuring1 = ptz.GetStatus(mediaToken)
                    req = {'Position': {'Zoom': {'x': '0', 'space': ''}, 'PanTilt': {'x': 0.5, 'space': '', 'y': -1}}, 'ProfileToken': mediaToken}
                    ptz.AbsoluteMove(req)
                    sleep(2)
                    statusDuring2 = ptz.GetStatus(mediaToken)
                    ptz.Stop(mediaToken)
                    if statusInit.Position == statusDuring1.Position and statusInit.Position == statusDuring2.Position:
                        testBuffer = "Not Supported - coordinates didn't change after moving"
                    else:
                        testBuffer = "Supported"
                    absMove = testBuffer
                except:
                    testBuffer = "Not Supported"
                    absMove = testBuffer
                    logging.exception('abs move getstatus')
                ptzResult = ptzResult + [['AbsoluteMove', testBuffer]]
            sleep(2)    
        
        file = open(os.getcwd() + '/engine/status.log', 'w')
        file.write('file')
        file.close()
        date = str(datetime.datetime.now())
        date = date.split('.')
        header = [['Device IP', ip], ['Test Performed', date[0]]]
        summary = [['Continuous Move', contMove], ['Absolute Move', absMove], ['Video Encoding', vCodecs], ['Video Resolutions', vResolutions], ['Audio Encoding', aCodecs], ['Relay Support', str(relayF)]]
        reportn = os.getcwd() + '/engine/reports/' + ip + '.csv'
        with open(reportn, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(header)
            writer.writerows(summary)
            if dmgmtF:
                writer.writerows([['testdmgmt', '']])
                writer.writerows(dmgmtResult)
            if mediaF:
                writer.writerows([['testmedia', '1']])
                writer.writerows(mediaResult)
            if imagingF:
                writer.writerows([['testimg', '1']])
                writer.writerows(imagingResult)
            if eventsF:
                writer.writerows([['testevents', '1']])
                writer.writerows(eventResult)
            if ptzF:
                writer.writerows([['testptz', '1']])
                writer.writerows(ptzResult)
        csvFile.close()
        file = open(os.getcwd() + '/engine/status.log', 'w')
        file.write('finished')
        file.close()