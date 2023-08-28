#
#	xml_sax_UFED_to_CASE: UFED  SAX parser from XML report to CASE-JSON-LD 
#

import xml.sax
import argparse
import os
import codecs
import AXIOMtoJSON as CJ
#from inspectrutils.case_builder import *
import timeit
from time import localtime, strftime
# import logging


class AXIOMparser():
	'''
	It represents all attributes and methods to process the traces extracted from XML reports by using
	the SAX parser.
	'''    
	def __init__(self, report_xml=None, json_output=None, report_type=None, 
	             base_local_path="", case_bundle=None, verbose=False):
		'''
		It initialises the main attributes for processing the XML report.
		    :param report_xml: The filename of the XML report, provided as argumnent in the command line (string).
		    :param json_output: The filename of the JSON-LD to be generated, provided as argumnent in the command line (string).
		    :param case_bundle: The container of all Objects in the JSON-LD file (list).
		    :param mode_verbose: True if the processing progress will be shown in the standard output (boolean).
		'''         
		self.xmlReport = report_xml
		self.jsonCASE = json_output
		self.reportType = report_type
		self.baseLocalPath = os.path.join(base_local_path,  'Attachments')
		self.tic_start = timeit.default_timer()
		self.bundle = case_bundle
		self.verbose = verbose
		# logging.basicConfig(filename='_axiom_log.txt', level=logging.INFO,
		#     filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
		# logging.basicConfig(filename='_ufed_log.txt', level=logging.INFO,
		#    filemode='w', format='%(message)s')

	def show_elapsed_time(self, tic, message):
		'''
		It shows the processing time gone.
		    :param tic: The initial time for calculating the processing time passed (float).
		    :param message: The message to be shown (string).
		    :return: None.
		'''           
		toc = timeit.default_timer()
		C_CYAN = '\033[36m'
		C_BLACK = '\033[0m'
		elapsed_seconds = round(toc - tic, 2)
		(ss, ms) = divmod(elapsed_seconds, 1)
		elapsedMm = str(int(ss) // 60)
		elapsedSs = str(int(ss) % 60)
		elapsedMs = str(round(ms, 2))[2:]
		elapsed_time = elapsedMm + ' min. ' +  elapsedSs + ' sec. and ' + \
		    elapsedMs + ' hundredths'
		if self.verbose:
			print('\n' + C_CYAN + 'elapsed time - ' + message + ': ' + elapsed_time + '\n' + C_BLACK)

	def processXmlReport(self):
		'''
		It implements the SAX parser overriding the default ContextHandler method.
		    :return: Handler of the JSON-LD file created.
		'''        
		SAXparser = xml.sax.make_parser()    
		Handler = ExtractTraces(self.baseLocalPath, self.verbose)
		Handler.createOutFile(self.jsonCASE)
		SAXparser.setContentHandler(Handler)
		SAXparser.parse(self.xmlReport)

		self.show_elapsed_time(self.tic_start, 'Extraction Traces')

		if self.verbose:
			print('\n\n\nCASE JSON-LD file is being generated ...')

		tic_case_start = timeit.default_timer()

		if self.reportType == 'mobile':
			if self.verbose:
				print("".join([Handler.C_cyan, "owner's phone number / name: ", Handler.CALLphoneNumberDevice,
					' / ', Handler.CALLphoneNameDevice,  '\n', Handler.C_end]))

		#---    create object and open JSON file and define the boolean value that
		#       indicates if the line with comma plus return must be written before
		#       writing the next ObservableObject   
		caseTrace = CJ.AXIOMtoJSON(json_output=Handler.fOut, case_bundle=self.bundle)

		#---    write CASE @context, version and description JSON file
		caseTrace.writeHeader()

		#---    write phoneAccountFacet for the device phone number
		if self.reportType == 'mobile':
			caseTrace.writeDeviceMobile(Handler.DEVICEidText, Handler.DEVICEimsiText,
				                        Handler.DEVICEbluetoothAddressText, Handler.DEVICEbluetoothNameText, 
				Handler.DEVICEimeiText, Handler.DEVICEserialNumberText, 
				Handler.DEVICEnameText, Handler.DEVICEmodelText, Handler.DEVICEiccidText, 
				Handler.DEVICEosVersionText)
			caseTrace.writePhoneOwner(Handler.CALLphoneNumberDevice, 
				                      Handler.CALLphoneNameDevice)
			caseTrace.writePhoneAccountFromContacts(Handler.CONTACTname, 
				                                    Handler.CONTACTphoneNumber)
		else:
			caseTrace.writeDeviceDisk(Handler.FILE_SYS_INFOvolumeSn, 
				                      Handler.FILE_SYS_INFOfileSystem, Handler.FILE_SYS_INFOcapacity,
				Handler.FILE_SYS_INFOunallocated, Handler.FILE_SYS_INFOallocated,
				Handler.FILE_SYS_INFOoffset)

		caseTrace.writeFiles(Handler.FILEid, Handler.FILEtag, Handler.FILEfileName,
						 Handler.FILEfileLocalPath, Handler.FILEimage, Handler.FILEfileSize,
			Handler.FILEcreated, Handler.FILEmodified, Handler.FILEaccessed, 
			Handler.FILEmd5, Handler.FILEexifMake, Handler.FILEexifModel,
			Handler.FILEexifLatitudeRef, Handler.FILEexifLatitude, 
			Handler.FILEexifLongitudeRef, Handler.FILEexifLongitude, Handler.FILEexifAltitude,
			Handler.FILEsource, Handler.FILElocation, 
			Handler.FILErecoveryMethod)            

		if self.reportType == 'mobile':
			caseTrace.writeCall(Handler.CALLid, Handler.CALLappName, Handler.CALLtimeStamp, 
				                Handler.CALLdirection, Handler.CALLduration, Handler.CALLpartner, 
				    Handler.CALLpartnerName, Handler.CALLsource, Handler.CALLlocation, 
				    Handler.CALLrecoveryMethod)
			caseTrace.writeCell_Tower(Handler.CELL_TOWERid, Handler.CELL_TOWERmcc,
				                      Handler.CELL_TOWERmnc, Handler.CELL_TOWERlac, Handler.CELL_TOWERcid, 
				Handler.CELL_TOWERlongitude,Handler.CELL_TOWERlatitude,
				Handler.CELL_TOWERtimeStamp,  Handler.CELL_TOWERsource, 
				Handler.CELL_TOWERlocation, Handler.CELL_TOWERrecoveryMethod)

			caseTrace.writeWireless_Net(Handler.WIRELESS_NETid, Handler.WIRELESS_NETmacAddress,
				                        Handler.WIRELESS_NETchannel, Handler.WIRELESS_NETlongitude, 
				Handler.WIRELESS_NETlatitude, Handler.WIRELESS_NETtimeStamp,  
				Handler.WIRELESS_NETaccuracy, Handler.WIRELESS_NETsource, 
				Handler.WIRELESS_NETlocation, Handler.WIRELESS_NETrecoveryMethod)

			caseTrace.writeDeviceEvent(Handler.EVENT_LOCKid, Handler.EVENT_LOCKdeviceStatus, 
				                       Handler.EVENT_LOCKdateTime, Handler.EVENT_LOCKsource, 
				Handler.EVENT_LOCKlocation, Handler.EVENT_LOCKrecoveryMethod)

			caseTrace.writeAppUsage(Handler.EVENT_APP_USEid, Handler.EVENT_APP_USEapplication, 
				                    Handler.EVENT_APP_USEstartTime, Handler.EVENT_APP_USEendTime,
				Handler.EVENT_APP_USEsource, Handler.EVENT_APP_USElocation, 
				Handler.EVENT_APP_USErecoveryMethod)

		caseTrace.writeSearched_Item(Handler.SEARCHED_ITEMid, Handler.SEARCHED_ITEMvalue,
								 Handler.SEARCHED_ITEMtimeStamp, Handler.SEARCHED_ITEMappSource, 
			Handler.SEARCHED_ITEMsource, Handler.SEARCHED_ITEMlocation, 
			Handler.SEARCHED_ITEMrecoveryMethod)

		caseTrace.writeSms(Handler.SMSid, Handler.SMSsender,
				           Handler.SMSrecipient, Handler.SMSreceivedDateTime, 
				Handler.SMSsentDateTime, Handler.SMSmessage, Handler.SMSdirection, 
				Handler.SMSsource, Handler.SMSlocation, Handler.SMSrecoveryMethod)

		caseTrace.writeChat(Handler.CHATid, Handler.CHATsender, Handler.CHATreceiver, 
				            Handler.CHATdateTimeSent, Handler.CHATdateTimeReceived, 
				        Handler.CHATmessage, Handler.CHATmessageStatus, 
				        Handler.CHATapplication, Handler.CHATsource,
				        Handler.CHATlocation, Handler.CHATrecoveryMethod)

		caseTrace.writeCookie(Handler.COOKIEid, Handler.COOKIEappSource, Handler.COOKIEname, 
				              Handler.COOKIEpath, Handler.COOKIEdomain, Handler.COOKIEcreatedDate, 
				        Handler.COOKIEaccessedDate, Handler.COOKIEexpirationDate, 
				        Handler.COOKIEsource, Handler.COOKIElocation, Handler.COOKIErecoveryMethod)

		caseTrace.writeEmail(Handler.EMAILid, Handler.EMAILappSource, Handler.EMAILsender, 
				             Handler.EMAILrecipient, Handler.EMAILcc, Handler.EMAILbcc, 
				        Handler.EMAILbody, Handler.EMAILsubject, Handler.EMAILdateTime, 
				        Handler.EMAILattachment, Handler.EMAILsource, 
				        Handler.EMAILlocation, Handler.EMAILrecoveryMethod)        

		caseTrace.writeWinTimeline(Handler.WIN_TIMELINEid, Handler.WIN_TIMELINEappName, 
				                   Handler.WIN_TIMELINEactivityType, Handler.WIN_TIMELINEtimeStamp, 
				       Handler.WIN_TIMELINEsource, Handler.WIN_TIMELINElocation, 
				       Handler.WIN_TIMELINErecoveryMethod)

		caseTrace.writeLocationDevice(Handler.LOCATIONid, Handler.LOCATIONtype, 
			Handler.LOCATIONlatitude, Handler.LOCATIONlongitude, Handler.LOCATIONcreated,
			Handler.LOCATIONsource, Handler.LOCATIONlocation) 

		caseTrace.writeWebPages(Handler.WEBid, Handler.WEBappSource, 
			Handler.WEBurl, Handler.WEBtitle, Handler.WEBvisitCount,
			Handler.WEBlastVisited, Handler.WEBsource, 
			Handler.WEBlocation, Handler.WEBrecoveryMethod)

		#--- JSON final line
		caseTrace.writeLastLine()
		self.show_elapsed_time(tic_case_start, 'Generation CASE JSON-LD file')
		Handler.fOut.close()

		return Handler

class ExtractTraces(xml.sax.ContentHandler):
	'''
	Used to extract the Traces from the XML reports and fill in the appropriate structure before generatign the JSON-LD file.
	''' 	
	def __init__(self, baseLocalPath, verbose):
		self.fOut = ''
		self.lineXML = 0

		self.skipLine = False
		self.verbose = verbose
		self.inHit = False
		self.Observable = False
		self.C_green  = '\033[32m'
		self.C_grey  = '\033[37m'
		self.C_red = '\033[31m'
		self.C_cyan = '\033[36m'
		self.C_end = '\033[0m'

#---    DEVICE INFO
		self.DEVICE_PATTERN = ('Android Device Information', 'iOS Device Information')
		self.DEVICEin = False
		self.DEVICEinSerialNumber = False
		self.DEVICEinId = False
		self.DEVICEinName = False
		self.DEVICEinImsi = False
		self.DEVICEinBluetoothAddress = False
		self.DEVICEinBluetoothName = False
		self.DEVICEinImei = False
		self.DEVICEinIccid = False
		self.DEVICEinModel = False
		self.DEVICEinOsVersion = False

		self.DEVICEserialNumberText = ''
		self.DEVICEidText = ''
		self.DEVICEnameText = ''
		self.DEVICEimsiText = ''
		self.DEVICEimeiText = ''
		self.DEVICEbluetoothAddressText = ''
		self.DEVICEbluetoothNameText = ''
		self.DEVICEmodelText = ''
		self.DEVICEiccidText = ''
		self.DEVICEosVersionText = ''


#---    CALL  section
		self.CALL_PATTERN = ('Android Call Logs', 'iOS Call Logs')
		self.CALLin = False
		self.CALLinPartner = False
		self.CALLinPartnerName = False
		self.CALLinDirection = False
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
		self.CALLpartnerNameText = ''
		self.CALLdirectionText = ''
		self.CALLtimeStampText = ''
		self.CALLdurationText = ''
		self.CALLsourceText = ''
		self.CALLlocationText = ''
		self.CALLrecoveyMethodText = ''
		self.CALLappNameText = ''
		self.CALLphoneNumberDevice = 'DEVICE_PHONE_NUMBER'
		self.CALLphoneNameDevice = ''

		self.CALLtotal = 0
		self.CALLid = []
		self.CALLappName = []
		self.CALLpartner = []
		self.CALLpartnerName = []
		self.CALLdirection = []        
		self.CALLtimeStamp = []
		self.CALLduration = []
		self.CALLsource = []
		self.CALLlocation = []
		self.CALLrecoveryMethod = []

#---    The CELL TOWER Artifact, Cellsite class in UCO/CASE
		self.CELL_TOWER_PATTERN = ('Cell Tower Locations')
		self.CELL_TOWERin = False
		self.CELL_TOWERinCID= False
		self.CELL_TOWERinLAC= False
		self.CELL_TOWERinMCC= False
		self.CELL_TOWERinMNC = False
		self.CELL_TOWERinTimeStamp = False
		self.CELL_TOWERinLatitude = False
		self.CELL_TOWERinLongitude = False
		self.CELL_TOWERinSource = False
		self.CELL_TOWERinLocation = False
		self.CELL_TOWERinRecoveryMethod = False

		self.CELL_TOWERmccText = ''
		self.CELL_TOWERmncText = ''
		self.CELL_TOWERlacText = ''
		self.CELL_TOWERcidText = ''
		self.CELL_TOWERlongitudeText = ''
		self.CELL_TOWERlatitudeText = ''
		self.CELL_TOWERtimeStampText = ''
		self.CELL_TOWERsourceText =  ''
		self.CELL_TOWERlocationText = ''
		self.CELL_TOWERrecoveryMethodText = ''

		self.CELL_TOWERtotal = 0
		self.CELL_TOWERid = []
		self.CELL_TOWERlongitude = []
		self.CELL_TOWERlatitude = []
		self.CELL_TOWERtimeStamp = []
		self.CELL_TOWERmcc = []
		self.CELL_TOWERmnc = []
		self.CELL_TOWERlac = []
		self.CELL_TOWERcid = []
		self.CELL_TOWERsource = []
		self.CELL_TOWERlocation = []
		self.CELL_TOWERrecoveryMethod = []

#---    CHAT  section
		self.CHAT_PATTERN = ('Android WhatsApp Messages', 'iOS WhatsApp Messages',
			'Android Telegram Messages', 'iOS Telegram Messages', 'iOS Telegram Chats', 
		    'Snapchat Chat Messages', 'TikTok Messages', 'Instagram Direct Messages',
		    'Signal Messages', 'Signal Messages - Windows', 'Signal Messages - iOS', 
		    'Facebook Messenger Messages', 'Discord Messages', 'LINE Messages', 'Skype Activity')
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

#---    CHAT Telegram: fields are different from Whatsapp
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

		self.CONTACT_PATTERN = ('Android Contacts', 'Apple Contacts - iOS')
		self.CONTACTin = False
		self.CONTACTinName = False
		self.CONTACTinFirstName = False
		self.CONTACTinLastName = False
		self.CONTACTinPhoneNumber = False
		self.CONTACTinSource = False
		self.CONTACTinLocation = False
		self.CONTACTinRecoveryMethod = False

		self.CONTACTnameText = ''
		self.CONTACTfirstNameText = ''
		self.CONTACTlastNameText = ''
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

#---    The Artifacts extracted are: Chrome Cookies, 
		self.COOKIE_PATTERN = ('Chrome Cookies', 'Edge Chromium Cookies', 'Firefox Cookies')
		self.COOKIEin = False
		self.COOKIEinName= False
		self.COOKIEinPath= False
		self.COOKIEinDomain = False
		self.COOKIEinCreatedDate = False
		self.COOKIEinAccessedDate = False
		self.COOKIEinExpirationDate = False
		self.COOKIEinSource = False
		self.COOKIEinLocation = False
		self.COOKIEinRecoveryMethod = False

		self.COOKIEappSourceText = ''
		self.COOKIEnameText = ''
		self.COOKIEpathText = ''
		self.COOKIEdomainText = ''
		self.COOKIEcreatedDateText = ''
		self.COOKIEaccessedDateText = ''
		self.COOKIEexpirationDateText = ''
		self.COOKIEsourceText =  ''
		self.COOKIElocationText = ''
		self.COOKIErecoveryMethodText = ''

		self.COOKIEtotal = 0
		self.COOKIEid = []
		self.COOKIEappSource = []
		self.COOKIEname = []
		self.COOKIEpath = []
		self.COOKIEdomain = []        
		self.COOKIEcreatedDate = []
		self.COOKIEaccessedDate = []
		self.COOKIEexpirationDate = []
		self.COOKIEsource = []
		self.COOKIElocation = []
		self.COOKIErecoveryMethod = []

#---    EVENT Artifacts
		self.EVENT_LOCK_PATTERN = ('KnowledgeC Device Lock States')
		self.EVENT_LOCKin = False
		self.EVENT_LOCKinDeviceStatus= False
		self.EVENT_LOCKinDateTime= False
		self.EVENT_LOCKinSource = False
		self.EVENT_LOCKinLocation = False
		self.EVENT_LOCKinRecoveryMethod = False

		self.EVENT_LOCKdeviceStatusText = ''
		self.EVENT_LOCKdateTimeText = ''
		self.EVENT_LOCKsourceText =  ''
		self.EVENT_LOCKlocationText = ''
		self.EVENT_LOCKrecoveryMethodText = ''

		self.EVENT_LOCKtotal = 0
		self.EVENT_LOCKid = []
		self.EVENT_LOCKdeviceStatus = []
		self.EVENT_LOCKdateTime = []
		self.EVENT_LOCKsource = []
		self.EVENT_LOCKlocation = []
		self.EVENT_LOCKrecoveryMethod = []

		self.EVENT_APP_USE_PATTERN = ('KnowledgeC Application Usage')
		self.EVENT_APP_USEin = False
		self.EVENT_APP_USEinApplication= False
		self.EVENT_APP_USEinStartTime= False
		self.EVENT_APP_USEinEndTime= False
		self.EVENT_APP_USEinSource = False
		self.EVENT_APP_USEinLocation = False
		self.EVENT_APP_USEinRecoveryMethod = False

		self.EVENT_APP_USEapplicationText = ''
		self.EVENT_APP_USEstartTimeText = ''
		self.EVENT_APP_USEendTimeText =  ''
		self.EVENT_APP_USEsourceText = ''
		self.EVENT_APP_USElocationText = ''
		self.EVENT_APP_USErecoveryMethodText = ''

		self.EVENT_APP_USEtotal = 0
		self.EVENT_APP_USEid = []
		self.EVENT_APP_USEapplication = []
		self.EVENT_APP_USEstartTime = []
		self.EVENT_APP_USEendTime = []
		self.EVENT_APP_USEsource = []
		self.EVENT_APP_USElocation = []
		self.EVENT_APP_USErecoveryMethod = []

#---    EMAIL Artifacts, not yet extracted: Outlook Emails
		self.EMAIL_PATTERN = ('Apple Mail', 'Gmail Emails', 'Android Emails', 'Apple Mail Fragments')
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

#---    FILE  Artifacts
		self.FILE_PATTERN =('Pictures', 'Videos', 'RTF Documents', 'Excel Documents',
			'PowerPoint Documents', 'Audio', 'PDF Documents', 'Word Documents', 
			'WordPerfect Files', 'Calc Documents', 'Writer Documents', 'Text Documents',
			'CSV Documents', 'Live Photos', 'TikTok Videos')
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
		self.FILEinExifLatitudeRef = False
		self.FILEinExifLatitude = False
		self.FILEinExifLongitudeRef = False
		self.FILEinExifLongitude = False
		self.FILEinExifAltitude = False
		self.FILEinExifMake = False
		self.FILEinExifModel = False
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
		self.FILEexifMakeText = ''
		self.FILEexifModelText = ''
		self.FILEexifLatitudeRefText = ''
		self.FILEexifLatitudeText = ''
		self.FILEexifLongitudeRefText = ''
		self.FILEexifLongitudeText = ''
		self.FILEexifAltitudeText = ''
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
		self.FILEexifMake = []
		self.FILEexifModel = []
		self.FILEexifLatitudeRef = []
		self.FILEexifLatitude = []
		self.FILEexifLongitudeRef = []
		self.FILEexifLongitude = []
		self.FILEexifAltitude = []
		self.FILEsource = []
		self.FILElocation = []
		self.FILErecoveryMethod = []

#---    FILE SYSTEM INFORMATION section (only for HD, USB etc.)
		self.FILE_SYS_INFO_PATTERN = ('File System Information')
		self.FILE_SYS_INFOin = False
		self.FILE_SYS_INFOinVolumeSn = False
		self.FILE_SYS_INFOinFileSystem = False
		self.FILE_SYS_INFOinCapacity = False
		self.FILE_SYS_INFOinUnallocated = False
		self.FILE_SYS_INFOinAllocated = False
		self.FILE_SYS_INFOinOffest = False

		self.FILE_SYS_INFOvolumeSnText = ''
		self.FILE_SYS_INFOfileSystemText = ''
		self.FILE_SYS_INFOcapacityText = ''
		self.FILE_SYS_INFOunallocatedText = ''
		self.FILE_SYS_INFOallocatedText = ''
		self.FILE_SYS_INFOoffsetText = ''

		self.FILE_SYS_INFOtotal = 0
		self.FILE_SYS_INFOid = []
		self.FILE_SYS_INFOvolumeSn = []
		self.FILE_SYS_INFOfileSystem  = []
		self.FILE_SYS_INFOcapacity = []
		self.FILE_SYS_INFOunallocated = []
		self.FILE_SYS_INFOallocated = []
		self.FILE_SYS_INFOoffset = []

#---    Signficant Location (Location Device)
		self.LOCATION_PATTERN = ('Significant Locations')
		self.LOCATIONin = False
		self.LOCATIONinType = False
		self.LOCATIONinCreated = False
		self.LOCATIONinLongitude = False
		self.LOCATIONinLatitude = False
		self.LOCATIONinSource = False
		self.LOCATIONinLocation = False
		self.LOCATIONinRecoveryMethod = False

		self.LOCATIONtotal = 0
		self.LOCATIONtypeText = ''
		self.LOCATIONcreatedText = ''
		self.LOCATIONlongitudeText = ''
		self.LOCATIONlatitudeText = ''
		self.LOCATIONsourceText =  ''
		self.LOCATIONlocationText = ''
		self.LOCATIONrecoveryMethodText = ''
		self.LOCATIONartifact = ''

		self.LOCATIONid = []
		self.LOCATIONtype = []
		self.LOCATIONcreated = []
		self.LOCATIONlongitude = []
		self.LOCATIONlatitude = []
		self.LOCATIONsource = []
		self.LOCATIONlocation = []
		self.LOCATIONrecoveryMethod = []

#---    Searched Item 
		self.SEARCHED_ITEM_PATTERN = ('Parsed Search Queries', 'Google Searches', 
			'iOS Safari Recent Search Terms', 'Chrome Keyword Search Terms')
		self.SEARCHED_ITEMin = False
		self.SEARCHED_ITEMinAppSource = False
		self.SEARCHED_ITEMinTimeStamp = False
		self.SEARCHED_ITEMinValue = False
		self.SEARCHED_ITEMinSource = False
		self.SEARCHED_ITEMinLocation = False
		self.SEARCHED_ITEMinRecoveryMethod = False

		self.SEARCHED_ITEMtotal = 0
		self.SEARCHED_ITEMappSourceText = ''
		self.SEARCHED_ITEMtimeStampText = ''
		self.SEARCHED_ITEMvalueText = ''
		self.SEARCHED_ITEMsourceText =  ''
		self.SEARCHED_ITEMlocationText = ''
		self.SEARCHED_ITEMrecoveryMethodText = ''
		self.SEARCHED_ITEMartifact = ''

		self.SEARCHED_ITEMid = []
		self.SEARCHED_ITEMappSource = []
		self.SEARCHED_ITEMtimeStamp = []
		self.SEARCHED_ITEMvalue = []
		self.SEARCHED_ITEMsource = []
		self.SEARCHED_ITEMlocation = []
		self.SEARCHED_ITEMrecoveryMethod = []

#---    SMS  Artifacts
		self.SMS_PATTERN = ('Android SMS', 'Android SMS/MMS', 'iOS iMessage/SMS/MMS')
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

#---    WEB_HISTORY 
		self.WEB_PATTERN = ('Chrome Web History', 'Safari History', 'Firefox Web History',
			'Samsung Browser Web History', 'Edge Chromium Web History')
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

#---    Wireless Network Artifact
		self.WIRELESS_NET_PATTERN = ('WiFi Locations')
		self.WIRELESS_NETin = False
		self.WIRELESS_NETinMacAaddress= False
		self.WIRELESS_NETinChannel= False
		self.WIRELESS_NETinTimeStamp = False
		self.WIRELESS_NETinLatitude = False
		self.WIRELESS_NETinLongitude = False
		self.WIRELESS_NETinAccuracy = False
		self.WIRELESS_NETinSource = False
		self.WIRELESS_NETinLocation = False
		self.WIRELESS_NETinRecoveryMethod = False

		self.WIRELESS_NETmacAddressText = ''
		self.WIRELESS_NETchannelText = ''
		self.WIRELESS_NETtimeStampText = ''
		self.WIRELESS_NETlongitudeText = ''
		self.WIRELESS_NETlatitudeText = ''
		self.WIRELESS_NETaccuracyText = ''
		self.WIRELESS_NETsourceText =  ''
		self.WIRELESS_NETlocationText = ''
		self.WIRELESS_NETrecoveryMethodText = ''

		self.WIRELESS_NETtotal = 0
		self.WIRELESS_NETid = []
		self.WIRELESS_NETmacAddress = []
		self.WIRELESS_NETchannel = []
		self.WIRELESS_NETtimeStamp = []
		self.WIRELESS_NETlongitude = []
		self.WIRELESS_NETlatitude = []
		self.WIRELESS_NETaccuracy = []
		self.WIRELESS_NETsource = []
		self.WIRELESS_NETlocation = []
		self.WIRELESS_NETrecoveryMethod = []

#---    Windows Timeline Activity, class uco-observable:EventFacet in UCO/CASE
		self.WIN_TIMELINE_PATTERN = ('Windows Timeline Activity')
		self.WIN_TIMELINEin = False
		self.WIN_TIMELINEinAppName = False
		self.WIN_TIMELINEinActivityType = False
		self.WIN_TIMELINEinTimeStamp = False
		self.WIN_TIMELINEinSource = False
		self.WIN_TIMELINEinLocation = False
		self.WIN_TIMELINEinRecoveryMethod = False

		self.WIN_TIMELINEtotal = 0
		self.WIN_TIMELINEappNameText = ''
		self.WIN_TIMELINEactivityTypeText = ''
		self.WIN_TIMELINEtimeStampText = ''
		self.WIN_TIMELINEsourceText =  ''
		self.WIN_TIMELINElocationText = ''
		self.WIN_TIMELINErecoveryMethodText = ''

		self.WIN_TIMELINEid = []
		self.WIN_TIMELINEappName = []
		self.WIN_TIMELINEactivityType = []
		self.WIN_TIMELINEtimeStamp = []
		self.WIN_TIMELINEsource = []
		self.WIN_TIMELINElocation = []
		self.WIN_TIMELINErecoveryMethod = []        

		self.CONTEXTimagePath = []
		self.CONTEXTimageSize = []
		self.CONTEXTimageMetadataHashSHA = []
		self.CONTEXTimageMetadataHashMD5 = []

	def createOutFile(self, filename):
		'''
		It transfers all the Traces (Observable in UCO/CASE terminology) from the memory to the file, whose name has been
		provided as an argument in the command line.
			:param filename: The JSON-LD filename that is being generated, complied with the UCO/CASE ontologies (string).
			:return:  None.
		''' 		
		self.fOut = codecs.open(filename, 'w', encoding='utf8')

	def __charactersCALL(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.CALL_PATTERN
			:return:  None.
		'''		
		if self.CALLinPartner:
			self.CALLpartnerText += ch
		elif self.CALLinPartnerName:
			self.CALLpartnerNameText += ch
		elif self.CALLinDirection:
			self.CALLdirectionText += ch
		elif self.CALLinTimeStamp:
			self.CALLtimeStampText += ch
		elif self.CALLinDuration:
			self.CALLdurationText += ch
		elif self.CALLinSource:
			self.CALLsourceText += ch
		elif self.CALLinLocation:
			self.CALLlocationText += ch
		elif self.CALLinRecoveryMethod:
			self.CALLrecoveyMethodText += ch 

	def __charactersCELL_TOWER(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.CELL_TOWER_PATTERN
			:return:  None.
		'''			
		if self.CELL_TOWERinCID:
			self.CELL_TOWERcidText += ch
		elif self.CELL_TOWERinLAC:
			self.CELL_TOWERlacText += ch
		elif self.CELL_TOWERinMCC:
			self.CELL_TOWERmccText += ch
		elif self.CELL_TOWERinMNC:
			self.CELL_TOWERmncText += ch
		elif self.CELL_TOWERinTimeStamp:
			self.CELL_TOWERtimeStampText += ch
		elif self.CELL_TOWERinLatitude:
			self.CELL_TOWERlatitudeText += ch
		elif self.CELL_TOWERinLongitude:
			self.CELL_TOWERlongitudeText += ch
		elif self.CELL_TOWERinSource:
			self.CELL_TOWERsourceText += ch
		elif self.CELL_TOWERinLocation:
			self.CELL_TOWERlocationText += ch
		elif self.CELL_TOWERinRecoveryMethod:
			self.CELL_TOWERrecoveryMethodText += ch

	def __charactersCONTACT(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.CONTACT_PATTERN
			:return:  None.
		'''			
		if self.CONTACTinName:
			self.CONTACTnameText += ch
		elif self.CONTACTinFirstName:
			self.CONTACTfirstNameText += ch
		elif self.CONTACTinLastName:
			self.CONTACTlastNameText += ch
		elif self.CONTACTinPhoneNumber:
			self.CONTACTphoneNumberText += ch
		elif self.CONTACTinSource:
			self.CONTACTsourceText += ch
		elif self.CONTACTinLocation:
			self.CONTACTlocationText += ch
		elif self.CONTACTinRecoveryMethod:
			self.CONTACTrecoveryMethodText += ch

	def __charactersCOOKIE(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.COOKIE_PATTERN
			:return:  None.
		'''			
		if self.COOKIEinName:
			self.COOKIEnameText += ch
		elif self.COOKIEinPath:
			self.COOKIEpathText += ch
		elif self.COOKIEinDomain:
			self.COOKIEdomainText += ch
		elif self.COOKIEinCreatedDate:
			self.COOKIEcreatedDateText += ch
		elif self.COOKIEinAccessedDate:
			self.COOKIEaccessedDate += ch
		elif self.COOKIEinExpirationDate:
			self.COOKIEexpirationDateText += ch
		elif self.COOKIEinSource:
			self.COOKIEsourceText += ch
		elif self.COOKIEinLocation:
			self.COOKIElocationText += ch
		elif self.COOKIEinRecoveryMethod:
			self.COOKIErecoveryMethodText += ch

	def __charactersCHAT(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.CHAT_PATTERN
			:return:  None.
		'''			
		if self.CHATinSender:
			self.CHATsenderText += ch
		elif self.CHATinReceiver:
			self.CHATreceiverText += ch
		elif self.CHATinPartner:
			self.CHATpartnerText += ch
		elif self.CHATinDateTimeSent:
			self.CHATdateTimeSentText += ch
		elif self.CHATinDateTimeReceived:
			self.CHATdateTimeReceivedText += ch
		elif self.CHATinDateTime:
			self.CHATdateTimeText += ch                
		elif self.CHATinMessage:
			self.CHATmessageText += ch
		elif self.CHATinMessageStatus:
			self.CHATmessageStatusText += ch
		elif self.CHATinMessageType:
			self.CHATmessageTypeText += ch
		elif self.CHATinSource:
			self.CHATsourceText += ch
		elif self.CHATinLocation:
			self.CHATlocationText += ch
		elif self.CHATinRecoveryMethod:
			self.CHATrecoveryMethodText += ch  

	def __charactersDEVICE(self, ch):        
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.DEVICE_PATTERN
			:return:  None.
		'''			
		if self.DEVICEinId:
			if self.DEVICEidText == '':
				self.DEVICEidText += ch
		elif self.DEVICEinImsi:
			if self.DEVICEimsiText == '':
				self.DEVICEimsiText += ch
		elif self.DEVICEinBluetoothAddress:
			if self.DEVICEbluetoothAddressText == '':
				self.DEVICEbluetoothAddressText += ch 
		elif self.DEVICEinBluetoothName:
			if self.DEVICEbluetoothNameText == '':
				self.DEVICEbluetoothNameText += ch
		elif self.DEVICEinImei:
			if self.DEVICEimeiText == '':
				self.DEVICEimeiText += ch
		elif self.DEVICEinSerialNumber:
			if self.DEVICEserialNumberText == '':
				self.DEVICEserialNumberText += ch
		elif self.DEVICEinName:
			if self.DEVICEnameText == '':
				self.DEVICEnameText += ch
		elif self.DEVICEinModel:
			if self.DEVICEmodelText == '':
				self.DEVICEmodelText += ch
		elif self.DEVICEinIccid:
			if self.DEVICEiccidText == '':
				self.DEVICEiccidText += ch
		elif self.DEVICEinOsVersion:
			if self.DEVICEosVersionText == '':
				self.DEVICEosVersionText += ch

	def __charactersEVENT_LOCK(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.EVENT_LOCK_PATTERN
			:return:  None.
		'''			
		if self.EVENT_LOCKinDeviceStatus:
			self.EVENT_LOCKdeviceStatusText += ch
		elif self.EVENT_LOCKinDateTime:
			self.EVENT_LOCKdateTimeText += ch
		elif self.EVENT_LOCKinSource:
			self.EVENT_LOCKsourceText += ch
		elif self.EVENT_LOCKinLocation:
			self.EVENT_LOCKlocationText += ch
		elif self.EVENT_LOCKinRecoveryMethod:
			self.EVENT_LOCKrecoveryMethodText += ch

	def __charactersEVENT_APP_USE(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.EVENT_APP_USE_PATTERN
			:return:  None.
		'''			
		if self.EVENT_APP_USEinStartTime:
			self.EVENT_APP_USEstartTimeText += ch
		elif self.EVENT_APP_USEinEndTime:
			self.EVENT_APP_USEendTimeText += ch
		elif self.EVENT_APP_USEinApplication:
			self.EVENT_APP_USEapplicationText += ch
		elif self.EVENT_APP_USEinLocation:
			self.EVENT_APP_USElocationText += ch
		elif self.EVENT_APP_USEinRecoveryMethod:
			self.EVENT_APP_USErecoveryMethodText += ch

	def __charactersEMAIL(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.EMAIL_PATTERN
			:return:  None.
		'''			
		if self.EMAILinSender:
			self.EMAILsenderText += ch
		elif self.EMAILinRecipients:
			self.EMAILrecipientText += ch
		elif self.EMAILinCC:
			self.EMAILccText += ch
		elif self.EMAILinBCC:
			self.EMAILbccText += ch
		elif self.EMAILinDateTime:
			self.EMAILdateTimeText += ch
		elif self.EMAILinSubject:
			self.EMAILsubjectText += ch
		elif self.EMAILinBody:
			self.EMAILbodyText += ch
		elif self.EMAILinAttachment:
			self.EMAILattachmentText += ch
		elif self.EMAILinSource:
			self.EMAILsourceText += ch
		elif self.EMAILinLocation:
			self.EMAILlocationText += ch
		elif self.EMAILinRecoveryMethod:
			self.EMAILrecoveryMethodText += ch

	def __charactersFILE(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.FILE_PATTERN
			:return:  None.
		'''			
		if self.FILEinTag:
			self.FILEtagText += ch
		elif self.FILEinFileName:
			self.FILEfileNameText += ch
		elif self.FILEinImage:
			self.FILEimageText += ch
		elif self.FILEinFileExtension:
			self.FILEfileExtensionText += ch
		elif self.FILEinFileSize:
			self.FILEfileSizeText += ch
		elif self.FILEinCreated:
			self.FILEcreatedText += ch
		elif self.FILEinModified:
			self.FILEmodifiedText += ch
		elif self.FILEinAccessed:
			self.FILEaccessedText += ch
		elif self.FILEinMD5:
			self.FILEmd5Text += ch
		elif self.FILEinExifMake:
			self.FILEexifMakeText += ch
		elif self.FILEinExifModel:
			self.FILEexifModelText += ch 
		elif self.FILEinExifLatitudeRef:
			self.FILEexifLatitudeRefText += ch
		elif self.FILEinExifLatitude:
			self.FILEexifLatitudeText += ch
		elif self.FILEinExifLongitudeRef:
			self.FILEexifLongitudeRef += ch
		elif self.FILEinExifLongitude:
			self.FILEexifLongitudeText += ch
		elif self.FILEinExifAltitude:
			self.FILEexifAltitudeText += ch
		elif self.FILEinSource:
			self.FILEsourceText += ch
		elif self.FILEinLocation:
			self.FILElocationText += ch
		elif self.FILEinRecoveryMethod:
			self.FILErecoveryMethodText += ch

	def __charactersFILE_SYS_INFO(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.FILE_SYS_INFO_PATTERN
			:return:  None.
		'''		
		if self.FILE_SYS_INFOinVolumeSn:
			self.FILE_SYS_INFOvolumeSnText += ch
		elif self.FILE_SYS_INFOinFileSystem:
			self.FILE_SYS_INFOfileSystemText += ch
		elif self.FILE_SYS_INFOinCapacity:
			self.FILE_SYS_INFOcapacityText += ch
		elif self.FILE_SYS_INFOinUnallocated:
			self.FILE_SYS_INFOunallocatedText += ch
		elif self.FILE_SYS_INFOinAllocated:
			self.FILE_SYS_INFOallocatedText += ch
		elif self.FILE_SYS_INFOinOffest:
			self.FILE_SYS_INFOoffsetText += ch        

	def __charactersLOCATION(self, ch):
		if self.LOCATIONinType:
			self.LOCATIONtypeText += ch
		elif self.LOCATIONinCreated:
			self.LOCATIONcreatedText += ch
		elif self.LOCATIONinLatitude:
			self.LOCATIONlatitudeText += ch
		elif self.LOCATIONinLongitude:
			self.LOCATIONlongitudeText += ch
		elif self.LOCATIONinSource:
			self.LOCATIONsourceText += ch
		elif self.LOCATIONinLocation:
			self.LOCATIONlocationText += ch
		elif self.LOCATIONinRecoveryMethod:
			self.LOCATIONrecoveryMethodText += ch

	def __charactersSEARCHED_ITEM(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.SEARCHED_ITEM_PATTERN
			:return:  None.
		'''		
		if self.SEARCHED_ITEMinValue:
			self.SEARCHED_ITEMvalueText += ch
		elif self.SEARCHED_ITEMinAppSource:
			self.SEARCHED_ITEMappSourceText += ch
		elif self.SEARCHED_ITEMinTimeStamp:
			self.SEARCHED_ITEMtimeStampText += ch
		elif self.SEARCHED_ITEMinSource:
			self.SEARCHED_ITEMsourceText += ch
		elif self.SEARCHED_ITEMinLocation:
			self.SEARCHED_ITEMlocationText += ch
		elif self.SEARCHED_ITEMinRecoveryMethod:
			self.SEARCHED_ITEMrecoveryMethodText += ch

	def __charactersSMS(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.SMS_PATTERN
			:return:  None.
		'''		
		if self.SMSinPartner:
			self.SMSpartnerText += ch
		elif self.SMSinRecipient:
			self.SMSrecipientText += ch
		elif self.SMSinSender:
			self.SMSsenderText += ch
		elif self.SMSinReceivedDateTime:
			self.SMSreceivedDateTimeText += ch
		elif self.SMSinSentDateTime:
			self.SMSsentDateTimeText += ch
		elif self.SMSinMessage:
			self.SMSmessageText += ch
		elif self.SMSinDirection:
			self.SMSdirectionText += ch
		elif self.SMSinSource:
			self.SMSsourceText += ch
		elif self.SMSinLocation:
			self.SMSlocationText += ch
		elif self.SMSinRecoveryMethod:
			self.SMSrecoveryMethodText += ch

	def __charactersWEB(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.WEB_PATTERN
			:return:  None.
		'''		
		if self.WEBinUrl:
			self.WEBurlText += ch
		elif self.WEBinLastVisited:
			self.WEBlastVisitedText += ch
		elif self.WEBinTitle:
			self.WEBtitleText += ch
		elif self.WEBinVisitCount:
			self.WEBvisitCountText += ch
		elif self.WEBinSource:
			self.WEBsourceText += ch
		elif self.WEBinLocation:
			self.WEBlocationText += ch
		elif self.WEBinRecoveryMethod:
			self.WEBrecoveryMethodText += ch

	def __charactersWIRELESS_NET(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.WIRELESS_NET_PATTERN
			:return:  None.
		'''		
		if self.WIRELESS_NETinMacAaddress:
			self.WIRELESS_NETmacAddressText += ch
		elif self.WIRELESS_NETinChannel:
			self.WIRELESS_NETchannelText += ch
		elif self.WIRELESS_NETinTimeStamp:
			self.WIRELESS_NETtimeStampText += ch
		elif self.WIRELESS_NETinLatitude:
			self.WIRELESS_NETlatitudeText += ch
		elif self.WIRELESS_NETinLongitude:
			self.WIRELESS_NETlongitudeText += ch
		elif self.WIRELESS_NETinAccuracy:
			self.WIRELESS_NETaccuracyText += ch
		elif self.WIRELESS_NETinSource:
			self.WIRELESS_NETsourceText += ch
		elif self.WIRELESS_NETinLocation:
			self.WIRELESS_NETlocationText += ch
		elif self.WIRELESS_NETinRecoveryMethod:
			self.WIRELESS_NETrecoveryMethodText += ch

	def __charactersWIN_TIMELINE(self, ch):
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact[@name="artifact_name"]//Hit/Fragment[@name="..."] with artifact_name in self.WIN_TIMELINE_PATTERN
			:return:  None.
		'''			
		if self.WIN_TIMELINEinAppName:
			self.WIN_TIMELINEappNameText += ch
		elif self.WIN_TIMELINEinActivityType:
			self.WIN_TIMELINEactivityTypeText += ch
		elif self.WIN_TIMELINEinTimeStamp:
			self.WIN_TIMELINEtimeStampText += ch
		elif self.WIN_TIMELINEinSource:
			self.WIN_TIMELINEsourceText += ch
		elif self.WIN_TIMELINEinLocation:
			self.WIN_TIMELINElocationText += ch
		elif self.WIN_TIMELINEinRecoveryMethod:
			self.WIN_TIMELINErecoveryMethodText += ch

	def __startElementFragmentPHONE_NUM(self, attrFragment):
		if attrFragment == 'Phone Number': 
			self.CALL_PHONE_NUM_DEVICE_VALUEin = True 

		if attrFragment == 'WhatsApp Name': 
			self.CALL_PHONE_NAME_DEVICE_VALUEin = True 

	def __startElementFragmentCALL(self, attrFragment):
		'''
        It captures the opening of the XML Element matching with the XPath expression
        //Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.CALL_PATTERN 
            :param attrFragment: Value of the attribute name of the ELement (string).
            :return:  None.
        '''	
		if attrFragment in ('Partner', 'Partners'):  
			self.CALLinPartner = True 
		elif attrFragment == 'Partner Name' :  
			self.CALLinPartnerName = True 
		elif attrFragment == 'Direction':  
			self.CALLinDirection = True 
		elif attrFragment.find('Call Date/Time') > -1:  
			self.CALLinTimeStamp = True 
		elif attrFragment.find('Call Duration') > -1:  
			self.CALLinDuration = True 
		elif attrFragment == 'Source':  
			self.CALLinSource = True 
		elif attrFragment == 'Location':  
			self.CALLinLocation = True 
		elif attrFragment.lower() == 'recovery method':  
			self.CALLinRecoveryMethod = True     

	def __startElementFragmentCELL_TOWER(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.CELL_TOWER_PATTERN 
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''			
		if attrFragment == 'CellID' :  
			self.CELL_TOWERinCID = True 
		elif attrFragment == 'Location Area Code':  
			self.CELL_TOWERinLAC = True 
		elif attrFragment == 'Mobile Country Code':
			self.CELL_TOWERinMCC = True 
		elif attrFragment == 'Mobile Network Code' :
			self.CELL_TOWERinMNC = True 
		elif attrFragment.find('Timestamp Date/Time - UTC') > -1:  
			self.CELL_TOWERinTimeStamp = True
		elif attrFragment == 'Latitude' :
			self.CELL_TOWERinLatitude = True 
		elif attrFragment == 'Longitude' :
			self.CELL_TOWERinLongitude = True 
		elif attrFragment == 'Source':  
			self.CELL_TOWERinSource = True 
		elif attrFragment == 'Location':  
			self.CELL_TOWERnLocation = True 
		elif attrFragment.lower() == 'recovery method':  
			self.CELL_TOWERinRecoveryMethod = True     

	def __startElementFragmentCHAT(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.CHAT_PATTERN 
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''		
#---    the first condition is for Android WhatsApp Messages, iOS WhatsApp Messages
#       and Snapchat Chat Messages, 
#       the second condition is for iOS Telegram Messages
		if attrFragment in ('Sender', 'Sender Name', 'Last Sender'):  
			self.CHATinSender = True 
#---    the first condition is for Android WhatsApp Messages and iOS WhatsApp Messages
#       the second condition is for iOS Telegram Messages
#       the third condition is for Snapchat Chat Messages            
		elif attrFragment in ('Receiver', 'Receiver Name', 'Recipient Name', 'Recipient', 'Recipient(s)'): 
			self.CHATinReceiver = True 
#---    the condition is for Android Telegram Messages
		elif attrFragment in ('Partner', 'Participant Information', 'Conversation Name'): 
			self.CHATinPartner = True 
		elif (attrFragment.find('Message Sent Date/Time') > -1 or 
		    attrFragment.find('Message Received Date/Time') > -1):              
			self.CHATinDateTimeReceived = True            
#---    the first condition is for iOS WhatsApp Messages
#       the second condition is for Telegram Messages   
		elif (attrFragment.find('Message Date/Time') > -1 or 
		    attrFragment.find('Creation Date/Time') > -1 or 
		    attrFragment.find('Date/Time', 0) > - 1 or
		    attrFragment.find('Last Message Date/Time', 0) > - 1 or
		    attrFragment == 'Created Date/Time'):  
			self.CHATinDateTime = True
			#---    the first condition is for WhatsApp Messages
#       the second condition is for Telegram Messages   
		elif attrFragment in ('Message', 'Message Body', 'Text', 'Last Message'):
			self.CHATinMessage = True 
		elif attrFragment == 'Message Status':  
			self.CHATinMessageStatus = True 
#---    only for iOS Whatsapp, Telegram and Skype Messages 
		elif attrFragment in ('Message Type', 'Conversation Type'):  
			self.CHATinMessageType = True 
		elif attrFragment == 'Source':  
			self.CHATinSource = True
		elif attrFragment == 'Location':  
			self.CHATinLocation = True 
		elif attrFragment.lower() == 'recovery method':  
			self.CHATinRecoveryMethod = True 


	def __startElementFragmentCONTACT(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.CONTACT_PATTERN 
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''		
		if attrFragment == 'Display Name':  
			self.CONTACTinName = True 
		elif attrFragment == 'First Name':  
			self.CONTACTinFirstName = True 
		elif attrFragment == 'Last Name':  
			self.CONTACTinLastName = True 
		elif attrFragment == 'Phone Number(s)':  
			self.CONTACTinPhoneNumber = True 
		elif attrFragment == 'Source':  
			self.CONTACTinSource = True
		elif attrFragment == 'Location':  
			self.CONTACTinLocation = True 
		elif attrFragment.lower() == 'recovery method':  
			self.CONTACTinRecoveryMethod = True 

	def __startElementFragmentCOOKIE(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.COOKIE_PATTERN 
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''		
		if attrFragment == 'Name':
			self.COOKIEinName = True

		if attrFragment.find('Accessed Date/Time') > - 1:
			self.COOKIEinAccessedDate = True

		if attrFragment.find('Created Date/Time') > - 1:
			self.COOKIEinCreatedDate = True

		if attrFragment.find('Expiration Date/Time') > - 1:
			self.COOKIEinExpirationDate = True

		if attrFragment == 'Path':
			self.COOKIEinPath = True

		if attrFragment == 'Host':  
			self.COOKIEinDomain = True 

		if attrFragment == 'Source':  
			self.COOKIEinSource = True

		if attrFragment == 'Location':  
			self.COOKIEinLocation = True 

		if attrFragment.lower() == 'recovery method':  
			self.COOKIEinRecoveryMethod = True 

	def __startElementFragmentDEVICE(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.DEVICE_PATTERN 
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''			
		if attrFragment == 'Serial Number':
			self.DEVICEinSerialNumber = True
		elif attrFragment == 'Device ID':
			self.DEVICEinId = True
		elif attrFragment == 'Device Name':
			self.DEVICEinName = True
		elif attrFragment == 'IMSI':
			self.DEVICEinImsi = True
		elif attrFragment == 'IMSE':
			self.DEVICEinImei = True
		elif attrFragment == 'Model ID':
			self.DEVICEinModel = True
		elif attrFragment == 'OS Version':
			self.DEVICEinOsVersion = True
		elif attrFragment == 'ICCID':
			self.DEVICEinIccid = True
		elif attrFragment == 'Bluetooth Address':
			self.DEVICEinBluetoothAddress = True
		elif attrFragment == 'Bluetooth Name':
			self.DEVICEinBluetoothName = True
		elif attrFragment == 'Bluetooth Address':
			self.DEVICEinBluetoothAddress = True

	def __startElementFragmentEVENT_APP_USE(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.EVENT_APP_USE_PATTERN
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''			
		if attrFragment == 'State':  
			self.EVENT_LOCKinDeviceStatus = True 
		elif attrFragment.find('Start Date/Time') > -1:  
			self.EVENT_APP_USEinStartTime = True 
		elif attrFragment.find('End Date/Time') > -1:  
			self.EVENT_APP_USEinEndTime = True 
		elif attrFragment == 'Application Name':  
			self.EVENT_APP_USEinApplication = True
		elif attrFragment == 'Location':  
			self.EVENT_APP_USEinLocation = True 
		elif attrFragment.lower() == 'recovery method':  
			self.EVENT_APP_USEinRecoveryMethod = True 

	def __startElementFragmentEVENT_LOCK(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.EVENT_LOCK_PATTERN 
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''			
		if attrFragment == 'State':  
			self.EVENT_LOCKinDeviceStatus = True 
		elif attrFragment.find('Recorded Date/Time') > -1:  
			self.EVENT_LOCKinDateTime = True 
		elif attrFragment == 'Source':  
			self.EVENT_LOCKinSource = True
		elif attrFragment == 'Location':  
			self.EVENT_LOCKinLocation = True 
		elif attrFragment.lower() == 'recovery method':  
			self.EVENT_LOCKinRecoveryMethod = True 

	def __startElementFragmentEMAIL(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.EMAIL_PATTERN
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''		
		if attrFragment in ('Sender', 'From Address', 'From'):  
			self.EMAILinSender = True
		elif attrFragment in ('Recipients', 'To Address(es)', 'To'):  
			self.EMAILinRecipients = True
		elif attrFragment.lower() in ('cc', 'cc address(es)'):  
			self.EMAILinCC = True 
		elif attrFragment.lower() in ('bcc', 'bcc address(es)'):  
			self.EMAILinBCC = True 
		elif attrFragment.find('Date/Time') > - 1:  
			self.EMAILinDateTime = True 
		elif attrFragment == 'Subject':  
			self.EMAILinSubject = True 
		elif attrFragment.find(' Body') > -1:  
			self.EMAILinBody = True 
		elif attrFragment == 'Attachments':  
			self.EMAILinAttachment = True 
		elif attrFragment == 'Source':  
			self.EMAILinSource = True
		elif attrFragment == 'Location':  
			self.EMAILinLocation = True 
		elif attrFragment.lower() == 'recovery method':  
			self.EMAILinRecoveryMethod = True 

	def __startElementFragmentFILE(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.FILE_PATTERN
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''			
		if attrFragment == 'Tags':
			self.FILEinTag = True
		elif attrFragment in ('File Name', 'Filename', 'File', '_Video'):
			self.FILEinFileName = True
		elif attrFragment == 'Image':
			self.FILEinImage = True
		elif attrFragment == 'File Extension':
			self.FILEinFileExtension = True
		elif attrFragment in ('Size (Bytes)', 'File Size (Bytes)'):
			self.FILEinFileSize = True
		elif attrFragment.find('Created Date/Time') > -1:
			self.FILEinCreated = True
		elif attrFragment.find('Last Modified Date/Time') > -1:
			self.FILEinModified = True
		elif attrFragment.find('Accessed Modified Date/Time') > -1 or \
		   attrFragment.find('Last Accessed Date/Time') > -1:
			self.FILEinAccessed = True
		elif attrFragment == 'MD5 Hash':
			self.FILEinMD5 = True
		elif attrFragment == 'Make':
			self.FILEinExifMake = True
		elif attrFragment == 'Model':
			self.FILEinExifModel = True
		elif attrFragment == 'GPS Latitude':
			self.FILEinExifLatitude = True
		elif attrFragment == 'GPS Latitude Reference':
			self.FILEinExifLatitudeRef = True
		elif attrFragment == 'GPS Longitude':
			self.FILEinExifLongitude = True
		elif attrFragment == 'GPS Longitude Reference':
			self.FILEinExifLongitudeRef = True
		elif attrFragment == 'Altitude (meters)':
			self.FILEinExifAltitude = True
		elif attrFragment == 'Source':
			self.FILEinSource = True
		elif attrFragment == 'Location':
			self.FILEinLocation = True
		elif attrFragment.lower() == 'recovery method':
			self.FILEinRecoveryMethod = True

	def __startElementFragmentFILE_SYS_INFO(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.FILE_SYS_INFO_PATTERN
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''		
		if attrFragment == 'Volume Serial Number':  
			self.FILE_SYS_INFOinVolumeSn = True 
		elif attrFragment == 'File System':  
			self.FILE_SYS_INFOinFileSystem = True
		elif attrFragment == 'Total Capacity (Bytes)':  
			self.FILE_SYS_INFOinCapacity = True 
		elif attrFragment == 'Unallocated Area (Bytes)':  
			self.FILE_SYS_INFOinUnallocated = True 
		elif attrFragment == 'Allocated Area (Bytes)':  
			self.FILE_SYS_INFOinAllocated = True 
		elif attrFragment == 'Volume Offset (Bytes)':  
			self.FILE_SYS_INFOinOffest = True 

	def __startElementFragmentLOCATION(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.LOCATION_PATTERN
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''		
		if attrFragment == 'Location Type':
			self.LOCATIONinType = True
		elif attrFragment.find('Created Date/Time') > - 1:
			self.LOCATIONinCreated = True
		elif attrFragment == 'Latitude':
			self.LOCATIONinLatitude = True
		elif attrFragment == 'Longitude':
			self.LOCATIONinLongitude = True
		elif attrFragment == 'Source':
			self.LOCATIONinSource = True
		elif attrFragment == 'Location':
			self.LOCATIONinLocation = True
		elif attrFragment.lower() == 'recovery method':
			self.LOCATIONinRecoveryMethod = True

	def __startElementFragmentSEARCHED_ITEM(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.SEARCHED_ITEM_PATTERN
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''		
		if attrFragment in ('Search Term', 'Keyword Search Term'):
			self.SEARCHED_ITEMinValue = True
		elif attrFragment.find('Date/Time - UTC') > -1 or \
		   attrFragment.find('Last Visited Date/Time - UTC') > -1:
			self.SEARCHED_ITEMinTimeStamp = True
		elif attrFragment == 'Search Engine':
			self.SEARCHED_ITEMinAppSource = True
		elif attrFragment == 'Source':
			self.SEARCHED_ITEMinSource = True
		elif attrFragment == 'Location':
			self.SEARCHED_ITEMinLocation = True
		elif attrFragment.lower() == 'recovery method':
			self.SEARCHED_ITEMinRecoveryMethod = True

	def __startElementFragmentSMS(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.SMS_PATTERN
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''		
		if attrFragment == 'Partner':
			self.SMSinPartner = True
		elif attrFragment in ('Recipient', 'Recipient(s)'):
			self.SMSinRecipient = True
		elif attrFragment == 'Sender':
			self.SMSinSender = True
		elif attrFragment.find('Received Date/Time') > -1:
			self.SMSinReceivedDateTime = True
		elif attrFragment.find('Sent Date/Time') > -1:
			self.SMSinSentDateTime = True
		elif attrFragment == 'Message':
			self.SMSinMessage = True
		elif attrFragment in ('Message Direction', 'Type'):
			self.SMSinDirection = True
		elif attrFragment == 'Source':
			self.SMSinSource = True
		elif attrFragment == 'Location':
			self.SMSinLocation = True
		elif attrFragment.lower() == 'recovery method':
			self.SMSinRecoveryMethod = True

	def __startElementFragmentWEB(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.WEB_PATTERN
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''	
		if attrFragment == 'URL':
			self.WEBinUrl = True
		elif attrFragment.find('Last Visited Date/Time') > -1:
			self.WEBinLastVisited = True
		elif attrFragment == 'Title':
			self.WEBinTitle = True
		elif attrFragment in ('Visit Count', 'Access Count'):
			self.WEBinVisitCount = True
		elif attrFragment == 'Source':
			self.WEBinSource = True
		elif attrFragment == 'Location':
			self.WEBinLocation = True
		elif attrFragment.lower() == 'recovery method':
			self.WEBinRecoveryMethod = True

	def __startElementFragmentWIRELESS_NET(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.WIRELESS_NET_PATTERN
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''			
		if attrFragment == 'MAC Address' :  
			self.WIRELESS_NETinMacAaddress = True 
		elif attrFragment == 'Channel':  
			self.WIRELESS_NETinChannel = True 
		elif attrFragment.find('Timestamp Date/Time - UTC') > -1:  
			self.WIRELESS_NETinTimeStamp = True
		elif attrFragment == 'Latitude' :
			self.WIRELESS_NETinLatitude = True 
		elif attrFragment == 'Longitude' :
			self.WIRELESS_NETinLongitude = True 
		elif attrFragment.find('Accuracy') > - 1:
			self.WIRELESS_NETinAccuracy= True 
		elif attrFragment == 'Source':  
			self.WIRELESS_NETinSource = True 
		elif attrFragment == 'Location':  
			self.WIRELESS_NETnLocation = True 
		elif attrFragment.lower() == 'recovery method':  
			self.WIRELESS_NETinRecoveryMethod = True 

	def __startElementFragmentWIN_TIMELINE(self, attrFragment):
		'''
		It captures the opening of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragmnet[@name="..."] with artifact_name in self.WIN_TIMELINE_PATTERN
		:param attrFragment: Value of the attribute name of the ELement (string).
		:return:  None.
		'''			
		if attrFragment == 'Application Name':
			self.WIN_TIMELINEinAppName = True
		elif attrFragment == 'Activity Type':
			self.WIN_TIMELINEinActivityType = True
		elif attrFragment.find('Start Date/Time') > -1:
			self.WIN_TIMELINEinTimeStamp = True
		elif attrFragment == 'Source':
			self.WIN_TIMELINEinSource = True
		elif attrFragment == 'Location':
			self.WIN_TIMELINEinLocation = True
		elif attrFragment.lower() == 'recovery method':
			self.WIN_TIMELINEinRecoveryMethod = True

	def printObservable(self, oName, oCount):        
		'''
		It prints the number of the kind of Trace item currently processed.
			:param oName: Name of the kind of Trace such as Contact, Call, Chat etc.  (string).
			:param oCount: The number of the kind of Trace item currently processed (int).
			:return:  None.
		'''		
		line =  'processing traces --> ' + oName +  ' n. ' +  \
		    str(oCount) + self.C_end
		if self.verbose:
			if oCount == 1:
				print(self.C_green + '\n' + line, end='\r') 
			else:
				print(self.C_green + line, end='\r') 

#---    it captures each Element when it is opened., the order depends on their 
#       position from the beginning of the document
#            
	def startElement(self, elementName, attrs):
		'''
		It captures the opening of any XML Element, the order depends on their 
		position from the beginning of the document.
			:return:  None.
		''' 
		self.lineXML +=1
		attrName = ''

		if elementName == 'Artifact':
			attrName = attrs.get('name')
			if  attrName in ('Android WhatsApp Accounts Information', 
			                 'SIM Card Activity'): 
				self.CALL_PHONE_NUM_DEVICEin = True
				self.Observable = True
				self.skipLine = True
			elif  attrName in self.CALL_PATTERN:
				self.CALLin = True
				self.Observable = True
				self.skipLine = True   
				self.CALLappNameText = attrName             
			elif  attrName in self.CELL_TOWER_PATTERN:
				self.CELL_TOWERin = True
				self.Observable = True
				self.skipLine = True
			elif  attrName in self.CHAT_PATTERN:            
				self.CHATin = True
				self.Observable = True
				self.skipLine = True
				self.CHATapplicationText = attrName 
			elif  attrName in self.CONTACT_PATTERN:
				self.CONTACTin = True
				self.Observable = True
				self.skipLine = True                   
			elif  attrName in self.COOKIE_PATTERN:
				self.COOKIEin = True
				self.Observable = True
				self.skipLine = True
				self.COOKIEappSourceText = attrName            
			elif  attrName in self.DEVICE_PATTERN:
				self.DEVICEin = True
			elif  attrName in self.EMAIL_PATTERN:
				self.EMAILin = True
				self.Observable = True
				self.skipLine = True
				self.EMAILappName = attrName
			elif  attrName in self.EVENT_LOCK_PATTERN:
				self.EVENT_LOCKin = True
				self.Observable = True
				self.skipLine = True
			elif  attrName in self.EVENT_APP_USE_PATTERN:
				self.EVENT_APP_USEin = True
				self.Observable = True
				self.skipLine = True
			elif  attrName in self.FILE_PATTERN:
				self.FILEin = True
				self.Observable = True 
				self.skipLine = True 
				self.FILEtagText = attrName 
			elif  attrName in self.FILE_SYS_INFO_PATTERN:
				self.FILE_SYS_INFOin = True
				self.Observable = True
				self.skipLine = True
			elif  attrName in self.LOCATION_PATTERN:
				self.LOCATIONin = True
				self.Observable = True
				self.skipLine = True
			elif  attrName in self.SEARCHED_ITEM_PATTERN:
				self.SEARCHED_ITEMin = True
				self.Observable = True
				self.skipLine = True
				self.SEARCHED_ITEMartifact = ''
				if attrName == 'Google Searches':
					self.SEARCHED_ITEMartifact = 'Google Search Engine'
				elif attrName == 'iOS Safari Recent Search Terms':
					self.SEARCHED_ITEMartifact = 'iOS Safari Search Engine'
				elif attrName == 'Chrome Keyword Search Terms':
					self.SEARCHED_ITEMartifact = 'Google Chrome Search Engine'
			elif  attrName in self.SMS_PATTERN:
				self.SMSin = True
				self.Observable = True
				self.skipLine = True
			elif  (attrName in self.WEB_PATTERN  or 
			       attrName.find('Edge/Internet Explorer') > -1):
				self.WEBin = True
				self.Observable = True
				self.skipLine = True
				self.WEBappName = attrName            
			elif  attrName in self.WIN_TIMELINE_PATTERN:
				self.WIN_TIMELINEin = True
				self.Observable = True
				self.skipLine = True
			elif  attrName in self.WIRELESS_NET_PATTERN:
				self.WIRELESS_NETin = True
				self.Observable = True
				self.skipLine = True

		if (elementName == 'Hit'):  
			self.inHit = True
			if self.CALLin:
				self.CALLtotal += 1
				self.printObservable('CALL', self.CALLtotal)
				self.CALLid.append(str(self.CALLtotal))
				self.CALLappName.append(self.CALLappNameText)
				self.CALLpartner.append('')
				self.CALLpartnerName.append('')
				self.CALLdirection.append('')
				self.CALLtimeStamp.append('')
				self.CALLduration.append('')
				self.CALLsource.append('')
				self.CALLlocation.append('')
				self.CALLrecoveryMethod.append('')
			elif self.CELL_TOWERin:
				self.CELL_TOWERtotal += 1
				self.printObservable('CELL TOWER', self.CELL_TOWERtotal)
				self.CELL_TOWERid.append(str(self.CELL_TOWERtotal))
				self.CELL_TOWERcid.append('')
				self.CELL_TOWERlac.append('')
				self.CELL_TOWERmcc.append('')
				self.CELL_TOWERmnc.append('')
				self.CELL_TOWERtimeStamp.append('')
				self.CELL_TOWERlatitude.append('')
				self.CELL_TOWERlongitude.append('')
				self.CELL_TOWERsource.append('')
				self.CELL_TOWERlocation.append('')
				self.CELL_TOWERrecoveryMethod.append('')
			elif self.DEVICEin:
				self.printObservable('DEVICE INFO', 1)
			elif self.CHATin:
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
			elif self.CONTACTin:
				self.CONTACTtotal += 1
				self.printObservable('CONTACT', self.CONTACTtotal)
				self.CONTACTid.append(str(self.CONTACTtotal))
				self.CONTACTname.append('')
				self.CONTACTphoneNumber.append('')
				self.CONTACTsource.append('')
				self.CONTACTlocation.append('')
				self.CONTACTrecoveryMethod.append('')
			elif self.COOKIEin:
				self.COOKIEtotal += 1
				self.printObservable('COOKIE', self.COOKIEtotal)
				self.COOKIEid.append(str(self.COOKIEtotal))
				self.COOKIEappSource.append(self.COOKIEappSourceText)
				self.COOKIEname.append('')
				self.COOKIEpath.append('')
				self.COOKIEdomain.append('')
				self.COOKIEcreatedDate.append('')
				self.COOKIEaccessedDate.append('')
				self.COOKIEexpirationDate.append('')
				self.COOKIEsource.append('')
				self.COOKIElocation.append('')
				self.COOKIErecoveryMethod.append('')
			elif self.EMAILin:
				self.EMAILtotal += 1
				self.printObservable('EMAIL', self.EMAILtotal)
				self.EMAILid.append(str(self.EMAILtotal))
				self.EMAILappSource.append(self.EMAILappName)
				self.EMAILsender.append('')
				self.EMAILrecipient.append('')
				self.EMAILcc.append('')
				self.EMAILbcc.append('')
				self.EMAILdateTime.append('')
				self.EMAILsubject.append('')
				self.EMAILbody.append('')
				self.EMAILattachment.append('')
				self.EMAILsource.append('')
				self.EMAILlocation.append('')
				self.EMAILrecoveryMethod.append('')
			elif self.EVENT_LOCKin:
				self.EVENT_LOCKtotal += 1
				self.printObservable('EVENT LOCK', self.EVENT_LOCKtotal)
				self.EVENT_LOCKid.append(str(self.EVENT_LOCKtotal))
				self.EVENT_LOCKdateTime.append('')
				self.EVENT_LOCKdeviceStatus.append('')
				self.EVENT_LOCKsource.append('')
				self.EVENT_LOCKlocation.append('')
				self.EVENT_LOCKrecoveryMethod.append('')
			elif self.EVENT_APP_USEin:
				self.EVENT_APP_USEtotal += 1
				self.printObservable('EVENT APP USE', self.EVENT_APP_USEtotal)
				self.EVENT_APP_USEid.append(str(self.EVENT_APP_USEtotal))
				self.EVENT_APP_USEstartTime.append('')
				self.EVENT_APP_USEendTime.append('')
				self.EVENT_APP_USEapplication.append('')
				self.EVENT_APP_USEsource.append('')
				self.EVENT_APP_USElocation.append('')
				self.EVENT_APP_USErecoveryMethod.append('')
			elif self.FILEin:
				self.FILEtotal += 1
				self.printObservable('FILE', self.FILEtotal)
				self.FILEid.append(str(self.FILEtotal))
				self.FILEtag.append(self.FILEtagText)
				self.FILEfileName.append('')
				self.FILEfileLocalPath.append('')
				self.FILEimage.append('')
				self.FILEfileExtension.append('')
				self.FILEfileSize.append('')
				self.FILEcreated.append('')
				self.FILEmodified.append('')
				self.FILEaccessed.append('')
				self.FILEmd5.append('')
				self.FILEexifMake.append('')
				self.FILEexifModel.append('')
				self.FILEexifLatitudeRef.append('')
				self.FILEexifLatitude.append('')
				self.FILEexifLongitude.append('')
				self.FILEexifLongitudeRef.append('')
				self.FILEexifAltitude.append('')
				self.FILEsource.append('')
				self.FILElocation.append('')
				self.FILErecoveryMethod.append('')
			elif self.FILE_SYS_INFOin:
				self.FILE_SYS_INFOtotal += 1
				self.printObservable('FILE SYSTEM INFO', self.FILE_SYS_INFOtotal)
				self.FILE_SYS_INFOid.append(str(self.FILE_SYS_INFOtotal))
				self.FILE_SYS_INFOvolumeSn.append('')
				self.FILE_SYS_INFOfileSystem.append('')
				self.FILE_SYS_INFOcapacity.append('')
				self.FILE_SYS_INFOunallocated.append('')
				self.FILE_SYS_INFOallocated.append('')
				self.FILE_SYS_INFOoffset.append('')
			elif self.LOCATIONin:
				self.LOCATIONtotal += 1
				self.printObservable('LOCATION DEVICE', self.LOCATIONtotal)
				self.LOCATIONid.append(str(self.LOCATIONtotal))                
				self.LOCATIONtype.append('')
				self.LOCATIONcreated.append('')
				self.LOCATIONlatitude.append('')
				self.LOCATIONlongitude.append('')
				self.LOCATIONsource.append('')
				self.LOCATIONlocation.append('')
				self.LOCATIONrecoveryMethod.append('') 
			elif self.SEARCHED_ITEMin:
				self.SEARCHED_ITEMtotal += 1
				self.printObservable('SEARCHED ITEMS', self.SEARCHED_ITEMtotal)
				self.SEARCHED_ITEMid.append(str(self.SEARCHED_ITEMtotal))
				self.SEARCHED_ITEMappSource.append(self.SEARCHED_ITEMartifact)
				self.SEARCHED_ITEMtimeStamp.append('')
				self.SEARCHED_ITEMvalue.append('')
				self.SEARCHED_ITEMsource.append('')
				self.SEARCHED_ITEMlocation.append('')
				self.SEARCHED_ITEMrecoveryMethod.append('') 
			elif self.SMSin:
				self.SMStotal += 1
				self.printObservable('SMS', self.SMStotal)
				self.SMSid.append(str(self.SMStotal))
				self.SMSsender.append('')
				self.SMSrecipient.append('')
				self.SMSreceivedDateTime.append('')
				self.SMSsentDateTime.append('')
				self.SMSmessage.append('')
				self.SMSdirection.append('')
				self.SMSsource.append('')
				self.SMSlocation.append('')
				self.SMSrecoveryMethod.append('')                 
			elif self.WEBin:
				self.WEBtotal += 1
				self.printObservable('WEB', self.WEBtotal)
				self.WEBid.append(str(self.WEBtotal))
				self.WEBurl.append('')
				self.WEBlastVisited.append('')
				self.WEBtitle.append('')
				self.WEBvisitCount.append('')
				self.WEBappSource.append(self.WEBappName)
				self.WEBsource.append('')
				self.WEBlocation.append('')
				self.WEBrecoveryMethod.append('') 
			elif self.WIRELESS_NETin:
				self.WIRELESS_NETtotal += 1
				self.printObservable('WIWIRELESS NETWORK', self.WIRELESS_NETtotal)
				self.WIRELESS_NETid.append(str(self.WIRELESS_NETtotal))
				self.WIRELESS_NETmacAddress.append('')
				self.WIRELESS_NETchannel.append('')
				self.WIRELESS_NETtimeStamp.append('')
				self.WIRELESS_NETlatitude.append('')
				self.WIRELESS_NETlongitude.append('')
				self.WIRELESS_NETaccuracy.append('')
				self.WIRELESS_NETsource.append('')
				self.WIRELESS_NETlocation.append('')
				self.WIRELESS_NETrecoveryMethod.append('')
			elif self.WIN_TIMELINEin:
				self.WIN_TIMELINEtotal += 1
				self.printObservable('WINDOWS TIME LINE', self.WIN_TIMELINEtotal)
				self.WIN_TIMELINEid.append(str(self.WIN_TIMELINEtotal))
				self.WIN_TIMELINEappName.append('')
				self.WIN_TIMELINEactivityType.append('')
				self.WIN_TIMELINEtimeStamp.append('')
				self.WIN_TIMELINEsource.append('')
				self.WIN_TIMELINElocation.append('')
				self.WIN_TIMELINErecoveryMethod.append('')             
		if elementName == 'Fragment':
			attrName = attrs.get('name')        
			if self.CALLin and self.inHit:
				self.__startElementFragmentCALL(attrName)
			elif self.CELL_TOWERin and self.inHit:
				self.__startElementFragmentCELL_TOWER(attrName)
			elif self.DEVICEin and self.inHit:
				self.__startElementFragmentDEVICE(attrName)
			elif self.CHATin and self.inHit: 
				self.__startElementFragmentCHAT(attrName)
			elif self.CONTACTin and self.inHit:
				self.__startElementFragmentCONTACT(attrName)
			elif self.COOKIEin and self.inHit:
				self.__startElementFragmentCOOKIE(attrName)
			elif self.CALL_PHONE_NUM_DEVICEin and self.inHit:
				self.__startElementFragmentPHONE_NUM(attrName)
			elif self.EMAILin and self.inHit:
				self.__startElementFragmentEMAIL(attrName)
			elif self.EVENT_LOCKin and self.inHit:
				self.__startElementFragmentEVENT_LOCK(attrName)
			elif self.EVENT_APP_USEin and self.inHit:
				self.__startElementFragmentEVENT_APP_USE(attrName)
			elif self.FILEin and self.inHit:
				self.__startElementFragmentFILE(attrName)
			elif self.FILE_SYS_INFOin and self.inHit:
				self.__startElementFragmentFILE_SYS_INFO(attrName)
			elif self.LOCATIONin and self.inHit:
				self.__startElementFragmentLOCATION(attrName)
			elif self.SEARCHED_ITEMin and self.inHit:
				self.__startElementFragmentSEARCHED_ITEM(attrName)
			elif self.SMSin and self.inHit:
				self.__startElementFragmentSMS(attrName)
			elif self.WEBin and self.inHit:
				self.__startElementFragmentWEB(attrName)
			elif self.WIRELESS_NETin and self.inHit:
				self.__startElementFragmentWIRELESS_NET(attrName)
			elif self.WIN_TIMELINEin and self.inHit:
				self.__startElementFragmentWIN_TIMELINE(attrName)

			if (not self.Observable):
				line = self.C_grey + '*\tProcessing Element <' + elementName + '> at line '
				line += str(self.lineXML) + ' ...'  + self.C_end
				if self.verbose:
					if self.skipLine:
						print ('\n' + line , end='\r')
						self.skipLine = False                  
					else:
						print (line , end='\r')                  

	def __endElementFragmentPHONE_NUM(self):        
		if self.CALL_PHONE_NUM_DEVICE_VALUEin:            
			self.CALL_PHONE_NUM_DEVICE_VALUEin = False

		if self.CALL_PHONE_NAME_DEVICE_VALUEin:            
			self.CALL_PHONE_NAME_DEVICE_VALUEin = False

	def __endElementFragmentCALL(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.CALL_PATTERN 
		'''		
		if self.CALLinPartner:
			self.CALLpartner[self.CALLtotal - 1] = self.CALLpartnerText
			self.CALLpartnerText = ''
			self.CALLinPartner = False
		elif self.CALLinPartnerName:
			self.CALLpartnerName[self.CALLtotal - 1] = self.CALLpartnerNameText
			self.CALLpartnerNameText = ''
			self.CALLinPartnerName = False
		elif self.CALLinDirection:
			self.CALLdirection[self.CALLtotal - 1] = self.CALLdirectionText
			self.CALLdirectionText = ''
			self.CALLinDirection = False
		elif self.CALLinTimeStamp:
			self.CALLtimeStamp[self.CALLtotal - 1] = self.CALLtimeStampText
			self.CALLtimeStampText = ''
			self.CALLinTimeStamp = False
		elif self.CALLinDuration:
			self.CALLduration[self.CALLtotal - 1] = self.CALLdurationText
			self.CALLdurationText = ''
			self.CALLinDuration = False
		elif self.CALLinSource:
			self.CALLsource[self.CALLtotal - 1] = self.CALLsourceText
			self.CALLsourceText = ''
			self.CALLinSource = False
		elif self.CALLinLocation:
			self.CALLlocation[self.CALLtotal - 1] = self.CALLlocationText
			self.CALLlocationText = ''
			self.CALLinLocation = False
		elif self.CALLinRecoveryMethod:
			self.CALLrecoveryMethod.append(self.CALLrecoveyMethodText)
			self.CALLrecoveyMethodText = ''
			self.CALLinRecoveryMethod = False

	def __endElementFragmentCELL_TOWER(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.CELL_TOWER_PATTERN 
		'''		
		if self.CELL_TOWERinCID:
			self.CELL_TOWERcid[self.CELL_TOWERtotal - 1] = self.CELL_TOWERcidText
			self.CELL_TOWERcidText = ''
			self.CELL_TOWERinCID = False
		elif self.CELL_TOWERinLAC:
			self.CELL_TOWERlac[self.CELL_TOWERtotal - 1] = self.CELL_TOWERlacText
			self.CELL_TOWERlacText = ''
			self.CELL_TOWERinLAC = False
		elif self.CELL_TOWERinMCC:
			self.CELL_TOWERmcc[self.CELL_TOWERtotal - 1] = self.CELL_TOWERmccText
			self.CELL_TOWERmccText = ''
			self.CELL_TOWERinMCC = False
		elif self.CELL_TOWERinMNC:
			self.CELL_TOWERmnc[self.CELL_TOWERtotal - 1] = self.CELL_TOWERmncText
			self.CELL_TOWERmncText = ''
			self.CELL_TOWERinMNC = False
		elif self.CELL_TOWERinTimeStamp:
			self.CELL_TOWERtimeStamp[self.CELL_TOWERtotal - 1] = self.CELL_TOWERtimeStampText
			self.CELL_TOWERtimeStampText = ''
			self.CELL_TOWERinTimeStamp = False
		elif self.CELL_TOWERinLatitude:
			self.CELL_TOWERlatitude[self.CELL_TOWERtotal - 1] = self.CELL_TOWERlatitudeText
			self.CELL_TOWERlatitudeText = ''
			self.CELL_TOWERinLatitude = False
		elif self.CELL_TOWERinLongitude:
			self.CELL_TOWERlongitude[self.CELL_TOWERtotal - 1] = self.CELL_TOWERlongitudeText
			self.CELL_TOWERlongitudeText = ''
			self.CELL_TOWERinLongitude = False
		elif self.CELL_TOWERinSource:
			self.CELL_TOWERsource[self.CELL_TOWERtotal - 1] = self.CELL_TOWERsourceText
			self.CELL_TOWERsourceText = ''
			self.CELL_TOWERinSource = False
		elif self.CELL_TOWERinLocation:
			self.CELL_TOWERlocation[self.CELL_TOWERtotal - 1] = self.CELL_TOWERlocationText
			self.CELL_TOWERlocationText = ''
			self.CELL_TOWERinLocation = False
		elif self.CELL_TOWERinRecoveryMethod:
			self.CELL_TOWERrecoveryMethod.append(self.CELL_TOWERrecoveryMethodText)
			self.CELL_TOWERrecoveyMethodText = ''
			self.CELL_TOWERinRecoveryMethod = False

	def __endElementFragmentCHAT(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.CHAT_PATTERN 
		'''		
		if self.CHATinSender:
			self.CHATsender[self.CHATtotal - 1] = self.CHATsenderText
			self.CHATsenderText = ''
			self.CHATinSender = False
		elif self.CHATinReceiver:
			self.CHATreceiver[self.CHATtotal - 1] = self.CHATreceiverText
			self.CHATreceiverText = ''
			self.CHATinReceiver = False
		elif self.CHATinPartner:
			self.CHATinPartner = False
		elif self.CHATinDateTimeSent:
			self.CHATinDateTimeSent = False
		elif self.CHATinDateTime:                        
			self.CHATinDateTime = False
		elif self.CHATinDateTimeReceived:
			self.CHATdateTimeReceived[self.CHATtotal - 1] = self.CHATdateTimeReceivedText
			self.CHATdateTimeReceivedText = ''
			self.CHATinDateTimeReceived = False
		elif self.CHATinMessage:
			self.CHATmessage[self.CHATtotal - 1] = self.CHATmessageText			
			self.CHATmessageText = ''
			self.CHATinMessage = False
		elif self.CHATinMessageStatus:
			self.CHATmessageStatus[self.CHATtotal - 1] = self.CHATmessageStatusText
			self.CHATmessageStatusText = ''
			self.CHATinMessageStatus = False
		elif self.CHATinMessageType:
			if self.CHATmessageTypeText.lower() == 'incoming':
				self.CHATdateTimeReceived[self.CHATtotal - 1] = self.CHATdateTimeText
			if self.CHATmessageTypeText.lower() == 'outgoing':
				self.CHATdateTimeSent[self.CHATtotal - 1] = self.CHATdateTimeText    
			self.CHATdateTimeText = ''
			self.CHATinMessageType = False
		elif self.CHATinSource:
			self.CHATsource[self.CHATtotal - 1] = self.CHATsourceText
			self.CHATsourceText = ''
			self.CHATinSource = False
#---    Facebook Messenger Messages do not have the type (Incoming/Outgoing) where
#       the Date/Time Received or Sent is set up, so if both are empty it is a Facebook
#       Message, whose Date/Time is still remained empty                        
			if  (self.CHATdateTimeSent[self.CHATtotal - 1] == '' and 
			     self.CHATdateTimeReceived[self.CHATtotal - 1] == ''):
				self.CHATdateTimeSent[self.CHATtotal - 1] = self.CHATdateTimeText
				self.CHATdateTimeText = ''
		elif self.CHATinLocation:
			self.CHATlocation[self.CHATtotal - 1] = self.CHATlocationText
			self.CHATlocationText = ''
			self.CHATinLocation = False
		elif self.CHATinRecoveryMethod:
			self.CHATrecoveryMethod[self.CHATtotal - 1] = self.CHATrecoveryMethodText
			self.CHATrecoveryMethodText = ''
			self.CHATinRecoveryMethod = False
#---    this is the last element to be processed for a CHAT, so it's possible to
#       manage 1) iOS Whatsapp Message that contains only the Message Date/Time that can
#       be for sent or received Message; 2) Telegram Messagge that contain only the
#       Creation Date/Time of the Message and the Partner so the Sender and the Receiver
#       must be determined on the base of the Message Type (incoming or outgoing)         
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
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.CONTACT_PATTERN 
		'''		
		if self.CONTACTinName:
			self.CONTACTname[self.CONTACTtotal - 1] = self.CONTACTnameText
			self.CONTACTnameText = ''
			self.CONTACTinName = False
		elif self.CONTACTinFirstName:
			name = self.CONTACTfirstNameText.replace('\n','').replace('\r','') + ' '
			self.CONTACTname[self.CONTACTtotal - 1] = name 
			self.CONTACTfirstNameText = ''
			self.CONTACTinFirstName = False
		elif self.CONTACTinLastName:
			name = self.CONTACTlastNameText.replace('\n','').replace('\r','')
			self.CONTACTname[self.CONTACTtotal - 1] += name 
			self.CONTACTlastNameText = ''
			self.CONTACTinLastName = False
		elif self.CONTACTinPhoneNumber:
			self.CONTACTphoneNumber[self.CONTACTtotal - 1] = self.CONTACTphoneNumberText
			self.CONTACTphoneNumberText = ''
			self.CONTACTinPhoneNumber = False
		elif self.CONTACTinSource:
			self.CONTACTsource[self.CONTACTtotal - 1] = self.CONTACTsourceText
			self.CONTACTsourceText = ''
			self.CONTACTinSource = False
		elif self.CONTACTinLocation:
			self.CONTACTlocation[self.CONTACTtotal - 1] = self.CONTACTlocationText
			self.CONTACTlocationText = ''
			self.CONTACTinLocation = False
		elif self.CONTACTinRecoveryMethod:
			self.CONTACTrecoveryMethod[self.CONTACTtotal - 1] = self.CONTACTrecoveryMethodText
			self.CONTACTrecoveryMethodText = ''
			self.CONTACTinRecoveryMethod = False

	def __endElementFragmentDEVICE(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.DEVICE_PATTERN 
		'''		
		if self.DEVICEinSerialNumber:            
			self.DEVICEinSerialNumber = False
		elif self.DEVICEinId:
			self.DEVICEinId = False
		elif self.DEVICEinName:
			self.DEVICEinName = False
		elif self.DEVICEinImsi:
			self.DEVICEinImsi = False
		elif self.DEVICEinImei:
			self.DEVICEinImei = False
		elif self.DEVICEinModel:
			self.DEVICEinModel = False
		elif self.DEVICEinOsVersion:
			self.DEVICEinOsVersion = False
		elif self.DEVICEinIccid:
			self.DEVICEinIccid = False
		elif self.DEVICEinBluetoothAddress:
			self.DEVICEinBluetoothAddress = False
		elif self.DEVICEinBluetoothName:
			self.DEVICEinBluetoothName = False

	def __endElementFragmentCOOKIE(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.COOKIE_PATTERN 
		'''		
		if self.COOKIEinName:
			self.COOKIEname[self.COOKIEtotal - 1] = self.COOKIEnameText
			self.COOKIEnameText = ''
			self.COOKIEinName = False
		elif self.COOKIEinPath:
			self.COOKIEpath[self.COOKIEtotal - 1] = self.COOKIEpathText
			self.COOKIEpathText = ''
			self.COOKIEinPath = False
		elif self.COOKIEinDomain:
			self.COOKIEdomain[self.COOKIEtotal - 1] = self.COOKIEdomainText
			self.COOKIEdomainText = ''
			self.COOKIEinDomain = False
		elif self.COOKIEinCreatedDate:
			self.COOKIEcreatedDate[self.COOKIEtotal - 1] = self.COOKIEcreatedDateText
			self.COOKIEcreatedDateText = ''
			self.COOKIEinCreatedDate = False
		elif self.COOKIEinAccessedDate:
			self.COOKIEaccessedDate[self.COOKIEtotal - 1] = self.COOKIEaccessedDateText
			self.COOKIEaccessedDateText = ''
			self.COOKIEinAccessedDate = False
		elif self.COOKIEinExpirationDate:
			self.COOKIEexpirationDate[self.COOKIEtotal - 1] = self.COOKIEexpirationDateText
			self.COOKIEexpirationDateText = ''
			self.COOKIEinExpirationDate = False
		elif self.COOKIEinSource:
			self.COOKIEsource[self.COOKIEtotal - 1] = self.COOKIEsourceText
			self.COOKIEsourceText = ''
			self.COOKIEinSource = False
		elif self.COOKIEinLocation:
			self.COOKIElocation[self.COOKIEtotal - 1] = self.COOKIElocationText
			self.COOKIElocationText = ''
			self.COOKIEinLocation = False
		elif self.COOKIEinRecoveryMethod:
			self.COOKIErecoveryMethod[self.COOKIEtotal - 1] = self.COOKIErecoveryMethodText
			self.COOKIErecoveryMethodText = ''
			self.COOKIEinRecoveryMethod = False

	def __endElementFragmentEVENT_APP_USE(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.EVENT_APP_USE_PATTERN 
		'''		
		if self.EVENT_APP_USEinStartTime:
			self.EVENT_APP_USEstartTime[self.EVENT_APP_USEtotal - 1] = \
			    self.EVENT_APP_USEstartTimeText
			self.EVENT_APP_USEstartTimeText = ''
			self.EVENT_APP_USEinStartTime = False
		elif self.EVENT_APP_USEinEndTime:
			self.EVENT_APP_USEendTime[self.EVENT_APP_USEtotal - 1] = \
			    self.EVENT_APP_USEendTimeText
			self.EVENT_APP_USEendTimeText = ''
			self.EVENT_APP_USEinEndTime = False
		elif self.EVENT_APP_USEinApplication:
			self.EVENT_APP_USEapplication[self.EVENT_APP_USEtotal - 1] = \
			    self.EVENT_APP_USEapplicationText
			self.EVENT_APP_USEapplicationText = ''
			self.EVENT_APP_USEinApplication = False
		elif self.EVENT_APP_USEinSource:
			self.EVENT_APP_USEsource[self.EVENT_APP_USEtotal - 1] = \
			    self.EVENT_APP_USEsourceText
			self.EVENT_APP_USEsourceText = ''
			self.EVENT_APP_USEinSource = False
		elif self.EVENT_APP_USEinLocation:
			self.EVENT_APP_USElocation[self.EVENT_APP_USEtotal - 1] = \
			    self.EVENT_APP_USElocationText
			self.EVENT_APP_USElocationText = ''
			self.EVENT_APP_USEinLocation = False
		elif self.EVENT_APP_USEinRecoveryMethod:
			self.EVENT_APP_USErecoveryMethod[self.EVENT_APP_USEtotal - 1] = \
			    self.EVENT_APP_USErecoveryMethodText
			self.EVENT_APP_USErecoveryMethodText = ''
			self.EVENT_APP_USEinRecoveryMethod = False

	def __endElementFragmentEVENT_LOCK(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.EVENT_LOCK_PATTERN 
		'''		
		if self.EVENT_LOCKinDateTime:
			self.EVENT_LOCKdateTime[self.EVENT_LOCKtotal - 1] = self.EVENT_LOCKdateTimeText
			self.EVENT_LOCKdateTimeText = ''
			self.EVENT_LOCKinDateTime = False
		elif self.EVENT_LOCKinDeviceStatus:
			self.EVENT_LOCKdeviceStatus[self.EVENT_LOCKtotal - 1] = \
			    self.EVENT_LOCKdeviceStatusText
			self.EVENT_LOCKdeviceStatusText = ''
			self.EVENT_LOCKinDeviceStatus = False
		elif self.EVENT_LOCKinSource:
			self.EVENT_LOCKsource[self.EVENT_LOCKtotal - 1] = self.EVENT_LOCKsourceText
			self.EVENT_LOCKsourceText = ''
			self.EVENT_LOCKinSource = False
		elif self.EVENT_LOCKinLocation:
			self.EVENT_LOCKlocation[self.EVENT_LOCKtotal - 1] = self.EVENT_LOCKlocationText
			self.EVENT_LOCKlocationText = ''
			self.EVENT_LOCKinLocation = False
		elif self.EVENT_LOCKinRecoveryMethod:
			self.EVENT_LOCKrecoveryMethod[self.EVENT_LOCKtotal - 1] = \
			    self.EVENT_LOCKrecoveryMethodText
			self.EVENT_LOCKrecoveryMethodText = ''
			self.EVENT_LOCKinRecoveryMethod = False

	def __endElementFragmentEMAIL(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.EMAIL_PATTERN 
		'''		
		if self.EMAILinSender:
			self.EMAILsender[self.EMAILtotal - 1] = self.EMAILsenderText
			self.EMAILsenderText = ''
			self.EMAILinSender = False
		elif self.EMAILinRecipients:
			self.EMAILrecipient[self.EMAILtotal - 1] = self.EMAILrecipientText
			self.EMAILrecipientText = ''
			self.EMAILinRecipients = False
		elif self.EMAILinCC:
			self.EMAILcc[self.EMAILtotal - 1] = self.EMAILccText
			self.EMAILccText = ''
			self.EMAILinCC = False
		elif self.EMAILinBCC:
			self.EMAILbcc[self.EMAILtotal - 1] = self.EMAILbccText
			self.EMAILbccText = ''
			self.EMAILinBCC = False
		elif self.EMAILinDateTime:
#---    Some Artifcats have the Sent and the Received Date/Time, one of them
#       is always empty   
			if self.EMAILdateTimeText != '':
				self.EMAILdateTime[self.EMAILtotal - 1] = self.EMAILdateTimeText
			self.EMAILdateTimeText = ''
			self.EMAILinDateTime = False
		elif self.EMAILinSubject:
			self.EMAILsubject[self.EMAILtotal - 1] = self.EMAILsubjectText
			self.EMAILsubjectText = ''
			self.EMAILinSubject = False
		elif self.EMAILinBody:
			self.EMAILbody[self.EMAILtotal - 1] = self.EMAILbodyText
			self.EMAILbodyText = ''
			self.EMAILinBody = False
		elif self.EMAILinAttachment:
			self.EMAILattachment[self.EMAILtotal - 1] = self.EMAILattachmentText
			self.EMAILattachmentText = ''
			self.EMAILinAttachment = False
		elif self.EMAILinSource:
			self.EMAILsource[self.EMAILtotal - 1] = self.EMAILsourceText
			self.EMAILsourceText = ''
			self.EMAILinSource = False
		elif self.EMAILinLocation:
			self.EMAILlocation[self.EMAILtotal - 1] = self.EMAILlocationText
			self.EMAILlocationText = ''
			self.EMAILinLocation = False
		elif self.EMAILinRecoveryMethod:
			self.EMAILrecoveryMethod[self.EMAILtotal - 1] = self.EMAILrecoveryMethodText
			self.EMAILrecoveryMethodText = ''
			self.EMAILinRecoveryMethod = False

	def __endElementFragmentFILE(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.FILE_PATTERN 
		'''		
		if self.FILEinTag:
			self.FILEtag[self.FILEtotal - 1] =  self.FILEtagText
			self.FILEtagText = ''
			self.FILEinTag = False
		elif self.FILEinFileName:
			if self.FILEfileName[self.FILEtotal - 1] == '':
				self.FILEfileName[self.FILEtotal - 1] =  self.FILEfileNameText
				self.FILEfileNameText = self.FILEfileNameText.replace('\\', '/')
				last_slash = self.FILEfileNameText.rfind('/')
				fileName = self.FILEfileNameText
				if last_slash > -1:
					fileName  = self.FILEfileNameText[last_slash + 1:]
				self.FILEfileLocalPath[self.FILEtotal - 1] = os.path.join(self.FILEbaseLocalPath, fileName)
			self.FILEfileNameText = ''
			self.FILEinFileName = False 
		elif self.FILEinImage:
			self.FILEimage[self.FILEtotal - 1] =  self.FILEimageText
			self.FILEimageText = self.FILEimageText.replace('\\', '/')
			last_slash = self.FILEimageText.rfind('/')
			fileName = ''
			if last_slash > -1:
				fileName  = self.FILEimageText[last_slash + 1:]
			self.FILEfileLocalPath[self.FILEtotal - 1] =  os.path.join(self.FILEbaseLocalPath, fileName)
			self.FILEimageText = ''
			self.FILEinImage = False 
		elif self.FILEinFileExtension:
			self.FILEfileExtension[self.FILEtotal - 1] =  self.FILEfileExtensionText
			self.FILEfileExtensionText = ''
			self.FILEinFileExtension = False 
		elif self.FILEinFileSize:
			self.FILEfileSize[self.FILEtotal - 1] =  self.FILEfileSizeText
			self.FILEfileSizeText = ''
			self.FILEinFileSize = False 
		elif self.FILEinCreated:
			self.FILEcreated[self.FILEtotal - 1] =  self.FILEcreatedText
			self.FILEcreatedText = ''
			self.FILEinCreated = False 
		elif self.FILEinModified:
			self.FILEmodified[self.FILEtotal - 1] =  self.FILEmodifiedText
			self.FILEmodifiedText = ''
			self.FILEinModified = False 
		elif self.FILEinAccessed:
			self.FILEaccessed[self.FILEtotal - 1] =  self.FILEaccessedText
			self.FILEaccessedText = ''
			self.FILEinAccessed = False 
		elif self.FILEinMD5:
			self.FILEmd5[self.FILEtotal - 1] =  self.FILEmd5Text
			self.FILEmd5Text = ''
			self.FILEinMD5 = False 
		elif self.FILEinExifMake:
			self.FILEexifMake[self.FILEtotal - 1] =  self.FILEexifMakeText
			self.FILEexifMakeText = ''
			self.FILEinExifMake = False 
		elif self.FILEinExifModel:
			self.FILEexifModel[self.FILEtotal - 1] =  self.FILEexifModelText
			self.FILEexifModelText = ''
			self.FILEinExifModel = False 
		elif self.FILEinExifLatitude:
			self.FILEexifLatitude[self.FILEtotal - 1] =  self.FILEexifLatitudeText
			self.FILEexifLatitudeText = ''
			self.FILEinExifLatitude = False
		elif self.FILEinExifLatitudeRef:
			self.FILEexifLatitudeRef[self.FILEtotal - 1] =  self.FILEexifLatitudeRefText
			self.FILEexifLatitudeRefText = ''
			self.FILEinExifLatitudeRef = False
		elif self.FILEinExifLongitude:
			self.FILEexifLongitude[self.FILEtotal - 1] =  self.FILEexifLongitudeText
			self.FILEexifLongitudeText = ''
			self.FILEinExifLongitude = False
		elif self.FILEinExifLongitudeRef:
			self.FILEexifLongitudeRef[self.FILEtotal - 1] =  self.FILEexifLongitudeRefText
			self.FILEexifLongitudeRefText = ''
			self.FILEinExifLongitudeRef = False
		elif self.FILEinExifAltitude:
			self.FILEexifAltitude[self.FILEtotal - 1] =  self.FILEexifAltitudeText
			self.FILEexifAltitudeText = ''
			self.FILEinExifAltitude = False
		elif self.FILEinSource:
			self.FILEsource[self.FILEtotal - 1] =  self.FILEsourceText
			self.FILEsourceText = ''
			self.FILEinSource = False 
		elif self.FILEinLocation:
			self.FILElocation[self.FILEtotal - 1] =  self.FILElocationText
			self.FILElocationText = ''
			self.FILEinLocation = False 
		elif self.FILEinRecoveryMethod:
			self.FILErecoveryMethod[self.FILEtotal - 1] =  self.FILErecoveryMethodText
			self.FILErecoveryMethodText = ''
			self.FILEinRecoveryMethod = False 

	def __endElementFragmentFILE_SYS_INFO(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.FILE_SYS_INFO_PATTERN 
		'''		
		if self.FILE_SYS_INFOinVolumeSn:
			self.FILE_SYS_INFOvolumeSn[self.FILE_SYS_INFOtotal - 1] = self.FILE_SYS_INFOvolumeSnText
			self.FILE_SYS_INFOvolumeSnText = ''
			self.FILE_SYS_INFOinVolumeSn = False
		elif self.FILE_SYS_INFOinFileSystem:
			self.FILE_SYS_INFOfileSystem[self.FILE_SYS_INFOtotal - 1] = self.FILE_SYS_INFOfileSystemText
			self.FILE_SYS_INFOfileSystemText = ''
			self.FILE_SYS_INFOinFileSystem = False
		elif self.FILE_SYS_INFOinCapacity:
			self.FILE_SYS_INFOcapacity[self.FILE_SYS_INFOtotal - 1] = self.FILE_SYS_INFOcapacityText
			self.FILE_SYS_INFOcapacityText = ''
			self.FILE_SYS_INFOinCapacity = False
		elif self.FILE_SYS_INFOinUnallocated:
			self.FILE_SYS_INFOunallocated[self.FILE_SYS_INFOtotal - 1] = self.FILE_SYS_INFOunallocatedText
			self.FILE_SYS_INFOunallocatedText = ''
			self.FILE_SYS_INFOinUnallocated = False
		elif self.FILE_SYS_INFOinAllocated:
			self.FILE_SYS_INFOallocated[self.FILE_SYS_INFOtotal - 1] = self.FILE_SYS_INFOallocatedText
			self.FILE_SYS_INFOallocatedText = ''
			self.FILE_SYS_INFOinAllocated = False
		elif self.FILE_SYS_INFOinOffest:
			self.FILE_SYS_INFOoffset[self.FILE_SYS_INFOtotal - 1] = self.FILE_SYS_INFOoffsetText
			self.FILE_SYS_INFOoffsetText = ''
			self.FILE_SYS_INFOinOffest = False

	def __endElementFragmentLOCATION(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.LOCATION_PATTERN 
		'''		
		if self.LOCATIONinType:
			self.LOCATIONinType = False
			self.LOCATIONtype[self.LOCATIONtotal - 1] = self.LOCATIONtypeText
			self.LOCATIONtypeText = ''
		elif self.LOCATIONinCreated:
			self.LOCATIONinCreated = False
			self.LOCATIONcreated[self.LOCATIONtotal - 1] = self.LOCATIONcreatedText
			self.LOCATIONcreatedText = ''
		elif self.LOCATIONinLatitude:
			self.LOCATIONinLatitude = False
			self.LOCATIONlatitude[self.LOCATIONtotal - 1] = self.LOCATIONlatitudeText
			self.LOCATIONlatitudeText = ''
		elif self.LOCATIONinLongitude:
			self.LOCATIONinLongitude = False
			self.LOCATIONlongitude[self.LOCATIONtotal - 1] = self.LOCATIONlongitudeText
			self.LOCATIONlongitudeText = ''
		elif self.LOCATIONinSource:
			self.LOCATIONsource[self.LOCATIONtotal - 1] = self.LOCATIONsourceText
			self.LOCATIONsourceText = ''
			self.LOCATIONinSource = False
		elif self.LOCATIONinLocation:
			self.LOCATIONlocation[self.LOCATIONtotal - 1] = self.LOCATIONlocationText
			self.LOCATIONlocationText = ''
			self.LOCATIONinLocation = False
		elif self.LOCATIONinRecoveryMethod:
			self.LOCATIONrecoveryMethod[self.LOCATIONtotal - 1] = self.LOCATIONrecoveryMethodText
			self.LOCATIONrecoveryMethodText = ''
			self.LOCATIONinRecoveryMethod = False 

	def __endElementFragmentSEARCHED_ITEM(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.SEARCHED_ITEM_PATTERN 
		'''		
		if self.SEARCHED_ITEMinValue:
			self.SEARCHED_ITEMinValue = False
			self.SEARCHED_ITEMvalue[self.SEARCHED_ITEMtotal - 1] = self.SEARCHED_ITEMvalueText
			self.SEARCHED_ITEMvalueText = ''
		elif self.SEARCHED_ITEMinTimeStamp:
			self.SEARCHED_ITEMinTimeStamp = False
			self.SEARCHED_ITEMtimeStamp[self.SEARCHED_ITEMtotal - 1] = self.SEARCHED_ITEMtimeStampText
			self.SEARCHED_ITEMtimeStampText = ''
		elif self.SEARCHED_ITEMinAppSource:
			self.SEARCHED_ITEMappSource[self.SEARCHED_ITEMtotal - 1] = self.SEARCHED_ITEMappSourceText
			self.SEARCHED_ITEMappSourceText = ''
			self.SEARCHED_ITEMinAppSource = False
		elif self.SEARCHED_ITEMinSource:
			self.SEARCHED_ITEMsource[self.SEARCHED_ITEMtotal - 1] = self.SEARCHED_ITEMsourceText
			self.SEARCHED_ITEMsourceText = ''
			self.SEARCHED_ITEMinSource = False
		elif self.SEARCHED_ITEMinLocation:
			self.SEARCHED_ITEMlocation[self.SEARCHED_ITEMtotal - 1] = self.SEARCHED_ITEMlocationText
			self.SEARCHED_ITEMlocationText = ''
			self.SEARCHED_ITEMinLocation = False
		elif self.SEARCHED_ITEMinRecoveryMethod:
			self.SEARCHED_ITEMrecoveryMethod[self.SEARCHED_ITEMtotal - 1] = self.SEARCHED_ITEMrecoveryMethodText
			self.SEARCHED_ITEMrecoveryMethodText = ''
			self.SEARCHED_ITEMinRecoveryMethod = False            

	def __endElementFragmentSMS(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.SMS_PATTERN 
		'''		
		if self.SMSinPartner:
			self.SMSinPartner = False
		elif self.SMSinRecipient:
			self.SMSrecipient[self.SMStotal - 1] = self.SMSrecipientText                    
			self.SMSrecipientText = ''            
			self.SMSinRecipient = False
		elif self.SMSinSender:
			self.SMSsender[self.SMStotal - 1] = self.SMSsenderText
			self.SMSsenderText = ''
			self.SMSinSender = False
		elif self.SMSinReceivedDateTime:
			self.SMSreceivedDateTime[self.SMStotal - 1] = self.SMSreceivedDateTimeText        
			self.SMSreceivedDateTimeText = ''
			self.SMSinReceivedDateTime = False
		elif self.SMSinSentDateTime:
			self.SMSsentDateTime[self.SMStotal - 1] = self.SMSsentDateTimeText        
			self.SMSsentDateTimeText = ''
			self.SMSinSentDateTime = False
		elif self.SMSinMessage:
			self.SMSmessage[self.SMStotal - 1] = self.SMSmessageText                    
			self.SMSmessageText = ''
			self.SMSinMessage = False
		elif self.SMSinDirection:
			self.SMSinDirection = False
		elif self.SMSinSource:
			self.SMSsource[self.SMStotal - 1] = self.SMSsourceText
			self.SMSsourceText = ''
			self.SMSinSource = False
		elif self.SMSinLocation:
			self.SMSlocation[self.SMStotal - 1] = self.SMSlocationText
			self.SMSlocationText = ''
			self.SMSinLocation = False
		elif self.SMSinRecoveryMethod:
			self.SMSrecoveryMethod[self.SMStotal - 1] = self.SMSrecoveryMethodText
			self.SMSrecoveryMethodText = ''
			self.SMSinRecoveryMethod = False            

#---    Android SMS includes the Partner element.
#       iOS iMessage/SMS/MMS includes the Sender and Recipient(s) elements and the
#       Incoming from Outgoing messages are identified by Received Date/time or Sent Date/Time                 
#       only the Message Sent Date/Time is set, so in case elements           
			if self.SMSpartnerText != '':
				if self.SMSdirectionText.lower() == 'outgoing':                    
					self.SMSsender[self.SMStotal - 1] = self.CALLphoneNumberDevice
					self.SMSrecipient[self.SMStotal - 1] = self.SMSpartnerText                    
				else:
					self.SMSsender[self.SMStotal - 1] = self.SMSpartnerText
					self.SMSrecipient[self.SMStotal - 1] = self.CALLphoneNumberDevice                    
				self.SMSpartnerText = ''
				self.SMSdirectionText = ''                

	def __endElementFragmentWEB(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.WEB_PATTERN 
		'''		
		if self.WEBinUrl:
			self.WEBurl[self.WEBtotal - 1] = self.WEBurlText        
			self.WEBurlText = ''
			self.WEBinUrl = False
		elif self.WEBinLastVisited:
			self.WEBlastVisited[self.WEBtotal - 1] = self.WEBlastVisitedText        
			self.WEBlastVisitedText = ''
			self.WEBinLastVisited = False
		elif self.WEBinTitle:
			self.WEBtitle[self.WEBtotal - 1] = self.WEBtitleText        
			self.WEBtitleText = ''
			self.WEBinTitle = False
		elif self.WEBinVisitCount:
			self.WEBvisitCount[self.WEBtotal - 1] = self.WEBvisitCountText        
			self.WEBvisitCountText = ''
			self.WEBinVisitCount = False
		elif self.WEBinSource:
			self.WEBsource[self.WEBtotal - 1] = self.WEBsourceText
			self.WEBsourceText = ''
			self.WEBinSource = False
		elif self.WEBinLocation:
			self.WEBlocation[self.WEBtotal - 1] = self.WEBlocationText
			self.WEBlocationText = ''
			self.WEBinLocation = False
		elif self.WEBinRecoveryMethod:
			self.WEBrecoveryMethod[self.WEBtotal - 1] = self.WEBrecoveryMethodText
			self.WEBrecoveryMethodText = ''
			self.WEBinRecoveryMethod = False

	def __endElementFragmentWIRELESS_NET(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.WIRELESS_NET_PATTERN 
		'''		
		if self.WIRELESS_NETinMacAaddress:
			self.WIRELESS_NETmacAddress[self.WIRELESS_NETtotal - 1] = \
			    self.WIRELESS_NETmacAddressText
			self.WIRELESS_NETmacAddressText = ''
			self.WIRELESS_NETinMacAaddress = False
		elif self.WIRELESS_NETinChannel:
			self.WIRELESS_NETchannel[self.WIRELESS_NETtotal - 1] = \
			    self.WIRELESS_NETchannelText
			self.WIRELESS_NETchannelText = ''
			self.WIRELESS_NETinChannel = False
		elif self.WIRELESS_NETinTimeStamp:
			self.WIRELESS_NETtimeStamp[self.WIRELESS_NETtotal - 1] = \
			    self.WIRELESS_NETtimeStampText
			self.WIRELESS_NETtimeStampText = ''
			self.WIRELESS_NETinTimeStamp = False
		elif self.WIRELESS_NETinLatitude:
			self.WIRELESS_NETlatitude[self.WIRELESS_NETtotal - 1] = \
			    self.WIRELESS_NETlatitudeText
			self.WIRELESS_NETlatitudeText = ''
			self.WIRELESS_NETinLatitude = False
		elif self.WIRELESS_NETinLongitude:
			self.WIRELESS_NETlongitude[self.WIRELESS_NETtotal - 1] = \
			    self.WIRELESS_NETlongitudeText
			self.WIRELESS_NETlongitudeText = ''
			self.WIRELESS_NETinLongitude = False
		elif self.WIRELESS_NETinAccuracy:
			self.WIRELESS_NETaccuracy[self.WIRELESS_NETtotal - 1] = \
			    self.WIRELESS_NETaccuracyText
			self.WIRELESS_NETaccuracyText = ''
			self.WIRELESS_NETinAccuracy = False
		elif self.WIRELESS_NETinSource:
			self.WIRELESS_NETsource[self.WIRELESS_NETtotal - 1] = \
			    self.WIRELESS_NETsourceText
			self.WIRELESS_NETsourceText = ''
			self.WIRELESS_NETinSource = False
		elif self.WIRELESS_NETinLocation:
			self.WIRELESS_NETlocation[self.WIRELESS_NETtotal - 1] = \
			    self.WIRELESS_NETlocationText
			self.WIRELESS_NETlocationText = ''
			self.WIRELESS_NETinLocation = False
		elif self.WIRELESS_NETinRecoveryMethod:
			self.WIRELESS_NETrecoveryMethod[self.WIRELESS_NETtotal - 1] = \
			    self.WIRELESS_NETrecoveryMethodText
			self.WIRELESS_NETrecoveryMethodText = ''
			self.WIRELESS_NETinRecoveryMethod = False

	def __endElementFragmentWIN_TIMELINE(self):
		'''
		It captures the closing of the XML Element matching with the XPath expression
		//Artifact[@name="artifact_name]//Fragment[@name="..."] with artifact_name in self.WIN_TIMELINE_PATTERN 
		'''		
		if self.WIN_TIMELINEinAppName:
			self.WIN_TIMELINEappName[self.WIN_TIMELINEtotal - 1] = self.WIN_TIMELINEappNameText
			self.WIN_TIMELINEappNameText = ''
			self.WIN_TIMELINEinAppName = False
		elif self.WIN_TIMELINEinActivityType:
			self.WIN_TIMELINEactivityType[self.WIN_TIMELINEtotal - 1] = self.WIN_TIMELINEactivityTypeText
			self.WIN_TIMELINEactivityTypeText = ''
			self.WIN_TIMELINEinActivityType = False
		elif self.WIN_TIMELINEinTimeStamp:
			self.WIN_TIMELINEtimeStamp[self.WIN_TIMELINEtotal - 1] = self.WIN_TIMELINEtimeStampText
			self.WIN_TIMELINEtimeStampText = ''
			self.WIN_TIMELINEinTimeStamp = False
		elif self.WIN_TIMELINEinSource:
			self.WIN_TIMELINEsource[self.WIN_TIMELINEtotal - 1] = self.WIN_TIMELINEsourceText
			self.WIN_TIMELINEsourceText = ''
			self.WIN_TIMELINEinSource = False
		elif self.WIN_TIMELINEinLocation:
			self.WIN_TIMELINElocation[self.WIN_TIMELINEtotal - 1] = self.WIN_TIMELINElocationText
			self.WIN_TIMELINElocationText = ''
			self.WIN_TIMELINEinLocation = False
		elif self.WIN_TIMELINEinRecoveryMethod:
			self.WIN_TIMELINErecoveryMethod[self.WIN_TIMELINEtotal - 1] = self.WIN_TIMELINErecoveryMethodText
			self.WIN_TIMELINErecoveryMethodText = ''
			self.WIN_TIMELINEinRecoveryMethod = False

	def endElement(self, name):
		'''
		It captures the closure of any XML Element, the method is included in the SAXparser class
			:return:  None.
		''' 		
		if name == 'Fragment':
			self.__endElementFragmentPHONE_NUM()
			if self.CALLin:
				self.__endElementFragmentCALL()
			elif self.CELL_TOWERin:
				self.__endElementFragmentCELL_TOWER()
			elif self.CHATin:
				self.__endElementFragmentCHAT()
			elif self.CONTACTin:
				self.__endElementFragmentCONTACT()
			elif self.COOKIEin:
				self.__endElementFragmentCOOKIE()
			elif self.DEVICEin:
				self.__endElementFragmentDEVICE()
			elif self.FILEin:
				self.__endElementFragmentFILE()
			elif self.EMAILin:
				self.__endElementFragmentEMAIL()
			elif self.EVENT_LOCKin:
				self.__endElementFragmentEVENT_LOCK()
			elif self.EVENT_APP_USEin:
				self.__endElementFragmentEVENT_APP_USE()
			elif self.FILE_SYS_INFOin:
				self.__endElementFragmentFILE_SYS_INFO()
			elif self.LOCATIONin:
				self.__endElementFragmentLOCATION()
			elif self.SEARCHED_ITEMin:
				self.__endElementFragmentSEARCHED_ITEM()
			elif self.SMSin:
				self.__endElementFragmentSMS()
			elif self.WEBin:
				self.__endElementFragmentWEB()
			elif self.WIN_TIMELINEin:
				self.__endElementFragmentWIN_TIMELINE()            
			elif self.WIRELESS_NETin:
				self.__endElementFragmentWIRELESS_NET()
		elif name == 'Hit':
			if self.inHit:
				self.inHit = False
		elif name == 'Artifact':
			if self.CALLin:
				self.CALLin = False
				self.Observable = False
			elif self.CALL_PHONE_NUM_DEVICEin:
				self.CALL_PHONE_NUM_DEVICEin = False
				self.Observable = False
			elif self.CELL_TOWERin:
				self.CELL_TOWERin = False
				self.Observable = False
			elif self.CHATin:
				self.CHATin = False
				self.Observable = False
			elif self.CONTACTin:
				self.CONTACTin = False
				self.Observable = False
			elif self.COOKIEin:
				self.COOKIEin = False
				self.Observable = False
			elif self.DEVICEin:
				self.DEVICEin = False
				self.Observable = False
			elif self.EVENT_LOCKin:
				self.EVENT_LOCKin = False
				self.Observable = False
			elif self.EVENT_APP_USEin:
				self.EVENT_APP_USEin = False
				self.Observable = False
			elif self.EMAILin:
				self.EMAILin = False
				self.Observable = False
			elif self.FILEin:
				self.FILEin = False
				self.Observable = False                        
			elif self.FILE_SYS_INFOin:
				self.FILE_SYS_INFOin = False
				self.Observable = False
			elif self.LOCATIONin:
				self.LOCATIONin = False
				self.Observable = False
			elif self.SEARCHED_ITEMin:
				self.SEARCHED_ITEMin = False
				self.Observable = False 
			elif self.SMSin:
				self.SMSin = False
				self.Observable = False 
			elif self.WEBin:
				self.WEBin = False
				self.Observable = False
			elif self.WIRELESS_NETin:
				self.WIRELESS_NETin = False
				self.Observable = False
			elif self.WIN_TIMELINEin:
				self.WIN_TIMELINEin = False
				self.Observable = False               

#---    it captures the value/character inside the Text Elements
	def characters(self, ch):        
		'''
		It captures the the CDATA (text) enclosed in any XML Element matching with the XPath expression
		//Artifact//Fragment[@name="..."]
		    :param ch: The text enclosed in the ELement (string)
			:return:  None.
		'''		
		if self.CALLin:
			self.__charactersCALL(ch)           
		elif self.CELL_TOWERin:
			self.__charactersCELL_TOWER(ch)
		elif self.CALL_PHONE_NUM_DEVICE_VALUEin:            
			if self.CALLphoneNumberDevice == 'DEVICE_PHONE_NUMBER':
				self.CALLphoneNumberDevice = ch
		elif self.CALL_PHONE_NAME_DEVICE_VALUEin:            
			self.CALLphoneNameDevice += ch
		elif self.CHATin:
			self.__charactersCHAT(ch)
		elif self.CONTACTin:
			self.__charactersCONTACT(ch)
		elif self.COOKIEin:
			self.__charactersCOOKIE(ch)
		elif self.DEVICEin:
			self.__charactersDEVICE(ch)
		elif self.EMAILin:
			self.__charactersEMAIL(ch)
		elif self.EVENT_LOCKin:
			self.__charactersEVENT_LOCK(ch)
		elif self.EVENT_APP_USEin:
			self.__charactersEVENT_APP_USE(ch)
		elif self.FILEin:
			self.__charactersFILE(ch)
		elif self.FILE_SYS_INFOin:
			self.__charactersFILE_SYS_INFO(ch)
		elif self.LOCATIONin:
			self.__charactersLOCATION(ch)
		elif self.SEARCHED_ITEMin:
			self.__charactersSEARCHED_ITEM(ch)
		elif self.SMSin:
			self.__charactersSMS(ch)
		elif self.WEBin:
			self.__charactersWEB(ch)
		elif self.WIRELESS_NETin:
			self.__charactersWIRELESS_NET(ch)
		elif self.WIN_TIMELINEin:
			self.__charactersWIN_TIMELINE(ch)            

if __name__ == '__main__':

	C_CYAN = '\033[36m'
	C_BLACK = '\033[0m'
#--- debug: ctime processing
	parserArgs = argparse.ArgumentParser(description='Parser to convert XML Report from AXIOM Process into CASE-JSON-LD standard.')

#---    report XML exported by AXIOM to be converted/parsed into CASE
	parserArgs.add_argument('-r', '--report', dest='inFileXML', required=True, 
	                        help='The AXIOM XML report from which to extract digital traces and convert them into CASE; it supports AXIOM Process version from 3.4 to 4.01')


#---    Type of device mobile or disk (HD, USB, SD, etc)
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
	print('\n\n' + C_CYAN + '*** Start processing: ' + strftime("%Y-%m-%d %H:%M:%S", localtime()) + C_BLACK + '\n')

#---    baseLocalPath is for setting the fileLocalPath property of FileFacet 
#       Observable. 
	baseLocalPath = ''

	parser = AXIOMparser(report_xml=args.inFileXML, json_output=args.outCASE_JSON, 
	                     report_type=args.inTypeEvidence, base_local_path=baseLocalPath, verbose=True) 

	Handler = parser.processXmlReport()    

	if args.outputDebug is None:
		pass
	else:
		import _AXIOMdebug
		debug = _AXIOMdebug.ParserDebug(args.outputDebug)
		debug.writeDebugCALL(Handler)
		debug.writeDebugCHAT(Handler)
		debug.writeDebugCONTACT(Handler)
		debug.writeDebugFILE(Handler)
		debug.writeDebugEMAIL(Handler)
		debug.writeDebugSMS(Handler)
		debug.writeDebugWEB(Handler)
		debug.closeDebug() 

	parser.show_elapsed_time(parser.tic_start, 'End processing')
