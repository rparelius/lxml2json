#!/usr/bin/env python
import re, collections, lxml, logging
from lxml import etree
from collections import OrderedDict
from copy import deepcopy


def convert(xml, ordered=False, noText=None, alwaysList=None, ignore=None, rename=None, move=None):
    '''Converts any xml object into its JSON equivalent.
    
    Each element creates the dictionary structure for its children based on their tags
    If an element has no children, its value becomes either the text value of the element or a default value.
    
    The iteration logic applies the following general rules:
    
        1) Elements with child elements:
            - for children with identical tags: create a list object for the child's tag
            - for children with unique tags: create a dict object for the child's tag
        
        2) Elements with no children:
            - if there are word characters in the text entry: use the text as the value.
            - if there are no word characters in the text entry, then
              set value to: None or whatever is specified in the 'noText' argument.
            
        3) Elements with attributes:
            - create a subelement dictionary with '@' as a key and the attributes dict as the value.
    
    Args:
        
        - xml: (required) The inputted xml object to be converted.
        
        - ordered: (optional) defaults to False. Specify whether or not to generate an OrderedDict
        
        - noText: (optional) defaults to None. Specify the value to give empty elements.
        
        - alwaysList: (optional) accepts a list or string of comma-separated xpath statements that
                      will specify elements to always store as a list of values. This is to allow 
                      for a more deterministic behavior for common elements. See README.md for an example
        
        - ignore: (optional) accepts a list or string of comma-separated xpath queries that
                             will specify elements to always ignore.
        
        - rename: (optional) accepts a tuple/list, or list of said objects, each containing
                             an xpath query of elements to match, along with the desired tag.
                  
                  e.g. to rename all elements with tag 'FOO' to 'BAR':  rename=(".//FOO", "BAR")
        
        - move: (optional) accepts a tuple/list, or list of said objects, each containing an xpath
                           query of elements to match, along with an xpath query relative to the
                           matched elements which specifies the desired location. 
                
                e.g. to move all elements with tag 'test' 1 level up use: move=(".//test", "./../..")
    
    Returns:  A dictionary of converted XML data
    '''
    
    
    #core iterator
    def iterate(xml, parent):
        self = dt()
        
        #get children, exluding those matched to be ignored
        children = [ x for x in xml.xpath("./*") if x not in ig ]
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
                if len(list(filter(lambda y: x == y.tag, children))) > 1:
                    self.update({ x: [] })
                
                #if there is only a single element for a given tag, create a dict structure unless it is specified as 'alwaysList'
                else:
                    if list(filter(lambda y: x == y.tag, children))[0] in al:
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
                    l.append((child, parent[-1][child.tag]))
        
        elif type(parent) in [ dict, collections.OrderedDict ]:
            parent.update(self)
            if len(children) > 0:
                for child in children:
                    l.append((child, parent[child.tag]))
    
    
    def move_element(xml_obj, move_what, move_to):
        
        elements = xml_obj.xpath(move_what)
        for e in elements:
            [ ee.insert(-1, e) for ee in e.xpath(move_to)]
    
    
    #convert input to xml if given a string or create deepcopy to prevent mutations to the original data (e.g. rename tag)
    if type(xml) == str:
        xml = etree.fromstring(xml)
    elif type(xml) is lxml.etree._Element:
        xml = deepcopy(xml)
    
    
    #determine whether to use an ordered dictionary
    if ordered is True:
        dt = OrderedDict
    else:
        dt = dict
    
    
    #handle elements specified to always be stored in a list
    al = []
    if alwaysList is not None:
        if type(alwaysList) is str:
            alwaysList = [ x.strip() for x in alwaysList.split(",") ]
        
        for x in alwaysList:
            try:
                [ al.append(e) for e in xml.xpath(x) if e not in al ]
            except Exception as Err:
                logging.error(Err.message, exc_info=True)
                continue
    
    
    #move specified elements
    if move is not None:
        if type(move) is list:
            if False in [ type(x) is tuple for x in move ]:
                raise Exception("arg: 'move' must be a single tuple or list of tuples")
        elif type(move) is tuple:
            move = [ move ]
        else:
            raise Exception("arg: 'move' must be a single tuple or list of tuples")

        for m in move:
            move_element(xml_obj=xml, move_what=m[0], move_to=m[1])
    
    
    #rename specified elements
    if rename is not None:
        if type(rename) is list:
            if False in [ type(x) is tuple for x in rename ]:
                raise Exception("arg: 'rename' must be a single tuple or list of tuples")
        elif type(rename) is tuple:
            rename = [ rename ]
        else:
            raise Exception("arg: 'rename' must be a single tuple or list of tuples")
        
        for r in rename:
            
            #rename each tag matched by the xpath query to the desired tag.
            for e in xml.xpath(r[0]):
                e.tag = r[1]
    
    
    #ignore specified elements
    ig = []
    if ignore is not None:
        if type(ignore) == str:
            ignore = [ x.strip() for x in ignore.split(",") ]
            
        for x in ignore:
            try:
                [ ig.append(e) for e in xml.xpath(x) if e not in ig ]
            except Exception as Err:
                logging.error(Err.message, exc_info=True)
                continue
        
    
    
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

