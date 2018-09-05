#!/usr/bin/env python

import re, collections
from lxml import etree
from collections import OrderedDict

def convert(xml, ordered=False, noText=None):
    '''Converts any xml object into its JSON equivalent.
    
    Each element creates the dictionary structure for its children based on their tags
    If an element has no children, its value becomes either the text value of the element or a default value.
    
    The iteration logic applies the following general rules:
    
        1) Elements with child elements:
            - for children with identical tags: create a list object for the child's tag
            - for children with unique tags: create a dict object for the child's tag
        
        2) Elements with no children:
            - if there are word characters in the text entry: use the text as the value.
            - if there are no word characters in the text entry: set value to: None or whatever is specified in the 'noText' argument.
            
        3) Elements with attributes:
            - create a subelement dictionary with '@' as a key and the attributes dict as the value.
    
    Args:
    
        - xml: (required) The inputted xml object to be converted.
        
        - ordered: (optional) defaults to False. Specify whether or not to generate an OrderedDict
        
        - noText: (optional) defaults to None. Specify the value to give empty elements.
        
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
        self = dt()
        
        #process own values
        tag = xml.tag
        text = xml.text
        if text is None or not re.search('\w', text):
            text = noText
        
        #get children
        children = xml.xpath("./*")
        childTags = []
        [ childTags.append(x.tag) for x in children if x.tag not in childTags ]
        
        #get attributes        
        attr = dt(xml.attrib)
        if len(attr) > 0:
            attr = dt({ '@': attr })
            self.update(attr)
        
        #if there are children, create the dict structure for children
        if len(children) > 0:
                               
            for x in childTags:
                if len(filter(lambda y: x == y.tag, children)) > 1:
                    self.update({ x: [] })
                else:
                    self.update({ x: dt()})
                    
            #process child text
            children_to_remove = []
            for child in children:
                if len(child.xpath("./*")) == 0:
                    if type(self[child.tag]) in [ dict, collections.OrderedDict ]:
                        if child.text is None or not re.search('\w', child.text):
                            self.update({ child.tag: noText })
                            children_to_remove.append(child)
                        elif child.text is not None:
                            self.update({ child.tag: child.text })
                            children_to_remove.append(child)
                        
            #update children
            children = [ x for x in children if x not in children_to_remove ]
        
        #if there are no children and no text value 
        elif xml.text is None or not re.search('\w', xml.text):
            self.update({ tag: text })
            
        #if there are no children, no attributes, but a text value
        elif xml.text is not None and re.search('\w', xml.text) is not None:
            self = xml.text
              
        if type(parent) == list:
            parent.append(self)
            if len(children) > 0:
                for child in children:
                    l.append((
                        child,
                        parent[-1][child.tag]
                        )
                    )
        elif type(parent) in [ dict, collections.OrderedDict ]:
            parent.update(self)
            if len(children) > 0:
                for child in children:
                    l.append((
                        child,
                        parent[child.tag]
                    ))
            
    #create list to contain xml-dictionary tuples for iteration
    l = []
    
    #create dictionary
    d = dt()
    
    #bootstrap the process
    rootTag = xml.tag
    if len(xml.xpath('./*')) > 0:
        d[rootTag] = dt()
        l.append((xml, d[rootTag]))
    
    #begin iteration logic, running the iteration function on the first entry in list l, then removing the entry after iteration.
    while True:
        if len(l) > 0:
            xmlElem, jsonObject = l.pop(0)
            iterate(xmlElem, jsonObject)
        else:
            break
    
    return d

