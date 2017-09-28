# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 23:29:13 2017

@author: thoma
"""

class Cut():
     
     def __init__(self, id, profile_id, length):
          """Constructor"""
          self._id = id
          self._length = length
          self._profile_id = profile_id

     @property
     def id(self):
          return self._id
     
     @property
     def length(self):
          return self._length
     