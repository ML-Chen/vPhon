###########################################################################
#       vPhon.py version 0.2.6m
#       Copyright 2008-2019 James Kirby <j.kirby@ed.ac.uk>, Michael Chen
# 
#
#       vPhon is free software: you can redistribute it and/or modify      
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or 
#       (at your option) any later version.                  
#
#       vPhon is distributed in the hope that it will be useful,     
#       but WITHOUT ANY WARRANTY; without even the implied warranty of 
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
#       GNU General Public License for more details.            
#
#       You should have received a copy of the GNU General Public License 
#       along with vPhon.  If not, see <http://www.gnu.org/licenses/>. 
#
###########################################################################

import sys, codecs, re, io
from argparse import ArgumentParser
from string import punctuation
from typing import Tuple

def trans(word: str, dialect: str, glottal: bool, pham: bool, cao: bool, palatals: bool, tone_letters: bool) -> Tuple[str, str, str, str]:
    """
    Convert a word to a tuple of the onset, nucleus, coda, and tone.
    """

    dialect = dialect.lower()

    if dialect == 'n':
        from Rules.north import onsets, nuclei, codas, tones, onglides, offglides, onoffglides, qu, gi
    elif dialect == 'c':
        from Rules.central import onsets, nuclei, codas, tones, onglides, offglides, onoffglides, qu, gi
    elif dialect == 's':
        from Rules.south import onsets, nuclei, codas, tones, onglides, offglides, onoffglides, qu, gi

    if pham or cao:
        if dialect == 'n':
            from Rules.north import tones_p
        if dialect == 'c':
            from Rules.central import tones_p
        if dialect == 's':
            from Rules.south import tones_p
        tones = tones_p

    ons = ''
    nuc = ''
    cod = ''
    ton = 0
    oOffset = 0
    cOffset = 0 
    l = len(word)

    if l > 0:
        if word[0:3] in onsets:         # if onset is 'ngh'
            ons = onsets[word[0:3]]
            oOffset = 3
        elif word[0:2] in onsets:       # if onset is 'nh', 'gh', 'kʷ' etc
            ons = onsets[word[0:2]]
            oOffset = 2
        elif word[0] in onsets:         # if single onset
            ons = onsets[word[0]]
            oOffset = 1

        if word[l-2:l] in codas:        # if two-character coda
            cod = codas[word[l-2:l]]
            cOffset = 2
        elif word[l-1] in codas:        # if one-character coda
            cod = codas[word[l-1]]
            cOffset = 1
                            
        if word[0:2] in gi and cod and len(word) == 3:  # if you just have 'gi' and a coda...
            nucl = 'i'
            ons = 'z'
        else:
            nucl = word[oOffset:l-cOffset]

        if nucl in nuclei:
            if oOffset == 0:
                if glottal:
                    if word[0] not in onsets:    # if there isn't an onset....  
                        ons = 'ʔ' + nuclei[nucl] # add a glottal stop
                    else:                        # otherwise...
                        nuc = nuclei[nucl]       # there's your nucleus 
                else: 
                    nuc = nuclei[nucl]           # there's your nucleus 
            else:                                # otherwise...
                nuc = nuclei[nucl]               # there's your nucleus
        
        elif nucl in onglides and ons != 'kw':   # if there is an onglide...
            nuc = onglides[nucl]                 # modify the nuc accordingly
            if ons:                              # if there is an onset...
                ons = ons+'w'                    # labialize it, but...
            else:                                # if there is no onset...
                ons = 'w'                        # add a labiovelar onset 

        elif nucl in onglides and ons == 'kw': 
            nuc = onglides[nucl]
                
        elif nucl in onoffglides:
            cod = onoffglides[nucl][-1]
            nuc = onoffglides[nucl][0:-1]
            if ons != 'kw':
                if ons:
                    ons = ons+'w'
                else:
                    ons = 'w'
        elif nucl in offglides:
            cod = offglides[nucl][-1]
            nuc = offglides[nucl][:-1]
                
        elif word in gi:      # if word == 'gi', 'gì',...
            ons = gi[word][0]
            nuc = gi[word][1]

        elif word in qu:      # if word == 'quy', 'qúy',...
            ons = qu[word][:-1]
            nuc = qu[word][-1]
                
        else:   
            # Something is non-Viet
            return (None, None, None, None)


        # Velar Fronting (Northern dialect)
        if dialect == 'n':
            if nuc == 'a':
                if cod == 'k' and cOffset == 2: nuc = 'ɛ'
                if cod == 'ɲ' and nuc == 'a': nuc = 'ɛ'

            # Final palatals (Northern dialect)
            if nuc not in ['i', 'e', 'ɛ']:
                if cod == 'ɲ': cod = 'ŋ'
            elif not palatals and nuc in ['i', 'e', 'ɛ']:
                if cod == 'ɲ': cod = 'ŋ'
            if palatals:
                if cod == 'k' and nuc in ['i', 'e', 'ɛ']: cod = 'c'

        # Velar Fronting (Southern and Central dialects)
        else:
            if nuc in ['i', 'e']:
                if cod == 'k': cod = 't'
                if cod == 'ŋ': cod = 'n'

            # There is also this reverse fronting, see Thompson 1965:94 ff.
            elif nuc in ['iə', 'ɯə', 'uə', 'u', 'ɯ', 'ɤ', 'o', 'ɔ', 'ă', 'ɤ̆']:
                if cod == 't': 
                    cod = 'k'
                if cod == 'n': cod = 'ŋ'

        # Monophthongization (Southern dialects: Thompson 1965: 86; Hoàng 1985: 181)
        if dialect == 's':
            if cod in ['m', 'p']:
                if nuc == 'iə': nuc = 'i'
                if nuc == 'uə': nuc = 'u'
                if nuc == 'ɯə': nuc = 'ɯ'

        # Tones 
        # Modified 20 Sep 2008 to fix aberrant 33 error
        tonelist = [tones[word[i]] for i in range(0,l) if word[i] in tones]
        if tonelist:
            ton = str(tonelist[len(tonelist)-1])
        else:
            if not (pham or cao):
                if dialect == 'c':
                    ton = '35'
                else:
                    ton = '33'
            else:
                ton = '1'
            
        # Modifications for closed syllables
        if cOffset != 0:

            # Obstruent-final nang tones are modal voice
            if (dialect == 'n' or dialect == 's') and ton == '21g' and cod in ['p', 't', 'k']:
                ton = '21'

            # Modification for sắc in closed syllables (Northern and Central only)
            if ((dialect == 'n' and ton == '24') or (dialect == 'c' and ton == '13')) and cod in ['p', 't', 'k']:
                ton = '45'

            # Modification for 8-tone system
            if cao == 1:
                if ton == '5' and cod in ['p', 't', 'k']:
                    ton = '5b'
                if ton == '6' and cod in ['p', 't', 'k']:
                    ton = '6b'

            # labialized allophony (added 17.09.08)
            if nuc in ['u', 'o', 'ɔ']:
                if cod == 'ŋ':
                    cod = 'ŋ͡m' 
                if cod == 'k':
                    cod = 'k͡p'

        if tone_letters and not pham and not cao:
            ton = ton.replace('1', '˩').replace('2', '˨').replace('3', '˧').replace('4', '˦').replace('5', '˥')

        return (ons, nuc, cod, ton)
    
def convert(word: str, dialect: str, glottal: bool, pham: bool, cao: bool, palatals: bool, delimit: str, tone_letters: bool) -> str:
    """Convert a single orthographic string to IPA."""

    ons = ''
    nuc = ''
    cod = ''
    ton = 0
    seq = ''

    try:
        (ons, nuc, cod, ton) = trans(word, dialect, glottal, pham, cao, palatals, tone_letters)
        if None in (ons, nuc, cod, ton):
            seq = '[' + word + ']'
        else:
            seq = delimit + delimit.join([_f for _f in (ons, nuc, cod, ton) if _f]) + delimit
    except TypeError:
        pass

    return seq
            
def main():
    sys.path.append('./Rules')      # make sure we can find the Rules files

    usage = 'python vPhon.py <input> -d, --dialect N|C|S'

    # Command line options
    parser = ArgumentParser(usage)
    parser.add_argument('-g', '--glottal', action='store_true', help='prepend glottal stops to onsetless syllables')
    parser.add_argument('-6', '--pham', action='store_true', help='phonetize tones as 1-6')
    parser.add_argument('-8', '--cao', action='store_true', help='phonetize tones as 1-4 + 5, 5b, 6, 6b')
    parser.add_argument('-p', '--palatals', action='store_true', help='use word-final palatal velars in Northern dialects')
    parser.add_argument('-t', '--tokenize', action='store_true', help='preserve underscores or hyphens in tokenized inputs (e.g., anh_ta = anh1_ta1)')
    parser.add_argument('-o', '--output_ortho', action='store_true', help='output orthography as well as IPA')
    parser.add_argument('-m', '--delimit', action='store', type=str, help='produce explicitly delimited output (e.g., bi ca = .b.i.33. .k.a.33.)')
    parser.add_argument('-d', '--dialect', action='store', type=str, help='specify dialect region ([N]orthern, [C]entral, [S]outhern)')
    parser.add_argument('-tl', '--tone_letters', action='store_true', help='use Chao tone letters instead of tone numerals, if --pham and --cao are not passed in')
    args = parser.parse_args()

    if not args.dialect:
        parser.error('Please enter a valid dialect.')
    if args.dialect.lower() not in ['n', 'c', 's']:
        parser.error('Please enter a valid dialect.')
    if not args.delimit:
        args.delimit = ''

    # read from stdin
    fh = io.TextIOWrapper(sys.stdin.buffer, encoding='utf8')

    # parse the input
    for line in fh:
        if line =='\n':
            pass
        else:
            compound = ''
            ortho = '' 
            words = line.split()
            words = [word for word in words if len(word) > 0 and word != '-' and word != '_']
            for i in range(0, len(words)):
                word = words[i].strip()
                ortho += word
                word = word.strip(punctuation).lower()
                ## 29.03.16: check if tokenize is true
                ## if true, call this routine for each substring
                ## and re-concatenate 
                if (args.tokenize and '-' in word) or (args.tokenize and '_' in word):
                    substrings = re.split(r'(_|-)', word)
                    values = substrings[::2]
                    delimiters = substrings[1::2] + ['']
                    ipa = [convert(x, args.dialect, args.glottal, args.pham, args.cao, args.palatals, args.delimit, args.tone_letters).strip() for x in values]
                    seq = ''.join(v + d for v, d in zip(ipa, delimiters))
                else:
                    seq = convert(word, args.dialect, args.glottal, args.pham, args.cao, args.palatals, args.delimit, args.tone_letters).strip()
                # concatenate
                if len(words) >= 2:
                    ortho += ' '
                if i < len(words) - 1:
                    seq = seq + ' '
                compound = compound + seq
            
            ## entire line has been parsed
            if ortho == '':
                pass
            else:
                ortho = ortho.strip()
                ## print orthography?
                if args.output_ortho: print(ortho, end=','),
                print(compound)

    # If we have an open filehandle, close it
    try:     
        fh.close()
    except AttributeError:
        sys.exit(0)

if __name__ == '__main__':
    main()
