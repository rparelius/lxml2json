# lxml2json

lxml2json is a python package that converts XML elements into their JSON equivalent.

**Usage Example:**
        
        from lxml2json import convert
        from pprint import pprint as pp

        xml = '''
        <parent>
            <c1>a</c1>
            <c1>b</c1>
            <c1>c</c1>
            <c2>
                <gc1>d</gc1>
                <gc2>e</gc2>
                <gc3>f</gc3>
            </c2>
            <c2>
                <gc1>g</gc1>
                <gc2>h</gc2>
                <gc3>i</gc3>
            </c2>
            <c3>
                <gc1>j</gc1>
                <gc1>k</gc1>
                <gc1>l</gc1>
            </c3>
            <c4/>
        </parent>'''

        d = convert(xml)
        pp(d)
        {'parent': {'c1': ['a', 'b', 'c'],
                    'c2': [{'gc1': 'd', 'gc2': 'e', 'gc3': 'f'},
                           {'gc1': 'g', 'gc2': 'h', 'gc3': 'i'}],
                    'c3': {'gc1': ['j', 'k', 'l']},
                    'c4': None}}
        

### Options

lxml2json provides the following optional arguments to modify conversion behavior or output data format:

-  **ordered:** Boolean, defaults to False. Specifies whether to generate output an OrderedDict object.
-  **noText:** Defaults to None. Specifies the value to give to elements that contain no children and no text value.
