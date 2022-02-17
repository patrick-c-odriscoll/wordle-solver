import numpy as np
import matplotlib.pyplot as plt

''' helper functions '''
def c2ind(c):
  return ord(c) - ord('a')

def entropyElement(p):
  return -p*np.log2(p) if ( (p > 0) and (p < 1) ) else 0

def find(s,c):
  return [i for i, l in enumerate(s) if l == c]

class cLogic():
  ''' class for detemring if a word is eligable '''
  def __init__(self):
    self.mask = np.ones((26,5),dtype=bool) # t/f letter location
    self.ncs = set() # character not in word
    self.cs = {} # character is in word
    return
  
  def grey(self,c,pos):
    if not c in self.cs:
      self.mask[c2ind(c),:] = False
      self.ncs.add(c)
    else:
      self.mask[c2ind(c),pos] = False
    return
  
  def yellow(self,c,pos):
    self.mask[c2ind(c),pos] = False
    if not c in self.cs:
      self.cs[c] = 1
    return

  def green(self,c,pos):
    self.mask[:,pos] = False
    self.mask[c2ind(c),pos] = True
    if not c in self.cs:
      self.cs[c] = 1
    return
  
  def countNonGrey(self,score,index):
    out = 0
    for ii in index:
      if score[ii] != '0':
        out += 1
    return out

  def applyScore(self,score,word):
    for c in word:
      index = find(word,c)
      if len(index) > 1:
        count = self.countNonGrey(score,index)
        if count == 0:
          for ii in index:
            self.grey(c,ii)
        else:
          if c in self.cs:
            if count > self.cs[c]:
              self.cs[c] = count
          else:
            self.cs[c] = count
          for ii in index:
            if score[ii] == '2':
              self.mask[:,ii] = False
              self.mask[c2ind(c),ii] = True
            else:
              self.mask[c2ind(c),ii] = False          
      else:
        index = index[0]
        if score[index] == '2':
          self.green(c,index)
        elif score[index] == '1':
          self.yellow(c,index)
        elif score[index] == '0':
          self.grey(c,index)
    return
  
  def checkWord(self,word):
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

def entropyWord(word,byPosition,byLetter):
  out = 0
  letters = set()
  for ii in range(5): # green information
    letters.add(word[ii])
    out += entropyElement(byPosition[c2ind(word[ii]),ii])
  for c in letters:   # yellow information
    out += entropyElement(byLetter[c2ind(c)])
  return out

def charFrequency(words,mask):
  out = np.zeros((26,5))
  for word in words:
    for ii in range(5):
      if mask.checkWord(word):
        out[c2ind(word[ii]),ii] += 1
  return out

def conditional(words,mask):
  freq = charFrequency(words,mask)
  byPosition = freq/np.sum(freq,0)
  byLetter = np.sum(freq,1)/(np.sum(freq,0)[0])
  return byPosition, byLetter

def differentialEntropy(words,byPosition,byLetter):
  out = np.zeros(len(words))
  ii = 0
  for word in words:
    out[ii] = entropyWord(word,byPosition,byLetter)
    ii += 1
  return out

def reduceWords(words,mask):
  ii = 0
  keep = np.ones(len(words),dtype=bool)
  for word in words:    
    keep[ii] = mask.checkWord(word)
    ii += 1
  return words[keep]

def getScore(word,truth):
  ''' wordle score of a guess
  input:
    word  - str - 5 letter guess
    truth - str - 5 letter secret
  output:
    string of the status of each letter of the word provided
    0 - grey   - letter appears more time in word than it does in truth
    1 - yellow - letter appears in word but in wrong position
    2 - green  - correct letter and possition
  '''
  out = ''
  cs = {} # letter, non-green count
  for ii in range(len(word)): # first pass is for green match
    if word[ii] == truth[ii]:
      out += '2'
    else:
      out += '0'
      if truth[ii] in cs:
        cs[truth[ii]] += 1
      else:
        cs[truth[ii]] = 1
  out = list(out)
  for ii in range(len(word)): # second pass is for yellow match
    if word[ii] in cs:
      if (out[ii] != '2') and (cs[word[ii]] > 0):
        out[ii] = '1'
      cs[word[ii]] -= 1
  return ''.join(out)

if __name__ == "__main__":
  hard = False
  file = open('../data/wordle-word-list.txt','r')
  words = np.array(file.readlines())
  for ii in range(len(words)):
    words[ii] = words[ii].strip()
  file.close()

  allWords = words
  guesses = np.zeros(len(allWords))
  jj = 0

  for secret in allWords:
    print(secret)
    mask = cLogic()
    words = allWords
    score = '00000'
    ii = 0
    while score != '22222':
      byPosition, byLetter = conditional(words,mask)
      entropy = differentialEntropy(words,byPosition,byLetter)
      print('\t' + str(ii) + '\t' + str(entropy[words==secret]) + '\t' + str(entropy[np.argmax(entropy)]))
      maxEntropy = entropy[np.argmax(entropy)]
      if maxEntropy > 0:
        guess = words[np.argmax(entropy)]
      else:
        guess = reduceWords(words,mask)[0]
      score = getScore(guess,secret)
      mask.applyScore(score,guess)
      if hard:
        print('\t' + str(ii) + '\t' + str(len(words)))
        words = reduceWords(words,mask)
      print('\t' + str(ii) + '\t' + str(guess))
      print('\t' + str(ii) + '\t' + str(score))
      print('')
      ii += 1  
    guesses[jj] = ii
    jj += 1

  print('mean',np.mean(guesses))
  print('median',np.median(guesses))
  print('std',np.std(guesses))
  print('win', np.sum(guesses<7)/len(guesses))
  plt.hist(guesses,bins=int(np.max(guesses)-np.min(guesses)))
  plt.show()
