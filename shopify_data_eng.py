#!/usr/bin/python

from argparse import ArgumentParser
import json


def merge_objects(obj1, obj2):
    '''
    Returns an object with all keys and values from `obj1` and `obj2`.
    If a key is shared between the two objects, the value in `obj2` will take precedence.
    '''
    merged = dict()
    merged.update(obj1)
    merged.update(obj2)
    return merged


def get_pairs(matches1, matches2, pad_with_null):
    '''
    Returns an array of objects created by merging every combination of objects in `matches1` and `matches2`.
    If `pad_with_null` is false and `matches1` or `matches2` is empty, this function returns an empty array.
    If `pad_with_null` is true and `matches1` or `matches2` is empty, then this function returns whichever array is not empty.
    If `pad_with_null` is true and `matches1` and `matches2` are empty, then this function returns an empty array.
    '''
    if pad_with_null == False or (len(matches1) > 0 and len(matches2) > 0):
        result = []
        for item1 in matches1:
            for item2 in matches2:
                result.append(merge_objects(item1, item2))
        return result
    elif len(matches1) == 0: # pad_with_null is True
        return matches2
    elif len(matches2) == 0: # pad_with_null is True
        return matches1


def join_simple(array1, key1, array2, key2):
    '''
    Join `array1` and `array2` on keys `key1` and `key2`.
    Uses simple nested loop algorithm.
    '''
    result = []
    for item1 in array1:
        for item2 in array2:
            if item1[key1] == item2[key2]:
                result.append(merge_objects(item1, item2))
    return result


def join_sort(array1, key1, array2, key2, is_outer_join):
    '''
    Join `array1` and `array2` on keys `key1` and `key2`.
    Uses sort-merge join algorithm.
    '''
    result = []
    array1.sort(key=lambda obj: obj[key1])
    array2.sort(key=lambda obj: obj[key2])

    while len(array1) > 0 and len(array2) > 0:
        matches1 = []
        matches2 = []
        min_val = min(array1[0][key1], array2[0][key2])

        # Find items in each array with a join key equal to min_val and place
        # them in their respective matches arrays then remove them from their
        # respective arrays.

        # array1
        while len(array1) > 0:
            item = array1[0]
            if item[key1] == min_val:
                matches1.append(item)
                array1.remove(item)
            else:
                break

        # array2
        while len(array2) > 0:
            item = array2[0]
            if item[key2] == min_val:
                matches2.append(item)
                array2.remove(item)
            else:
                break

        result.extend(get_pairs(matches1, matches2, is_outer_join))

    return result


def main():
    # Get file paths and join keys from command line
    parser = ArgumentParser(description='Join two JSON arrays on a common key.')
    parser.add_argument('file1', type=str, help='path to first JSON file')
    parser.add_argument('key1', type=str, help='key in first JSON file to join on')
    parser.add_argument('file2', type=str, help='path to second JSON file')
    parser.add_argument('key2', type=str, help='key in second JSON file to join on')
    parser.add_argument('--outer', action='store_true', help='if provided, perform outer join')
    args = parser.parse_args()

    result = []
    with open(args.file1) as f1, open(args.file2) as f2:
        array1 = json.load(f1)
        array2 = json.load(f2)
        result = join_sort(array1, args.key1, array2, args.key2, args.outer)

    print(json.dumps(result))


if __name__ == '__main__':
    main()
