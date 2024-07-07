from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
import re

class LowercaseConverterInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        # Create a text node with the matched text converted to lowercase
        el = etree.Element('span')
        el.text = f'<a href="https://google.com"><u style="text-decoration:underline dotted; color:black">{m.group(1)}</u></a>'
        return el, m.start(0), m.end(0)

class KeywordLinkerExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            #'url_map': [{}, 'Mapping of keywords to URLs']
            'words': [[], 'List of words to convert to lowercase']
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, markdown):
        # Use regex pattern to find words that exactly match the specified words
        pattern = r'\b(' + '|'.join(re.escape(word) for word in self.getConfig('words')) + r')\b'
        markdown.inlinePatterns.register(LowercaseConverterInlineProcessor(pattern, self), 'keyword_linker', 175)
                        

def makeExtension(**kwargs):
    print("exention called", kwargs)
    return KeywordLinkerExtension(**kwargs)
