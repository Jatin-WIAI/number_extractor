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
        return self.number_extractor.extract_number(text)
    
    def extract_all_numbers_and_normalized_text(self,text):
        return self.number_extractor.extract_all_numbers_and_normalized_text(text)
