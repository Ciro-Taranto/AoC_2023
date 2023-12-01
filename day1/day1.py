
import regex
import re
from pathlib import Path

import inflect

from aoc_utils import timing

numbers = []
with  open(Path(__file__).parent / 'input.txt', 'r') as fin: 
    for line in fin.readlines():
        vals = re.findall(r'\d', line)
        numbers.append(int(vals[0] + vals[-1]))
        
print(sum(numbers))


# Part 2 
numbers = []
mapping = {str(val): str(val) for val in range(0,10)}
words_mapping = {inflect.engine().number_to_words(val): str(val) for val in range(0, 10)}
mapping = mapping | words_mapping
pattern = regex.compile(r'\d|{}'.format("|".join(words_mapping)))
with timing():
    with  open(Path(__file__).parent / 'input.txt', 'r') as fin: 
        for line in fin.readlines():
            vals = pattern.findall(line, overlapped=True)
            numbers.append(int(mapping[vals[0]] + mapping[vals[-1]]))
    print(sum(numbers))

# part 2 without third party lib

def find_first_and_last(pattern: re.Pattern, string: str) -> tuple[str, str]:
    match = pattern.search(string)
    first = last = match.group()
    string = string[match.start() + 1:]
    while (match := pattern.search(string)):
        last = match.group()
        string = string[match.start() + 1:]
    return first, last

numbers = []
pattern = re.compile(r'\d|{}'.format("|".join(words_mapping)))
with timing():
    with  open(Path(__file__).parent / 'input.txt', 'r') as fin: 
        for line in fin.readlines():
            vals = find_first_and_last(pattern, line)
            numbers.append(int(mapping[vals[0]] + mapping[vals[-1]]))
print(sum(numbers))
