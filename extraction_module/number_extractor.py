import json
import pandas as pd
import sys
from word2number import w2n
import json
import re
from num2words import num2words
from collections import Counter

def read_json(file_name):
    with open(file_name,"r") as f:
        data = json.load(f)
    return data


class NumberExtractor():
    def __init__(self,lang, config_file) -> None:
        self.lang = lang
        self.config = read_json(config_file)[lang]
        self.wh_num_dict = read_json(self.config["wh_num_dict_file"])
        self.frac_dict =  read_json(self.config["frac_key_dict_file"])
        self.deci_dict = read_json(self.config["deci_key_dict_file"])
        self.en_num_dict = read_json(self.config["en_num_dict_file"])

    def translate(self,model,text):
        trans_text = model.translate_paragraph(text, self.lang, 'en')
        return trans_text
    
    def extract_by_w2n(self,text):
        try:
            number = w2n.word_to_num(text)
        except:
            number = -1
        return number
    
    def extract_numerics_from_string(self,s):
        temp = re.findall(r'[-+]?(?:\d*\.\d+|\d+)', s)
        res = list(map(float, temp))
        if len(res)>0:
            return res[0]
        return -1
    
    def spot_keyword(self,text,keywords):
        for key in keywords:
            if text.find(" "+key+" ")!=-1:
                return 1
        return 0
    
    def replace_keywords(self,text,keywords,target):
        new_target = " "+target+" "
        for key in keywords:
            new_key = " "+key+" "
            text = text.replace(new_key,new_target)
        return text

    def postprocess_en_text(self,text):
        text= text.replace("th "," ").replace("st", " ").replace("rd "," ").replace("-"," ")
        return text
    
    def extract_by_og_lang_spot(self,text):
        numbers = []
        for k,v in self.wh_num_dict.items():
            if self.spot_keyword(text,v)==1:
                numbers.append(float(k))
        for k,v in self.frac_dict.items():
            if self.spot_keyword(text,v)==1:
                numbers.append(float(k))
        if len(numbers)==0:
            return -1
        return max(numbers)
    
    def extract_by_en_spot(self,text):
        numbers = []
        for k,v in self.en_num_dict.items():
            if self.spot_keyword(text,v)==1:
                numbers.append(float(k))
        if len(numbers)==0:
            return -1
        
        return max(numbers)


    def extract_by_replace(self,text):
        for k,v in self.deci_dict.items():
            text = self.replace_keywords(text,v,k)
        # print(text)
        words = [x for x in text.split(" ")]
        new_words = []
        for word in words:
            if word.isdigit():
                new_words.append(num2words(int(word)))
            else:
                new_words.append(word)
        new_text = " ".join(new_words).replace(" one hundred "," hundred ").replace(" one thousand "," thousand ")
        number = self.extract_by_w2n(new_text)
        # print(new_text)
        return number
    
    def extract_by_translate(self,model,normalizer,text):
        trans_text = self.translate(model,text).replace("1 / 2","one and half") 
        trans_text = normalizer.normalize(" "+trans_text+" ")
        # print(trans_text)
        number_1 = self.extract_numerics_from_string(trans_text)
        number_2 = self.extract_by_w2n(trans_text)
        number_3 = self.extract_by_en_spot(trans_text)
        pros_text = self.postprocess_en_text(trans_text)
        number_4 = self.extract_by_w2n(pros_text)
        number_5 = self.extract_by_en_spot(pros_text)
        # print(number_1,number_2,number_3,number_4,number_5)
        L = [number_1,number_2,number_3,number_4,number_5]
        most_common,num_most_common = Counter(L).most_common(1)[0]
        if num_most_common>2 and most_common!=-1:
            return most_common
        else:
            return max(number_1,number_2,number_3,number_4,number_5)

    def master_extract_fn(self,model,normalizer,text):
        text = normalizer.normalize(" "+text+" ")
        number_1 = float(self.extract_by_og_lang_spot(text))
        number_2 = float(self.extract_by_replace(text))
        number_3 = float(self.extract_by_translate(model,normalizer,text))
        print(number_1,number_2,number_3)
        if number_1.is_integer()!=True:
            if (number_1*10)%5==0:
                return number_1
        if number_2.is_integer()!=True:
            return number_2
        else:
            if number_2.is_integer()!=True:
                return number_3
            else:
                L = [number_1,number_2,number_3]
                most_common,num_most_common = Counter(L).most_common(1)[0]
                if num_most_common>1 and most_common!=-1:
                    return most_common
                else:
                    return max(number_2,number_3)

        # return (number_1,number_2,number_3)


# from fairseq import checkpoint_utils, distributed_utils, options, tasks, utils
# import sys
# sys.path.append("/home/jatin/indic_lib")
# sys.path.append("/home/jatin/indic_lib/indicTrans")
# from indicTrans.inference.engine import Model
# import indicnlp
# indic2en_model = Model(expdir='/home/jatin/indic_lib/indic-en')

# normalizer = indicnlp.normalize.indic_normalize.DevanagariNormalizer()

# extractor_obj = NumberExtractor("hi","/home/jatin/huggingface_demo/cotton_ace/configs/num_ext.json")
# examples = [
#     "सौ एकर जमीन है",
#     "पाँच सौ एकर जमीन है",
#     "पांचसौ एकर जमीन है",
#     "पाँच सौ सात एकर जमीन है",
#     "देढ़ एकर जमीन है",
#     "एक दशमलव तीन एकर जमीन है",
#     "501 एकर जमीन है",
#     "आधा एकर जमीन है",
#     "देढ़ एकर जमीन है",
#     "देड़ एकर",
#     "साढ़े छः एकड़ जमीन",
#     "मेरे पास साढ़े दस एकड़ जमीन है",
#     "निश्लसेलिशन चार सौ छः एकर जमीन है",
#     "दो हज़ार पाँच सौ तीस"
# ]
# numbers = []
# for example in examples:
#     numbers.append(extractor_obj.master_extract_fn(indic2en_model,normalizer,example))

# print(numbers)

## सौ and सो
## साड़े and साढ़े

    
