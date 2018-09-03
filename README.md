# lxml2json

lxml2json is a python package that converts XML elements into their JSON equivalent.

**Usage Example:**
        
        from lxml2json import convert
        from pprint import pprint as pp

        xml = """
          <parent>
            <child>1</child>
            <child>2</child>
            <child>3</child>
          </parent>"""

        d = convert(xml)
        pp(d)
        {'parent': {'child': ['1', '2', '3']}}
        
        d = convert(xml, noCombine=True)
        pp(d)
        {'parent': [{'child': '1'}, {'child': '2'}, {'child': '3'}]}
        
        d = convert(xml, noCombine=True, ordered=True)
        pp(d)
        OrderedDict([('parent', [OrderedDict([('child', '1')]), OrderedDict([('child', '2')]), OrderedDict([('child', '3')])])])

            
### Options

lxml2json provides the following optional arguments to modify conversion behavior or output data format:

-  **ordered:** Boolean, defaults to False. Specifies whether to generate output an OrderedDict object.
-  **noText:** Defaults to None. Specifies the value to give to elements that contain no children and no text value.
-  **noCombine:** Defaults to False. Specifies whether or not to consolidate similar child elements' text values into a list. Accepts a list of tag values to exclude from consolidation, or when set to True, does not attempt to consolidate at all.
