"""
PC-BASIC - strings.py
String values

(c) 2013, 2014, 2015, 2016 Rob Hagemans
This file is released under the GNU GPL version 3 or later.
"""

import struct
import logging
from operator import itemgetter

from ..base import error
from . import numbers
import copy

class String(numbers.Value):
    """String pointer."""

    sigil = '$'
    size = 3

    def __init__(self, buffer, values):
        """Initialise the pointer."""
        numbers.Value.__init__(self, buffer, values)
        self._stringspace = values.stringspace

    def length(self):
        """String length."""
        return ord(self._buffer[0])

    def address(self):
        """Pointer address."""
        return struct.unpack_from('<H', self._buffer, 1)[0]

    def dereference(self):
        """String value pointed to."""
        length, address = struct.unpack('<BH', self._buffer)
        return self._stringspace.view(length, address).tobytes()

    def from_str(self, python_str):
        """Set to value of python str."""
        self._buffer[:] = struct.pack('<BH', *self._stringspace.store(python_str))
        return self

    def from_pointer(self, length, address):
        """Set buffer to string pointer."""
        self._buffer[:] = struct.pack('<BH', length, address)
        return self

    def to_pointer(self):
        """Get length and address."""
        return struct.unpack('<BH', self._buffer)

    from_value = from_str
    to_value = dereference
    to_str = dereference

    def add(self, right):
        """Concatenate strings. In-place for the pointer."""
        return self.new().from_str(self.dereference() + right.dereference())

    def eq(self, right):
        """This string equals the right-hand side."""
        return self.to_str() == right.to_str()

    def gt(self, right):
        """This string orders after the right-hand side."""
        left = self.to_str()
        right = right.to_str()
        shortest = min(len(left), len(right))
        for i in range(shortest):
            if left[i] > right[i]:
                return True
            elif left[i] < right[i]:
                return False
        # the same so far...
        # the shorter string is said to be less than the longer,
        # provided they are the same up till the length of the shorter.
        if len(left) > len(right):
            return True
        # left is shorter, or equal strings
        return False

    def lset(self, in_str, justify_right):
        """Justify a str into an existing buffer and pad with spaces."""
        # v is empty string if variable does not exist
        # trim and pad to size of target buffer
        length = self.length()
        in_str = in_str.to_value()
        if justify_right:
            in_str = in_str[:length].rjust(length)
        else:
            in_str = in_str[:length].ljust(length)
        # make a copy only if not in a writeable location
        target = self._stringspace.check_modify(*self.to_pointer())
        self.from_pointer(*target)
        # copy the new string in
        self._stringspace.view(*target)[:] = in_str
        return self

    def midset(self, start, num, val):
        """Modify a string in an existing buffer."""
        # we need to decrement basic offset by 1 to get python offset
        offset = start - 1
        # don't overwrite more of the old string than the length of the new string
        num = min(num, val.length())
        # ensure the length of source string matches target
        length = self.length()
        if offset + num > length:
            num = length - offset
        if num <= 0:
            return self
        # make a copy only if not in a writeable location
        target = self._stringspace.check_modify(*self.to_pointer())
        self.from_pointer(*target)
        source = val.to_pointer()
        if source != target:
            self._stringspace.view(*target)[offset:offset+num] = self._stringspace.view(*source)[:num]
        else:
            # copy byte by byte from left to right
            # to conform to GW overwriting of source string on overlap
            for i in range(num):
                self._stringspace.view(*target)[i+offset:i+offset+1] = self._stringspace.view(*source)[i]
        return self


    ######################################################################
    # unary functions

    def len(self):
        """LEN: length of string."""
        return numbers.Integer(None, self._values).from_int(self.length())

    def asc(self):
        """ASC: ordinal ASCII value of a character."""
        s = self.to_str()
        error.throw_if(not s)
        return numbers.Integer(None, self._values).from_int(ord(s[0]))

    def space(self, num):
        """SPACE$: repeat spaces."""
        num = num.to_integer().to_int()
        error.range_check(0, 255, num)
        return self.new().from_str(' ' * num)


class StringSpace(object):
    """Table of strings accessible by their length and address."""

    def __init__(self, memory):
        """Initialise empty string space."""
        self._memory = memory
        self._strings = {}
        self._temp = None
        self.clear()

    def __str__(self):
        """Debugging representation of string table."""
        return '\n'.join('%x: %s' % (n, repr(v)) for n, v in self._strings.iteritems())

    def clear(self):
        """Empty string space."""
        self._strings.clear()
        # strings are placed at the top of string memory, just below the stack
        self.current = self._memory.stack_start()
        logging.debug('strings.py, StringSpace.clear(), self.current changed to'+str(self.current))

    def rebuild(self, stringspace):
        """Rebuild from stored copy."""
        self.clear()
        self._strings.update(stringspace._strings)
        self.current = stringspace.current

    def copy_to(self, string_space, length, address):
        """Copy a string to another string space."""
        string_to_copy=self.view(length, address).tobytes()
        #return string_space.store(self.view(length, address).tobytes())
        return string_space.store(string_to_copy)

    def _retrieve(self, length, address):
        """Retrieve a string by its pointer."""
        # if string length == 0, return empty string
        #if length != 0:
        #    try:
        #        strval=self._strings[address]
        #    except KeyError:
        #        logging.debug('strings.py, _retrieve, KeyError with address='+str(address)+', length='+str(length))
        return bytearray() if length == 0 else self._strings[address]

    def view(self, length, address):
        """Return a writeable view of a string from its string pointer."""
        # empty string pointers can point anywhere
        if length == 0:
            return memoryview(bytearray())
        if address >= self._memory.var_start(): #if we no longer double-store code strings in string space object
        #if address >= self._memory.code_start:
            # string stored in string space
            return memoryview(self._retrieve(length, address))
        elif address >= self._memory.code_start:
            # get string stored in code as bytearray
            codestr = self._memory.program.get_memory_block(address, length)
            return memoryview(codestr)
        else:
            # string stored in field buffers
            # find the file we're in
            start = address - self._memory.field_mem_start
            number = 1 + start // self._memory.field_mem_offset
            offset = start % self._memory.field_mem_offset
            if (number not in self._memory.fields) or (start < 0):
                raise KeyError('Invalid string pointer')
            # memoryview slice continues to point to buffer, does not copy
            return memoryview(self._memory.fields[number].buffer)[offset:offset+length]

    def check_modify(self, length, address):
        """Assign a new string into an existing buffer."""
        # if it is a code literal, we now do need to allocate space for a copy
        if address >= self._memory.code_start and address < self._memory.var_start():
            length, address = self.store(self.view(length, address).tobytes())
        return length, address

    def store(self, in_str, address=None):
        """Store a new string and return the string pointer."""
        length = len(in_str)
        # don't store overlong strings
        if length > 255:
            raise error.RunError(error.STRING_TOO_LONG)
        currentstart = copy.deepcopy(self.current)
        # don't store if address is provided (code or FIELD strings)
        if address is None:
            # reserve string space; collect garbage if necessary
            self._memory.check_free(length, error.OUT_OF_STRING_SPACE)
            # find new string address
            self.current -= length
            address = self.current + 1
            # don't store empty strings
            if length > 0:
                logging.debug('strings.py, store, self.current at start='+str(currentstart)+', storing:' + str(in_str) + ' into address:' + str(address)+ ', self.current at end='+str(self.current)+', len='+str(length))
                # copy and convert to bytearray
                self._strings[address] = bytearray(in_str)
        return length, address

    def _delete_last(self):
        """Delete the string provided if it is at the top of string space."""
        last_address = self.current + 1
        try:
            length = len(self._strings[last_address])
            self.current += length
            del self._strings[last_address]
            logging.debug('strings.py, StringSpace.delete_last(), self.current changed to: ' + str(self.current))
        except KeyError:
            # happens if we're called before an out-of-memory exception is handled
            # and the string wasn't allocated
            pass

    def collect_garbage(self, string_ptrs):
        """Re-store the strings referenced in string_ptrs, delete the rest."""
        # string_ptrs should be a list of memoryviews to the original pointers
        # retrieve addresses and copy strings
        string_list = []
        for view in string_ptrs:
            length, addr = struct.unpack('<BH', view.tobytes())
            # exclude empty elements of string arrays
            if not (length==0 and addr==0):
                try:
                    string_list.append((view, addr, self._retrieve(length, addr)))
                except KeyError:
                    if addr >= self._memory.var_start():
                        logging.error('String not found in string space when collecting garbage: %x', addr)
                        raise
                    # else: string is not located in memory - FIELD or code
        # sort by address, largest first (maintain order of storage)
        string_list.sort(key=itemgetter(1), reverse=True)
        # clear the string buffer and re-store all referenced strings
        self.clear()
        for view, _, string in string_list:
            # re-allocate string space
            # update the original pointers supplied (these are memoryviews)
            view[:] = struct.pack('<BH', *self.store(string))
        # readdress temporary at top of string space
        if self._temp is not None:
            self._temp = self.current

    def get_memory(self, address):
        """Retrieve data from data memory: string space """
        # find the variable we're in
        for try_address, value in self._strings.iteritems():
            length = len(value)
            if try_address <= address < try_address + length:
                return value[address - try_address]
        return -1

    def __enter__(self):
        """Enter temp-string context guard."""
        self._temp = self.current

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit temp-string context guard."""
        if self._temp != self.current:
            self._delete_last()
        self._temp = None

    def next_temporary(self, args):
        """Retrieve a value from an iterator and return as Python value. Store strings in a temporary."""
        with self:
            expr = next(args)
            if isinstance(expr, String):
                return expr.to_value()
            elif expr is None:
                return expr
            else:
                raise error.RunError(error.TYPE_MISMATCH)
