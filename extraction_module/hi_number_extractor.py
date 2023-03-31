import sys
from word2number import w2n
import re
from collections import Counter
import logging
from extraction_module.utils import read_json,replace_all, create_number_array_from_text
import numpy as np

class HINumberExtractor():
    """
    The Class which extracts number from a text
    """
    def __init__(self,lang, config_file, normalizer = None,use_translate=True, translation_model=None,debug=False):
        self.supported_languages = ["hi","mr"]
        assert lang in self.supported_languages, "Language not supported"
        self.lang = lang
        self.config = read_json(config_file)[lang]
        self.wh_num_dict = read_json(self.config["wh_num_dict_file"])
        self.frac_dict =  read_json(self.config["frac_key_dict_file"])
        self.num_word_dict = read_json(self.config["num_word_dict_file"])
        self.en_num_dict = read_json(self.config["en_num_dict_file"])
        self.model = translation_model
        self.normalizer = normalizer
        self.use_translate = use_translate
        self.do_deaccentification = self.config["deaccentification"]
        if self.do_deaccentification:
            self.accents_dict = read_json(self.config["accent_file"])[lang]
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
    
    def normalize_text(self,text): 
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

    def extract_by_w2n(self,text):
        """Extract number using the word2number library for English. Return -1 if no number found
        Args:
            text (str): Input Text

        Returns:
            str: float
        """
        try:
            number = w2n.word_to_num(text)
        except:
            number = -1
        return number
    
    def extract_numerics_from_string(self,s):
        """Extract numerics from a string. It can be whole number or decimal.
        Args:
            s (str): Input string

        Returns:
            float: Extracted Number
        """
        temp = re.findall(r'[-+]?(?:\d*\.\d+|\d+)', s)
        res = list(map(float, temp))
        if len(res)>0:
            return res[0]
        return -1
    
    def spot_keyword(self,text,keywords):
        """Do string matching and spot keyword in text. If spotted return 1

        Args:
            text (str): Input text
            keywords (List): Keywords to spot

        Returns:
            _type_: 1 if spotted else 0
        """
        for key in keywords:
            if text.find(" "+key+" ")!=-1:
                return 1
        return 0
    
    def replace_keywords(self,text,keywords,target):
        """Replace keywords with target in the text.

        Args:
            text (_type_): Input text
            keywords (_type_): Keywordsd to replace
            target (_type_): string that replaces the keyword.

        Returns:
            _type_: replaced text
        """
        new_target = " "+target+" "
        new_keywords = [" "+key+" " for key in keywords]
        text = replace_all(text,new_keywords,new_target)

        return text


    def extract_number_from_array(self,arr):
        """Extract number from an array of numbers. 
        If the array has only one element, return that element.
        find the largest element position in the array. Multiply all the elements before that position and add all the elements after that position.

        Args:
            arr (List): List of numbers

        Returns:
            float: Extracted number
        """

        if len(arr)==2:
            if arr[0]>arr[1]:
                return arr[0]+arr[1]
            else:
                return arr[1]*arr[0]
        if len(arr)==1:
            return arr[0]
        max_index = np.argmax(arr)
        if max_index==0:
            return arr[0]+self.extract_number_from_array(arr[1:])
        elif max_index==len(arr)-1:
            return arr[-1]*self.extract_number_from_array(arr[:-1])
        else:
            return arr[max_index]*self.extract_number_from_array(arr[:max_index])+self.extract_number_from_array(arr[max_index+1:])
        
    def extract_decimal_number_from_array(self,arr):
        number_string = "".join([str(x) for x in arr])
        number_string = "0."+number_string
        return float(number_string)
    
    def compute(self,text):
        """Compute the number from the text.

        Args:
            text (_type_): Input text after replacing the keywords

        Returns:
            Float: Extracted number
        """
        number_array, decimal_number_array = create_number_array_from_text(text)
        number=0 ; decimal_number=0
        if len(number_array)==0 and len(decimal_number_array)==0:
            return -1
        if len(number_array)>0:
            number = self.extract_number_from_array(number_array)
        if len(decimal_number_array)>0:
            decimal_number = self.extract_decimal_number_from_array(decimal_number_array)
        return number+decimal_number

    def postprocess_en_text(self,text):
        """Postprocessing step for english text.

        Args:
            text (_type_): _description_

        Returns:
            _type_: _description_
        """
        removal_list = ["th ","st ","rd ","-"]
        target = " "

        text= replace_all(text,removal_list,target)
        return text
    
    def extract_by_og_lang_spot(self,text):
        """Extract number by spotting keywords in the original language. Spot fraction as well as whole numbers.
        Use fraction_dict and wholenumber_dict to perform this operation. If multiple number spotted, return maximum.
        Args:
            text (str): Input text (og language)

        Returns:
            float: Return maximum of all the numbers spotted.
        """
        wh_spots = []
        frac_spots = []
        # numbers = []
        for k,v in self.wh_num_dict.items():
            if self.spot_keyword(text,v)==1:
                wh_spots.append(float(k))
        for k,v in self.frac_dict.items():
            if self.spot_keyword(text,v)==1:
                frac_spots.append(float(k))
        if len(wh_spots+frac_spots)==0:
            return -1, None
        max_num = float(max(wh_spots+frac_spots))
        if max_num in frac_spots:
            return max_num, "frac"
        else:
            return max_num, "whole"
    
    def extract_by_en_spot(self,text):
        """Extract number by spotting keywords in english language.
        Use en_num_dict to perform this operation. If multiple number spotted, return maximum.
        Args:
            text (str): Input text (en language)

        Returns:
            float: Return maximum of all the numbers spotted.
        """
        numbers = []
        for k,v in self.en_num_dict.items():
            if self.spot_keyword(text,v)==1:
                numbers.append(float(k))
        if len(numbers)==0:
            return -1
        
        return max(numbers)


    def extract_by_replace(self,text):
        """Function perform extraction by replace. The first step is to replace keywords. Use num_word_dict for this.


        Args:
            text (_type_): _description_

        Returns:
            _type_: _description_
        """
        for k,v in self.num_word_dict.items():
            text = self.replace_keywords(text,v,k)
        # print(text)
        number = self.compute(text)
        if self.debug:
            print("Replaced Text: ",text)
        return number
    
    def combining_fn_for_translate(self,output_dict):
        """This function returns an output for multiple translation outputs. The outputs are combined using a specific combination strategy.
        1) Check for the most repeated number. If it is not -1 and more than 2 times repeated, return that.
        2) If above condition is not met, return the maximum.

        Args:
            output_dict (dict): A dictionary of outputs

        Returns:
           float: Output number, -1 if no number found.
        """
        L = [v for k,v in output_dict.items()]
        most_common,num_most_common = Counter(L).most_common(1)[0]
        if num_most_common>2 and most_common!=-1:
            return most_common
        else:
            return max(L)

    def extract_by_translate(self,text):
        """Function which perform number extraction by translation. 

        Args:
            text (str): input text

        Returns:
            float: output number, -1 if not found.
        """

        trans_text = self.translate(text).replace("1 / 2","one and half") 
        trans_text = self.normalize_text(trans_text)
        if self.debug:
            print(trans_text)
        output_dict = {}
        output_dict["numerics"] = self.extract_numerics_from_string(trans_text)
        output_dict["w2n"] = self.extract_by_w2n(trans_text)
        output_dict["spot"] = self.extract_by_en_spot(trans_text)
        pros_text = self.postprocess_en_text(trans_text)
        output_dict["pros_w2n"] = self.extract_by_w2n(pros_text)
        output_dict["pros_spot"] = self.extract_by_en_spot(pros_text)
        return self.combining_fn_for_translate(output_dict)
        # print(number_1,number_2,number_3,number_4,number_5)
        

    def final_combining_fn(self,output_dict, spot_type):
        """This function returns an output for multiple extraction outputs. The outputs are combined using a specific combination strategy."""

        if spot_type=="frac":
            return output_dict["spot"]
        if output_dict["replace"].is_integer()!=True:
            return output_dict["replace"]
        else:
            if self.use_translate==True:
                if output_dict["translate"].is_integer()!=True:
                    return output_dict["translate"]
                else:
                    L = [v for k,v in output_dict.items()]
                    most_common,num_most_common = Counter(L).most_common(1)[0]
                    if num_most_common>1 and most_common!=-1:
                        return most_common
                    else:
                        return max(output_dict["replace"],output_dict["translate"])
            else:
                return max(output_dict["spot"],output_dict["replace"])
        # if self.use_translate==True:
        #     if output_dict["spot"].is_integer()!=True:
        #         if (output_dict["spot"]*10)%5==0:
        #             return output_dict["spot"]
        #     if output_dict["replace"].is_integer()!=True:
        #         return output_dict["replace"]
        #     else:
        #         if output_dict["translate"].is_integer()!=True:
        #             return output_dict["translate"]
        #         else:
        #             L = [v for k,v in output_dict.items()]
        #             most_common,num_most_common = Counter(L).most_common(1)[0]
        #             if num_most_common>1 and most_common!=-1:
        #                 return most_common
        #             else:
        #                 return max(output_dict["replace"],output_dict["translate"])
        
        # else:
        #     if output_dict["spot"].is_integer()!=True:
        #         if (output_dict["spot"]*10)%5==0:
        #             return output_dict["spot"]
        #     if output_dict["replace"].is_integer()!=True:
        #         return output_dict["replace"]
        #     else:
        #         return max(output_dict["spot"],output_dict["replace"])

    def extract_number_main(self,text):
        text = text.lstrip().rstrip()
        text = self.normalize_text(" "+text+" ")
        output_dict = {}
        output_dict["spot"], spot_type = self.extract_by_og_lang_spot(text)
        output_dict["replace"] = float(self.extract_by_replace(text))
        if self.use_translate==True:
            output_dict["translate"] = float(self.extract_by_translate(text))
        if self.debug:
            print(output_dict)
        output = self.final_combining_fn(output_dict, spot_type)
        return output

    def extract_number(self,text):
        output = self.extract_number_main(text)
        if self.do_deaccentification:
            text = self.perfrom_deaccentification(text)
            # print(text)
            output_2 = self.extract_number_main(text)
            ouptut =  max(output,output_2)

        return ouptut

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
    extractor_obj = HINumberExtractor(lang,"/home/jatin/number_extractor/configs/num_ext.json",normalizer=normalizer,use_translate=False,translation_model=None,debug=True)
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

    
