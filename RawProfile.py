from Cut import *

class RawProfile():
     
     def __init__(self, id, length):
          """Constructor"""
          self.id = id
          self.length = length
          self.cut_list = []
          self.remainder = length
          self.scrap = 0
          self.cut_id = "A"

     def cut(self, profile_id, cut_length):
          self.remainder = self.remainder - cut_length
          cut_id = self.__get_cut_id()
          NewCut = Cut(cut_id, profile_id, self.id, cut_length)
          self.cut_list.append(NewCut)

     def __get_cut_id(self):
          id = self.cut_id
          self.cut_id = chr(ord(self.cut_id) + 1)
          return id
          
     def scrap_remainder(self):
          self.scrap = self.remainder
          self.remainder = 0
          
     def is_raw(self):
          return self.length == self.remainder