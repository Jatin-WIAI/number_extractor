# Word to Number for Hindi
 
This is a Python module to convert number words (eg. मेरे पास पाँच सौ तीस एकर जमीन है) to numeric digits (530). It works for positive numbers upto the range of 100000, it can be easily extended to work for much larger range. It also supports fractions and decimals with one decimal place. 

This library works in two modes:
- Translation
- Without Translation

Our system works well for small errors in accents even in normal mode (`without Translation`)

The `translation` mode is the intelligent mode but little less reliable. It is capable of extracting number even from a text with some errors. Use this if you want to extract number from output of an ASR (Automatic Speech Recognition) model.


We have tried to build this library in such a way that it can be used to extract numbers for other languages as well with a little effort. A guide to add
a new language will be updated later.

Examples:
```
1) मेरे पास पाँच सौ तीस एकर जमीन है : Answer : 530
2) मेरे पास देढ़ एकर जमीन है : Answer : 1.5
3) मेरे पास एक दशमलव तीन एकर जमीन है : Answer : 1.3

```
## Implementation Details

![Overall Workflow](/imgs/sentence_to_number.jpeg)

To read more about how this was implemented, you can read this [blog](https://docs.google.com/document/d/14RPJ9xrvaM-ct5Q6VkYqRP0hagHSr1zkGvNKo1Q8XOQ/edit?usp=sharing)

Below is the installation, usage and other details of this module.

## Tutorial on Installation
Colab Notebook Tutorial: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1vjD0-SpdWN9maOWEUkPnKGFtMxps6Hcl?usp=sharing)


