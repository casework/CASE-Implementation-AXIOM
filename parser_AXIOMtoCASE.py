#
#	xml_sax_UFED_to_CASE: UFED  SAX parser from XML report to CASE-JSON-LD 
#

import xml.sax 
import string
import argparse
import os
import codecs
import AXIOMtoJSON as CJ
import re
import sys
import timeit

class AXIOMgadget():
    def __init__(self, xmlReport, jsonCASE, reportType, baseLocalPath):    
        self.xmlReport = xmlReport
        self.jsonCASE = jsonCASE
        self.reportType = reportType
        self.baseLocalPath = baseLocalPath + 'Attachments/'

    def processXmlReport(self):

#---    create a parser
#    
        SAXparser = xml.sax.make_parser()

#---    override the default ContextHandler
#    
        Handler = ExtractTraces(self.baseLocalPath)

        Handler.createOutFile(self.jsonCASE)

        SAXparser.setContentHandler(Handler)
   
        SAXparser.parse(self.xmlReport)

        print(Handler.C_cyan + '\n\n\CASE is being generated...' + Handler.C_end)

        if self.reportType == 'mobile':
            print(Handler.C_cyan + "owner's phone number / name: " + 
                Handler.CALLphoneNumberDevice + ' / ' + Handler.CALLphoneNameDevice + 
                '\n' + Handler.C_end)


#---    create object and open JSON file and define the boolean value that
#       indicates if the line with comma plus return must be written before
#       writing the next ObservableObject   
#
        caseTrace = CJ.AXIOMtoJSON(Handler.fOut, False)


#---    write CASE @context, version and description JSON file
#
        caseTrace.writeHeader()


#---    write phoneAccountFacet for the device phone number
#
        if self.reportType == 'mobile':
            caseTrace.writePhoneOwner(Handler.CALLphoneNumberDevice, 
                Handler.CALLphoneNameDevice)

        caseTrace.writeFiles(Handler.FILEid, Handler.FILEtag, Handler.FILEfileName,
                Handler.FILEfileLocalPath, Handler.FILEimage, Handler.FILEfileSize,
                Handler.FILEcreated, Handler.FILEmodified, Handler.FILEaccessed, 
                Handler.FILEmd5, Handler.FILEsource, Handler.FILElocation, 
                Handler.FILErecoveryMethod)


#---    write PhoneAccountFacet relying on CONTACT
#       CONTACTname is a list of names of contacts, 
#       CONTACTphoneNums is a list of list of phone numbers, each item represents 
#       the list of phone numbers of a contact. So a contact is identified by 
#       the item CONTACname[i] and this contact may have many phone numbers 
#       identified by CONTACTphoneNums[i][j] iterating on the index j
#       The writeContacts method must be invoked before the processing of
#       the SMS and Call traces, both of them are based on the list of phone numbers

        if self.reportType == 'mobile':    
            caseTrace.writePhoneAccountFromContacts(Handler.CONTACTname, 
                Handler.CONTACTphoneNumber)

#---    write  CALL
#       
        if self.reportType == 'mobile':
            caseTrace.writeCall(Handler.CALLid, Handler.CALLappName, Handler.CALLtimeStamp, 
                    Handler.CALLdirection, Handler.CALLduration, Handler.CALLpartner, 
                    Handler.CALLsource, Handler.CALLlocation, Handler.CALLrecoveryMethod)

#-- write SMS
#
        if self.reportType == 'mobile':
            caseTrace.writeSms(Handler.SMSid, Handler.SMSsender,
                    Handler.SMSrecipient, Handler.SMSreceivedDateTime, 
                    Handler.SMSsentDateTime, 
                    Handler.SMSmessage, Handler.SMSdirection, Handler.SMSsource, 
                    Handler.SMSlocation, Handler.SMSrecoveryMethod)

#---    write CHAT

        caseTrace.writeChat(Handler.CHATid, Handler.CHATsender, Handler.CHATreceiver, 
                        Handler.CHATdateTimeSent, Handler.CHATdateTimeReceived, 
                        Handler.CHATmessage, Handler.CHATmessageStatus, 
                        Handler.CHATapplication, Handler.CHATsource,
                        Handler.CHATlocation, Handler.CHATrecoveryMethod)

        caseTrace.writeEmail(Handler.EMAILid, Handler.EMAILappSource, Handler.EMAILsender, 
                        Handler.EMAILrecipient, Handler.EMAILcc, Handler.EMAILbcc, 
                        Handler.EMAILbody, Handler.EMAILsubject, Handler.EMAILdateTime, 
                        Handler.EMAILattachment, Handler.EMAILsource, 
                        Handler.EMAILlocation, Handler.EMAILrecoveryMethod)

#---    all parameters are lists containing data of the extracted WEB_PAGE
#
        caseTrace.writeWebPages(Handler.WEBid, Handler.WEBappSource, 
                       Handler.WEBurl, Handler.WEBtitle, Handler.WEBvisitCount,
                       Handler.WEBlastVisited, Handler.WEBsource, 
                        Handler.WEBlocation, Handler.WEBrecoveryMethod)

#---    Write the context info: Device info, only, the other data such as
#       Forensic tool info, Acquisition/Extraction investigative Actions, Peformer,
#       are not included in the AXIOM XML report
#
        caseTrace.generateTraceDevice('', Handler.DEVICEserialNumberText,  
            Handler.DEVICEnameText, '', '', '', '', '', '', '', '')

# Handler.CONTEXTimagePath = ['blk0_sda.bin', 'blk16_sdb.bin', 
#     'blk32_sdc.bin', 'procdata.zip']
# Handler.CONTEXTimageSize = ['31989956608', '4194304', 
#     '4194304', '1429913']    
# Handler.CONTEXTimageMetadataHashSHA.append('62765111E7195CE75C6CB255CD03AD3433D35ACFF31AF89CCBF07CE34CE1E17E')
# Handler.CONTEXTimageMetadataHashSHA.append('005A783BAC24E3782DE8C16C2933CD9FF95EE0E4EFF3EE7C0BA4253636301127')
# Handler.CONTEXTimageMetadataHashSHA.append('1301CA17CF7DE7DA7B52AE178C1DBBFED8FA4BCC97F081C6FB29C981EF43FD0B')
# Handler.CONTEXTimageMetadataHashSHA.append('894CF1D6ED65909104A519031CDF685E8445EE367D2887D491E03FEA875FE13A')
# Handler.CONTEXTimageMetadataHashMD5 = ['0', '0', '0', '0']

# caseTrace.writeContextAxiom('4.0.1.19617', 
#    '2020-06-01T11:00:00+0', '2020-06-01T08:00:00+0',
#    '2020-06-01T10:15:00+0', 'Fabrizio',
#    '00:56:78:99:AC', 'AC78234', 'Samsung SM-DX-80', 'Android', 
#    '5.1', 'Samsung', '00:78:E4:90:1C', '12356707079', '6907072103', 
#    '7869664323912760', Handler.CONTEXTimagePath, Handler.CONTEXTimageSize, 
#    Handler.CONTEXTimageMetadataHashSHA, Handler.CONTEXTimageMetadataHashMD5)

# this write a single line to complete the JSON output file

        caseTrace.writeLastLine()
        Handler.fOut.close()

        return Handler


class ExtractTraces(xml.sax.ContentHandler):

    def __init__(self, baseLocalPath):
        self.fOut = ''
        self.lineXML = 0

        self.skipLine = False
        self.FILEkind = ['Pictures', 'Videos', 'RTF Documents', 'Excel Documents',\
            "PowerPoint Documents", "Audio", "PDF Documents", "Word Documents", \
            "WordPerfect Files", "Calc Documents", "Writer Documents", "Text Documents"]


        self.inHit = False
        self.Observable = False
        self.C_green  = '\033[32m'
        self.C_grey  = '\033[37m'
        self.C_red = '\033[31m'
        self.C_cyan = '\033[36m'
        self.C_end = '\033[0m'


#---    DEVICE INFO  section - XPath
#       {CALL_PATH} = //Artifact[@name="File System Information"]/Hits/Hit
#       /Fragment[@name="Volume Serial Number"] and Fragment[@name="Source"]
#
        self.DEVICEin = False
        self.DEVICEinSerialNumber = False
        self.DEVICEinName = False        
        self.DEVICEserialNumberText = ''
        self.DEVICEnameText = ''


#---    CALL  section - XPath
#       {CALL_PATH} = //Artifact[@name="Android Call Logs"]/Hits/Hit
#       {CALL_PATH} = //Artifact[@name="iOS Call Logs"]/Hits/Hit
#
        self.CALLtrace = 'call'
        self.CALLin = False
        self.CALLinPartner = False
        self.CALLinDirection = False
        #self.CALLinCallStatus = False
        self.CALLinTimeStamp = False
        self.CALLinDuration = False
        self.CALLinSource = False
        self.CALLinLocation = False
        self.CALLinRecoveryMethod = False

#---    Device phone number
#       //Artifact[@name="Android WhatsApp Accounts Information"]
#       /Hits/Hit/Fragment[@name="Phone Number"]        

        self.CALL_PHONE_NUM_DEVICEin = False
        self.CALL_PHONE_NUM_DEVICE_VALUEin = False
        self.CALL_PHONE_NAME_DEVICE_VALUEin = False
        
        self.CALLpartnerText = ''
        self.CALLdirectionText = ''
        self.CALLtimeStampText = ''
        self.CALLdurationText = ''
        self.CALLsourceText = ''
        self.CALLlocationText = ''
        self.CALLrecoveyMethodText = ''
        self.CALLappNameText = ''
        self.CALLphoneNumberDevice = ''
        self.CALLphoneNameDevice = ''

        self.CALLtotal = 0
        self.CALLid = []
        self.CALLappName = []
        self.CALLpartner = []
        self.CALLdirection = []        
        self.CALLtimeStamp = []
        self.CALLduration = []
        self.CALLsource = []
        self.CALLlocation = []
        self.CALLrecoveryMethod = []

#---    CHAT  section - XPath
#       {CHAT_PATH} = //Artifact[@name="Android WhatsApp Messages"]/Hits/Hit
#       {CALL_PATH} = //Artifact[@name="iOS Call Logs"]/Hits/Hit
#       {CALL_PATH} = //Artifact[@name="Skype Chat Messages"]/Hits/Hit
#       {CALL_PATH} = //Artifact[@name="Skype Chatsync Messages"]/Hits/Hit
#       {CALL_PATH} = //Artifact name="Android Telegram Messages">
#       {CALL_PATH} = //Artifact name="Snapchat Chat Messages">
#
        self.CHATtrace = 'chat'
        self.CHATin = False
        self.CHATinSender = False
        self.CHATinReceiver = False
        self.CHATinDateTimeSent = False
        self.CHATinDateTimeReceived = False
        self.CHATinMessage = False
        self.CHATinMessageStatus = False
        self.CHATinSource = False
        self.CHATinLocation = False
        self.CHATinRecoveryMethod = False

#---    Chat Telegram: fields are different from Whatsapp
#        
        self.CHATinPartner = False
        self.CHATinDateTime = False
        self.CHATinMessageType = False

        
        self.CHATsenderText = ''
        self.CHATreceiverText = ''
        self.CHATpartnerText = ''
        self.CHATdateTimeSentText = ''
        self.CHATdateTimeReceivedText = ''
        self.CHATdateTimeText = ''
        self.CHATmessageText =  ''
        self.CHATmessageStatusText =  ''
        self.CHATmessageTypeText =  ''
        self.CHATsourceText =  ''
        self.CHATlocationText = ''
        self.CHATrecoveryMethodText = ''
        self.CHATapplicationText = ''

        self.CHATtotal = 0
        self.CHATid = []
        self.CHATsender = []
        self.CHATreceiver = []
        self.CHATdateTimeSent = []
        self.CHATdateTimeReceived = []
        self.CHATmessage = [] 
        self.CHATmessageStatus = [] 
        self.CHATapplication = []
        self.CHATsource =  []
        self.CHATlocation = []
        self.CHATrecoveryMethod = []

#---    These are list of list: each item contains a list with all the data relating 
#       to the messages of a single Chat, because they are grouped in the same thread. 
#       Therefore the item i (Chat[i]) contains many text messages and each of them is
#       stored in the item CHATmessages[i] that, actually, is a list. For instance, if
#       the Chat[0] contains three messages whose body are "How are you?", "I',m fine, and you?"
#       "So far so good", then the  CHATmessages[0] is the following list
#       ["How are you?", "I'm fine, and you?", "So far so good!"]
#               
        self.CHATids = []
        self.CHATapplications = []
        self.CHATsenders = []
        self.CHATreceivers = []
        self.CHATdateTimeSents = []
        self.CHATdateTimeReceiveds = []
        self.CHATmessages = [] 
        self.CHATmessageStatuses = []
        self.CHATsources =  []
        self.CHATlocations = []
        self.CHATrecoveryMethods = []

        self.CONTACTtrace = 'contact'
        self.CONTACTin = False
        self.CONTACTinName = False
        self.CONTACTinPhoneNumber = False
        self.CONTACTinSource = False
        self.CONTACTinLocation = False
        self.CONTACTinRecoveryMethod = False

        self.CONTACTnameText = ''
        self.CONTACTphoneNumberText = ''
        self.CONTACTsourceText =  ''
        self.CONTACTlocationText = ''
        self.CONTACTrecoveryMethodText = ''

        self.CONTACTtotal = 0
        self.CONTACTid = []
        self.CONTACTname = []
        self.CONTACTphoneNumber = []
        self.CONTACTsource = []
        self.CONTACTlocation = []
        self.CONTACTrecoveryMethod = []

#---    The Artifacts extracted are: Android Emails, Gmail Emails, Apple Email,
#       Android Yahoo Mail Emails.
#       Not yet extracted: Outlook Emails
#        
        self.EMAILtrace = 'email'
        self.EMAILin = False
        self.EMAILinSender= False
        self.EMAILinRecipients= False
        self.EMAILinCC = False
        self.EMAILinBCC = False
        self.EMAILinDateTime = False
        self.EMAILinSubject = False
        self.EMAILinBody = False
        self.EMAILinAttachment = False
        self.EMAILinSource = False
        self.EMAILinLocation = False
        self.EMAILinRecoveryMethod = False

        self.EMAILsenderText = ''
        self.EMAILrecipientText = ''
        self.EMAILccText = ''
        self.EMAILbccText = ''
        self.EMAILdateTimeText = ''
        self.EMAILsubjectText = ''
        self.EMAILbodyText = ''
        self.EMAILattachmentText = ''        
        self.EMAILsourceText =  ''
        self.EMAILlocationText = ''
        self.EMAILrecoveryMethodText = ''

        self.EMAILtotal = 0
        self.EMAILid = []
        self.EMAILappName = ''
        self.EMAILappSource = []
        self.EMAILsender = []
        self.EMAILrecipient = []
        self.EMAILcc = []
        self.EMAILbcc = []
        self.EMAILdateTime = []
        self.EMAILsubject = []
        self.EMAILbody = []
        self.EMAILattachment = []
        self.EMAILsource = []
        self.EMAILlocation = []
        self.EMAILrecoveryMethod = []

#---    FILE  section - XPath
#       {FILE_PATH} = //Artifact[@name="Pictures"]/Hits/Hit
#
        self.FILEin = False
        self.FILEinTag = False
        self.FILEinFileName = False
        self.FILEinImage = False
        self.FILEinFileExtension = False
        self.FILEinFileSize = False
        self.FILEinCreated = False
        self.FILEinModified = False
        self.FILEinAccessed = False
        self.FILEinMD5 = False
        self.FILEinSource = False
        self.FILEinLocation = False
        self.FILEinRecoveryMethod = False


        self.FILEtotal = 0
        self.FILEtagText = ''
        self.FILEfileNameText = ''
        self.FILEimageText = ''
        self.FILEfileExtensionText = ''
        self.FILEbaseLocalPath = baseLocalPath
        self.FILEfileSizeText = ''
        self.FILEcreatedText = ''
        self.FILEmodifiedText = ''
        self.FILEaccessedText = ''
        self.FILEmd5Text = ''
        self.FILEsourceText = ''
        self.FILElocationText = ''
        self.FILErecoveryMethodText = ''
        
        self.FILEid = []
        self.FILEtag = []
        self.FILEfileName = []
        self.FILEfileLocalPath = []
        self.FILEimage =  []
        self.FILEfileExtension = []
        self.FILEfileSize = []
        self.FILEcreated = []
        self.FILEmodified = []
        self.FILEaccessed = []
        self.FILEmd5 = []
        self.FILEsource = []
        self.FILElocation = []
        self.FILErecoveryMethod = []

#---    SMS  section - XPath
#       {SMS_PATH} = //Artifact[@name="Android SMS"]/Hits/Hit
#       {SMS_PATH} = //Artifact[@name="Android MMS"]/Hits/Hit
#       {SMS_PATH} = //Artifact[@name="iOS iMessage/SMS/MMS"]/Hits/Hit
#    
        self.SMStrace = 'sms'
        self.SMSin = False
        self.SMSinPartner = False
        self.SMSinRecipient = False
        self.SMSinSender = False
        self.SMSinReceivedDateTime = False
        self.SMSinSentDateTime = False
        self.SMSinMessage = False
        self.SMSinDirection = False
        self.SMSinSource = False
        self.SMSinLocation = False
        self.SMSinRecoveryMethod = False

        self.SMSpartnerText = ''
        self.SMSrecipientText = ''
        self.SMSsenderText = ''
        self.SMSreceivedDateTimeText = ''
        self.SMSsentDateTimeText = ''
        self.SMSmessageText = ''
        self.SMSdirectionText = ''
        self.SMSsourceText =  ''
        self.SMSlocationText = ''
        self.SMSrecoveryMethodText = ''

        self.SMStotal = 0
        self.SMSid = []
        self.SMSrecipient = []
        self.SMSsender = []
        self.SMSreceivedDateTime = []
        self.SMSsentDateTime = []
        self.SMSmessage = []
        self.SMSdirection = []
        self.SMSsource = []
        self.SMSlocation = []
        self.SMSrecoveryMethod = []

#---    WEB_HISTORY  section - XPath
#       {WEB_HISTORY_PATH} = //Artifact[@name="Chrome Web History"]/Hits/Hit
#       {WEB_HISTORY_PATH} = //Artifact[@name="Safari History"]/Hits/Hit
#       {WEB_HISTORY_PATH} = //Artifact[@name="Firefox Web History"]/Hits/Hit 
#       {WEB_HISTORY_PATH} = //Artifact[@name="Edge/Internet Explorer 10-11 Main History"]/Hits/Hit         
#    
        self.WEBtrace = 'web'
        self.WEBin = False
        self.WEBinUrl = False
        self.WEBinLastVisited = False
        self.WEBinTitle = False
        self.WEBinVisitCount = False
        self.WEBinSource = False
        self.WEBinLocation = False
        self.WEBinRecoveryMethod = False

        self.WEBurlText = ''
        self.WEBlastVisitedText = ''
        self.WEBtitleText = ''
        self.WEBvisitCountText = ''
        self.WEBsourceText =  ''
        self.WEBlocationText = ''
        self.WEBrecoveryMethodText = ''

        self.WEBtotal = 0
        self.WEBid = []
        self.WEBurl = []
        self.WEBappName = ''
        self.WEBappSource = []
        self.WEBtitle = []
        self.WEBlastVisited = []
        self.WEBvisitCount = []
        self.WEBsource = []
        self.WEBlocation = []
        self.WEBrecoveryMethod = []

        self.CONTEXTimagePath = []
        self.CONTEXTimageSize = []
        self.CONTEXTimageMetadataHashSHA = []
        self.CONTEXTimageMetadataHashMD5 = []


    def createOutFile(self, filename):
        self.fOut = codecs.open(filename, 'w', encoding='utf8')

    
    def __processPHONE_NUM(self, attrFragment):
        if attrFragment == 'Phone Number': 
            self.CALL_PHONE_NUM_DEVICE_VALUEin = True 

        if attrFragment == 'WhatsApp Name': 
            self.CALL_PHONE_NAME_DEVICE_VALUEin = True 

    def __processCALL(self, attrFragment):
        if attrFragment.find('Partner', 0) > -1:  
                self.CALLinPartner = True 

        if attrFragment == 'Direction':  
                self.CALLinDirection = True 

        if attrFragment.find('Call Date/Time') > -1:  
                self.CALLinTimeStamp = True 

        if attrFragment.find('Call Duration') > -1:  
                self.CALLinDuration = True 

        if attrFragment == 'Source':  
                self.CALLinSource = True 

        if attrFragment == 'Location':  
                self.CALLinLocation = True 

        if attrFragment == 'Recovery Method':  
                self.CALLinRecoveryMethod = True     

    def __processCHAT(self, attrFragment):
#---    the first condition is for Android WhatsApp Messages, iOS WhatsApp Messages
#       and for Snapchat Chat Messages
#       the second condition is for iOS Telegram Messages
#        
        if (attrFragment == 'Sender' or 
            attrFragment == 'Sender Name'):  
            self.CHATinSender = True 

#---    the first condition is for Android WhatsApp Messages and iOS WhatsApp Messages
#       the second condition is for iOS Telegram Messages
#       the third condition is for Snapchat Chat Messages            
#
        if (attrFragment == 'Receiver' or
            attrFragment == 'Recipient Name' or 
            attrFragment == 'Recipient(s)'): 
            #print("CHATapplicationText=" + self.CHATapplicationText)
            self.CHATinReceiver = True 

#---    the condition is for Android Telegram Messages
#
        if attrFragment == 'Partner':  
            self.CHATinPartner = True 

        if attrFragment.find('Message Sent Date/Time') > -1:  
            self.CHATinDateTimeReceived = True            

        if attrFragment.find('Message Received Date/Time') > -1: 
            self.CHATinDateTimeReceived = True 
#---    the first condition is for iOS WhatsApp Messages
#       the second condition is for Telegram Messages   
#            
        if (attrFragment.find('Message Date/Time') > -1 or 
            attrFragment.find('Creation Date/Time') > -1):  
            self.CHATinDateTime = True

#---    the first condition is for WhatsApp Messages
#       the second condition is for Telegram Messages   
#            
        if (attrFragment == 'Message' or 
            attrFragment == 'Message Body'):
            self.CHATinMessage = True 

        if attrFragment == 'Message Status':  
            self.CHATinMessageStatus = True 

#---    only for iOS Whatsapp, Telegram and Skype Messages
#            
        if attrFragment == 'Message Type':  
            self.CHATinMessageType = True 

        if attrFragment == 'Source':  
            self.CHATinSource = True

        if attrFragment == 'Location':  
            self.CHATinLocation = True 

        if attrFragment == 'Recovery Method':  
            self.CHATinRecoveryMethod = True 

    
    def __processCONTACT(self, attrFragment):
        if attrFragment == 'Display Name':  
            self.CONTACTinName = True 

        if attrFragment == 'Phone Number(s)':  
            self.CONTACTinPhoneNumber = True 

        if attrFragment == 'Source':  
            self.CONTACTinSource = True

        if attrFragment == 'Location':  
            self.CONTACTinLocation = True 

        if attrFragment == 'Recovery Method':  
            self.CONTACTinRecoveryMethod = True 

    def __processDEVICE(self, attrFragment):
        if attrFragment == 'Volume Serial Number':  
            self.DEVICEinSerialNumber = True 
        if attrFragment == 'Source':  
            self.DEVICEinName = True 

    def __processEMAIL(self, attrFragment):
        if (attrFragment == 'Sender' or attrFragment == 'From Address' or 
            attrFragment == 'From'):  
            self.EMAILinSender = True 

        if (attrFragment == 'Recipients' or attrFragment == 'To Address(es)' or 
            attrFragment == 'To'):  
            self.EMAILinRecipients = True

        if (attrFragment.lower() == 'cc' or attrFragment.lower() == 'cc address(es)'):  
            self.EMAILinCC = True 

        if (attrFragment.lower() == 'bcc' or attrFragment.lower() == 'bcc address(es)'):  
            self.EMAILinBCC = True 

        if attrFragment.find('Date/Time') > - 1:  
            self.EMAILinDateTime = True 

        if attrFragment == 'Subject':  
            self.EMAILinSubject = True 

        if attrFragment.find(' Body') > -1:  
            self.EMAILinBody = True 

        if attrFragment == 'Attachments':  
            self.EMAILinAttachment = True 

        if attrFragment == 'Source':  
            self.EMAILinSource = True

        if attrFragment == 'Location':  
            self.EMAILinLocation = True 

        if attrFragment == 'Recovery Method':  
            self.EMAILinRecoveryMethod = True 

    
    def __processFILE(self, attrFragment):
        if attrFragment == 'Tags':
            self.FILEinTag = True
        if (attrFragment == 'File Name' or 
            attrFragment == 'Filename' or 
            attrFragment == " File" or 
            attrFragment == "_Video" or 
            attrFragment == "File"):
            self.FILEinFileName = True
        if attrFragment == 'Image':
            self.FILEinImage = True
        if attrFragment == 'File Extension':
            self.FILEinFileExtension = True
        if (attrFragment == 'Size (Bytes)' or 
            attrFragment == 'File Size (Bytes)'):
            self.FILEinFileSize = True
        if attrFragment.find('Created Date/Time') > -1:
            self.FILEinCreated = True
        if attrFragment.find('Last Modified Date/Time') > -1:
            self.FILEinModified = True
        if attrFragment.find('Accessed Modified Date/Time') > -1:
            self.FILEinAccessed = True
        if attrFragment == 'MD5 Hash':
            self.FILEinMD5 = True
        if attrFragment == 'Source':
            self.FILEinSource = True
        if attrFragment == 'Location':
            self.FILEinLocation = True
        if attrFragment == 'Recovery Method':
            self.FILEinRecoveryMethod = True

    def __processSMS(self, attrFragment):
        if attrFragment == 'Partner':
            self.SMSinPartner = True
        if attrFragment == 'Recipient':
            self.SMSinRecipient = True
        if attrFragment == 'Sender':
            self.SMSinSender = True
        if attrFragment.find('Received Date/Time') > -1:
            self.SMSinReceivedDateTime = True
        if attrFragment.find('Sent Date/Time') > -1:
            self.SMSinSentDateTime = True
        if attrFragment == 'Message':
            self.SMSinMessage = True
        if (attrFragment == 'Message Direction' or 
            attrFragment == 'Type'):
            self.SMSinDirection = True
        if attrFragment == 'Source':
            self.SMSinSource = True
        if attrFragment == 'Location':
            self.SMSinLocation = True
        if attrFragment == 'Recovery Method':
            self.SMSinRecoveryMethod = True

    def __processWEB(self, attrFragment):
        if attrFragment == 'URL':
            self.WEBinUrl = True
        if attrFragment.find('Last Visited Date/Time') > -1:
            self.WEBinLastVisited = True
        if attrFragment == 'Title':
            self.WEBinTitle = True
        if (attrFragment == 'Visit Count' or 
            attrFragment == 'Access Count'):
            self.WEBinVisitCount = True
        if attrFragment == 'Source':
            self.WEBinSource = True
        if attrFragment == 'Location':
            self.WEBinLocation = True
        if attrFragment == 'Recovery Method':
            self.WEBinRecoveryMethod = True
    
    def printObservable(self, oName, oCount):        
        line =  'processing traces --> ' + oName +  ' n. ' +  \
            str(oCount) + self.C_end
        if oCount == 1:
            print(self.C_green + '\n' + line, end='\r') 
        else:
            print(self.C_green + line, end='\r') 

#---    it captures each Element when it is opened., the order depends on their 
#       position from the beginning of the document
#            
    def startElement(self, elementName, attrs):

        self.lineXML +=1

        attrName = ''

#*---   checks on Elements
#        
        if elementName == 'Artifact':
            attrName = attrs.get('name')
#---    checks on Attributes
#        
            if  (attrName == 'Android WhatsApp Accounts Information'): 
                self.CALL_PHONE_NUM_DEVICEin = True
                self.Observable = True
                self.skipLine = True

            if  (attrName == 'Android Call Logs' or 
                attrName == 'iOS Call Logs') :
                self.CALLin = True
                self.Observable = True
                self.skipLine = True   
                self.CALLappNameText = attrName 

            if  attrName == 'File System Information':
                self.DEVICEin = True

#---    It captures both "Android WhatsApp Messages"  and "iOS WhatsApp Messages"
#                
            if  (attrName.find('WhatsApp Messages') > -1 or 
                attrName.find('Telegram Messages') > -1 or 
                attrName == 'Snapchat Chat Messages'):
                self.CHATin = True
                self.Observable = True
                self.skipLine = True
                self.CHATapplicationText = attrName 
                #print("CHATin, application: " + self.CHATapplicationText ) 

            if  (attrName == 'Android Contacts'):
                self.CONTACTin = True
                self.Observable = True
                self.skipLine = True

            if  attrName in self.FILEkind:
                self.FILEin = True
                self.Observable = True 
                self.skipLine = True 
                self.FILEtagText = attrName        

            #if  attrName == 'Skype Chat Messages':
            #    self.CHATin = True
            #    self.CHATapplicationText = 'Skype'


            #if  attrName == 'Snapchat Chat Messages':
            #    self.CHATin = True
            #    self.CHATapplicationText = 'Snapchat'                                              

#---    for the Emails attrName can assume the values of:
#       Android Emails. Gmail Emails, Android Yahoo Mail Emails, Outlook Emails, 
#       MBOX Emails or Apple Mail
#
            if  (attrName.find(' Emails') > -1 or 
                attrName == 'Apple Email'):
                self.EMAILin = True
                self.Observable = True
                self.skipLine = True
                self.EMAILappName = attrName

            if  (attrName == 'Android SMS' or 
                 attrName == 'iOS iMessage/SMS/MMS'):
                self.SMSin = True
                self.Observable = True
                self.skipLine = True

            if  (attrName == 'Chrome Web History' or
                attrName == 'Safari History' or 
                attrName == 'Firefox Web History' or                
                attrName == 'Samsung Browser Web History' or 
                attrName.find('Edge/Internet Explorer') > -1):
                self.WEBin = True
                self.Observable = True
                self.skipLine = True
                self.WEBappName = attrName
                #print("self.WEBappName=" + self.WEBappName)
         
               
#---    there is a Hit Element for each Observable (CALL, CHAT etc.)
#            
        if (elementName == 'Hit'):  
            self.inHit = True
            
            if self.CALLin:
                self.CALLtotal += 1
                self.printObservable('CALL', self.CALLtotal)
                self.CALLid.append(str(self.CALLtotal))
                self.CALLappName.append(self.CALLappNameText)
                self.CALLpartner.append('EMPTY')
                self.CALLdirection.append('EMPTY')
                self.CALLtimeStamp.append('EMPTY')
                self.CALLduration.append('EMPTY')
                self.CALLsource.append('EMPTY')
                self.CALLlocation.append('EMPTY')
                self.CALLrecoveryMethod.append('EMPTY')

            if self.DEVICEin:
                self.DEVICEnameText= ''
                if self.DEVICEserialNumberText != '':
                    pass             

            
            if self.CHATin:
                self.CHATtotal += 1
                self.printObservable('CHAT', self.CHATtotal)
                self.CHATid.append(str(self.CHATtotal))
                self.CHATsender.append('')
                self.CHATreceiver.append('')
                self.CHATdateTimeSent.append('')
                self.CHATdateTimeReceived.append('')
                self.CHATmessage.append('')
                self.CHATmessageStatus.append('')
                self.CHATsource.append('')
                self.CHATlocation.append('')
                self.CHATrecoveryMethod.append('')
                self.CHATapplication.append(self.CHATapplicationText)

            if self.CONTACTin:
                self.CONTACTtotal += 1
                self.printObservable('CONTACT', self.CONTACTtotal)
                self.CONTACTid.append(str(self.CONTACTtotal))
                self.CONTACTname.append('EMPTY')
                self.CONTACTphoneNumber.append('EMPTY')
                self.CONTACTsource.append('EMPTY')
                self.CONTACTlocation.append('EMPTY')
                self.CONTACTrecoveryMethod.append('EMPTY')


            if self.EMAILin:
                self.EMAILtotal += 1
                self.printObservable('EMAIL', self.EMAILtotal)
                self.EMAILid.append(str(self.EMAILtotal))
                self.EMAILappSource.append(self.EMAILappName)
                self.EMAILsender.append('EMPTY')
                self.EMAILrecipient.append('EMPTY')
                self.EMAILcc.append('EMPTY')
                self.EMAILbcc.append('EMPTY')
                self.EMAILdateTime.append('EMPTY')
                self.EMAILsubject.append('EMPTY')
                self.EMAILbody.append('EMPTY')
                self.EMAILattachment.append('EMPTY')
                self.EMAILsource.append('EMPTY')
                self.EMAILlocation.append('EMPTY')
                self.EMAILrecoveryMethod.append('EMPTY')

            if self.FILEin:
                self.FILEtotal += 1
                self.printObservable('FILE', self.FILEtotal)
                self.FILEid.append(str(self.FILEtotal))
                self.FILEtag.append(self.FILEtagText)
                self.FILEfileName.append('EMPTY')
                self.FILEfileLocalPath.append('EMPTY')
                self.FILEimage.append('EMPTY')
                self.FILEfileExtension.append('EMPTY')
                self.FILEfileSize.append('EMPTY')
                self.FILEcreated.append('EMPTY')
                self.FILEmodified.append('EMPTY')
                self.FILEaccessed.append('EMPTY')
                self.FILEmd5.append('EMPTY')
                self.FILEsource.append('EMPTY')
                self.FILElocation.append('EMPTY')
                self.FILErecoveryMethod.append('EMPTY')

            if self.SMSin:
                self.SMStotal += 1
                self.printObservable('SMS', self.SMStotal)
                self.SMSid.append(str(self.SMStotal))
                self.SMSsender.append('EMPTY')
                self.SMSrecipient.append('EMPTY')
                self.SMSreceivedDateTime.append('EMPTY')
                self.SMSsentDateTime.append('EMPTY')
                self.SMSmessage.append('EMPTY')
                self.SMSdirection.append('EMPTY')
                self.SMSsource.append('EMPTY')
                self.SMSlocation.append('EMPTY')
                self.SMSrecoveryMethod.append('EMPTY') 

            if self.WEBin:
                self.WEBtotal += 1
                self.printObservable('WEB', self.WEBtotal)
                self.WEBid.append(str(self.WEBtotal))
                self.WEBurl.append('EMPTY')
                self.WEBlastVisited.append('EMPTY')
                self.WEBtitle.append('EMPTY')
                self.WEBvisitCount.append('')
                self.WEBappSource.append(self.WEBappName)
                self.WEBsource.append('EMPTY')
                self.WEBlocation.append('EMPTY')
                self.WEBrecoveryMethod.append('EMPTY')                

        if elementName == 'Fragment':
            attrName = attrs.get('name')        
#---    processing Fragment CALL
#
            if self.CALLin and self.inHit:
                self.__processCALL(attrName)

            if self.DEVICEin and self.inHit:
                self.__processDEVICE(attrName)

            if self.CHATin and self.inHit: 
                self.__processCHAT(attrName)

            if self.CONTACTin and self.inHit:
                self.__processCONTACT(attrName)            
            
            if self.CALL_PHONE_NUM_DEVICEin and self.inHit:
                self.__processPHONE_NUM(attrName)  

            if self.EMAILin and self.inHit:
                self.__processEMAIL(attrName)  

            if self.FILEin and self.inHit:
                self.__processFILE(attrName)
            
            if self.SMSin and self.inHit:
                self.__processSMS(attrName) 

            if self.WEBin and self.inHit:
                self.__processWEB(attrName)  

            
            if (not self.Observable):
                line = self.C_grey + '*\tProcessing Element <' + elementName + '> at line '
                line += str(self.lineXML) + ' ...'  + self.C_end
                if self.skipLine:
                    print ('\n' + line , end='\r')
                    self.skipLine = False                  
                else:
                    print (line , end='\r')                  


    def __endElementFragmentPHONE_NUM(self):        
        if self.CALL_PHONE_NUM_DEVICE_VALUEin:            
            #self.CALLphoneNumberDevice = '' 
            self.CALL_PHONE_NUM_DEVICE_VALUEin = False

        if self.CALL_PHONE_NAME_DEVICE_VALUEin:            
            #self.CALLphoneNumberDevice = '' 
            self.CALL_PHONE_NAME_DEVICE_VALUEin = False

    def __endElementFragmentCALL(self):
        if self.CALLinPartner:
            self.CALLpartner[self.CALLtotal - 1] = self.CALLpartnerText
            self.CALLpartnerText = ''
            self.CALLinPartner = False

        if self.CALLinDirection:
            self.CALLdirection[self.CALLtotal - 1] = self.CALLdirectionText
            self.CALLdirectionText = ''
            self.CALLinDirection = False

        if self.CALLinTimeStamp:
            self.CALLtimeStamp[self.CALLtotal - 1] = self.CALLtimeStampText
            self.CALLtimeStampText = ''
            self.CALLinTimeStamp = False

        if self.CALLinDuration:
            self.CALLduration[self.CALLtotal - 1] = self.CALLdurationText
            self.CALLdurationText = ''
            self.CALLinDuration = False

        if self.CALLinSource:
            self.CALLsource[self.CALLtotal - 1] = self.CALLsourceText
            self.CALLsourceText = ''
            self.CALLinSource = False

        if self.CALLinLocation:
            self.CALLlocation[self.CALLtotal - 1] = self.CALLlocationText
            self.CALLlocationText = ''
            self.CALLinLocation = False

        if self.CALLinRecoveryMethod:
            self.CALLrecoveryMethod.append(self.CALLrecoveyMethodText)
            self.CALLrecoveyMethodText = ''
            self.CALLinRecoveryMethod = False

    def __endElementFragmentCHAT(self):
        if self.CHATinSender:
            self.CHATsender[self.CHATtotal - 1] = self.CHATsenderText
            self.CHATsenderText = ''
            self.CHATinSender = False
        
        if self.CHATinReceiver:
            self.CHATreceiver[self.CHATtotal - 1] = self.CHATreceiverText
            #print('CHATapplication: ' + self.CHATapplicationText + 
            #    ', CHATreceiver: ' + self.CHATreceiverText)
            self.CHATreceiverText = ''
            self.CHATinReceiver = False

        if self.CHATinPartner:
            self.CHATinPartner = False

        if self.CHATinDateTimeSent:
            self.CHATinDateTimeSent = False

        if self.CHATinDateTime:                        
            #self.CHATdateTimeText = ''
            self.CHATinDateTime = False

        if self.CHATinDateTimeReceived:
            self.CHATdateTimeReceived[self.CHATtotal - 1] = self.CHATdateTimeReceivedText
            self.CHATdateTimeReceivedText = ''
            self.CHATinDateTimeReceived = False

        if self.CHATinMessage:
            self.CHATmessage[self.CHATtotal - 1] = self.CHATmessageText
            self.CHATmessageText = ''
            self.CHATinMessage = False

        if self.CHATinMessageStatus:
            self.CHATmessageStatus[self.CHATtotal - 1] = self.CHATmessageStatusText
            self.CHATmessageStatusText = ''
            self.CHATinMessageStatus = False

        if self.CHATinMessageType:
            if self.CHATmessageTypeText.lowercase() == 'incoming':
                self.CHATdateTimeReceived[self.CHATtotal - 1] = self.CHATdateTimeText    
            if self.CHATmessageTypeText.lowercase() == 'outgoing':
                self.CHATdateTimeSent[self.CHATtotal - 1] = self.CHATdateTimeText    

            self.CHATdateTimeText = ''
            self.CHATinMessageType = False

        if self.CHATinSource:
            self.CHATsource[self.CHATtotal - 1] = self.CHATsourceText
            self.CHATsourceText = ''
            self.CHATinSource = False

        if self.CHATinLocation:
            self.CHATlocation[self.CHATtotal - 1] = self.CHATlocationText
            self.CHATlocationText = ''
            self.CHATinLocation = False

        if self.CHATinRecoveryMethod:
            self.CHATrecoveryMethod[self.CHATtotal - 1] = self.CHATrecoveryMethodText
            self.CHATrecoveryMethodText = ''
            self.CHATinRecoveryMethod = False
#---    this is the last element to be processed for a CHAT, so it's possible to
#       manage 1) iOS Whatsapp Message that contains only the Message Date/Time that can
#       be for sent or received Message; 2) Telegram Messagge that contain only the
#       Creation Date/Time of the Message and the Partner so the Sender and the Receiver
#       must be determined on the base of the Message Type (incoming or outgoing)
#           
            if self.CHATdateTimeText != '':
                if self.CHATmessageTypeText.lower() == 'incoming':
                    self.CHATdateTimeReceived[self.CHATtotal - 1] = self.CHATdateTimeText
                    self.CHATdateTimeSent[self.CHATtotal - 1] = ''
                else:
                    self.CHATdateTimeSent[self.CHATtotal - 1] = self.CHATdateTimeText
                    self.CHATdateTimeReceived[self.CHATtotal - 1] = ''
                self.CHATdateTimeText = ''

            if self.CHATpartnerText != '':
                if self.CHATmessageTypeText.lower() == 'incoming':
                    self.CHATsender[self.CHATtotal - 1] = self.CHATapplicationText + \
                    ' - ' + self.CHATpartnerText
                    self.CHATreceiver[self.CHATtotal - 1] = self.CALLphoneNumberDevice
                else:
                    self.CHATreceiver[self.CHATtotal - 1] = self.CHATapplicationText + \
                    ' - ' + self.CHATpartnerText
                    self.CHATsender[self.CHATtotal - 1] = self.CALLphoneNumberDevice
                self.CHATpartnerText = ''
                


    def __endElementFragmentCONTACT(self):
        if self.CONTACTinName:
            self.CONTACTname[self.CONTACTtotal - 1] = self.CONTACTnameText
            self.CONTACTnameText = ''
            self.CONTACTinName = False

        if self.CONTACTinPhoneNumber:
            self.CONTACTphoneNumber[self.CONTACTtotal - 1] = self.CONTACTphoneNumberText
            self.CONTACTphoneNumberText = ''
            self.CONTACTinPhoneNumber = False

        if self.CONTACTinSource:
            self.CONTACTsource[self.CONTACTtotal - 1] = self.CONTACTsourceText
            self.CONTACTsourceText = ''
            self.CONTACTinSource = False

        if self.CONTACTinLocation:
            self.CONTACTlocation[self.CONTACTtotal - 1] = self.CONTACTlocationText
            self.CONTACTlocationText = ''
            self.CONTACTinLocation = False

        if self.CONTACTinRecoveryMethod:
            self.CONTACTrecoveryMethod[self.CONTACTtotal - 1] = self.CONTACTrecoveryMethodText
            self.CONTACTrecoveryMethodText = ''
            self.CONTACTinRecoveryMethod = False

    def __endElementFragmentDEVICE(self):
        if self.DEVICEinSerialNumber:            
            self.DEVICEinSerialNumber = False
        if self.DEVICEinName:
            self.DEVICEinName = False


    def __endElementFragmentEMAIL(self):
        if self.EMAILinSender:
            self.EMAILsender[self.EMAILtotal - 1] = self.EMAILsenderText
            self.EMAILsenderText = ''
            self.EMAILinSender = False
        
        if self.EMAILinRecipients:
            self.EMAILrecipient[self.EMAILtotal - 1] = self.EMAILrecipientText
            self.EMAILrecipientText = ''
            self.EMAILinRecipients = False
        
        if self.EMAILinCC:
            self.EMAILcc[self.EMAILtotal - 1] = self.EMAILccText
            self.EMAILccText = ''
            self.EMAILinCC = False

        if self.EMAILinBCC:
            self.EMAILbcc[self.EMAILtotal - 1] = self.EMAILbccText
            self.EMAILbccText = ''
            self.EMAILinBCC = False

        if self.EMAILinDateTime:
#---    Some Artifcats have the Sent and the Received Date/Time, one of them
#       is always empty
#            
            if self.EMAILdateTimeText != '':
                self.EMAILdateTime[self.EMAILtotal - 1] = self.EMAILdateTimeText
            self.EMAILdateTimeText = ''
            self.EMAILinDateTime = False

        if self.EMAILinSubject:
            self.EMAILsubject[self.EMAILtotal - 1] = self.EMAILsubjectText
            self.EMAILsubjectText = ''
            self.EMAILinSubject = False

        if self.EMAILinBody:
            self.EMAILbody[self.EMAILtotal - 1] = self.EMAILbodyText
            self.EMAILbodyText = ''
            self.EMAILinBody = False

        if self.EMAILinAttachment:
            self.EMAILattachment[self.EMAILtotal - 1] = self.EMAILattachmentText
            self.EMAILattachmentText = ''
            self.EMAILinAttachment = False

        if self.EMAILinSource:
            self.EMAILsource[self.EMAILtotal - 1] = self.EMAILsourceText
            self.EMAILsourceText = ''
            self.EMAILinSource = False

        if self.EMAILinLocation:
            self.EMAILlocation[self.EMAILtotal - 1] = self.EMAILlocationText
            self.EMAILlocationText = ''
            self.EMAILinLocation = False

        if self.EMAILinRecoveryMethod:
            self.EMAILrecoveryMethod[self.EMAILtotal - 1] = self.EMAILrecoveryMethodText
            self.EMAILrecoveryMethodText = ''
            self.EMAILinRecoveryMethod = False

    def __endElementFragmentFILE(self):
        if self.FILEinTag:
            self.FILEtag[self.FILEtotal - 1] =  self.FILEtagText
            self.FILEtagText = ''
            self.FILEinTag = False

        if self.FILEinFileName:
            if self.FILEfileName[self.FILEtotal - 1] == 'EMPTY':
                self.FILEfileName[self.FILEtotal - 1] =  self.FILEfileNameText
                self.FILEfileNameText = self.FILEfileNameText.replace('\\', '/')
                last_slash = self.FILEfileNameText.rfind('/')
                fileName = self.FILEfileNameText
                
                if last_slash > -1:
                    fileName  = self.FILEfileNameText[last_slash + 1:]

                
                self.FILEfileLocalPath[self.FILEtotal - 1] =  self.FILEbaseLocalPath + \
                    fileName
            self.FILEfileNameText = ''
            self.FILEinFileName = False 

        if self.FILEinImage:
            self.FILEimage[self.FILEtotal - 1] =  self.FILEimageText
            self.FILEimageText = self.FILEimageText.replace('\\', '/')
            last_slash = self.FILEimageText.rfind('/')
            fileName = ''
            if last_slash > -1:
                fileName  = self.FILEimageText[last_slash + 1:]

            self.FILEfileLocalPath[self.FILEtotal - 1] =  self.FILEbaseLocalPath + \
                fileName
            self.FILEimageText = ''
            self.FILEinImage = False 

        if self.FILEinFileExtension:
            self.FILEfileExtension[self.FILEtotal - 1] =  self.FILEfileExtensionText
            self.FILEfileExtensionText = ''
            self.FILEinFileExtension = False 

        if self.FILEinFileSize:
            self.FILEfileSize[self.FILEtotal - 1] =  self.FILEfileSizeText
            self.FILEfileSizeText = ''
            self.FILEinFileSize = False 

        if self.FILEinCreated:
            self.FILEcreated[self.FILEtotal - 1] =  self.FILEcreatedText
            self.FILEcreatedText = ''
            self.FILEinCreated = False 

        if self.FILEinModified:
            self.FILEmodified[self.FILEtotal - 1] =  self.FILEmodifiedText
            self.FILEmodifiedText = ''
            self.FILEinModified = False 

        if self.FILEinAccessed:
            self.FILEaccessed[self.FILEtotal - 1] =  self.FILEaccessedText
            self.FILEaccessedText = ''
            self.FILEinAccessed = False 

        if self.FILEinMD5:
            self.FILEmd5[self.FILEtotal - 1] =  self.FILEmd5Text
            self.FILEmd5Text = ''
            self.FILEinMD5 = False 

        if self.FILEinSource:
            self.FILEsource[self.FILEtotal - 1] =  self.FILEsourceText
            self.FILEsourceText = ''
            self.FILEinSource = False 

        if self.FILEinLocation:
            self.FILElocation[self.FILEtotal - 1] =  self.FILElocationText
            self.FILElocationText = ''
            self.FILEinLocation = False 

        if self.FILEinRecoveryMethod:
            self.FILErecoveryMethod[self.FILEtotal - 1] =  self.FILErecoveryMethodText
            self.FILErecoveryMethodText = ''
            self.FILEinRecoveryMethod = False 

    def __endElementFragmentSMS(self):
        if self.SMSinPartner:
            self.SMSinPartner = False

        if self.SMSinRecipient:
            self.SMSrecipient[self.SMStotal - 1] = self.SMSrecipientText        
            self.SMSrecipientText = ''
            self.SMSinRecipient = False

        if self.SMSinSender:
            self.SMSsender[self.SMStotal - 1] = self.SMSsenderText        
            self.SMSsenderText = ''
            self.SMSinSender = False

        if self.SMSinReceivedDateTime:
            self.SMSreceivedDateTime[self.SMStotal - 1] = self.SMSreceivedDateTimeText        
            self.SMSreceivedDateTimeText = ''
            self.SMSinReceivedDateTime = False

        if self.SMSinSentDateTime:
            self.SMSsentDateTime[self.SMStotal - 1] = self.SMSsentDateTimeText        
            self.SMSsentDateTimeText = ''
            self.SMSinSentDateTime = False

        if self.SMSinMessage:
            self.SMSmessage[self.SMStotal - 1] = self.SMSmessageText        
            self.SMSmessageText = ''
            self.SMSinMessage = False

        if self.SMSinDirection:
            self.SMSinDirection = False

        if self.SMSinSource:
            self.SMSsource[self.SMStotal - 1] = self.SMSsourceText
            self.SMSsourceText = ''
            self.SMSinSource = False

        if self.SMSinLocation:
            self.SMSlocation[self.SMStotal - 1] = self.SMSlocationText
            self.SMSlocationText = ''
            self.SMSinLocation = False

        if self.SMSinRecoveryMethod:
            self.SMSrecoveryMethod[self.SMStotal - 1] = self.SMSrecoveryMethodText
            self.SMSrecoveryMethodText = ''
            self.SMSinRecoveryMethod = False
            
            if self.SMSpartnerText != '':
                if self.SMSdirectionText.lower() == 'incoming':                    
                    self.SMSsender[self.SMStotal - 1] = self.SMSpartnerText
                    self.SMSrecipient[self.SMStotal - 1] = self.CALLphoneNumberDevice
                else:
                    self.SMSsender[self.SMStotal - 1] = self.CALLphoneNumberDevice
                    self.SMSrecipient[self.SMStotal - 1] = self.SMSpartnerText
                self.SMSpartnerText = ''
            else:
#---    for iOS iMessage/SMS/MMS only the Message Sent Date/Time is set, so in case
#       the message has been received the Data value is referred to the receeiving Date
#                
                if self.SMSdirectionText.lower() == 'incoming':
                    self.SMSreceivedDateTime[self.SMStotal - 1] = self.SMSsentDateTimeText
                    self.SMSsentDateTime[self.SMStotal - 1] = 'EMPTY'
                    self.SMSrecipient[self.SMStotal - 1] = 'Local user'
                else:
                    self.SMSsender[self.SMStotal - 1] = 'Local user'
                self.SMSdirectionText = ''

    def __endElementFragmentWEB(self):
        if self.WEBinUrl:
            self.WEBurl[self.WEBtotal - 1] = self.WEBurlText        
            self.WEBurlText = ''
            self.WEBinUrl = False

        if self.WEBinLastVisited:
            self.WEBlastVisited[self.WEBtotal - 1] = self.WEBlastVisitedText        
            self.WEBlastVisitedText = ''
            self.WEBinLastVisited = False

        if self.WEBinTitle:
            self.WEBtitle[self.WEBtotal - 1] = self.WEBtitleText        
            self.WEBtitleText = ''
            self.WEBinTitle = False

        if self.WEBinVisitCount:
            self.WEBvisitCount[self.WEBtotal - 1] = self.WEBvisitCountText        
            self.WEBvisitCountText = ''
            self.WEBinVisitCount = False

        if self.WEBinSource:
            self.WEBsource[self.WEBtotal - 1] = self.WEBsourceText
            self.WEBsourceText = ''
            self.WEBinSource = False

        if self.WEBinLocation:
            self.WEBlocation[self.WEBtotal - 1] = self.WEBlocationText
            self.WEBlocationText = ''
            self.WEBinLocation = False

        if self.WEBinRecoveryMethod:
            self.WEBrecoveryMethod[self.WEBtotal - 1] = self.WEBrecoveryMethodText
            self.WEBrecoveryMethodText = ''
            self.WEBinRecoveryMethod = False


#    It captures each Element when it is closed
    def endElement(self, name):
        #print('END element ' + name + ', ' + str(self.lineXML))
        if name == 'Fragment':
            self.__endElementFragmentPHONE_NUM()
            if self.CALLin:
                self.__endElementFragmentCALL()
            if self.CHATin:
                self.__endElementFragmentCHAT()
            if self.CONTACTin:
                self.__endElementFragmentCONTACT()
            if self.DEVICEin:
                self.__endElementFragmentDEVICE()
            if self.FILEin:
                self.__endElementFragmentFILE()
            if self.EMAILin:
                self.__endElementFragmentEMAIL()
            if self.SMSin:
                self.__endElementFragmentSMS()
            if self.WEBin:
                self.__endElementFragmentWEB()            

        if name == 'Hit':
            if self.inHit:
                self.inHit = False

        if name == 'Artifact':
            if self.CALLin:
                self.CALLin = False
                self.Observable = False

            if self.CALL_PHONE_NUM_DEVICEin:
                self.CALL_PHONE_NUM_DEVICEin = False
                self.Observable = False

            if self.CHATin:
                self.CHATin = False
                self.Observable = False

            if self.CONTACTin:
                self.CONTACTin = False
                self.Observable = False

            if self.EMAILin:
                self.EMAILin = False
                self.Observable = False

            if self.FILEin:
                self.FILEin = False
                self.Observable = False
            
            if self.SMSin:
                self.SMSin = False
                self.Observable = False 

            if self.WEBin:
                self.WEBin = False
                self.Observable = False                

#---    it captures the value/character inside the Text Elements
    def characters(self, ch):        
#---    CALL processing
#        
        if self.CALLin:
            if self.CALLinPartner:
                self.CALLpartnerText += ch
            if self.CALLinDirection:
                self.CALLdirectionText += ch
            if self.CALLinTimeStamp:
                self.CALLtimeStampText += ch
            if self.CALLinDuration:
                self.CALLdurationText += ch
            if self.CALLinSource:
                self.CALLsourceText += ch
            if self.CALLinLocation:
                self.CALLlocationText += ch
            if self.CALLinRecoveryMethod:
                self.CALLrecoveyMethodText += ch

        if self.CALL_PHONE_NUM_DEVICE_VALUEin:            
            self.CALLphoneNumberDevice += ch

        if self.CALL_PHONE_NAME_DEVICE_VALUEin:            
            self.CALLphoneNameDevice += ch

#---    CHAT processing
#        
        if self.CHATin:
            if self.CHATinSender:
                self.CHATsenderText += ch
            if self.CHATinReceiver:
                self.CHATreceiverText += ch
            if self.CHATinPartner:
                self.CHATpartnerText += ch
            if self.CHATinDateTimeSent:
                self.CHATdateTimeSentText += ch
            if self.CHATinDateTimeReceived:
                self.CHATdateTimeReceivedText += ch
            if self.CHATinDateTime:
                self.CHATdateTimeText += ch
            if self.CHATinMessage:
                self.CHATmessageText += ch
            if self.CHATinMessageStatus:
                self.CHATmessageStatusText += ch
            if self.CHATinMessageType:
                self.CHATmessageTypeText += ch
            if self.CHATinSource:
                self.CHATsourceText += ch
            if self.CHATinLocation:
                self.CHATlocationText += ch
            if self.CHATinRecoveryMethod:
                self.CHATrecoveryMethodText += ch

#---    CONTACT processing
#        
        if self.CONTACTin:
            if self.CONTACTinName:
                self.CONTACTnameText += ch
            if self.CONTACTinPhoneNumber:
                self.CONTACTphoneNumberText += ch
            if self.CONTACTinSource:
                self.CONTACTsourceText += ch
            if self.CONTACTinLocation:
                self.CONTACTlocationText += ch
            if self.CONTACTinRecoveryMethod:
                self.CONTACTrecoveryMethodText += ch

#---    DEVICE processing
#        
        if self.DEVICEin:
            if self.DEVICEinSerialNumber:
                if self.DEVICEserialNumberText == '':
                    self.DEVICEserialNumberText += ch
            if self.DEVICEinName:
                if self.DEVICEnameText == '':
                    self.DEVICEnameText += ch

#---    EMAIL processing
#        
        if self.EMAILin:
            if self.EMAILinSender:
                self.EMAILsenderText += ch
            if self.EMAILinRecipients:
                self.EMAILrecipientText += ch
            if self.EMAILinCC:
                self.EMAILccText += ch
            if self.EMAILinBCC:
                self.EMAILbccText += ch
            if self.EMAILinDateTime:
                self.EMAILdateTimeText += ch
            if self.EMAILinSubject:
                self.EMAILsubjectText += ch
            if self.EMAILinBody:
                self.EMAILbodyText += ch
            if self.EMAILinAttachment:
                self.EMAILattachmentText += ch
            if self.EMAILinSource:
                self.EMAILsourceText += ch
            if self.EMAILinLocation:
                self.EMAILlocationText += ch
            if self.EMAILinRecoveryMethod:
                self.EMAILrecoveryMethodText += ch

#---    FILE processing
#        
        if self.FILEin:
            if self.FILEinTag:
                self.FILEtagText += ch

            if self.FILEinFileName:
                self.FILEfileNameText += ch

            if self.FILEinImage:
                self.FILEimageText += ch

            if self.FILEinFileExtension:
                self.FILEfileExtensionText += ch

            if self.FILEinFileSize:
                self.FILEfileSizeText += ch

            if self.FILEinCreated:
                self.FILEcreatedText += ch

            if self.FILEinModified:
                self.FILEmodifiedText += ch

            if self.FILEinAccessed:
                self.FILEaccessedText += ch

            if self.FILEinMD5:
                self.FILEmd5Text += ch

            if self.FILEinSource:
                self.FILEsourceText += ch

            if self.FILEinLocation:
                self.FILElocationText += ch

            if self.FILEinRecoveryMethod:
                self.FILErecoveryMethodText += ch

#---    SMS processing
#        
        if self.SMSin:
            if self.SMSinPartner:
                self.SMSpartnerText += ch

            if self.SMSinRecipient:
                self.SMSrecipientText += ch

            if self.SMSinSender:
                self.SMSsenderText += ch

            if self.SMSinReceivedDateTime:
                self.SMSreceivedDateTimeText += ch

            if self.SMSinSentDateTime:
                self.SMSsentDateTimeText += ch

            if self.SMSinMessage:
                self.SMSmessageText += ch

            if self.SMSinDirection:
                self.SMSdirectionText += ch

            if self.SMSinSource:
                self.SMSsourceText += ch

            if self.SMSinLocation:
                self.SMSlocationText += ch

            if self.SMSinRecoveryMethod:
                self.SMSrecoveryMethodText += ch

#---    WEB_HISTORY processing
#        
        if self.WEBin:
            if self.WEBinUrl:
                self.WEBurlText += ch

            if self.WEBinLastVisited:
                self.WEBlastVisitedText += ch

            if self.WEBinTitle:
                self.WEBtitleText += ch

            if self.WEBinVisitCount:
                self.WEBvisitCountText += ch

            if self.WEBinSource:
                self.WEBsourceText += ch

            if self.WEBinLocation:
                self.WEBlocationText += ch

            if self.WEBinRecoveryMethod:
                self.WEBrecoveryMethodText += ch                


if __name__ == '__main__':

#--- debug: ctime processing
#
    tic=timeit.default_timer()

    parserArgs = argparse.ArgumentParser(description='Parser to convert XML Report from AXIOM Process into CASE-JSON-LD standard.')

#---    report XML exported by AXIOM to be converted/parsed into CASE
#
    parserArgs.add_argument('-r', '--report', dest='inFileXML', required=True, 
                    help='The AXIOM XML report from which to extract digital traces and convert them into CASE; it supports AXIOM Process version from 3.4 to 4.01')


#---    Type of device mobile or disk (HD, USB, SD, etc)
#
    parserArgs.add_argument('-e', '--evidence', type=str, dest='inTypeEvidence', 
	               required=True, choices=['mobile', 'disk',], 
	               help="Type of Evidence to be processed, default mobile", default='mobile')

    parserArgs.add_argument('-o', '--output', dest='outCASE_JSON', required=True, help='File CASE-JSON-LD of output')

    parserArgs.add_argument('-d', '--debug', dest='outputDebug', required=False, help='File for writing debug')

    args = parserArgs.parse_args()




    print('*--- Input paramaters start \n')
    print('\tFile XML:\t\t' + args.inFileXML)

    print('\tType of Evidence:\t' + args.inTypeEvidence)

    head, tail = os.path.split(args.outCASE_JSON)
    print('\tFile Output:\t\t' + args.outCASE_JSON)

    if args.outputDebug is None:
        pass
    else:
        print('\tFile Debug:\t\t' + args.outputDebug)

    print('\n*--- Input paramaters end')
    print('\n\n*** Start processing\n')

#---    baseLocalPath is for setting the fileLocalPath property of FileFacet 
#       Observable. 
#    
    baseLocalPath = ''

    gadget = AXIOMgadget(args.inFileXML, args.outCASE_JSON, args.inTypeEvidence, baseLocalPath)    
    
    Handler = gadget.processXmlReport()
    

    if args.outputDebug is None:
        pass
    else:
        import AXIOMdebug
        debug = AXIOMdebug.ParserDebug(args.outputDebug)
        debug.writeDebugCALL(Handler)
        debug.writeDebugCHAT(Handler)
        debug.writeDebugCONTACT(Handler)
        debug.writeDebugFILE(Handler)
        debug.writeDebugEMAIL(Handler)
        debug.writeDebugSMS(Handler)
        debug.writeDebugWEB(Handler)
        debug.closeDebug() 


    

    toc=timeit.default_timer()
    elapsedTime = round(toc - tic, 2)
    (ss, ms) = divmod(elapsedTime, 1)
    elapsedMm = str(int(ss) // 60)
    elapsedSs = str(int(ss) % 60)
    elapsedMs = str(round(ms, 2))[2:]
    elapsedTime = elapsedMm + ' min. ' +  elapsedSs + ' sec. and ' + \
    elapsedMs + ' hundredths'
    print(Handler.C_green + '\n*** End processing, elapsed time: ' + \
        elapsedTime + '\n\n' + Handler.C_end)
# else:    
#     xmlFile = '../CASE-dataset.xml.reports/AXIOM/ANDROID/19_AXIOM_ANDROID_CROSSOVER.xml'
#     jsonFile = './_19-AXIOM-gadget.json'   
#     print("start XML processing " + jsonFile)     
#     gadget = AXIOMgadget(xmlFile, jsonFile, 'mobile')
#     gadget.processXmlReport()
#     print("end XML processing, created " + jsonFile)     
