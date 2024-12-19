from lark import Lark

ksd_grammar = \
    """
    start: WORD "," WORD "!"
    %import common.WORD   // imports from terminal library
    %ignore " "           // Disregard spaces in text
    """

class KSDParser:
    def do_it(self, kgm_path, ksd_filename):
        print("ksd_filename:", ksd_filename, type(ksd_filename))
        print("kgm_path:", kgm_path)
        
        l = Lark(ksd_grammar)
        with open(ksd_filename, 'r') as f:
            ksd_code = f.read()

        #print(ksd_code)
        #print(l.parse("Hello, world!"))
        print(l.parse(ksd_code))
