from .base_model import _FileModel

class ModelConverter():
    @classmethod
    def convert(cls, model_class):
        class TempFileModel(_FileModel):
            CONTENT_DIR = model_class.CONTENT_DIR
            REQUIRED_META = model_class.REQUIRED_META
            OPTIONAL_META = model_class.OPTIONAL_META

        for model in TempFileModel.all():
            meta = model.metadata
            meta['markdown'] = model.markdown

            bad_keys = [key for key in meta if key not in model_class._columns().keys()]
            for key in bad_keys:
                del meta[key]

            model_class.create(**meta)
