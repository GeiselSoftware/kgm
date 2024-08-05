#import ipdb
import sys
import pandas as pd
import sqlite3

def make_URI(prefix, keys):
    ret = []
    for k in keys:
        ret.append(prefix + "--" + str(k))
    return ret

def dump_node_members(df, prefix, rdfs_classname, node_uri_col, obj_cols, exclude_cols):
    if exclude_cols:
        df = df.drop(exclude_cols, axis = 1)    
    literal_cols = list(set(df.columns) - set([node_uri_col]) - set(obj_cols))
    
    df.insert(0, 'URI', make_URI(rdfs_classname, df[node_uri_col]))
    df.drop(node_uri_col, inplace = True, axis = 1)

    output_cols = []
    for obj_col in obj_cols:        
        classname = prefix + ":" + obj_col.replace("ID", "")
        pred = prefix + ":" + obj_col.replace("ID", "").lower()
        df[pred] = make_URI(classname, df[obj_col])
        output_cols.append(pred)

    for col in literal_cols:
        pred = prefix + ":" + col.lower()
        df[pred] = df[col].apply(lambda x: f'"{x}"^^xsd:string')
        output_cols.append(pred)

    #if "nw:customer" in output_cols:
    #    ipdb.set_trace()
        
    rdf = []
    rdf.append(f"{rdfs_classname} rdf:type rdfs:Class .")
    for ii, r in df.iterrows():
        rdf.append(f"{r['URI']} rdf:type {rdfs_classname} .")
        for col in output_cols:
            rdf.append(f"{r['URI']} {col} {r[col]} .")
        
    return rdf
    
def dump_triples(df, prefix, pred):
    #print(df.head())
    #if pred == "nw:customer":
    #    ipdb.set_trace()
        
    subj_col = df.columns[0]; subj_classname = prefix + ":" + subj_col.replace("IDs", "").replace("ID", "")
    obj_col = df.columns[1]; obj_classname = prefix + ":" + obj_col.replace("IDs", "").replace("ID", "")
    triples = []
    for ii, r in df.iterrows():
        triples.append(f"{subj_classname}--{r[subj_col]} {pred} {obj_classname}--{r[obj_col]} .")
    return triples        
    
if __name__ == "__main__":
    conn = sqlite3.connect('./northwind.sqlitedb')

    # output prefixes
    print("prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>")
    print("prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>")
    print("prefix xsd: <http://www.w3.org/2001/XMLSchema#>")
    print("prefix nw: <http://www.geisel-software.com/RDF/NorthWind#>")
    
    # nodes and links
    triples = []
    
    df = pd.read_sql("select * from Orders", conn)
    triples.extend(dump_node_members(df, "nw", "nw:Order", "OrderID", ["CustomerID", "EmployeeID", "ShipperID"], None))

    df = pd.read_sql("select * from OrderDetails", conn)
    triples.extend(dump_node_members(df, "nw", "nw:OrderDetail", "OrderDetailID", ["ProductID"], ["OrderID"]))
    df = pd.read_sql("select o.OrderID, od.OrderDetailID from Orders o join OrderDetails od on o.orderID = od.orderID", conn)
    triples.extend(dump_triples(df, prefix = "nw", pred = "nw:order_detail"))

    df = pd.read_sql("select * from Products", conn)
    triples.extend(dump_node_members(df, "nw", "nw:Product", "ProductID", ["SupplierID", "CategoryID"], None))

    df = pd.read_sql("select * from Suppliers", conn)
    triples.extend(dump_node_members(df, "nw", "nw:Supplier", "SupplierID", [], None))

    df = pd.read_sql("select * from Categories", conn)
    triples.extend(dump_node_members(df, "nw", "nw:Category", "CategoryID", [], None))

    df = pd.read_sql("select * from Customers", conn)
    triples.extend(dump_node_members(df, "nw", "nw:Customer", "CustomerID", [], None))

    df = pd.read_sql("select * from Employees", conn)
    triples.extend(dump_node_members(df, "nw", "nw:Employee", "EmployeeID", [], None))

    df = pd.read_sql("select * from Shippers", conn)
    triples.extend(dump_node_members(df, "nw", "nw:Shipper", "ShipperID", [], None))

    for t in triples:
        print(t)
    
