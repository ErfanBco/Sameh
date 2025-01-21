from django import forms
from ProjectK.data import gregorian_to_jalali, getDefaultMonth
import datetime


class CreateTaskForm(forms.Form):
    months = [('01', 'فروردین'), ('02', 'اردیبهشت'), ('03', 'خرداد'), ('04', 'تیر'), ('05', 'مرداد'), ('06', 'شهریور'),
              ('07', 'مهر'), ('08', 'آبان'), ('09', 'آذر'), ('10', 'دی'), ('11', 'بهمن'), ('12', 'اسفند')]

    title = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'style': 'text-align: right;direction:rtl', 'placeholder': 'عنوان برنامه',
                   'value': ''}))
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': '6', 'style': 'text-align: right;direction:rtl', 'placeholder': 'شرح برنامه'}),
        required=False)

    employee = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={'class': 'form-group', 'required': 'True', 'style': 'text-align: right;direction:rtl', 'id': 'multiple-checkboxes'}),
        initial=0,
        label='کارمندان', required=True)

    fee = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'style': 'text-align: right;direction:rtl', 'x-data': 'true',
               'x-mask:dynamic': "$money($input, '.', ',')",
               'placeholder': 'پاداش اقدام(ریال)'}), label='پاداش', required=True)
    delay_punishment = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'style': 'text-align: right;direction:rtl', 'x-data': 'true',
                   'x-mask:dynamic': "$money($input, '.', ',')", 'placeholder': 'جریمه دیرکرد به ازای روز (ریال)'}))

    validator = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'ValidatorChange()', 'id': 'Validator', 'style': 'text-align: right;direction:rtl'}), initial=0,
        label='تاییدکننده', required=True)
    ValidatorFee = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'ValidatorFee', 'disabled': 'true', 'style': 'text-align: right;direction:rtl', 'x-data': 'true',
               'x-mask:dynamic': "$money($input, '.', ',')",
               'placeholder': 'پاداش تایید(ریال)'}), label='پاداش', required=True)

    GregorianDate = [int(datetime.datetime.now().strftime("%Y")), int(datetime.datetime.now().strftime("%#m")),
                     int(datetime.datetime.now().strftime("%#d"))]
    print(datetime.datetime.now().strftime("%d/%#m/%y"))
    year = forms.IntegerField(widget=forms.NumberInput(
        attrs={'class': 'form-control', 'x-data': 'true', 'minlength': '4', 'maxlength': '4', 'x-mask': "9999", 'style': 'text-align: right', 'value':
            getDefaultMonth()[0]}), label='سال')
    month = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'FormMonth', 'style': 'text-align: right', 'value':
            getDefaultMonth()[1]}), choices=months, label='ماه')

    delivery_date = forms.DateTimeField(
        widget=forms.DateInput(
            attrs={'name': 'persianDatapicker', 'style': 'text-align: right', 'x-data': 'true',
                   'x-mask:dynamic': "9999/99/99", 'id': 'persianDatapicker', 'type': 'text', 'class': 'form-control',
                   'placeholder': 'تاریخ تحویل'}),
        label='تاریخ تحویل')

    def __init__(self, args):
        super(CreateTaskForm, self).__init__(args)
        # print(args["Options"])
        # TODO validator and employee can be the same person
        self.fields['employee'].choices = args["Options"]
        self.fields['validator'].choices = args["Validators"]


class EditTaskForm(forms.Form):
    months = [('01', 'فروردین'), ('02', 'اردیبهشت'), ('03', 'خرداد'), ('04', 'تیر'), ('05', 'مرداد'), ('06', 'شهریور'),
              ('07', 'مهر'), ('08', 'آبان'), ('09', 'آذر'), ('10', 'دی'), ('11', 'بهمن'), ('12', 'اسفند')]

    # TODO employee field doesn't give error when is empty
    title = forms.CharField(label='عنوان برنامه', required=True)
    comment = forms.CharField(label='شرح برنامه', required=False)

    # employee = forms.MultipleChoiceField(initial=0, label='کارمندان')
    fee = forms.CharField(label='پاداش (ریال)')
    delay_punishment = forms.CharField(label='جریمه تاخیر به ازای روز (ریال)')

    validator = forms.ChoiceField(initial=0, label='تاییدکننده', required=True)
    ValidatorFee = forms.CharField(label='پاداش تاییدکننده', required=True)

    GregorianDate = [int(datetime.datetime.now().strftime("%Y")), int(datetime.datetime.now().strftime("%#m")),
                     int(datetime.datetime.now().strftime("%#d"))]
    ##print(datetime.datetime.now().strftime("%d/%#m/%y"))
    year = forms.IntegerField(label='سال')
    month = forms.ChoiceField(widget=forms.Select(
        attrs={'class': 'form-control', 'id': 'FormMonth', 'style': 'text-align-last: right', 'value':
            gregorian_to_jalali(GregorianDate[0], GregorianDate[1], GregorianDate[2])[1]}), choices=months, label='ماه',
        initial='مرداد')

    delivery_date = forms.DateTimeField(label='تاریخ تحویل')

    def __init__(self, args):
        super(EditTaskForm, self).__init__(args)
        # print(args["Options"])
        if args['PreviousValues'] is not None:
            # print(args["PreviousValues"])
            self.fields['title'].widget = forms.TextInput(
                attrs={'class': 'form-control', 'style': 'text-align:right;direction:rtl', 'placeholder': 'عنوان',
                       'value': args["PreviousValues"][0]})

            self.fields['comment'].widget = forms.TextInput(
                attrs={'class': 'form-control', 'style': 'text-align: right;direction:rtl', 'placeholder': 'توضیحات',
                       'value': args["PreviousValues"][1]})
            # self.fields['employee'].widget = forms.SelectMultiple(
            #    attrs={'class': 'form-group', 'style': 'text-align-last: right', 'id': 'multiple-checkboxes'})

            self.fields['fee'].widget = forms.TextInput(
                attrs={'class': 'form-control', 'style': 'text-align: right;direction:rtl', 'x-data': 'true',
                       'x-mask:dynamic': "$money($input, '.', ',')", 'placeholder': 'پاداش',
                       'value': args["PreviousValues"][2]})

            self.fields['delay_punishment'].widget = forms.TextInput(
                attrs={'class': 'form-control', 'style': 'text-align: right;direction:rtl', 'x-data': 'true',
                       'x-mask:dynamic': "$money($input, '.', ',')", 'placeholder': 'جریمه دیرکرد به ازای روز',
                       'value': args["PreviousValues"][3]})

            self.fields['validator'].widget = forms.Select(
                attrs={'class': 'form-control', 'onchange': 'ValidatorChange()', 'id': 'Validator', 'style': 'text-align: right;direction:rtl'})

            self.fields['ValidatorFee'].widget = forms.TextInput(
                attrs={'class': 'form-control', 'id': 'ValidatorFee', 'style': 'text-align: right;direction:rtl', 'x-data': 'true',
                       'x-mask:dynamic': "$money($input, '.', ',')", 'placeholder': 'پاداش تاییدکننده(ریال)', 'value': args["PreviousValues"][6]})

            self.fields['year'].widget = forms.NumberInput(
                attrs={'class': 'form-control', 'style': 'text-align: right;direction:rtl',
                       'value': args["PreviousValues"][4]})

            self.fields['delivery_date'].widget = forms.DateInput(
                attrs={'name': 'persianDatapicker', 'style': 'text-align: right;direction:rtl',
                       'maxlength': "0", 'id': 'persianDatapicker', 'type': 'text',
                       'class': 'form-control', 'placeholder': 'تاریخ تحویل',
                       'value': args["PreviousValues"][5]})
        # self.fields['employee'].choices = args["Options"]
        self.fields['validator'].choices = args["Validators"]
        # self.initial['employee'] = '02'
