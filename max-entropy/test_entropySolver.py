import entropySolver

__author__ = "Patrick C O\'Driscoll"
__copyright__ = "2022"
__credits__ = ["Patrick C O\'Driscoll"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Patrick C O\'Driscoll"
__email__ = "patrick.c.odriscoll@gmail.com"

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
