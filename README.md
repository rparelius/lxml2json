# lxml2json

**lxml2json is a python package that converts XML elements into their JSON equivalent, and vice versa. 
There are many options to convert the data to a desired format:**
- **rename tags**
- **ignore elements**
- **move elements within the tree**
- **always represent data as lists**
- **supply value to give empty elements**



**Installation:**
        
        pip install lxml2json
        
        

**Usage:**
        
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
        
        
        

## Options

lxml2json provides the following optional arguments to modify conversion behavior or output data format::

-  **ordered:** Boolean, defaults to False. Specifies whether to generate output as an OrderedDict.
   
-  **noText:** Defaults to None. Specifies the value to give to elements that contain no children and no text value.

-  **alwaysList:** Defaults to None. Allows specification of xpath queries to apply to the inputted XML element that will
                   cause all matched elements to be stored as lists. This is useful for creating a deterministic data structure.
                   See below for an example.
                   
-  **ignore:** Defaults to None. Allows specification of xpath queries to apply to the inputted XML element that will cause
               all matched elements to be ignored.
               
-  **rename:** Defaults to None. Allows renaming tags by supplying tuples/lists of tuples containing xpath queries to match elements, along
               with a string specifying the desired tag. See below for example.
               
-  **move:** Defaults to None. Provides the option to move elements to a desired place within the hierarchy. Use case: flattening
             a deeply nested structure. Requires tuples/lists of tuples containing xpath queries for matching elements, along with xpath queries
             (relative to the matched element's location) of where to move the element. See below for example

The order of operations is: move, rename, ignore.  This allows you to essentially replace an element with a subelement by moving the subelement to the same level of hierarchy, renaming the original element, then ignoring it.


## alwaysList

lxml2json's processing logic will always attempt to represent an element as a dictionary, **unless there are multiple
sibling elements with the same tag**, in which case it must represent the object as a list, since dictionaries require unique keys.

This creates the possibility of variance within the overall json data structure, since some portions of the xml may be represented as lists and
other sections with the same tag may be represented as dictionaries or text values, depending on the number of siblings with the same tag.

**Consider the following example:**
    
        >>> from lxml2json import convert
        >>> from pprint import pprint as pp
        >>> 
        >>> xml = '''
        ... <parent>
        ...     <c1>
        ...         <num>1</num>
        ...         <num>2</num>
        ...         <num>3</num>
        ...     </c1>
        ...     <c2>
        ...         <num>4</num>
        ...         <num>5</num>
        ...         <num>6</num>
        ...     </c2>
        ...     <c3>
        ...         <num>7</num>
        ...     </c3>
        ... </parent>
        ... '''
        >>>

**By default, lxml2json will represent this xml object as:**

        >>> pp(convert(xml))
        {'parent': {'c1': {'num': ['1', '2', '3']},
                    'c2': {'num': ['4', '5', '6']},
                    'c3': {'num': '7'}}}
                    
        
Notice that the values for 'num' key are contained in a **list** for the first 2 instances, but for the last it is just its native value of seven.
This behavior is expected, and for many situations functions perfectly well as a representation of the xml structure. However, it can present
challenges when iterating over the resultant json object, as additional logic may be necessary to handle whether the values are contained in a list or not.

To allow for a more deterministic structure, lxml2json allows you to supply xpath queries that it will apply to the inputted xml, resulting in any matching elements
being stored as lists, regardless of the number of identical sibling tags.

In this example, the xpath query: **".//num"** will match all the 'num' elements, resulting in all such elements storing their values in a list.

**Let us see this in action:**
        

        >>> 
        >>> pp(convert(xml, alwaysList=".//num"))
        {'parent': {'c1': {'num': ['1', '2', '3']},
                    'c2': {'num': ['4', '5', '6']},
                    'c3': {'num': ['7']}}}
        >>> 
                    

Notice that the 3rd 'num' value is now a list, similar to the first 2 instances.
                    
You can supply as many xpath queries as you like, either as a list of queries, or a string of comma-separated values. In either case, the matching elements will be flagged.



## ignore

The 'ignore' option allows specifying elements to ignore. 
Example:
    
    >>> from lxml2json import convert
    >>> from pprint import pprint as pp
    >>>
    xml = '''
    <parent>
        <son>
            <grandson>Thomas</grandson>
            <grandson>Robert</grandson>
            <granddaughter>Karen</granddaughter>
        </son>
    </parent>
    '''
    >>> 
    >>> pp(convert(xml))
    {'parent': {'son': {'granddaughter': 'Karen',
                        'grandson': ['Thomas', 'Robert']}}}
    >>> 
    >>> pp(convert(xml, ignore=".//granddaughter"))
    {'parent': {'son': {'grandson': ['Thomas', 'Robert']}}}
    >>> 
    
By specifiying the xpath query ".//grandaughter", lxml2json will ignore any elements with that tag when converting.
    

## move

The 'move' option allows for mutation of the data structure to match a desired state. One use-case is to 'flatten' the nesting structure. 

Requires providing a tuple/list of tuples, each containing an xpath query to match elements along with a corresponding xpath query (relative to the location of the matched element) specifying where in the hierarchy to move the data.

Example:
    
    
    xml = """
    <children>
        <child>
            <name>Joey</name>
            <age>7</age>
            <favorite>
                <things>
                    <toys>
                        <toy>legos</toy>
                        <toy>playstation</toy>
                        <toy>bike</toy>
                    </toys>
                </things>
            </favorite>
        </child>
    </children>"""
    
    #default result
    >>> pp(convert(xml))
    {'children': {'child': {'age': '7',
                            'favorite': {'things': {'toys': {'toy': ['legos',
                                                                     'playstation',
                                                                     'bike']}}},
                            'name': 'Joey'}}}
    >>> 
    
    #perhaps we want a flattened child dictionary
    >>> pp(convert(xml, move=(".//toy", "./../../../.."), ignore=".//favorite"))
        {'children': {'child': {'age': '7',
                                'name': 'Joey',
                                'toy': ['legos', 'playstation', 'bike']}}}
                                
                                
        
## Converting from JSON to XML

lxml2json provides a 'reverse' function that generates an XML element (or string) for an inputted dictionary object.

Note: if the inputted dictionary has multiple top-level k:v pairs, or if the value of the top-level key is a list, then a 'root' element is created so as to allow for a properly
formatted xml structure, which requires a single root element.

**Options**

There is a single boolean option: 'text', which defaults to False. When set to True, the reverse function will output a pretty-printed string of the xml element created.






