# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 21:08:20 2019

@author: weiho
"""
import string
from Parse import parse_lines, get_eclogues_url

#Usage: scan_line(line), where line is a string of Latin dactylic hexameter
#returns an array of scanned syllables
#[[syllable1, stress1], ...], where stresses are True for long, False for short, None for elided

#Issues
    #mihi tibi are marked long when they are not necessarily
    #diphthongs are marked long when they are not necessarily
    #does not always render diphthongs properly -> ui?
    #fifth foot is always dactyl

class Syllable:
    #line[start:end] = syllable
    #vowel_index = index of last vowel in syllable
    #word_ender tracks if syllable ends word, used in heuristics for evaluating stress
    #stress true = long, false = short
    #elided tracks if syllable is elided in line
    def __init__(self, start, end, vowel_index, word_ender, stress, elided):
        self.start = start
        self.end = end
        self.vowel_index = vowel_index
        self.word_ender = word_ender
        self.stress = stress
        self.elided = elided
        
def preprocess(line):
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    
    line = line.lower()
    line = line.translate(str.maketrans('', '', string.punctuation))
    #treats qu as a single consonant
    line = line.replace('qu','q')
    
    #if [i, u] is surrounded by two vowels or by a space on the left and a vowel on the right, treat as [j, v]
    #TODO: address cases such as 'silvae'
    
    vowel_corrected = ''
    i = 0
    while i < len(line):
        if line[i:i+1] == 'i' and i < len(line)-1 and line[i+1:i+2] in vowels and (i == 0 or line[i-1:i] in vowels or line[i-1:i] == ' '):
            vowel_corrected += 'j'
        elif line[i:i+1] == 'u' and i < len(line)-1 and line[i+1:i+2] in vowels and (i == 0 or line[i-1:i] in vowels or line[i-1:i] == ' '):
            vowel_corrected += 'v'
        else:
            vowel_corrected += line[i:i+1]
        i += 1
    
    return(vowel_corrected)
    
def make_syllables(line):
    syllable_list = list()
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    diphthongs = ['ae', 'ai', 'au', 'ei', 'eu', 'oe', 'oi']#, 'ui']
    #TODO: add better conditions for recognizing diphthongs

    processed_line = preprocess(line)
    
    i = 0
    start = 0
    while i < len(processed_line):
        #Diphthong starting at i: end syllable and start at i+2
        if i+2 <= len(processed_line) and processed_line[i:i+2] in diphthongs:
            s = Syllable(start=start, end=i+2, vowel_index=i+1, word_ender=False, stress=True, elided=False)
            syllable_list.append(s)
            start = i+2
            i += 1
        #Vowel at i: end syllable and start at i+1
        elif processed_line[i:i+1] in vowels:
            s = Syllable(start=start, end=i+1, vowel_index=i, word_ender=False, stress=None, elided=False)
            syllable_list.append(s)
            start = i+1
        #Space before vowel is found: previous syllable ended word, correct previous syllable end index and note possible elision
        elif processed_line[i:i+1] == ' ':
            prev_s = syllable_list[len(syllable_list)-1]
            prev_s.end = i
            prev_s.word_ender = True
            prev_s.elided = True #this marks all syllables that could be elided (a space ends the syllable)
            start = i+1
        i += 1
    syllable_list[len(syllable_list)-1].end = len(processed_line)
    
    #Check elisions
    for s in range(len(syllable_list)-1):
        spaceprev = syllable_list[s].end-1
        spacenext = syllable_list[s+1].start
        if not ((processed_line[spaceprev:spaceprev+1] in vowels or processed_line[spaceprev-1:spaceprev] in vowels and processed_line[spaceprev:spaceprev+1] == 'm') and 
                (processed_line[spacenext:spacenext+1] in vowels or processed_line[spacenext:spacenext+1] == 'h' and processed_line[spacenext+1:spacenext+2] in vowels)):
            syllable_list[s].elided = False
            
    #Remove spaces in processed_line and edit syllable_list to reflect this
    processed_line = processed_line.translate(str.maketrans('', '', ' '))
    
    counter = 0
    for i in range(len(syllable_list)-1):
        if syllable_list[i].end != syllable_list[i+1].start-counter:
            counter += 1
        syllable_list[i+1].start -= counter
        syllable_list[i+1].end -= counter
        syllable_list[i+1].vowel_index -= counter

    return [processed_line, syllable_list]

def check_long(line, s):
    index = s.vowel_index
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    mutes = ['b', 'c', 'd', 'f', 'g', 'p', 't']
    liquids = ['l', 'r']
    doubles = ['x', 'z']
    
    #Cases for long:
        #vowel followed by double
        #vowel followed by two consonants (not a mute + liquid)
        #vowel followed by three consonants
        #i, o, u ending word
        #diphthong
        
    #TODO: better heuristics for long/short by nature
    
    if ((index < len(line)-1 and line[index+1:index+2] in doubles) or
        (index < len(line)-2 and (line[index+1:index+2] not in vowels) and (line[index+2:index+3] not in vowels) and not ((line[index+1:index+2] in mutes) and (line[index+2:index+3] in liquids))) or
        (index < len(line)-3 and (line[index+1:index+2] not in vowels) and (line[index+2:index+3] not in vowels) and (line[index+3:index+4] not in vowels)) or
        (s.word_ender == True and index == s.end-1 and line[index:index+1] in ['i', 'o', 'u']) or
        s.stress == True):
           return True
    return False

def scan_syllables(line, syllable_list):
    count = 0
    non_elided = list()
    for s in syllable_list:
        if s.elided == False:
            count += 1
            non_elided.append(s)
    dactyls = count - 2*6
    spondees = 6 - dactyls
    #Begin frontier is leftmost syllable to not be classified
    #End frontier is rightmost syllable to not be classified
    begin_frontier = 0
    end_frontier = count-1
       
    #Sets last foot
    #Sets fifth foot to dactyl
    try:
        non_elided[count-2].stress = True
        non_elided[count-3].stress = False
        non_elided[count-4].stress = False
        non_elided[count-5].stress = True
        count -= 5
        end_frontier = count-1
        dactyls -= 1
        spondees -= 1
    except:
        print('Error: not enough syllables')
    
    while (spondees > 0 or dactyls > 0):
        #Check if all dactyls
        if dactyls == 0:
            count = 0
            spondees = 0
            for i in range(begin_frontier, end_frontier+1):
                non_elided[i].stress = True
        #Check if all spondees
        elif spondees == 0:
            count = 0
            dactyls = 0
            for i in range(begin_frontier, end_frontier+1):
                if i % 3 == begin_frontier % 3:
                    non_elided[i].stress = True
                else:
                    non_elided[i].stress = False
        #Check if last foot is spondee
        elif check_long(line, non_elided[end_frontier]) or check_long(line, non_elided[end_frontier-1]):
            count -= 2
            spondees -= 1
            non_elided[end_frontier].stress = True
            non_elided[end_frontier-1].stress = True
            end_frontier -= 2
        #Check if first foot is spondee
        elif check_long(line, non_elided[begin_frontier+1]) or check_long(line, non_elided[begin_frontier+2]):
            count -= 2
            spondees -= 1
            non_elided[begin_frontier].stress = True
            non_elided[begin_frontier+1].stress = True
            begin_frontier += 2
        #Assume if fourth syllable is long, first foot is dactyl
        elif check_long(line, non_elided[begin_frontier+3]):
            count -= 3
            dactyls -= 1
            non_elided[begin_frontier].stress = True
            non_elided[begin_frontier+1].stress = False
            non_elided[begin_frontier+2].stress = False
            begin_frontier += 3
        #Assume if third from last syllable is long, last foot is dactyl
        elif check_long(line, non_elided[end_frontier-2]):
            count -= 3
            dactyls -= 1
            non_elided[end_frontier-2].stress = True
            non_elided[end_frontier-1].stress = False
            non_elided[end_frontier].stress = False
            end_frontier -= 3
        else:
            #Failure to scan all of line
            break
        
        #TODO: optimize priorities of conditions checked
        
    return(syllable_list)
    
def print_syllables(line, syllable_list):
    retlist = list()
    for s in syllable_list:
        processed_text = line[s.start:s.end]
        retlist.append([processed_text.replace('q','qu'), s.stress])
    print(retlist)

def scan_line(l):
    [processed_l, syllable_list] = make_syllables(l)
    try:
        scan = scan_syllables(processed_l, syllable_list)
        print_syllables(processed_l, scan)
    except:
        print('Scansion failed')

def scan_eclogues(book_num):
    line_list = parse_lines(get_eclogues_url(book_num))
    lines = list()
    for line in line_list:
        l = ''
        for word in line:
            l += word + ' '
        lines.append(l.strip())
    
    scanned_lines = list()
    for l in lines:
        scanned_lines.append(scan_line(l))
    
    return(scanned_lines)