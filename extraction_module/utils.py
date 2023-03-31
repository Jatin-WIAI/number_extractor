import json
import logging

def read_json(file_name):
    try:
        with open(file_name,"r") as f:
            data = json.load(f)
    except:
        logging.error("Error in reading the file "+file_name)
    return data

def replace_all(text,keywords,target):
    """Replace keywords with target in the text.

    Args:
        text (_type_): Input text
        keywords (_type_): Keywordsd to replace
        target (_type_): string that replaces the keyword.

    Returns:
        _type_: replaced text
    """
    for key in keywords:
        text = text.replace(key,target)
    return text

def create_number_array_from_text(text:str):
    """Create an array of numbers from the text. It can be whole number or decimal.

    Args:
        text (str): Input text

    Returns:
        List: List of numbers
    """
    words = [word for word in text.split(' ') if word!='']
    arr = []
    deci_arr = []
    is_decimal = 0
    for word in words:
        if word.isnumeric() and is_decimal==0:
            arr.append(float(word))
        elif word.isnumeric() and is_decimal==1:
            deci_arr.append(int(word))
        elif word=='point':
            is_decimal = 1
    return arr, deci_arr

