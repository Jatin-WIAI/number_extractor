import sys
# from word2number import w2n
import re
from collections import Counter
import logging
import numpy as np
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append(SCRIPT_DIR)
util_data_dir = os.path.join(os.path.dirname(SCRIPT_DIR),"util_data")
itn_dir = os.path.join(os.path.dirname(SCRIPT_DIR),"indic-ITN/src")
sys.path.append(itn_dir)

from extraction_module.utils import read_json,replace_all, create_number_array_from_text
from inverse_text_normalization.hi.run_predict import inverse_normalize_numbers_in_text
from en_number_extractor import ENNumberExtractor

class HINumberExtractor():
    """
    The Class which extracts number from a text
    """
    def __init__(self,lang, config_file, normalizer = None, do_deaccentification = True,use_translate=False, translation_model=None,debug=False):
        self.supported_languages = ["hi","mr"]
        assert lang in self.supported_languages, "Language not supported"
        self.lang = lang
        self.config = read_json(config_file)[lang]
        self.model = translation_model
        self.normalizer = normalizer
        self.use_translate = use_translate
        self.do_deaccentification = do_deaccentification
        if self.do_deaccentification:
            self.accents_dict = read_json(os.path.join(util_data_dir,self.config["accent_file"]))[lang]

        if self.use_translate:
            self.en_number_extractor = ENNumberExtractor()

        self.debug = debug

    def perfrom_deaccentification(self,text):
        """Remove accents from the input text.

        Args:
            text (_type_): Input string

        Returns:
            _type_: text with accents removed.
        """
        for k,v in self.accents_dict.items():
            text = text.replace(k,v)
        return text

    def translate(self,text):
        """Translate text to english.

        Args:
            text (_type_): Text to be translated

        Returns:
            _type_: translated text
        """
        trans_text = self.model.translate_paragraph(text, self.lang, 'en')
        return trans_text
    
    def unicode_normalize_text(self,text): 
        """Unicode normalize the input text

        Args:
            text (str): Input string

        Returns:
            str: Normalized text
        """
        if self.normalizer!=None:
            unicode_normalized_text = self.normalizer.normalize(text)
        else:
            unicode_normalized_text = text
            logging.warn("You have not provided normalizer, text will not be unicode normalized")
        return unicode_normalized_text
    
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

    def extract_by_translate(self,text):
        """Function which perform number extraction by translation. 

        Args:
            text (str): input text

        Returns:
            float: output number, -1 if not found.
        """

        trans_text = self.translate(text).replace("1 / 2","one and half") 
        return self.en_number_extractor.extract_number(trans_text)
        # print(number_1,number_2,number_3,number_4,number_5)
        
    def get_numbers_list_and_normalized_text(self,text):
        text = text.lstrip().rstrip()
        text = self.unicode_normalize_text(text)
        output_dict = {}
        
        try:
            inverse_normalized_text = inverse_normalize_numbers_in_text([text])[0]
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
    # from fairseq import checkpoint_utils, distributed_utils, options, tasks, utils
    # import sys
    # sys.path.append("/home/jatin/")
    # sys.path.append("/home/jatin/indicTrans")
    # from indicTrans.inference.engine import Model
    from indicnlp.normalize.indic_normalize import DevanagariNormalizer
    import indicnlp
    # indic2en_model = Model(expdir='/home/jatin/indicTrans/indic-en')

    normalizer = indicnlp.normalize.indic_normalize.DevanagariNormalizer()
    lang = "hi"
    # extractor_obj = NumberExtractor("hi","/home/jatin/huggingface_demo/number_extractor/configs/num_ext.json",normalizer=normalizer,use_translate=False)
    extractor_obj = HINumberExtractor(lang,"/home/users/prayushif/data_backup/voice_survey_tool/git/voice_survey_tool/helper_modules/number_extractor/configs/num_ext.json",normalizer=normalizer,use_translate=False,translation_model=None,debug=True)
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
    ] }
    numbers = []
    for example in examples[lang]:
        print(example)
        numbers.append(extractor_obj.get_numbers_list_and_normalized_text(example))
        print("\n")

    print(numbers)

    ## सौ and सो
    ## साड़े and साढ़े