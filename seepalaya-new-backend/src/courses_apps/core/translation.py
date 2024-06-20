from modeltranslation.translator import translator, TranslationOptions
from .models import Grade, Language, Subject

class LanguageTranslationOptions(TranslationOptions):
    fields = ('language',)

translator.register(Language, LanguageTranslationOptions)


class SubjectTranslationOptions(TranslationOptions):
    fields = ('subject',)

translator.register(Subject, SubjectTranslationOptions)



class GradeTranslationOptions(TranslationOptions):
    fields = ('grade',)

translator.register(Grade, GradeTranslationOptions)