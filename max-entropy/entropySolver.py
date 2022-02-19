import numpy as np
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(str(os.path.dirname(os.path.realpath(__file__)))+'//..')
import wordle
import argparse

__author__ = "Patrick C O\'Driscoll"
__copyright__ = "2022"
__credits__ = ["Patrick C O\'Driscoll"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Patrick C O\'Driscoll"
__email__ = "patrick.c.odriscoll@gmail.com"

def c2ind(c):
  '''
    Determine the index of a character
      input:
        c - char - target char
      output:
        zero index integer of location in alphabet
  '''
  return ord(c) - ord('a')

def find(word,c):
  '''
    Find the index of an input character
    input:
      c - char - target char
      word - str - string to find the char i
    output:
      list of indecies that have character c
  '''
  return [i for i, l in enumerate(word) if l == c]

def entropyElement(p):
  '''
    Safe calculation of entropy. It garuantees is 0 if is is outside of p in (0,1) 
      input:
        p - float - the probability of an event
      output:
        entropy of p
  '''
  return -p*np.log2(p) if ( (p > 0) and (p < 1) ) else 0

class cLogic():
  def __init__(self):
    '''
      Create a mask and maintain it based upon the feedback from the guesses
      members:
        mask - mask of bools to know if the word is possible
        ncs  - set of chars that are not in the secret
        cs   - hash map of key: char, value: number of known occurances in the secret
    '''
    self.mask = np.ones((26,5),dtype=bool)  # t/f letter location
    self.ncs = set()                        # character not in word
    self.cs = {}                            # character is in word
    return
  
  def grey(self,c,pos):
    '''
      If the feedback is grey apply it to the mask
      input:
        c   - char - chacter that got the grey feedback
        pos - int  - position of the character
      output:
        Update the mask items
    '''
    if not c in self.cs:
      self.mask[c2ind(c),:] = False
      self.ncs.add(c)
    else:
      self.mask[c2ind(c),pos] = False
    return
  
  def countNonGrey(self,score,index):
    '''
      Count the number of non-grey feedback on an index array
      input:
        score - str in 0-2 - score of performance
        index - list[int]  - list of indexes of hte same character
      output:
        Number of non-grey in index list
    '''
    out = 0
    for ii in index:
      if score[ii] != '0':
        out += 1
    return out

  def applyScore(self,score,word):
    '''
      Apply the score to the mask matrix.
      input:
        score - str in 0-2 - score of performance
        word  - str        - current guess
      output:
        updated mask structure
    '''
    for c in word:
      index = find(word,c) # find indexes for each character
      if len(index) > 1:                        # if there is more than 1 match
        count = self.countNonGrey(score,index)  # get non-grey entries
        if count == 0:                          # if only grey
          for ii in index:
            self.grey(c,ii)
        else:                                   # otherwise
          if c in self.cs:                      # update the count of c in secret
            if count > self.cs[c]:
              self.cs[c] = count
          else:
            self.cs[c] = count
          for ii in index:                      # update mask based upon yellow / green info
            if score[ii] == '2':
              self.mask[:,ii] = False
              self.mask[c2ind(c),ii] = True
            else:
              self.mask[c2ind(c),ii] = False          
      else:                                     # if there is 1 match
        index = index[0]
        if score[index] == '2':                 # simple green update
          self.mask[:,index] = False
          self.mask[c2ind(c),index] = True
          if not c in self.cs:
            self.cs[c] = 1
        elif score[index] == '1':               # simple yellow update
          self.mask[c2ind(c),index] = False
          if not c in self.cs:
            self.cs[c] = 1
        elif score[index] == '0':               # simple grey update
          self.grey(c,index)
    return
  
  def checkWord(self,word):
    '''
      Check and see if the word is a valid one
        input:
          word - str - word to see if it is valid
        output:
          Bool - is the input a posibility
    '''
    for ii in range(5):
      if not self.mask[c2ind(word[ii]),ii]:
        return False
      if word[ii] in self.ncs:
        return False
    for c in self.cs:
      if not c in word:
        return False
      elif self.cs[c] > len(find(word,c)):
        return False
    return True

  def reduceWords(self,words):
    '''
      Reduce words from the list of guessable answers
        input:
          words - list of words
        output:
          list of words that are still possible
    '''
    ii = 0
    keep = np.ones(len(words),dtype=bool)
    for word in words:    
      keep[ii] = self.checkWord(word)
      ii += 1
    return words[keep]


class entropySolver():
  def __init__(self,words):
    ''' 
      Class to act as the predictor for the next best guesses.
      members:
        mask  - cLogic      - entity to predict viable words
        words - list[str]   - list of all avalible words
        byPosition - float[26,5] - probability of each character position
        byLetter - float[26] - probability of each character in the words
        entropy - float[len(words)] - entropy calculation for each word
        guessIndex - index of the best guess
    '''
    self.mask = cLogic()
    self.words = words
    return

  def conditional(self):
    '''
      Conditional probablity calculator of the current list of eligable words
      updated entities: byPosition, byLetter
    '''
    freq = np.zeros((26,5))
    for word in self.words:
      for ii in range(5):
        if self.mask.checkWord(word):
          freq[c2ind(word[ii]),ii] += 1
    self.byPosition = freq/np.sum(freq,0)
    self.byLetter = np.sum(freq,1)/(np.sum(freq,0)[0])
    return 
  
  def entropyWord(self,word):
    '''
      Calculate the entropy of the given word
      input:
        word - string - word to get the entropy of
      output:
        entropy calculaton of the word
    '''
    out = 0
    letters = set()
    for ii in range(5): # green information
      letters.add(word[ii])
      out += entropyElement(self.byPosition[c2ind(word[ii]),ii])
    for c in letters:   # yellow information
      out += entropyElement(self.byLetter[c2ind(c)])
    return out
  
  def differentialEntropy(self):
    '''
      Calcualte the entropy for each elegable word
      update: entropy
    '''
    self.entropy = np.zeros(len(self.words))
    ii = 0
    for word in self.words:
      self.entropy[ii] = self.entropyWord(word)
      ii += 1
    return
  
  def nextGuess(self):
    '''
      Main loop to determine the optimal next guess
      output: guess - word
    '''
    self.conditional()
    self.differentialEntropy()
    self.guessIndex = np.argmax(self.entropy)
    if self.entropy[self.guessIndex] > 0:
      return self.words[self.guessIndex]
    else:
      return self.mask.reduceWords(self.words)[0]

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Wordle Solver via Maximum Entropy Information Theory Approach')
  parser.add_argument('--hard',   action='store_true', help='solve in hard more')
  parser.add_argument('--debug',  action='store_true', help='print debug information')
  parser.add_argument('--play',   action='store_true', help='use as a wordle aid')
  args = parser.parse_args()

  allWords = wordle.getAllWords()

  if not args.play:
    guesses = np.zeros(len(allWords))
    jj = 0
    for secret in allWords:
      if args.debug:
        print('secret\t'+secret)
      solver = entropySolver(allWords)
      score = '00000'
      ii = 0
      while score != '22222':
        guess = solver.nextGuess()
        if args.debug:
          print('\t' + str(ii) + '\t' + str(solver.entropy[solver.words==secret]) + 
                '\t' + str(solver.entropy[solver.guessIndex]))
        score = wordle.getScore(guess,secret)
        solver.mask.applyScore(score,guess)
        if args.hard:
          if args.debug:
            print('\t' + str(ii) + '\t' + str(len(solver.words)))
          solver.mask.reduceWords()
        if args.debug:
          print('\t' + str(ii) + '\t' + str(guess))
          print('\t' + str(ii) + '\t' + str(score))
        ii += 1  
      guesses[jj] = ii
      jj += 1
      print('')
    print('mean',np.mean(guesses))
    print('median',np.median(guesses))
    print('std',np.std(guesses))
    print('win', np.sum(guesses<7)/len(guesses))
    plt.hist(guesses,bins=int(np.max(guesses)-np.min(guesses)))
    plt.show()
  
  else:
    score = '00000'
    solver = entropySolver(allWords)
    while score != '22222':
      guess = solver.nextGuess()
      print('Best guess:\t'+guess)
      score = str(input('Please give score: 0-grey, 1-yellow, 2-green\n'))
      assert len(score)==5
      for ii in score:
        assert ii in '012'
      solver.mask.applyScore(score,guess)
      if args.hard:
        solver.mask.reduceWords()
    print('Congradulations: You won!')
  