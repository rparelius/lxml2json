#!/usr/bin/env python

import re, collections
from lxml import etree
from collections import OrderedDict


def convert(xml, ordered=False, noText=None, noCombine=False):
    '''Converts any xml object into its JSON equivalent.
    
    Each element creates a unique key in the dictionary structure based on its tag.
    The value is either the text value of the element, or a placeholder for its children.
    
    The iteration logic applies the following general rules:
    
        1) Elements with child elements:
            - if any children have identical tags: create a list entry if those children do not have text values
            - if all children have unique tags: create a dictionary entry
        
        2) Elements with no children:
            - if there are word characters in the text entry: use the text as the value.
            - if there are no word characters in the text entry: set value to: None or whatever is specified in the 'noText' argument.
            
        3) Elements with attributes:
            - create a subelement dictionary with '@' as a key and the attributes dict as the value.
    
    Args:
    
        - xml: (required) The inputted xml object to be converted.
        
        - ordered: (optional) defaults to False. Specify whether or not to generate an OrderedDict
        
        - noText: (optional) defaults to None. Specify the value to give empty elements.
        
        - noCombine: (optional) defaults to False. By default the function will try to combine sibling elements'
                    text values in a list if all of the siblings have text values and no children.
        
                    Input a list of tags to exclude from this process. 
                    Or set to True skip combining any sibling elements.
                            
    
    Returns:  A dictionary of converted XML data
    '''
    
    #convert input to xml if given a string
    if type(xml) == str:
        xml = etree.fromstring(xml)
    
    #determine whether to use an ordered dictionary
    if ordered is True:
        dt = OrderedDict
    else:
        dt = dict
        
    
    def iterate(xml, parent):
        #get own tag, text
        tag = xml.tag
        text = xml.text
          
        #get children
        children = xml.xpath("./*")
        childTags = [ x.tag for x in children ]
        
        #logic for handing no children
        if len(children) == 0:
            if text is None or not re.search('\w', text):
                value = noText
            else:
                value = text
        else:
            #logic for when child elements have duplicate tags, which therefore require a list
            if len(childTags) > len(set(childTags)):
                
                if noCombine is not True:
                
                    #check if the duplicate children have text values
                    childDict = dt()
                    parent_must_be_list = False
                    
                    for x in set(childTags):
                        
                        if noCombine is False or x not in noCombine:
                        
                            #if there are multiple elements with the same tag
                            if len(filter(lambda y: x == y , childTags)) > 1:
                                
                                #ensure that those elements don't have children
                                if len(xml.xpath("./{}/*".format(x))) == 0:
                                    
                                    #collect all of their text elements in a list
                                    combinedChildText = [ elem.text for elem in xml.xpath("./{}".format(x)) ]
   
                                    #validate that each entry in the list contains valid text
                                    if False not in [ t is not None or re.search('\w', t) is not None for t in combinedChildText ]:
                                    
                                        #validate that no entries contain attributes
                                        if False not in [ len(a.attrib) == 0 for a in children ]:
                                    
                                            #create an dict entry for the tag, with the list as the value
                                            childDict.update({ x: combinedChildText })
                                            
                                        else:
                                            parent_must_be_list = True
                                    else: 
                                        parent_must_be_list = True
                                else:
                                    parent_must_be_list = True
                                                   
                    if len(childDict) > 0:
                        #remove combined elements from children list to prevent iteration on the next loop
                        children = [ x for x in children if x.tag not in childDict.keys() ]
                        
                        if parent_must_be_list is False:
                            value = childDict
                        else:
                            value = [ childDict ]
                    else:
                        value = []
                else:
                    value = []
            else:
                value = dt()
        
        #get attributes
        attr = dt(xml.attrib)
        if len(attr) > 0:
            attr = dt({ '@': attr })
            if type(value) == list:
                value.append(attr)
            elif type(value) in [ dict, collections.OrderedDict ]:
                value.update(attr)
        
        #create a dictionary object for current element
        self = dt({ tag: value })
        
        #if parent object is a list
        if type(parent) == list:
            
            #append to parent and append tuples of children-to-self to iteration list
            parent.append(self)
            [ l.append(( x, parent[-1][tag] )) for x in children ]
        
        #if parent is a dict
        elif type(parent) in [ dict, collections.OrderedDict ]:
            
            #add entry to parent and append tuples of children-to-self to iteration list
            parent.update(self)
            [ l.append(( x, parent[tag] )) for x in children ]
            
    #create list to contain xml-dictionary tuples for iteration
    l = []
    
    #create dictionary
    d = dt()
    
    #bootstrap the process    
    l.append((xml, d))
    
    #begin iteration logic, running the iteration function on the first entry in list l, then removing the entry after iteration.
    while True:
        if len(l) > 0:
            xmlElem, jsonObject = l.pop(0)
            iterate(xmlElem, jsonObject)
        else:
            break
    
    return d

