import wordle

__author__ = "Patrick C O\'Driscoll"
__copyright__ = "2022"
__credits__ = ["Patrick C O\'Driscoll"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Patrick C O\'Driscoll"
__email__ = "patrick.c.odriscoll@gmail.com"

def test_getScore():
  assert wordle.getScore('speed','dares') == '10021'
  assert wordle.getScore('speed','creep') == '01220'
  assert wordle.getScore('neens','creep') == '01200'
  assert wordle.getScore('sneed','creep') == '00220'
  assert wordle.getScore('parks','reaps') == '11102'
