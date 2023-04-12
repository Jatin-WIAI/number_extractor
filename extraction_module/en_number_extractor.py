import sys
# from word2number import w2n
import re
from collections import Counter
import logging
from extraction_module.utils import read_json,replace_all, create_number_array_from_text
import numpy as np
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append(SCRIPT_DIR)
util_data_dir = os.path.join(os.path.dirname(SCRIPT_DIR),"util_data")
itn_dir = os.path.join(os.path.dirname(SCRIPT_DIR),"indic-ITN/src")
sys.path.append(itn_dir)

from inverse_text_normalization.en.run_predict import inverse_normalize_text


class ENNumberExtractor():
    """
    The Class which extracts number from a text
    """
    def __init__(self,lang="en", config_file = None, normalizer = None, do_deaccentification = False,use_translate=False, translation_model=None,debug=False):
        self.supported_languages = ["en"]
        assert lang in self.supported_languages, "Language not supported"
        self.lang = lang
        self.do_deaccentification = do_deaccentification
        self.use_translate = use_translate
        self.debug = debug
        self.normalizer = normalizer
        
    def extract_numerics_from_string(self,s):
        """Extract numerics from a string. It can be whole number or decimal.
        Args:
            s (str): Input string

        Returns:
            float: Extracted Number
        """
        temp = re.findall(r'[-+]?(?:\d*\.\d+|\d+)', s)
        res = list(map(float, temp))
        return res
        
    def get_numbers_list_and_normalized_text(self,text):
        text = text.lstrip().rstrip()
        output_dict = {}
        
        try:
            inverse_normalized_text = inverse_normalize_text([text])[0]
            # print(inverse_normalized_text)
        except:
            inverse_normalized_text = text
        # print
        numbers_list = self.extract_numerics_from_string(inverse_normalized_text)
        if len(numbers_list)==0 and self.use_translate==True:
            number = self.extract_by_translate(text)
            if number!=-1:
                numbers_list.append(number)
            inverse_normalized_text = text
        return numbers_list, inverse_normalized_text

    # def extract_number(self,text):
    #     """Function which perform number extraction. Returns the maximum of all the numbers extracted.
    #     Args:
    #         text (str): input text

    #     Returns:
    #         float: output number, -1 if not found.
    #     """
    #     output_list,_ = self.get_numbers_list_and_normalized_text(text)
    #     output = -1
    #     if len(output_list)>0:
    #         for i in range(len(output_list)):
    #             if "." in str(output_list[i]):
    #                 if output<output_list[i]:
    #                     output = output_list[i]
    #         if output==-1:
    #             output = max(output_list)
    #     if self.do_deaccentification:
    #         text = self.perfrom_deaccentification(text)
    #         # print(text)
    #         output_list_2,_ = self.get_numbers_list_and_normalized_text(text)
    #         output_2 = -1
    #         if len(output_list_2)>0:
    #             for i in range(len(output_list_2)):
    #                 if "." in str(output_list_2[i]):
    #                     output_2 = output_list_2[i]
    #                     break
    #             if output_2==-1:
    #                 output_2 = max(output_list_2)
    #         if output_2>output:
    #             output = output_2
    #             output_list = output_list_2
    #     return output
    
    # def extract_best_number_and_normalized_text(self,text):
    #     output_list, normalized_text = self.get_numbers_list_and_normalized_text(text)
    #     output = -1
    #     if len(output_list)>0:
    #         for i in range(len(output_list)):
    #             if "." in str(output_list[i]):
    #                 if output<output_list[i]:
    #                     output = output_list[i]
    #         if output==-1:
    #             output = max(output_list)
    #     if self.do_deaccentification:
    #         text = self.perfrom_deaccentification(text)
    #         output_list_2, normalized_text_2 =  self.get_numbers_list_and_normalized_text(text)
    #         output_2 = -1
    #         if len(output_list_2)>0:
    #             for i in range(len(output_list_2)):
    #                 if "." in str(output_list_2[i]):
    #                     output_2 = output_list_2[i]
    #                     break
    #             if output_2==-1:
    #                 output_2 = max(output_list_2)
    #         if output_2>output:
    #             output = output_2
    #             output_list = output_list_2
    #             normalized_text = normalized_text_2
    #     return output, normalized_text

    
    # def extract_all_numbers_and_normalized_text(self,text):
    #     """Function which perform number extraction. Returns all the numbers extracted along with the normalized text.

    #     Args:
    #         text (str): input text
        
    #     Returns:
    #         list: list of all the numbers extracted.
    #     """
    #     output_list, normalized_text = self.get_numbers_list_and_normalized_text(text)
    #     return_list = []
    #     return_list.append({
    #         "original":{
    #         "number_list": output_list,
    #         "normalized_text": normalized_text,
    #         "original_text": text
    #         }
    #     })
    #     if self.do_deaccentification:
    #         text = self.perfrom_deaccentification(text)
    #         output_list_2, normalized_text =  self.get_numbers_list_and_normalized_text(text)
    #         return_list.append({
    #                     "deaccentified":{
    #                     "number_list": output_list_2,
    #                     "normalized_text": normalized_text,
    #                     "original_text": text
    #                     }
    #                 })
    #     return return_list
        # return (number_1,number_2,number_3)


if __name__ == "__main__":
    from fairseq import checkpoint_utils, distributed_utils, options, tasks, utils
    import sys
    sys.path.append("/home/jatin/")
    sys.path.append("/home/jatin/indicTrans")
    from indicTrans.inference.engine import Model
    import indicnlp
    # indic2en_model = Model(expdir='/home/jatin/indicTrans/indic-en')

    normalizer = indicnlp.normalize.indic_normalize.DevanagariNormalizer()
    lang = "hi"
    # extractor_obj = NumberExtractor("hi","/home/jatin/huggingface_demo/number_extractor/configs/num_ext.json",normalizer=normalizer,use_translate=False)
    extractor_obj = ENNumberExtractor(lang,"/home/jatin/number_extractor/configs/num_ext.json",normalizer=normalizer,use_translate=False,translation_model=None,debug=True)
    examples = {
        "hi":[
        "सौ एकर जमीन है",
        "पाँच सौ एकर जमीन है",
        "पांचसौ एकर जमीन है",
        "पाँच सौ सात एकर जमीन है",
        "देढ़ एकर जमीन है",
        "एक दशमलव तीन एकर जमीन है",
        "501 एकर जमीन है",
        "आधा एकर जमीन है",
        "देढ़ एकर जमीन है",
        "देड़ एकर",
        "साढ़े छः एकड़ जमीन",
        "मेरे पास साढ़े दस एकड़ जमीन है",
        "निश्लसेलिशन चार सौ छः एकर जमीन है",
        "दो हज़ार पाँच सौ तीस",
        "पाँच सौ सैतालीस एकर जमीन है",
        "मेरे पास पात सौ तीस एकर जमीन है",
        "तिरपन",
        "सैंतालिस",
        "दो हज़ार पाँच सौ त्रेपन",
        "देढ़ सौ एकर जमीन है",
        "साढ़े छः सौ एकड़ जमीन",
        "ग्यारह सौ एकर जमीन है",
        "ढाई सो एकर जमीन",
        "ढाईसो एकर जमीन",
        "मेरे परिवार में कुल बारा लोग है",
        "दो लाख पंद्रह हजार छः सौ इक्कीस",
        "सोलह करोड़ दो लाख पंद्रह हजार छः सौ इक्कीस",
        "एक दशमलव तीन एकर जमीन है",
        "दो दशमलव तीन चार"
    ],
    "mr":[
        "शंभर एकर जमीन",
        "पाचशे एकर जमीन",
        "पाचशे एकर जमीन",
        "पाचशे सात एकर जमीन",
        "दीड एकर जमीन",
        "एक पूर्णांक तीन एकर जमीन",
        "501 एकर आहे",
        "अर्धा एकर जमीन",
        "दीड एकर जमीन",
        "साडे सहा एकर जमीन",
        "माझ्याकडे साडे दहा एकर जमीन आहे",
        "निसलेशन म्हणजे चारशे सहा एकर जमीन",
        "दोन हजार पाचशे तीस",
        "पाचशे चाळीस एकर जमीन",
        "माझ्याकडे 100 आणि 30 एकर जमीन आहे",
        "त्रेपन्न",
        "सत्तेचाळीस",
        "दोन हजार पाचशे त्रेपन्न"
    ]
    }
    numbers = []
    for example in examples[lang]:
        print(example)
        numbers.append(extractor_obj.extract_number(example))
        print("\n")

    print(numbers)

    ## सौ and सो
    ## साड़े and साढ़े

    
