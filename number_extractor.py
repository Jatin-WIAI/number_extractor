import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
sys.path.append(os.path.dirname(SCRIPT_DIR))
# print(SCRIPT_DIR)

from indicnlp.normalize.indic_normalize import DevanagariNormalizer
from extraction_module.hi_number_extractor import HINumberExtractor
from extraction_module.en_number_extractor import ENNumberExtractor

class NumberExtractor():
    def __init__(self, lang, use_translate = False, translation_model_path = "/home/jatin/indicTrans/indic-en",debug = False) -> None:
        self.supported_langs = ["hi","en"]
        assert lang in self.supported_langs, "Language not supported"
        self.lang = lang
        self.use_translate = use_translate
        self.debug = debug
        self.translation_model = None
        if lang in ["hi"]:
            self.normalizer = DevanagariNormalizer()
        if use_translate:
            from fairseq import checkpoint_utils, distributed_utils, options, tasks, utils
            import sys
            sys.path.append("/home/jatin/")
            sys.path.append("/home/jatin/indicTrans")
            from indicTrans.inference.engine import Model
            self.translation_model = Model(expdir=translation_model_path)
        self.config_file_path = os.path.join(SCRIPT_DIR,"configs/num_ext.json")
        # print(self.config_file_path)
        if self.lang in ["hi"]:
            self.number_extractor = HINumberExtractor(lang,self.config_file_path,normalizer=self.normalizer,use_translate=use_translate,translation_model=self.translation_model,debug=debug)

        if self.lang in ["en"]:
            self.number_extractor = ENNumberExtractor()

    def extract_number(self,text):
        """Function which perform number extraction. Returns the maximum of all the numbers extracted.
        Args:
            text (str): input text

        Returns:
            float: output number, -1 if not found.
        """
        output_list,_ = self.number_extractor.get_numbers_list_and_normalized_text(text)
        output = -1
        if len(output_list)>0:
            for i in range(len(output_list)):
                if "." in str(output_list[i]):
                    if output<output_list[i]:
                        output = output_list[i]
            if output==-1:
                output = max(output_list)
        if self.number_extractor.do_deaccentification:
            text = self.number_extractor.perfrom_deaccentification(text)
            # print(text)
            output_list_2,_ = self.number_extractor.get_numbers_list_and_normalized_text(text)
            output_2 = -1
            if len(output_list_2)>0:
                for i in range(len(output_list_2)):
                    if "." in str(output_list_2[i]):
                        output_2 = output_list_2[i]
                        break
                if output_2==-1:
                    output_2 = max(output_list_2)
            if output_2>output:
                output = output_2
                output_list = output_list_2
        return output
    
    def extract_best_number_and_normalized_text(self,text):
        output_list, normalized_text = self.number_extractor.get_numbers_list_and_normalized_text(text)
        output = -1
        if len(output_list)>0:
            for i in range(len(output_list)):
                if "." in str(output_list[i]):
                    if output<output_list[i]:
                        output = output_list[i]
            if output==-1:
                output = max(output_list)
        if self.number_extractor.do_deaccentification:
            text = self.number_extractor.perfrom_deaccentification(text)
            output_list_2, normalized_text_2 =  self.number_extractor.get_numbers_list_and_normalized_text(text)
            output_2 = -1
            if len(output_list_2)>0:
                for i in range(len(output_list_2)):
                    if "." in str(output_list_2[i]):
                        output_2 = output_list_2[i]
                        break
                if output_2==-1:
                    output_2 = max(output_list_2)
            if output_2>output:
                output = output_2
                output_list = output_list_2
                normalized_text = normalized_text_2
        return output, normalized_text
    
    def extract_all_numbers_and_normalized_text(self,text):
        """Function which perform number extraction. Returns all the numbers extracted along with the normalized text.

        Args:
            text (str): input text
        
        Returns:
            list: list of all the numbers extracted.
        """
        output_list, normalized_text = self.number_extractor.get_numbers_list_and_normalized_text(text)
        return_list = []
        return_list.append({
            "original":{
            "number_list": output_list,
            "normalized_text": normalized_text,
            "original_text": text
            }
        })
        if self.number_extractor.do_deaccentification:
            text = self.number_extractor.perfrom_deaccentification(text)
            output_list_2, normalized_text =  self.number_extractor.get_numbers_list_and_normalized_text(text)
            return_list.append({
                        "deaccentified":{
                        "number_list": output_list_2,
                        "normalized_text": normalized_text,
                        "original_text": text
                        }
                    })
        return return_list
