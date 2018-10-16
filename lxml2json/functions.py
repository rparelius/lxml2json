#!/usr/bin/env python

import re, collections
from lxml import etree
from collections import OrderedDict

def convert(xml, ordered=False, noText=None, alwaysList=None):
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
        
        - alwaysList: (optional) accepts a list or string of comma-separated xpath statements that will specify elements to always
                      store as a list of values. This is to allow for a more deterministic behavior for common elements. See README.md for an example
        
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
    
    #handle elements specified to always be stored in a list
    al = []
    if alwaysList is not None:
        if type(alwaysList) == str:
            alwaysList = [ x.strip() for x in alwaysList.split(",") ]
        
        for x in alwaysList:
            try:
                [ al.append(e) for e in xml.xpath(x) if e not in al ]
            except Exception as Err:
                log.error("alwaysList: {}".format(Err))
                continue
            
    
    def iterate(xml, parent):
        self = dt()
              
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
                #if there are multiple child elements with the same tag, create a list structure to hold them
                if len(filter(lambda y: x == y.tag, children)) > 1:
                    self.update({ x: [] })
                
                #if there is only a single element for a given tag, create a dict structure unless it is specified as 'alwaysList'
                else:
                    if filter(lambda y: x == y.tag, children)[0] in al:
                        self.update({ x: [] })
                    else:
                        self.update({ x: dt()})
                
            #process lone child text, i.e. children w/ no children & no attributes
            children_to_remove = []
            for child in children:
                if len(child.xpath("./*")) == 0:
                    if len(child.attrib) == 0:
                        if type(self[child.tag]) in [ dict, collections.OrderedDict ]:
                            if child.text is None or not re.search('\w', child.text):
                                self.update({ child.tag: noText })
                            else:
                                self.update({ child.tag: child.text })
                            
                            children_to_remove.append(child)
                        
                        elif type(self[child.tag]) == list:
                            if child.text is None or not re.search('\w', child.text):
                                self[child.tag].append(noText)
                            else:
                                self[child.tag].append(child.text)
                            
                            children_to_remove.append(child)
            
            #remove processed children
            children = [ child for child in children if child not in children_to_remove ]
        
        #this should only be true if the root element has children and/or attributes AND a text value
        if xml.text is not None and re.search('\w', xml.text) is not None:
            self.update({'text': xml.text})
        
        
        #update parent dict/list and add children to l for iteration
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
    d[rootTag] = dt()
    
    if len(xml.xpath('./*')) > 0:
        l.append((xml, d[rootTag]))
    else:
        if len(xml.attrib) == 0:
            if xml.text is not None and re.search('\w', xml.text):
                d[rootTag] = xml.text
            else:
                d[rootTag] = noText
        else:
            l.append((xml, d[rootTag]))
                
    
    #begin iteration logic, running the iteration function on the first entry in list l, then removing the entry after iteration.
    while len(l) > 0:
        xmlElem, jsonObject = l.pop(0)
        iterate(xmlElem, jsonObject)

    return d

def reverse(inputDict, text=False):
    """Creates an XML element from an input dictionary.
    
    Args: 
        inputDict: input dictionary. If the inputted data has more than 1 key-value pair, it will create a 'root' element
        text: <bool> Specify whether to output a string of the xml data.
    
    Returns:
        xml element OR pretty printed string of xml element.
    """
    l = []
    
    #determine if 'root' element is necessary. e.g. for multiple top-level key-value pairs, or top-level value is a list.
    if len(inputDict) > 1:
        inputDict = { 'root': inputDict }
    if True in [ type(inputDict[x]) == list for x in inputDict ]:
        inputDict = { 'root': inputDict }
    
    for key in inputDict:
        xmlData = etree.Element(key)
        l.append((xmlData, inputDict[key]))
    
    while len(l) > 0:       
        parentXml, data = l.pop(0)
        
        def processText(data):
            parentXml.text = str(data)
        
        def processDict(data):
            for k, v in data.items():
                #if attributes, update attributes
                if k == '@':
                    parentXml.attrib.update(v)
                else:
                    #process lists
                    if type(v) == list:
                        for item in v:
                            parent = etree.SubElement(parentXml, k)
                            l.append((parent, item))
                    else:
                        parent = etree.SubElement(parentXml, k)        
                        l.append((parent, v))   
        
        
        if type(data) in [ dict, collections.OrderedDict ]:
            processDict(data)
        
        elif type(data) in [ int, str ]:
            processText(data)
    
    if text is True:
        xmlData = etree.tostring(xmlData, pretty_print=True)
    
    return xmlData
