from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
import re

class LowercaseConverterInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        # Create a text node with the matched text converted to lowercase
        el = etree.Element('span')
        word = m.group(1)
        if word in self.l_config['words'][0]:
            word_url = self.l_config['words'][0].get(word)
            el.text = f'<a href="{word_url}"><u style="text-decoration:underline dotted; color:black">{word}</u></a>'
        else:
            el.text = word
            
        return el, m.start(0), m.end(0)

class KeywordLinkerExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'words': [{}, 'Mapping of keywords to URLs']
            #'words': [[], 'List of words to convert to lowercase']
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, markdown):
        # Use regex pattern to find words that exactly match the specified words
        pattern = r'\b(' + '|'.join(re.escape(word) for word in self.getConfig('words')) + r')\b'
        proc = LowercaseConverterInlineProcessor(pattern, self)
        proc.l_config = self.config
        markdown.inlinePatterns.register(proc, 'keyword_linker', 175)
                        

def makeExtension(**kwargs):
    print("exention called", kwargs)
    return KeywordLinkerExtension(**kwargs)
