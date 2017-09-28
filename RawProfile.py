# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 23:05:47 2017

@author: thoma
"""

from Cut import *

class RawProfile():
     
     def __init__(self, id, length, ):
          """Constructor"""
          self._id = id
          self._length = length
          self._cut_list = []
          self._remainder = length
          self._scrap = 0
          self._cut_id = "A"
          
     @property
     def id(self):
          return self._id
     
     @property
     def length(self):
          return self._length
     
     @property
     def remainder(self):
          return self._remainder
     
     @remainder.setter
     def remainder(self, value):
          self._remainder = value
     
     @property
     def cut_list(self):
          return self._cut_list

     @property
     def scrap(self):
          return self._scrap

     def cut_profile(self, profile_id, cut_length):
          self._remainder = self._remainder - cut_length
          cut_id = self.__get_cut_id()
          NewCut = Cut(cut_id, profile_id, cut_length)
          self._cut_list.append(NewCut)
          
          
     def __get_cut_id(self):
          id = self._cut_id
          self._cut_id = chr(ord(self._cut_id) + 1)
          return id
          
     def scrap_remainder(self):
          self._scrap = self._remainder
          self._remainder = 0