#!/usr/bin/env python

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
#
#
#
#                                                                              |

import sys, datetime, uuid
from sets import Set

from rdflib import *

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor, 'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,    'rdfextras.sparql.query',     'SPARQLQueryResult')

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

DatatypeProperties = session.get_class(ns.OWL["DatatypeProperty"])
ObjectProperties   = session.get_class(ns.OWL["ObjectProperty"])
Classes            = session.get_class(ns.OWL["Class"])
Thing              = session.get_class(ns.OWL["Thing"])

all_ordered = { 'classes' : [], 'properties' : [],
                'datatypeproperties' : [], 'objectproperties' : []}

for owlClass in Classes.all():
   if owlClass.subject.startswith(focus_namespace):
      all_ordered['classes'].append(owlClass.subject)

for prop in DatatypeProperties.all():
   if prop.subject.startswith(focus_namespace):
      all_ordered['properties'].append(prop.subject)
      all_ordered['datatypeproperties'].append(prop.subject)

for prop in ObjectProperties.all():
   if prop.subject.startswith(focus_namespace):
      all_ordered['properties'].append(prop.subject)
      all_ordered['objectproperties'].append(prop.subject)

all_ordered['classes'].sort()
all_ordered['properties'].sort()
all_ordered['objectproperties'].sort()
all_ordered['datatypeproperties'].sort()

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

      # at-a-glance
      glance = open(glanceName, 'w')
      glance.write('\n')
      glance.write('<div\n')
      glance.write('     class="'+PREFIX+'-'+category+' owl-classes at-a-glance">\n')
      glance.write('  <ul class="hlist">\n')

      for uri in ordered['classes']:
         owlClass = session.get_resource(uri,Classes)
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

      for uri in ordered['properties']:
         property = session.get_resource(uri,Thing)
         qname = property.subject.split('#')
         glance.write('    <li class="'+propertyTypes[uri]+'">\n')
         glance.write('      <a href="#'+qname[1]+'">'+PREFIX+':'+qname[1]+'</a>\n')
         glance.write('    </li>\n')
      glance.write('  </ul>\n')
      glance.write('</div>\n')
      glance.close()

      cross  = open(crossName, 'w')
      cross.close()

      quals  = open(qualsName, 'w')
      quals.close()
   else:
      print '  '+glanceName + ' or ' + crossName + " already exists. Not modifying."
