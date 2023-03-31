from indicnlp.normalize.indic_normalize import DevanagariNormalizer
from extraction_module.hi_number_extractor import HINumberExtractor

class NumberExtractor():
    def __init__(self, lang, use_translate = False, translation_model_path = "/home/jatin/indicTrans/indic-en",debug = False) -> None:
        self.supported_langs = ["hi","mr"]
        assert lang in self.supported_langs, "Language not supported"
        self.lang = lang
        self.use_translate = use_translate
        self.debug = debug
        self.translation_model = None
        if lang in ["hi","mr"]:
            self.normalizer = DevanagariNormalizer()
        if use_translate:
            from fairseq import checkpoint_utils, distributed_utils, options, tasks, utils
            import sys
            sys.path.append("/home/jatin/")
            sys.path.append("/home/jatin/indicTrans")
            from indicTrans.inference.engine import Model
            self.translation_model = Model(expdir=translation_model_path)
        if self.lang in ["hi","mr"]:
            self.number_extractor = HINumberExtractor(lang,"../configs/num_ext.json",normalizer=self.normalizer,use_translate=use_translate,translation_model=self.translation_model,debug=debug)

    def extract_number(self,text):
        return self.number_extractor.extract_number(text)
