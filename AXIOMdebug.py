import codecs

#---	class ParserDebug.py
class ParserDebug:
	def __init__(self, debugFile):
		self.dFileName = debugFile
		self.dFileHandle = codecs.open(self.dFileName, 'w', encoding='utf8')

		self.C_cyan = '\033[36m'
		self.C_end = '\033[0m'

	def extractFileInfo(self, source):
		
		filePath = ''

		charSeparator = '/'
		separator = source.find(charSeparator)
		if separator > - 1:
			filePath = source[separator:]
			charSeparator = '/'
		else:
			charSeparator = '\\'
			separator = source.find(charSeparator)
			filePath = source[separator:]
			

		fileName = filePath.split(charSeparator)[-1]
		fileExt = fileName[fileName.rfind('.') + 1:]

		openPar = source.find('(')
		closePar = source.find(')')
		fileSystemType = source[openPar + 1: closePar]

		return (fileName + ' @' + filePath + ' @' + fileExt + ' @' + fileSystemType)




	def writeDebugFILE(self, data):	
		line = "\n*---\nTotal FILE/PICTURE (deleted?)  " + str(data.FILEtotal)
		line += '\n*---'		    	
		self.dFileHandle.write(line)		

		for i in range(data.FILEtotal):
			
			line = '[Tag] ' + data.FILEtag[i]  + '\n'        
			if data.FILEfileName[i] == 'EMPTY':
				line += '[File image] ' + data.FILEimage[i]  + '\n'        
			else:
				line += '[File name] ' + data.FILEfileName[i]  + '\n'        
			line += '[File extension] ' + data.FILEfileExtension[i]  + '\n'        
			line += '[File size] ' + data.FILEfileSize[i]  + '\n'        
			line += '[created] ' + data.FILEcreated[i]  + '\n'        
			line += '[modified] ' + data.FILEmodified[i]  + '\n'        
			line += '[accessed] ' + data.FILEaccessed[i]  + '\n'        
			line += '[md5] ' + data.FILEmd5[i]  + '\n'        
			line += '[source] '  + self.extractFileInfo(data.FILEsource[i]) + '\n'        
			line += '[location] ' + data.FILElocation[i]  + '\n'        
			line += '[Recovery Method] ' + data.FILErecoveryMethod[i]  + '\n'        
			self.dFileHandle.write(line)    
      

	def writeDebugCALL(self, data):    
		print(self.C_cyan + '\n DEVICE PHONE NUM:' + data.CALLphoneNumberDevice + '\n\n' + self.C_end)
		line = "\n*---\nTotal CALL (deleted?)  " + str(data.CALLtotal)
		#line += ' (' + str(data.CALLdeleted) + ')'
		line += '\n*---'		
		self.dFileHandle.write(line)
		#print("DEBUG --- CALLappName: ")
		#print(data.CALLappName)
		for i in range(data.CALLtotal):			
			if data.CALLdirection[i].lower() == 'incoming':
				phoneTO = data.CALLphoneNumberDevice
				phoneFROM = data.CALLpartner[i]
			else:
				phoneTO = data.CALLpartner[i]
				phoneFROM = data.CALLphoneNumberDevice

			line = '\n[id] ' + data.CALLid[i]
			line += '\n\t[partnerFROM] ' + phoneFROM
			line += '\n\t[partnerTO] ' + phoneTO
			line += '\n\t[direction] ' + data.CALLdirection[i]
			line += '\n\t[date-time] ' + data.CALLtimeStamp[i]
			line += '\n\t[duration] ' + data.CALLduration[i]
			line += '\n\t[source] ' + self.extractFileInfo(data.CALLsource[i])
			line += '\n\t[location] ' + data.CALLlocation[i]
			line += '\n\t[recovery method]' + data.CALLrecoveryMethod[i] 

			self.dFileHandle.write(line)  

	def fillArray(self, aInput, max):
		if len(aInput) < max:
			for i in range(len(aInput), max):						
				aInput.append('EMPTY')

	def setChatThread(self, chatThread, data):

		for i in range(len(data.CHATsender)):
			#print('CHATsender[' + str(i) + ']=' + data.CHATsender[i])
			if data.CHATsender[i].lower().find('local user') > -1:
				data.CHATsender[i] = data.CALLphoneNumberDevice
			
			#print('CHATreceiver[' + str(i) + ']=' + data.CHATreceiver[i])
			if data.CHATreceiver[i].lower().find('local user') > -1:
				data.CHATreceiver[i] = data.CALLphoneNumberDevice

			#print('CHATreceiver[' + str(i) + ']=' + data.CHATreceiver[i])
			#print(chatThread) 
			chatFound = False
			idx = -1
			for j in range(len(chatThread)):
				if (data.CHATsender[i] in chatThread[j] and  
					  data.CHATreceiver[i] in chatThread[j] and 
					  data.CHATapplication[i] in chatThread[j]):
					idx = j
					chatFound = True
					break
			
			if chatFound:		
				data.CHATids[idx].append(data.CHATid[i])
				data.CHATsenders[idx].append(data.CHATsender[i])
				data.CHATreceivers[idx].append(data.CHATreceiver[i])
				data.CHATdateTimeSents[idx].append(data.CHATdateTimeSent[i])
				data.CHATdateTimeReceiveds[idx].append(data.CHATdateTimeReceived[i])
				data.CHATmessages[idx].append(data.CHATmessage[i])
				data.CHATmessageStatuses[idx].append(data.CHATmessageStatus[i])
				data.CHATsources[idx].append(data.CHATsource[i])
				data.CHATlocations[idx].append(data.CHATlocation[i])
				data.CHATrecoveryMethods[idx].append(data.CHATrecoveryMethod[i])
				data.CHATapplications[idx].append(data.CHATapplication[i])
			else:
				idx = len(chatThread) - 1
				#print("data.CHATid len=" + str(len(data.CHATid)))
				data.CHATids.append([data.CHATid[i]])
				data.CHATsenders.append([data.CHATsender[i]])
				data.CHATreceivers.append([data.CHATreceiver[i]])
				data.CHATdateTimeSents.append([data.CHATdateTimeSent[i]])
				data.CHATdateTimeReceiveds.append([data.CHATdateTimeReceived[i]])
				data.CHATmessages.append([data.CHATmessage[i]])
				data.CHATmessageStatuses.append([data.CHATmessageStatus[i]])
				data.CHATsources.append([data.CHATsource[i]])
				data.CHATlocations.append([data.CHATlocation[i]])
				data.CHATrecoveryMethods.append([data.CHATrecoveryMethod[i]])
				data.CHATapplications.append([data.CHATapplication[i]])
				chatThread.append(data.CHATsender[i] + '#' + data.CHATreceiver[i] + 
					'#' + data.CHATapplication[i])
				


	def writeDebugCHAT(self, data):    
		line = "\n*---\nTotal CHAT (deleted?)  " + str(data.CHATtotal)		
		line += '\n*---\n'		
		self.dFileHandle.write(line)
		
		# self.fillArray(data.CHATsender, data.CHATtotal)
		# self.fillArray(data.CHATreceiver, data.CHATtotal)
		# self.fillArray(data.CHATdateTimeSent, data.CHATtotal)
		# self.fillArray(data.CHATdateTimeReceived, data.CHATtotal)
		# self.fillArray(data.CHATmessage, data.CHATtotal)
		# self.fillArray(data.CHATmessageStatus, data.CHATtotal)

		CHATthread = []
		self.setChatThread(CHATthread, data)
		
		for i in range(len(data.CHATids)):
			#print('CHAT.CHATids[' + str(i) + ']=' + str(len(data.CHATids[i])))
			line = '\n---> CHAT n. ' + str(i + 1) + '\n'	
			for j in range(len(data.CHATids[i])):
				line += '\n\n\t[msg n.] ' + str(j + 1)
				line += '\n\t[id] ' + data.CHATids[i][j]
				line += '\n\t[sender] ' + data.CHATsenders[i][j]
				line += '\n\t[receiver] ' + data.CHATreceivers[i][j]
				line += '\n\t[dateTimeSent] ' + data.CHATdateTimeSents[i][j]
				line += '\n\t[dateTimeReceived] ' + data.CHATdateTimeReceiveds[i][j]
				line += '\n\t[body] ' + data.CHATmessages[i][j]
				line += '\n\t[source] ' + self.extractFileInfo(data.CHATsources[i][j])
				line += '\n\t[location] ' + data.CHATlocations[i][j]
				line += '\n\t[recovery method] ' + data.CHATrecoveryMethods[i][j]
				line += '\n\t[application] ' + data.CHATapplications[i][j]
				
			self.dFileHandle.write(line) 


	def writeDebugCONTACT(self, data):    
		
		self.fillArray(data.CONTACTphoneNumber, data.CONTACTtotal)

		line = "\n*---\nTotal CONTACT (deleted?)  " + str(data.CONTACTtotal)
		#line += ' (' + str(data.CALLdeleted) + ')'
		line += '\n*---'		
		self.dFileHandle.write(line)
		for i in range(data.CONTACTtotal):
		
			line = '\n[id] ' + data.CONTACTid[i]
			line += '\n\t[name] ' + data.CONTACTname[i]
			line += '\n\t[Phone num.] ' + data.CONTACTphoneNumber[i]
			line += '\n\t[source] ' + self.extractFileInfo(data.CONTACTsource[i])
			line += '\n\t[location] ' + data.CONTACTlocation[i]
			line += '\n\t[recovery method]' + data.CONTACTrecoveryMethod[i] 

			self.dFileHandle.write(line)    	
	
	def writeDebugEMAIL(self, data):   

		line = "\n*---\nTotal EMAIL (deleted?)  " + str(data.EMAILtotal)		
		line += '\n*---'		
		self.dFileHandle.write(line)
				
		for i in range(data.EMAILtotal):			
			line = ''
			line += '\n[id] ' + data.EMAILid[i]
			line += '\n\t[app] ' + data.EMAILappSource[i]
			line += '\n\t[sender] ' + data.EMAILsender[i]
			line += '\n\t[recipients] ' + data.EMAILrecipient[i]
			line += '\n\t[cc] ' + data.EMAILcc[i]
			line += '\n\t[bcc] ' + data.EMAILbcc[i]
			line += '\n\t[dateTime] ' + data.EMAILdateTime[i]
			line += '\n\t[subject] ' + data.EMAILsubject[i]
			line += '\n\t[body] ' + data.EMAILbody[i]
			line += '\n\t[attachments] ' + data.EMAILattachment[i]
			line += '\n\t[source] ' + self.extractFileInfo(data.EMAILsource[i])
			line += '\n\t[location] ' + data.EMAILlocation[i]
			line += '\n\t[recovery method] ' + data.EMAILrecoveryMethod[i]
			self.dFileHandle.write(line) 

	def writeDebugSMS(self, data):   

		line = "\n*---\nTotal SMS (deleted?)  " + str(data.SMStotal)		
		line += '\n*---'		
		self.dFileHandle.write(line)
				
		for i in range(data.SMStotal):			
			line = ''
			line += '\n[id] ' + data.SMSid[i]
			line += '\n\t[sender] ' + data.SMSsender[i]
			line += '\n\t[recipients] ' + data.SMSrecipient[i]
			line += '\n\t[received Date/Time] ' + data.SMSreceivedDateTime[i]
			line += '\n\t[sent Date/Time] ' + data.SMSsentDateTime[i]
			line += '\n\t[message] ' + data.SMSmessage[i]
			line += '\n\t[direction] ' + data.SMSdirection[i]
			line += '\n\t[source] ' + self.extractFileInfo(data.SMSsource[i])
			line += '\n\t[location] ' + data.SMSlocation[i]
			line += '\n\t[recovery method] ' + data.SMSrecoveryMethod[i]
			self.dFileHandle.write(line) 

	def writeDebugWEB(self, data):   
		line = "\n*---\nTotal WEB_HISTORY (deleted?)  " + str(data.WEBtotal)		
		line += '\n*---'		
		self.dFileHandle.write(line)
				
		for i in range(data.WEBtotal):			
			line = ''
			line += '\n[id] ' + data.WEBid[i]
			line += '\n\t[url] ' + data.WEBurl[i]
			line += '\n\t[last visited] ' + data.WEBlastVisited[i]
			line += '\n\t[title] ' + data.WEBtitle[i]
			line += '\n\t[visit count] ' + data.WEBvisitCount[i]
			line += '\n\t[source] ' + self.extractFileInfo(data.WEBsource[i])
			line += '\n\t[location] ' + data.WEBlocation[i]
			line += '\n\t[recovery method] ' + data.WEBrecoveryMethod[i]
			self.dFileHandle.write(line) 

	def closeDebug(self):
		self.dFileHandle.close()
