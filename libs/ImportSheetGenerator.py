#!/usr/local/bin/python
# -*- coding: utf-8 -*-

class ImportSheetGenerator:

   def get_title(self, title):
      return title.rsplit('.', 1)[0].rstrip()  #split once at full-stop (assumptuon 'ext' follows)

