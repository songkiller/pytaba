from tforms import forms, validators
from tforms.fields import TextField, TextAreaField
from tforms.widgets import Input


# --- Some helper classes here
class FileInput(Input):
    input_type = 'file'


class FileField(TextField):
    widget = FileInput()


# --- Pytabas forms
class BaseForm(forms.TornadoForm):
    '''theme = TextField('Theme',
                  [validators.Length(min=4, max=50,
                                     message='Need correct theme'),
                                     validators.Required()])'''

    body = TextAreaField('Post',
                      [validators.Length(min=4, max=1000,
                                         message='Need correct message body'),
                                         validators.Required()])
    image = FileField()


# --- Unusefull but need forms
class TopicForm(BaseForm):
    pass


class CommentForm(BaseForm):
    pass
