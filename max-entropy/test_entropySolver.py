import entropySolver
import numpy as np

def test_c2ind():
  assert entropySolver.c2ind('a') == 0
  assert entropySolver.c2ind('b') == 1
  assert entropySolver.c2ind('c') == 2
  assert entropySolver.c2ind('z') == 25

def test_entropyElement():
  assert entropySolver.entropyElement(0.0) == 0.0
  assert entropySolver.entropyElement(1.0) == 0.0
  assert entropySolver.entropyElement(0.5) == 0.5

def test_find():
  assert entropySolver.find('aaaabb','a') == [0,1,2,3]
  assert entropySolver.find('bbaaaa','a') == [2,3,4,5]

def test_getScore():
  assert entropySolver.getScore('speed','dares') == '10021'
  assert entropySolver.getScore('speed','creep') == '01220'
  assert entropySolver.getScore('neens','creep') == '01200'
  assert entropySolver.getScore('sneed','creep') == '00220'
  assert entropySolver.getScore('parks','reaps') == '11102'
