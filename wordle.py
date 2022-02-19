import numpy as np
import os

def getScore(word,truth):
  ''' 
    Wordle score of a guess
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

def getAllWords():
  '''
    Grab the data stored for all valid 5 letter words
      input:
        None
      output:
        list of all valid 5 letter words
  '''
  file = open(str(os.path.dirname(os.path.realpath(__file__)))+'\data\wordle-word-list.txt','r')
  words = np.array(file.readlines())
  for ii in range(len(words)):
    words[ii] = words[ii].strip()
  file.close()
  return words