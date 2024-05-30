from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL

# Definir el Namespace
ECSDI = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI")

# Crear un grafo RDF
g = Graph()

# Cargar la ontología desde un archivo TTL exportado de Protégé
print("Cargando el archivo Ontologies_v8.ttl...")
g.parse("Ontologies_v8.ttl", format="ttl")

# Ejemplo de cómo agregar una clase a la ontología
nueva_clase = URIRef(ECSDI['NuevaClase'])
g.add((nueva_clase, RDF.type, OWL.Class))
g.add((nueva_clase, RDFS.label, Literal("Nueva Clase")))

# Ejemplo de cómo agregar una instancia de la clase
nueva_instancia = URIRef(ECSDI['InstanciaDeNuevaClase'])
g.add((nueva_instancia, RDF.type, nueva_clase))
g.add((nueva_instancia, RDFS.label, Literal("Instancia de Nueva Clase")))

# Guardar los cambios en un nuevo archivo TTL
g.serialize(destination="nueva_ontologia.ttl", format="ttl")

# Consulta de la ontología y mostrar las tripletas
for s, p, o in g:
    print(s, p, o)
