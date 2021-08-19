## XML SAX parser to extract digital traces from MAGNET XML reports generated by  AXIOM PROCESS tool and represent them into CASE Observables complied with UCO/CASE ontologies

This repository proivides a XML SAX parser to extract the most relevant traces (Call, Chat, Contact, File, Email, SMS, URL History) from XML reports generated by MAGNET AXIOM PROCESS  and convert this data into CASE ontology (see https://caseontology.org/index.html). Further to the digital traces the  Chain of Evidence and the Device info are represented in CASE. The ontology is serialized in JSON-LD format.

The parser is able to process any report, regardless their size.

The parsers has been developed using **Python, version 3.x** and is based on **SAX** (Simple API for XML).

The parser supports the latest CASE version. 

The AXIOM parser is composed of three different modules:

* parser_AXIOMtoCASE (main program: SAX parser)
* AXIOMtoJSON.py (class for generating the JSON-LD files of the UCO/CASE ontology)
* AXIOMdebug.py 	(class for producing text files for debugging)

## Requirements
The tool has been developed in Python version 3.x and here are some required modules:

* xml.sax (SAX classes)
* string (string utilities)
* argparse (args input management)
* os (operating system utilities)
* codecs (UTF-8 and other codec management)
* re (regular expressions management)
* uuid (global unique identifier management)

## Usage

> *parser_AXIOMtoCASE.py  [-h]*
>                       *-r INFILEXML*
>                       *-o OUTPUT_JSON*
>                       *-e type of device: mobile or disk*
>                       *-d OUTPUT_DEBUG*

where:

* -h, --help (shows the help message, including the AXIOM PROCESS versions supported, then exit)
* -r | --report INFILEXML (the AXIOM XML report to be processed, compulsory parameter)
* -o | --output OUTPUT_JSON (JSON-LD file to be generated, compulsory)
* -e | --evidence type of device: mobile or disk (HD, SD, USB), compulsory
* -d | --debug OUTPUT_DEBUG (output file for debug, optional)

## Mobile Forensic Data set
The parser has been developed and tested relying on a huge collection of mobile forensic dataset. This is composed of images made available on the Computer Forensic Reference Data Sets  (CFReDS) Project and a few provided by some LEA partners of the project. All the provided data is fictitious, so there is no issue  from the privacy point of view: these datasets have been provided to investigators for examination but they represent sets of simulated digital evidence. At the moment the processed dataset is huge, about 300 GB.

## CASE representation: JSON-LD files
All the XML reports have been processed to generate the corresponding CASE representation of the following traces, or facet according to the CASE terminology:
* Call
* Chat (Whatsapp, Skype, etc.)
* Contact
* File
* Email
* SMS
* URL History
* Chain of Evidence
* Context
  * Device
  * Tool

The reports can be found in the *json* folder.


## Ontologies compatibility
The JSON-LD files generated are complied with the last version of CASE/UCO ontologies, at the moment CASE 0.4 / UCO 0.6.