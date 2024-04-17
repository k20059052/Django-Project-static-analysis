from django import forms
from ticketing.models import User
import AdvancedHTMLParser


class NoLabelStyledRadioSelect(forms.RadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(html)
        labels = parser.getElementsByTagName('label')
        inputs = parser.getElementsByTagName('input')
        divs = parser.getElementsByTagName('div')
        parent = divs[0]
        parent.addClass('btn-group')
        for i in range(1, len(divs)):
            children = divs[i].getAllChildNodes()
            divs[i].remove()

        for i in range(0, len(labels)):
            labels[i].addClass('btn btn-outline-primary')
            inputs[i].addClass('btn-check')
            parent.appendChild(inputs[i])
            labels[i].removeChild(labels[i].firstChild)
            parent.appendChild(labels[i])
            
        parent.setStyle('padding-top', '0px;')
        parent.setStyle('vertical-align', 'middle')
        html_result = parser.getFormattedHTML(indent='\n    ')
        return html_result


class StyledRadioSelect(NoLabelStyledRadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)

        return '<br>' + html


class NoLabelClearableRadioSelect(NoLabelStyledRadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)

        parser = AdvancedHTMLParser.AdvancedHTMLParser()

        parser.parseStr(html)

        divs = parser.getElementsByTagName('div')

        parent = divs[0]

        reset_button_html = (
            '<div style="display:inline-block"><a id="reset_button" href="javascript:var radio_buttons = document.getElementsByName(\''
            + name
            + "'); "
            'for(var i = 0; i < radio_buttons.length; i++){'
            'radio_buttons[i].checked = false;'
            '}'
            '" style="display:inline-block; position:relative; top: 0px; padding-left:20px; text-decoration: none;">Reset</a></div>'
        )

        html_result = parser.getFormattedHTML(indent='\n    ')

        final_html_result = html_result + reset_button_html

        return final_html_result


class ClearableRadioSelect(NoLabelClearableRadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)

        return '<br>' + html


class RoleRadioSelect(ClearableRadioSelect):
    def __init__(self, department_select_name, attrs=None, choices=()):
        super().__init__(attrs, choices)

        self.department_select_name = department_select_name
        self.linked_to_select = True

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)

        parser = AdvancedHTMLParser.AdvancedHTMLParser()

        parser.parseStr(html)

        radio_buttons = parser.getElementsByName(name)

        # department_select_element = parser.getElementsByName(self.department_select.name)[0]

        ######## make_javascript ########
        def make_javascript(is_specialist):
            if is_specialist == True:
                js_bool = 'false'
            else:
                js_bool = 'true'

            if self.linked_to_select:
                return (
                    "var select = document.getElementsByName('"
                    + self.department_select_name
                    + "')[0]; select.disabled = "
                    + js_bool
                    + '; select.selectedIndex = 0;'
                )
            else:
                return ''

        for i in range(len(radio_buttons)):

            if radio_buttons[i].value == User.Role.SPECIALIST:
                radio_buttons[i].setAttribute('onclick', make_javascript(True))
            else:
                radio_buttons[i].setAttribute(
                    'onclick', make_javascript(False)
                )

        reset_button = parser.getElementById('reset_button')

        # if(self.linked_to_select):
        #     reset_javascript = ""

        reset_button.setAttribute(
            'href', reset_button.getAttribute('href') + make_javascript(False)
        )

        html_result = parser.getFormattedHTML(indent='\n    ')

        return html_result


class StyledSelect(forms.Select):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)

        parser = AdvancedHTMLParser.AdvancedHTMLParser()

        parser.parseStr(html)

        first = parser.getElementsByTagName('option')[0]

        # print("BLOCKS ARE: ", first.blocks)
        # for i in range(len(first.blocks)):
        #     first.blocks[i] = ""

        first.blocks = ['']

        html_result = parser.getFormattedHTML(indent='\n    ')

        return html_result
