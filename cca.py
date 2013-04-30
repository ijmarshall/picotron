#
# Cochrane PICOs
#

import glob
from xml.dom import minidom
from datetime import datetime
import codecs
from bs4 import BeautifulSoup
from decimal import *
import os
import re
import random
import collections
import codecs



#constants

pt = {} # path variables

#
# commented out windows directories
#

#pt["code"] = "c:\\code\\cca\\py\\"
#pt["docs"] = "c:\\code\\cca\\doc\\"
#pt["op"] = "c:\\code\\cca\\op2\\"
#pt["rev"] = "c:\\code\\cca\\allreviews\\"


pt["code"] = ""
#pt["docs"] = "../doc/"
pt["op"] = "output/"
#pt["rev"] = "../../../data/allreview2013/"

pt["rev"] = "/Users/iain/Code/data/cdsr/"





ccom = False # display compiler comments

abs_if_sig_only = True #display absolute numbers only where significant result

sver = "24"

htmlheader = """
<html>

	<head>
		<title></title>
		<meta name="GENERATOR" CONTENT="Cochrane Clinical Answers generator">
		<meta http-equiv="content-type" content="text/html; charset="utf-8">
		<style type="text/css">
		<!--
			body { font-family: Calibri, Arial; font-size: 10pt;}
			h1, h3, h4 { font-family: Calibri, Arial;}
			h1 { color: #394F91;}
			p { font-size: 10pt;}
			h3 { font-size: 12pt;}
			h4 { font-size: 10pt;}
			ul, li { font-size: 10pt;}
			table { border-collapse: collapse; border-style: solid; border-color: #444444; border-width: 1px; width:100%;}
			td, th { vertical-align: top; height: 100%; border-color: #444444; border-style: solid; border-width: 1px;}
            .leftcol {width:200px;}
			.compiler {color: #0096FF;}
            .edittext {color: #0096FF;}
		-->
		</style>
	</head>
	<body>
"""

tableheader = """
		<table>
"""

tablefooter = """
		</table>
"""


htmlfooter = """
	</body>
</html>
"""

intro = """
 PICO generator
"""


patterns = [[
"What are the effects of intname in people with cndname?",
"In people with cndname, what are the effects of intname?",
"What are the benefits and harms of intname in people with cndname?",
"In people with cndname, what are the benefits and harms of intname?",
"How does intname affect outcomes in people with cndname?",
"In people with cndname, how does intname affect outcomes?",
"Does intname improve outcomes in people with cndname?",
"In people with cndname, does intname improve outcomes?",
"Is there evidence to support the use of intname in people with cndname?",
"In people with cndname, is there evidence to support the use of intname?"],

["What are the effects of intname in popname with cndname?",
"In popname with cndname, what are the effects of intname?",
"What are the benefits and harms of intname in popname with cndname?",
"In popname with cndname, what are the benefits and harms of intname?",
"How does intname affect outcomes in popname with cndname?",
"In popname with cndname, how does intname affect outcomes?",
"Does intname improve outcomes in popname with cndname?",
"In popname with cndname, does intname improve outcomes?",
"Is there evidence to support the use of intname in popname with cndname?",
"In popname with cndname, is there evidence to support the use of intname?"],

["What are the effects of intname versus cntname in people with cndname?", 
"In people with cndname, what are the effects of intname versus cntname?",
"What are the benefits and harms of intname versus cntname in people with cndname?",
"In people with cndname, what are the benefits and harms of intname versus cntname?",
"How does intname compare with cntname at improving outcomes in people with cndname?",
"In people with cndname, how does intname compare with cntname at improving outcomes?",
"Which treatment is most effective at improving outcomes in people with cndname: intname or cntname?",
"In people with cndname, which treatment is most effective at improving outcomes: intname or cntname?",
"Is there evidence to support the use of intname instead of cntname in people with cndname?",
"In people with cndname, is there evidence to support the use of intname instead of cntname?"],

["What are the effects of intname versus cntname in popname with cndname?", 
"In popname with cndname, what are the effects of intname versus cntname?",
"What are the benefits and harms of intname versus cntname in popname with cndname?",
"In popname with cndname, what are the benefits and harms of intname versus cntname?",
"How does intname compare with cntname at improving outcomes in popname with cndname?",
"In popname with cndname, how does intname compare with cntname at improving outcomes?",
"Which treatment is most effective at improving outcomes in popname with cndname: intname or cntname?",
"In popname with cndname, which treatment is most effective at improving outcomes: intname or cntname?",
"Is there evidence to support the use of intname instead of cntname in popname with cndname?",
"In popname with cndname, is there evidence to support the use of intname instead of cntname?"]
]


unitdict = {"MD": "mean difference", "SMD": "standardised mean difference", "PETO_OR": "Peto OR", "RELATIVE RISK": "RR", "ODDS RATIO": "OR", "RISK RATIO": "RR"}
wordnumdict = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"}
vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"

capitalignore = ["VAS", "VAS.", "NSAID", "LABA", "ICS", "PEF", "FEV", "RCT", "TCC", "FEV1"]

monthnames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

errorlog = []

def convPc(f): # returns string with percentage to 1 decimal place
    f=round(f,1)
    return str(f)+"%"

def numberword(noun, number):
    number = str(number)
    if number == "0":
        return "no " + pluralise(noun)
    elif number == "1":
        return "one " + noun
    elif number in wordnumdict:
        return wordnumdict[number] + " " + pluralise(noun)
    else:
        return number + " " + pluralise(noun)

def pluralise(word):
    wordl = word.lower()
    
    if wordl[-1:] in ["s", "x", "o"] or wordl[-2:] in ["ch", "sh"]:
        return word + "es"
    elif wordl[-1:] == "f":
        return word [:-1] + "ves"
    elif wordl[-2:] == "fe":
        return word [:-2] + "ves"
    elif wordl[-1:] == "y" and wordl[-2:-1] not in vowels:
        return word[:-1] + "ies"
    else:
        return word + "s"

def midsent(txt): #capitalises as if mid sentence
    words = txt.split(' ')
    op = []
    for word in words:
        if word in capitalignore:
            op.append(word)
        else:
            op.append(word.lower())
    return " ".join(op)

def startsent(txt): #capitalises for start of sentence
    return txt[0].upper() + txt[1:]


def favours_parser(favours_pre): # checks if Forest plot labels are in predictable form, then changes to editorial preferred sentence "in favour of..."
    # return error if string < 7 characters
    
    lc = favours_pre.lower()
    
    if "control" in lc or "experimental" in lc or "treatment" in lc or "intervention" in lc:
        favours_pre += " <span class='edittext'>ALERT! - default 'favored' text left here by authors - please check and change to favoured intervention name if needed</span>"
    
    if len(favours_pre) < 7:
        return "<span class='edittext'>ALERT! - expected Forest plot key to start with 'favors', instead found - '" + favours_pre + "' - please add text 'in favor of [favoured intervention]'</span>"
    # first check for English or US spelling at start of word
    elif favours_pre[:7].lower() == "favours":
        return "in favor of" + favours_pre[7:]
    elif favours_pre[:6].lower() == "favors":
        return "in favor of" + favours_pre[6:]
    else:
        return "<span class='edittext'>ALERT! - expected Forest plot key to start with 'favors', instead found - '" + favours_pre + "' - please add text 'in favor of [favored intervention]'</span>"
    

#
#   revman parsing functions
#

def xmltagcontents(xml, tag, silentfail = False): # returns inside contents of xml of first instance of a tag (use for unique tag ids)

    els = xml.getElementsByTagName(tag)

    if len(els) > 0:
        return ('').join([node.toxml() for node in els[0].childNodes])
    else:
        if silentfail == False:
            return "<span class='edittext'>The tag " + tag + " was not found in the source RevMan file</span>"
        else:
            return None

def getElement(xml, tag, silentfail = False):
    try:
        r = xml.attributes[tag].value
    except:
        if silentfail == False:
            r = "<span class='edittext'>The tag " + tag + " was not found in the source RevMan file</span>"
        else:
            r = None
    return r

def ocparse(xml, checkfav = True): # takes xml.dom object containing a dichotomous or continuous outcome, returns tuple of values, or None if not estimible

    name = xmltagcontents(xml, 'NAME')

    if checkfav:
        favours1 = xmltagcontents(xml, 'GRAPH_LABEL_1')
        favours2 = xmltagcontents(xml, 'GRAPH_LABEL_2')
    else:
        favours1 = ""
        favours2 = ""

    studies=xml.attributes['STUDIES'].value

    octype = xml.nodeName


    if xml.attributes['ESTIMABLE'].value == "NO":
        return (None, name, None, None, None, None, None, None, studies, None, None, None)
    else:
        units = getElement(xml, "EFFECT_MEASURE", silentfail = True)
        if units == None:
#            units = xmltagcontents(xml, "EFFECT_MEASURE")
            try:
                units = xml.getElementsByTagName("EFFECT_MEASURE")[0].firstChild.data
            except:
                units = "No units found"

        point = Decimal(getElement(xml, 'EFFECT_SIZE'))
        ci95low = Decimal(getElement(xml, 'CI_START'))
        ci95up = Decimal(getElement(xml, 'CI_END'))
        totalInt=getElement(xml, 'TOTAL_1')
        totalCnt=getElement(xml, 'TOTAL_2')
        studies=getElement(xml, 'STUDIES')
        usetotal=getElement(xml, 'TOTALS')       
        subgroups=getElement(xml, 'SUBGROUPS')       


        participants=int(totalInt)+int(totalCnt)
        if units.upper() in unitdict:
            units = unitdict[units.upper()]




    return (octype, name, units, point, ci95low, ci95up, favours1, favours2, studies, participants, usetotal, subgroups)


def ier(cer, units, point):
    
    if units[-2:] == "RR":
        return cer * point
    elif units[-2:] == "OR":
        
        return cer * (point/(1 - (cer * (1 - point))))
    else:
        return None

def natfreq (risk, denom):
    return str((risk * denom).quantize(Decimal("1"))) + " per " + str(denom) + " people"
    
def natfreq_nodenom (risk, denom):
    return str((risk * denom).quantize(Decimal("1")))

def cerparse(xml): # returns a weighted median (as decimal object) for CER from an xml.dom object containing dichotomous outcome

    data = xml.getElementsByTagName('DICH_DATA')

    studydata = []
    total = 0

    for datum in data:
        int_n = Decimal(datum.attributes['EVENTS_1'].value)
        cnt_n = Decimal(datum.attributes['EVENTS_2'].value)
        int_d = Decimal(datum.attributes['TOTAL_1'].value)
        cnt_d = Decimal(datum.attributes['TOTAL_2'].value)
        study_cer = cnt_n / cnt_d # find the cer for each study
        studydata.append((study_cer, int_d + cnt_d)) # then add to a list
        total += (int_d + cnt_d) # and the total population for weighting purpose
        
    
    studydata = sorted(studydata)
    
    midpoint = total / 2 # find the midpoint of the studies weighted by size
    
    cer = None

    counter = 0
    for (study_cer, total) in studydata: #then run through again, stopping when pass the midway point
    
        if (counter < midpoint):
            cer = study_cer
        counter += total
    
    
    
    return cer


def cntmeanparse(xml): # returns a weighted median (as decimal object) for control group mean from an xml.dom object containing continuous outcome

    data = xml.getElementsByTagName('CONT_DATA')

    studydata = []
    total = 0

    for datum in data:
        cnt_m = Decimal(datum.attributes['MEAN_2'].value)
        int_d = Decimal(datum.attributes['TOTAL_1'].value)
        cnt_d = Decimal(datum.attributes['TOTAL_2'].value)

        studydata.append((cnt_m, int_d + cnt_d)) # then add to a list
        total += (int_d + cnt_d) # and the total population for weighting purpose
        
    studydata = sorted(studydata)

    midpoint = total / 2 # find the midpoint of the studies weighted by size

    cntmean = None
    counter = 0

    for (study_cntmean, total) in studydata: #then run through again, stopping when pass the midway point

        if (counter < midpoint):
            cntmean = study_cntmean
        counter += total
   
    return cntmean


### FOR TESTING - INTERVENTION MEDIAN TO CHECK DIRECTION OF EFFECTS

def intmeanparse(xml): # returns a weighted median (as decimal object) for control group mean from an xml.dom object containing continuous outcome

    data = xml.getElementsByTagName('CONT_DATA')

    studydata = []
    total = 0

    for datum in data:
        int_m = Decimal(datum.attributes['MEAN_1'].value)
        cnt_m = Decimal(datum.attributes['MEAN_2'].value)
        int_d = Decimal(datum.attributes['TOTAL_1'].value)
        cnt_d = Decimal(datum.attributes['TOTAL_2'].value)

        studydata.append((cnt_m, int_m, total)) # then add to a list
        total += (int_d + cnt_d) # and the total population for weighting purpose
        
    studydata = sorted(studydata)

    midpoint = total / 2 # find the midpoint of the studies weighted by size

    intmean = None

    for (study_cntmean, study_intmean, total) in studydata: #then run through again, stopping when pass the midway point

        if (total < midpoint):
            intmean = study_intmean
   
    return intmean




def rm_abs_values(octype, intname, cntname, name, units, point, ci95low, ci95up, studies, participants, xml): # returns nice bit of absolute value text for an xml.dom obj, (dich outcome)


    if units[-1] == "R" or units.upper()[-10:] == "RATE RATIO":
        cutoff = 1
    else:
        cutoff = 0

    if (Decimal(ci95low) < cutoff) and (Decimal(ci95up) > cutoff) and abs_if_sig_only:
        aresult = "There was no statistically significant difference between groups."
    else:
    
        
        abcer = cerparse(xml)
        
        abier = ier(abcer, units, point)
        
        abci95low = ier(abcer, units, ci95low)
        abci95up = ier(abcer, units, ci95up)

        aresult =  natfreq(abier, 100) + " (95% CI " + natfreq_nodenom(abci95low, 100) + " to " + natfreq_nodenom(abci95up, 100) + ") with " + midsent(intname) + " compared with " + natfreq(abcer ,100) + " with " + midsent(cntname) + "."
        
        #aresult =  natfreq(abier, 100) + " (between " + natfreq_nodenom(abci95low, 100) + " and " + natfreq_nodenom(abci95up, 100) + ") with " + midsent(intname) + " compared with " + natfreq(abcer ,100) + " with " + midsent(cntname)  pre change 2
         
    return aresult


def int_mean(cer_mean, dif): # estimates mean differences given these values
    return (cer_mean + dif).quantize(Decimal('.01'))

        
        
def rm_mean_values(octype, intname, cntname, name, units, point, ci95low, ci95up, studies, participants, xml): # returns nice bit of absolute value text for an xml.dom obj, (dich outcome)

    cutoff = 0 

    if (Decimal(ci95low) < cutoff) and (Decimal(ci95up) > cutoff) and abs_if_sig_only:
    
        aresult = "There was no statistically significant difference between groups."
    else:
    
        cntmean = cntmeanparse(xml)
        intmean = int_mean(cntmean, point)
        meanci95low = int_mean(cntmean, ci95low)
        meanci95up = int_mean(cntmean, ci95up)


        #aresult = str(cntmean) + " with " + midsent(cntname) + " compared with " + str(intmean) + " with " + midsent(intname) + " (95% CI " + str(meanci95low) + " to " + str(meanci95up) + ")"
                
        #aresult =  + " with " + midsent(intname) + " (95% CI " +  + " to " +  + ")" + " compared with " +  + " with " + midsent(cntname) 
        
        aresult =  str(intmean) + " (between " + str(meanci95low) + " and " + str(meanci95up) + ") with " + midsent(intname) + " compared with " + str(cntmean) + " with " + midsent(cntname) + "."


        
    return aresult


def rm_unique(xml): #retrieves unique identifier => string
    cr = xml.getElementsByTagName('COCHRANE_REVIEW')
    doi = cr[0].attributes['DOI'].value
    doi_l = doi.split('.')
    
    for d in doi_l:
        if d[:2] == "CD":
            return d
    return "[no CD number found in revman file]"



def rm_title(xml): #retrieves title => string
    cover = xml.getElementsByTagName('COVER_SHEET')
    title = cover[0].getElementsByTagName('TITLE')
    t = title[0].firstChild.data
    #t = t[0].lower() + t[1:]
    #return "What are the effects of " + t + "?" # previously converted to question, new version simply reports original title
    return t
    
    
def splitter(n):

    # first split into A and B removing the word ' for ' if present
    # if no ' for ' always generates an error
    
    
    
    list1 = n.split(' for ')
    if len(list1) is not 2: # if not exactly 2 returned parts return error
        return (None, None, None, None, None)
    
    a = list1[0] #list is working variable, not used outside fn
    b = list1[1]
    
    patternno = 0

    if ' in ' in b:
        list1 = b.split(' in ')
        cndname = list1[0]
        popname = list1[1]
        patternno += 1
    else:
        cndname = b
        popname = None

    
    if ' versus ' in a:
        list1 = a.split(' versus ')
        intname = list1[0]
        cntname = list1[1]
        patternno += 2
    else:
        intname = a
        cntname = None
    return (intname, cntname, cndname, popname, patternno)

    
def randomquestion(intname, cntname, cndname, popname, patternno):
   
    random.seed()
    patternpointer = patterns[patternno]
    tmpind = random.randint(0, len(patternpointer) - 1)

    text = patternpointer[tmpind]
    
    text = re.sub("intname", intname, text) # sub the intervention for intname
    text = re.sub("cndname", cndname, text) # sub the condition for cndname
    
    if cntname:
        text = re.sub("cntname", cntname, text) # sub the intervention for cntname
        
    if popname:
        text = re.sub("popname", popname, text) # sub the intervention for popname
    
    
    
    return  text



def rm_overview_p(xml):
    return xmltagcontents(xml, 'CRIT_PARTICIPANTS')

    
def rm_overview_i(xml):
    return xmltagcontents(xml, 'CRIT_INTERVENTIONS')


def rm_summaryshort(xml): #retrieves a short summary (conclusion from the abstract), returns html tagged
    return xmltagcontents(xml, 'ABS_CONCLUSIONS')
    

def rm_implications(xml): #retrieves the clinical implications, returns html tagged
    return xmltagcontents(xml, 'IMPLICATIONS_PRACTICE')


def rm_summarylong(xml): #retrieves the clinical implications, returns html tagged
    return xmltagcontents(xml, 'SUMMARY_BODY')

def rm_quality(xml): #retrieves the clinical implications, returns html tagged
    return xmltagcontents(xml, 'QUALITY_OF_EVIDENCE')


def rm_outcomes(xml): #retrieves the clinical implications, returns html tagged
    return xmltagcontents(xml, 'CRIT_OUTCOMES')
    
    
def rm_searchdate(xml): # retrives the search date

    last_search = xml.getElementsByTagName('LAST_SEARCH')
    date = last_search[0].getElementsByTagName('DATE')
    year = date[0].attributes['YEAR'].value
    # sketched in code to retrieve month
    month = date[0].attributes['MONTH'].value

    return "%s %s" % (monthnames[int(month)-1], year)



def rm_narrative(octype, intname, cntname, name, units, point, ci95low, ci95up, studies, participants, show_participants): # returns a CE style sentence from all this data

    if units[-1] == "R" or units.upper()[-10:] == "RATE RATIO":
        cutoff = 1
    else:
        cutoff = 0

    intname = midsent(intname)
    cntname = midsent(cntname)
    name = midsent(name)

    if show_participants:
        participants_str = "with %s participants" % (participants,)
    else:
        participants_str = "(number of participants not available)"


    if (Decimal(ci95low) < cutoff) and (Decimal(ci95up) > cutoff):
        nresult = "%s %s found no statistically significant difference between groups." % (startsent(numberword("RCT", int(studies))), participants_str)
    elif (Decimal(ci95low) < cutoff) and (Decimal(ci95up) < cutoff):
        nresult = "%s %s found that %s reduced %s compared with %s." % (startsent(numberword("RCT", int(studies))), participants_str, intname, name, cntname)
    elif (Decimal(ci95low) > cutoff) and (Decimal(ci95up) > cutoff):
        nresult = "%s %s found that %s increased %s compared with %s." % (startsent(numberword("RCT", int(studies))), participants_str, intname, name, cntname)
    return nresult


def rm_picos(xml): #retrieves a list of PICO (i.e. comparison) titles
    picolist = []
    comparisons = xml.getElementsByTagName('COMPARISON')
    cdno =  rm_unique(xml)
    searchdate = rm_searchdate(xml)

    for c in range(len(comparisons)):
        titlexml = comparisons[c].getElementsByTagName('NAME')
        title = titlexml[0].firstChild.data
        
        
        c_no = getElement(comparisons[c], "NO")
        

        val_comparison(title)
        

        
        
        
        
        picolist.append(tabtag(tag("Comparison ", "h3"), tag(title, "h3")))

        
        picolist.append(tabtag("Population", " "))
        picolist.append(tabtag("Intervention", " "))
        picolist.append(tabtag("Comparator", " "))
        picolist.append(tabtag("Safety alerts", " "))

#        outcomes=comparisons[c].getElementsByTagName('DICH_OUTCOME') + comparisons[c].getElementsByTagName('CONT_OUTCOME') + comparisons[c].getElementsByTagName('IV_OUTCOME') 
        
        outcomes=[i for i in comparisons[c].childNodes if i.nodeName in ["DICH_OUTCOME", "CONT_OUTCOME", "IV_OUTCOME"]]
        
        
        #print len(outcomes), len(outcomes2)
        #print outcomes, outcomes2
        
        for o in range(len(outcomes)):
            intxml = outcomes[o].getElementsByTagName('GROUP_LABEL_1')
            if len(intxml) > 0:
                try:
                    intname = intxml[0].firstChild.data
                except:
                    print "SKIPPED COMPARISON" # bug in XML here - need to make better solution
                    picolist.append(tabtag(tag(("Comparison skipped from Revman file here"), "h3")))
                    picolist.append(tabtag(("In tests, this was due to errors in the original file where the authors have incorrectly filled in the intervention field.")))
                    continue
                    
            else:
                intname = "NO INTERVENTION FOUND"
            try: 
                cntxml = outcomes[o].getElementsByTagName('GROUP_LABEL_2')
            except:
                print "SKIPPED COMPARISON" # bug in XML here - need to make better solution
                picolist.append(tabtag(tag(("Comparison skipped from Revman file here"), "h3")))
                picolist.append(tabtag(("In tests, this was due to errors in the original file where the authors have incorrectly filled in the control field.")))

            
            if len(cntxml) > 0:
                cntname = cntxml[0].firstChild.data
            else:
                intname = "NO CONTROL FOUND"



            


            
            participants_shown_attr = outcomes[o].attributes.get("SHOW_PARTICIPANTS")
            if participants_shown_attr and participants_shown_attr.value == "NO":
                show_participants = False
            else:
                show_participants = True

            data = ocparse(outcomes[o])
            
            
            o_no = getElement(outcomes[o], "NO")
            
            (octype, name, units, point, ci95low, ci95up, favours1, favours2, studies, participants, usetotal, subgroupspresent) = data
            ocstr = "%s.%s" % (c_no, o_no)
            octitle = ("Outcome %s" % (ocstr, ))
            picolist += rm_dataparse(title, octitle, octype, name, intname, cntname, units, point, ci95low, ci95up, favours1, favours2, studies, participants, show_participants, usetotal, outcomes[o], cdno, ocstr, searchdate)

            if subgroupspresent == "YES":
                subgroups = outcomes[o].getElementsByTagName('DICH_SUBGROUP') + outcomes[o].getElementsByTagName('CONT_SUBGROUP') + outcomes[o].getElementsByTagName('IV_SUBGROUP') 
                for s in range(len(subgroups)):

                    participants_shown_attr = outcomes[o].attributes.get("SHOW_PARTICIPANTS")
                    if participants_shown_attr and participants_shown_attr.value == "NO":
                        show_participants = False
                    else:
                        show_participants = True

                    s_no = getElement(subgroups[s], "NO")
                
                    data = ocparse(subgroups[s], checkfav = False) #want to use the existing favours string
                    (octype, sgname, dummy0, point, ci95low, ci95up, dummy1, dummy2, studies, participants, usetotal, dummy3) = data #slight hack, assigning favours to dummystring, subgroups, and units
                    ocstr = "%s.%s.%s" % (c_no, o_no, s_no)
                    octitle = ("Outcome (subgroup) %s" % (ocstr,))
                    picolist += rm_dataparse(title, octitle, octype, name, intname, cntname, units, point, ci95low, ci95up, favours1, favours2, studies, participants, show_participants, usetotal, subgroups[s], cdno, ocstr, searchdate, sgname)
    return picolist


def rm_dataparse(title, octitle, octype, name, intname, cntname, units, point, ci95low, ci95up, favours1, favours2, studies, participants, show_participants, usetotal, xml, cdno, ocstr, searchdate, sgname = None):

    

    if sgname:
        sgname = name + " - [subgroup: " + sgname + "]"
    else:
        sgname = name

    picolist = []
    picolist.append(tabtag(tag(octitle, "h4"), tag(sgname, "h4")))

    if usetotal == "SUB":

        picolist.append(tabtag(tag("Analysed by subgroup only", "h4")))

    else:

        if studies == "0":
            nresult = "We found no studies meeting our criteria which assessed the effect of " + midsent(title) + " on " + midsent(name)
            qresult = "n/a"
            abresult = "n/a"
        elif type(point) == type(None):
            nresult = "Not estimable"
            qresult = "The relative effect/mean difference cannot be calculated as data were not meta-analysed."
            abresult = "The absolute effect in each group cannot be calculated as data were not meta-analysed."
        else:
            nresult = rm_narrative(octype, intname, cntname, name, units, point, ci95low, ci95up, studies, participants, show_participants)
            if xml.nodeName == "IV_OUTCOME" or xml.nodeName == "IV_SUBGROUP":
                abresult = "The absolute effect in each group cannot be calculated using only the generic inverse variance data from this analysis."
            elif xml.nodeName == "CONT_OUTCOME" or xml.nodeName == "CONT_SUBGROUP": # new insertion - no longer want continuous o/cs calculated
                abresult = " "
            elif units[-1] == "R" or units.upper()[-10:] == "RATE RATIO":
                abresult = rm_abs_values(octype, intname, cntname, name, units, point, ci95low, ci95up, studies, participants, xml)
            #elif units.lower() == "mean difference": # not needed at present
            #    abresult = rm_mean_values(octype, intname, cntname, name, units, point, ci95low, ci95up, studies, participants, xml)
            else:
                abresult = "The absolute effect in each group cannot be calculated using " + units + " from this analysis"
                
                
            if units[-1] == "R" or units.upper()[-10:] == "RATE RATIO":
                cutoff = 1
            else:
                cutoff = 0

            if ci95up < cutoff:
                favours = "There was a statistically significant difference between groups, " + favours_parser(favours1)
            elif ci95low > cutoff:
                favours = "There was a statistically significant difference between groups, " + favours_parser(favours2)
            else:
                favours = "There was no statistically significant difference between groups"
            
            qresult = favours + " (" + units + " " + str(point.quantize(Decimal('.01'))) + ", 95% CI " + str(ci95low.quantize(Decimal('.01'))) + " to " + str(ci95up.quantize(Decimal('.01'))) + "). Forest plot details: " + cdno + " Analysis " + ocstr

        picolist.append(tabtag("Narrative result", nresult))
        picolist.append(tabtag("Risk of bias of studies", " "))
        picolist.append(tabtag("Quality of the evidence", " "))
        picolist.append(tabtag("Quantitative result: relative effect or mean difference", qresult))
        
        picolist.append(tabtag("Quantitative result: absolute effect", abresult))
        picolist.append(tabtag("Reference", cdno))
        picolist.append(tabtag("Search date", searchdate))
    return picolist


#
# data validation functions
#

def val_comparison(txt): #check comparisons, return true or false
    #check 1 - does it have v, versus, or vs?
    vcheck = False

    for v in [" v ", " v. ", " vs ", " vs. ", " versus "]:
        if v in txt:
            vcheck = True

    if not vcheck:
        errorlog.append("Outcome name without intervention and control")
    return vcheck
     
#
#   output functions
#

def outputfile(inputfile): # returns output filename from input filename (same name with txt extension moved to op directory)
    #return pt["op"] + inputfile.split('\\')[-1][:-3] + "doc"
    return pt["op"] + ('').join(inputfile.split('/')[-2:])[:-3] + "doc"# TODO change to doc


def htmlfile(inputfile): # returns output filename from input filename (same name with txt extension moved to op directory)
    return pt["www"] + inputfile.split('/')[-1][:-3] + "html"



def datecode(): # top of file date/time/compiler options stamp
    if ccom:
        ccom_s = "ON"
    else:
        ccom_s = "OFF"
    d = datetime.now()
    d_s = d.strftime('%d-%m-%y - %H:%M:%S')
    return "PICO generator v" + sver + "; text complied @ " + d_s + "; compiler comments " + ccom_s 

def tag(contents, tag, cls = ""): # returns content html tagged, and indented 2x tabs
	if cls is not "":
		cls = ' class="' + cls + '"'
	return "\t\t<" + tag + cls + ">" + contents + "</" + tag + ">"

def tabtag(x, y = "", celltag = "td"): # returns a one or two headed table row, with option to make different tag (i.e. th)

    if y == "":
        colspan = ' colspan = 2'
    else:
        colspan = ''
        y = "<" + celltag + ">" + y + "</" + celltag + ">"
    x = "<" + celltag + colspan + " class='leftcol'>" + x + "</" + celltag + ">"
    return "\t\t\t<tr>" + x + y + "</tr>"

def writefile(filename, txt):

    
    #soup = BeautifulSoup(txt)
    op = codecs.open(filename, 'wb', 'utf-8')
    #op.write(soup.prettify())
    op.write(txt)
    op.close()


def get_file_list():
    with open("files_todo.txt", 'rb') as f:
        #cd_nos = f.read().splitlines()
        cd_nos = f.read().splitlines()
    print pt["rev"]
    
    files = []
    
    for i in cd_nos:#[:20]:# remove [:20] for full list
        
        try:
            print pt["rev"] + i + "*.rm5"
            files.append(glob.glob(pt["rev"] + i + "*.rm5")[0])
        except:
            print "Requested CD number: " + i + " not found"
    
    return files
    
    
def main():
    files = glob.glob(pt["rev"] + "*.rm5")
    #nofiles = len(files)    
    
    
    

    os.system("clear")
    print intro
    
    #files = get_file_list()
    
    nofiles = len(files)    
    nofiles_u = len(set(files))    
    print "%d files found - processing..." % (nofiles,)
    print "(%d unique files)" % (nofiles_u,)
    
    files_count = collections.Counter(files)
    duplicates = [i for i in files_count if files_count[i]>1]
    if duplicates:
        print "The following duplicates were found ", ",".join(duplicates)

    
    not_done = []
    
    for c in range(nofiles):
        
        try:
            
            f = files[c]
            
            op = []
            xmldoc = minidom.parse(f)
            op.append(htmlheader)
            op.append(tag("Cochrane Clinical Answers", "h3"))
            
            
                    
            q = rm_title(xmldoc)
            
            (intname, cntname, cndname, popname, patternno) = splitter(midsent(q))
            if intname:
                qu = randomquestion(intname, cntname, cndname, popname, patternno)
            else:
                qu = "[Sorry, it was not possible to auto-generate a question (the wording of the review title was not in the expected format).]"
            
            op.append(tag(qu, "h1"))
            
            
            op.append(tableheader)
            
            cdno =  rm_unique(xmldoc)
            
            op.append(tabtag(tag("Notes for authors from Cochrane Review " + cdno + " [not for publication]", "h3")))
            print cdno
            
            op.append(tabtag("Review title", q))
            
            op.append(tabtag("Short conclusions<br/>(Abstract > Conclusions)", rm_summaryshort(xmldoc)))
            op.append(tabtag("Long conclusions<br/>(Authors' conclusions > Implications for practice)", rm_implications(xmldoc)))
            
            op.append(tabtag("Population<br/>(Methods > Criteria for considering studies for this review > Types of participants)", rm_overview_p(xmldoc)))
            op.append(tabtag("Interventions<br/>(Methods > Criteria for considering studies for this review > Types of interventions)", rm_overview_i(xmldoc)))
            op.append(tabtag("Outcomes<br/>(Methods > Criteria for considering studies for this review > Types of outcome measures)", rm_outcomes(xmldoc)))
            op.append(tabtag("Risk of bias of studies<br/>(Results > Risk of bias in included studies)", rm_quality(xmldoc)))
            op.append(tablefooter)
            
            
            op.append(tag(" ", "br"))
            
            op.append(tableheader)
            op.append(tabtag(tag("CCA number", "h4"), " "))
            op.append(tabtag(tag("DOI", "h4"), " "))
            op.append(tablefooter)
            
            op.append(tag(" ", "br"))
            
            
            op.append(tableheader)
            op.append(tabtag(tag("Clinical question", "h4"), qu))
            op.append(tabtag("Clinical answer", " "))
            op.append(tabtag("Abstract", "<p></p><p></p>"))
            op.append(tabtag("Keywords", " "))
            op.append(tabtag("Subject (1)", " "))
            op.append(tabtag("Subject (2)", " "))
            op.append(tabtag("Subject (3)", " "))
            op.append(tabtag("MeSH codes", " "))
            op.append(tablefooter)
            
            
            op.append(tag(" ", "br"))
            
            op.append(tag(datecode(), "p", "compiler"))
            op.append("!/!/!/!/COMPILER!/!/!/!/")
            
            
            op.append(tableheader)
            op.append(tabtag(tag("PICOS", "h3")))
            op += rm_picos(xmldoc)
            op.append(tablefooter)        
    
    
            op.append(htmlfooter)
    
    
            # add in error log if compiler comments = True
            ccom_index = op.index("!/!/!/!/COMPILER!/!/!/!/")
    
            if ccom:
                for e in range(len(errorlog)):
                    errorlog[e] = tag(errorlog[e], "p", "compiler")
                op = op[:ccom_index] + errorlog + op [ccom_index + 1:]
            else:
                op[ccom_index] = ""
        
            writefile(outputfile(f), '\n'.join(op))
        
        except:
            print "error, file %s not done" % (files[c], )
            not_done.append(files[c])
         
    
    with open('not_done_log.txt', 'wb') as not_done_f:
        not_done_f.write("\n".join(not_done))
    print ""
    print "done!"

        

if __name__ == "__main__":
    main()







    
    
    
