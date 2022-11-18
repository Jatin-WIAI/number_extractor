# Word to Number for Hindi
 
This is a Python module to convert number words (eg. twenty one) to numeric digits (21). It works for positive numbers upto the range of 999,999,999,999 (i.e. billions)
This library works in two modes:
- Translation
- Without Translation

The `translation` mode is the intelligent mode. It is capable of extracting number even from a text with some errors. Use this if you want to extract number from
output of an ASR (Automatic Speech Recognition) model.

The 'Without translation' mode relies completely on strict keyword matching, hence, it is much faster than `translation mode`. But, it will fail for inputs with
small variations or errors.

We have tried to build this library in such a way that it can be used to extract numbers for other languages as well with a little effort. A guide to add
a new language will be updated later.

Examples:
```
1) मेरे पास पाँच सौ तीस एकर जमीन है : Answer : 530
2) मेरे पास देढ़ एकर जमीन है : Answer : 1.5
3) मेरे पास एक दशमलव तीन एकर जमीन है : Answer : 1.3

```
## Implementation Details
To read more about how this was implemented, you can read this [blog](https://docs.google.com/document/d/14RPJ9xrvaM-ct5Q6VkYqRP0hagHSr1zkGvNKo1Q8XOQ/edit?usp=sharing)

Below is the installation, usage and other details of this module.
