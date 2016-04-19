#!/usr/bin/env python3

#julia_latex_to_unicode.py
#
# Copyright (C) 2016 Nathan Smith <nathan.smith5@mail.mcgill.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import gi
import os

gi.require_version('GtkSource', '3.0')
gi.require_version('Ide', '1.0')

from gi.repository import GObject
from gi.repository import GtkSource
from gi.repository import Ide

class CompletionProvider(Ide.Object, GtkSource.CompletionProvider, Ide.CompletionProvider):
    _dictionary = None
    _dictionary_filled = False

    def do_populate(self, context):
        iter1 = context.props.iter              # Current cursor position
        textbuffer = iter1.get_buffer()         # Text buffer
        iter2 = iter1.copy()                    # Copy the first buffer
        iter1.backward_word_starts(1)            # Stick iter1 at the begining of the word
        iter1.backward_char()                    # Start of word ignores "\" for some reason

        text = textbuffer.get_text(iter1, iter2, True)      # Text from buffer between iter1 and iter2

        if not text.startswith('\\'):                    # If the word doesn't start with "\" then quit
            context.add_proposals(self, [], True)
            return

        if self._dictionary_filled == False:
            self.init_dict()

        if text in self._dictionary.keys():
            item = GtkSource.CompletionItem(label=self._dictionary[text], text=self._dictionary[text])
            context.add_proposals(self, [item], True)

    def do_get_start_iter(self, context, proposal):
        iter = context.props.iter
        iter.backward_word_starts(1)
        iter.backward_char()
        return True, iter

    def init_dict(self):
        # Initialize the latex to unicode symbol dictionary
        __location__ = os.path.dirname(__file__)
        latex_file = open(os.path.join(__location__, 'Latex_Keys.txt'), 'r')
        symbol_file = open(os.path.join(__location__, 'Unicode_keys.txt'), 'r')

        latex_keys = list(latex_file)
        unicode_symbols = list(symbol_file)

        for index in range(len(latex_keys)):
            latex_keys[index] = latex_keys[index].rstrip('\n')

        for index in range(len(unicode_symbols)):
            unicode_symbols[index] = unicode_symbols[index].rstrip('\n').encode('utf-8').decode('unicode-escape')

        self._dictionary = dict(zip(latex_keys, unicode_symbols))
        self._dictionary_filled = True
        return