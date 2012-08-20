#!/usr/bin/env python

#
# Writes many html files to disk, for inclusion in an OWL ontology documentation
# page. Organizes terms by prov:category.
#
# To install dependencies, see https://github.com/timrdf/DataFAQs/wiki/Errors
#
# When the focus ontology has terms annotated with:
#    prov:category = { 'base', 'extended', 'more' }
#
# The following HTML files are written:
#    at-a-glance-{category}.html
#    cross-reference-{category}.html
#    qualified-forms-{category}.html
#
#                                                                              |

import sys, datetime, uuid
from sets import Set

from rdflib import *

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query',     'SPARQLQueryResult')
from surf import *
from surf.query import a, select

if len(sys.argv) < 4 or len(sys.argv) > 5:
   print "usage: cross-reference.py prefix focus-namespace http://some.owl [extended-namespace]"
   print
   print "  prefix             - prefix to use for the ontology to be documented"
   print "                       e.g. 'pml'"
   print
   print "  focus-namespace    - namespace of the ontology to be documented"
   print "                       e.g. 'http://provenanceweb.org/ns/pml#'"
   print
   print "  http://some.owl    - web URL of the ontology's OWL file"
   print "                       e.g. https://raw.github.com/timrdf/pml/master/ontology/pml-3.0.owl"
   print
   print "  extended-namespace - namespace of the [principal] ontology that focus-namespace extends"
   print "                       e.g. 'http://provenanceweb.org/ns/pml#'"
   sys.exit(1)

PREFIX             = sys.argv[1] # pml
focus_namespace    = sys.argv[2] # http://provenanceweb.org/ns/pml#
ont_url            = sys.argv[3] # https://raw.github.com/timrdf/pml/master/ontology/pml-3.0.owl
extended_namespace = sys.argv[4] if len(sys.argv) > 3 else ''

EXAMPLE_BASE_URL   = 'http://dvcs.w3.org/hg/prov/raw-file/tip/examples/eg-41-pml-3-html-examples/rdf/create/rdf/'
EXAMPLE_BASE_LOCAL = 'hg-prov-wg/examples/eg-41-pml-3-html-examples/rdf/create/rdf/'

ns.register(prov='http://www.w3.org/ns/prov#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(pml='http://provenanceweb.org/ns/pml#')

# as SuRF
store   = Store(reader='rdflib', writer='rdflib', rdflib_store = 'IOMemory')
session = Session(store)
store.load_triples(source=ont_url) # From URL

# as rdflib (via SuRF)
graph = store.reader.graph
prefixes = dict(prov=str(ns.PROV), rdf=str(ns.RDF), owl=str(ns.OWL), pml=str(ns.PML))

Thing              = session.get_class(ns.OWL["Thing"])
Classes            = session.get_class(ns.OWL["Class"])
DatatypeProperties = session.get_class(ns.OWL["DatatypeProperty"])
ObjectProperties   = session.get_class(ns.OWL["ObjectProperty"])
RDFProperties      = session.get_class(ns.RDF["Property"])

def inFocus(uri) : return uri.subject.startswith(focus_namespace)
ontology = {}
ontology['classes']             = filter(inFocus, Classes.all())
ontology['object-properties']   = filter(inFocus, ObjectProperties.all())
ontology['datatype-properties'] = filter(inFocus, DatatypeProperties.all())
ontology['properties']          = filter(inFocus, ObjectProperties.all())
ontology['properties'].extend(filter(inFocus, DatatypeProperties.all()))

sorts = { 
   'narrative' : lambda R: float(R.pml_order.first if len(R.pml_order)>0 else sys.maxint),
   'uri'       : lambda R: R.subject
}

# ontology['classes'].sort(key=sorts['narrative'])
# ontology['classes'].sort(key=sorts['uri'])

categories = {}
for bindings in graph.query('select distinct ?cat where { [] prov:category ?cat } order by ?cat', initNs=prefixes):
   categories[bindings] = True # distinct operator is not being recognized. Need to reimplement here.
for category in categories.keys():
   print category

   glanceName =     'at-a-glance-'+category+'.html'
   crossName  = 'cross-reference-'+category+'.html'
   qualsName  =  'qualifed-forms-'+category+'.html'

   if not(os.path.exists(glanceName)) and not(os.path.exists(crossName)) and not(os.path.exists(qualsName)):
      print '  ' + glanceName + '  -  ' + crossName + '  -  ' + qualsName

      def inCategory(R) : return R.prov_category.first == category
      focus = { 
         'classes'    : filter(inCategory, ontology['classes']),
         'properties' : filter(inCategory, ontology['properties'])
      }
      focus['classes'].sort(key=sorts['narrative'])
      focus['properties'].sort(key=sorts['narrative'])

      cssClass = { 
         ns.OWL['ObjectProperty']   : 'object-property',
         ns.OWL['DatatypeProperty'] : 'datatype-property',
      }

      # at-a-glance # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
      glance = open(glanceName, 'w')                                          #
      glance.write('\n')
      glance.write('<div\n')
      glance.write('     class="'+PREFIX+'-'+category+' owl-classes at-a-glance">\n')
      glance.write('  <ul class="hlist">\n')

      for owlClass in focus['classes']:
         qname = owlClass.subject.split('#')
         glance.write('    <li>\n')
         glance.write('      <a href="#'+qname[1]+'">'+PREFIX+':'+qname[1]+'</a>\n')
         glance.write('    </li>\n')
      glance.write('  </ul>\n')
      glance.write('</div>\n')

      glance.write('\n')
      glance.write('<div\n')
      glance.write('     class="'+PREFIX+'-'+category+' owl-properties at-a-glance">\n')
      glance.write('  <ul class="hlist">\n')

      for property in focus['properties']:
         qname = property.subject.split('#')
         glance.write('    <li class="'+cssClass[property.rdf_type.first]+'">\n')
         glance.write('      <a href="#'+qname[1]+'">'+PREFIX+':'+qname[1]+'</a>\n')
         glance.write('    </li>\n')
      glance.write('  </ul>\n')
      glance.write('</div>\n')                                               #
      glance.close() # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

      cross = open(crossName, 'w')
      # 178
      cross.write('<div\n') # We want to include it multiple times: id="'+PREFIX+'-'+category+'-owl-classes-crossreference"\n')
      cross.write('     class="'+PREFIX+'-'+category+' owl-classes crossreference"\n')
      cross.write('     xmlns:dcterms="http://purl.org/dc/terms/"\n')
      cross.write('     xmlns:prov="http://www.w3.org/ns/prov#">\n')
      for owlClass in focus['classes']:
         qname = owlClass.subject.split('#')
         cross.write('\n')
         cross.write('  <div id="'+qname[1]+'" class="entity">\n')
         cross.write('    <h3>\n')
         cross.write('      Class: <a href="#'+qname[1]+'"><span class="dotted" title="'+owlClass.subject+'">'+PREFIX+':'+qname[1]+'</span></a>\n')
         cross.write('      <span class="backlink">\n')
         #cross.write('         back to <a href="#toc">ToC</a> or\n')
         cross.write('         back to <a href="#'+PREFIX+'-'+category+'-owl-terms-at-a-glance">'+category+' classes</a>\n')
         cross.write('      </span>\n')
         cross.write('    </h3>\n')
      # 194
      # 729
         cross.write('\n')
         cross.write('      </dl>\n')


         cross.write('    </div>\n') # e.g. <div class="description">
         cross.write('  </div>\n')   # e.g. <div id="wasGeneratedBy" class="entity">
         cross.write('\n')
      cross.write('</div>\n')        # e.g. <div id="prov-starting-point-owl-classes-crossreference"
      # 736  
      cross.close()

      quals  = open(qualsName, 'w')
      quals.close()
   else:
      print '  '+glanceName + ' or ' + crossName + " already exists. Not modifying."


# SuRF and rdflib can't handle SPARQL querying very well, otherwise,
# It'd be great to use this:
termsQuery = '''
select ?term
where {
     ?term a ?type .
     filter(?type = rdf:Property         ||
            ?type = owl:DatatypeProperty ||
            ?type = owl:ObjectProperty   ||
            ?type = owl:Class)
     filter(regex(str(?term),"'''+focus_namespace+'''"))
} order by ?term'''
