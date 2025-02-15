# AUTOGENERATED! DO NOT EDIT! File to edit: 04_determine_graph_format.ipynb (unless otherwise specified).

__all__ = ['parse_result_row_graph', 'drop_duplicates', 'parse_result_graph', 'graph_renderer', 'row_renderer',
           'is_neo4j_httpapi_format', 'is_neo4j_parsed_format', 'is_cytoscape_format', 'is_neo4j_downloaded_format',
           'false']

# Cell
import json
import pandas as pd
from collections import OrderedDict

def parse_result_row_graph(jsonobj, name_col='name'):
    '''
    Parse Neo4j HTTP API Graph Result row
    
    input: element of result list
    output: tuple of nodes and edges
    '''
    def parse_nodes(gobj):
        node_dict={}
        for n in gobj['nodes']:
            _id=n['id']
            label=n['labels'][0]
            props=n['properties']
            props['label']=label
            
            keys=props.keys()
            headcols=['identifier',name_col,'label']
            orderedkeys=headcols+list(set(keys)-set(headcols))
            orderedobj={k: props[k] for k in orderedkeys}
            
            node_dict[_id]=orderedobj

        return node_dict

    def parse_edges(gobj, node_dict):
        edges=[]
        for r in gobj['relationships']:
            _type=r['type']
            start_id=r['startNode']
            end_id=r['endNode']

            start_node=node_dict[start_id]
            end_node=node_dict[end_id]

            edge_dict={
                'type': _type,
                'start_identifier':start_node['identifier'],
                'start_name': start_node[name_col],
                'end_identifier':end_node['identifier'],
                'end_name': end_node[name_col]
            }

            # inject the rest properties
            propobj=r['properties']
            for k in propobj:
                edge_dict[k]=propobj[k]

            edges.append(edge_dict)

        return edges
    
    gobj=jsonobj['graph']
    
    node_dict=parse_nodes(gobj)    
    nodes=[node_dict[k] for k in node_dict]
    
    edges=parse_edges(gobj, node_dict)

    return nodes, edges

def drop_duplicates(items):
    df=pd.DataFrame(items)
    df=df.drop_duplicates()
    items=df.to_dict(orient='records')
    
    return items

def parse_result_graph(data, name_col='name'):
    '''
    Parse Neo4j HTTP API Graph Result
    '''
    nodes=[]
    edges=[]
    for item in data:
        _nodes, _edges = parse_result_row_graph(item, name_col)
        nodes=nodes+_nodes
        edges=edges+_edges
    
    nodes=drop_duplicates(nodes)
    edges=drop_duplicates(edges)
    
    return nodes, edges

def graph_renderer(neo4j_output, name_col='name'):
    output=neo4j_output['results'][0]
    nodes, edges = parse_result_graph(output['data'], name_col)
    output = {'nodes':nodes, 'edges':edges}

    return output

def row_renderer(neo4j_output):
    output=neo4j_output['results'][0]
    cols=output['columns']
    df=pd.DataFrame([e['row'] for e in output['data']], columns=cols)
    output=df.to_dict(orient='records')

    return output



# Cell
import json
from numpy import nan as NaN
false=False
def is_neo4j_httpapi_format(obj):
    if type(obj) != dict:
        return False
    if 'results' not in obj:
        return False
    return True

def is_neo4j_parsed_format(obj):
    if type(obj) != dict:
        return False
    if 'nodes' not in obj or 'edges' not in obj:
        return False
    if 'identifier' not in obj['nodes'][0]:
        return False
    return True

def is_cytoscape_format(obj):
    if type(obj) != dict:
        return False
    if 'nodes' not in obj or 'edges' not in obj:
        return False
    if 'data' not in obj['nodes'][0]:
        return False
    return True

def is_neo4j_downloaded_format(obj):
    if type(obj) != list:
        return False

    for _, item in obj[0].items():
        keys=item.keys()
        for k in ['start', 'end', 'segments', 'length']:
            if k not in keys:
                return False

    return True