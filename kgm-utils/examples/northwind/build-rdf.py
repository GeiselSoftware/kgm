import sys
import pandas as pd
import sqlite3

def make_URI(prefix, keys):
    ret = []
    for k in keys:
        ret.append(prefix + "\#" + str(k))
    return ret


def dump_node_members(df, prefix, rdfs_classname, node_uri_col, obj_cols, exclude_cols = None):    
    if exclude_cols:
        df = df.drop(exclude_cols, axis = 1)    
    literal_cols = list(set(df.columns) - set([node_uri_col]) - set(obj_cols))
    
    df.insert(0, 'URI', make_URI(rdfs_classname, df[node_uri_col]))
    df.drop(node_uri_col, inplace = True, axis = 1)

    output_cols = []
    for obj_col in obj_cols:        
        classname = prefix + ":" + obj_col.replace("ID", "s")
        pred = prefix + ":" + obj_col.replace("ID", "").lower()
        df[pred] = make_URI(classname, df[obj_col])
        output_cols.append(pred)

    for col in literal_cols:
        pred = prefix + ":" + col.lower()
        df[pred] = df[col].apply(lambda x: f'"{x}"^^xsd:string')
        output_cols.append(pred)

    rdf = []
    rdf.append(f"{rdfs_classname} rdf:type rdfs:Class .")
    for ii, r in df.iterrows():
        rdf.append(f"{r['URI']} rdf:type {rdfs_classname} .")
        for col in output_cols:
            rdf.append(f"{r['URI']} {col} {r[col]} .")
        
    return rdf
    
def dump_triples(df, prefix, pred):
    #print(df.head())
    subj_col = df.columns[0]; subj_classname = prefix + ":" + subj_col.replace("ID", "s")
    obj_col = df.columns[1]; obj_classname = prefix + ":" + obj_col.replace("ID", "s")
    triples = []
    for ii, r in df.iterrows():
        triples.append(f"{subj_classname}\#{r[subj_col]} {pred} {obj_classname}\#{r[obj_col]} .")
    return triples        
    
if __name__ == "__main__":
    conn = sqlite3.connect('./NW.sqlitedb')

    # output prefixes
    print("prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>")
    print("prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>")
    print("prefix xsd: <http://www.w3.org/2001/XMLSchema#>")
    print("prefix NW: <NW:>")
    
    # nodes
    n_triples = []
    df = pd.read_sql("select * from Orders", conn)
    n_triples.extend(dump_node_members(df, "NW", "NW:Orders", "OrderID", ["CustomerID", "EmployeeID", "ShipperID"]))
    df = pd.read_sql("select * from OrderDetails", conn)
    n_triples.extend(dump_node_members(df, "NW", "NW:OrderDetails", "OrderDetailID", ["ProductID"], ["OrderID"]))
    df = pd.read_sql("select * from Products", conn)
    n_triples.extend(dump_node_members(df, "NW", "NW:Products", "ProductID", ["SupplierID", "CategoryID"]))
    df = pd.read_sql("select * from Suppliers", conn)
    n_triples.extend(dump_node_members(df, "NW", "NW:Suppliers", "SupplierID", []))
    df = pd.read_sql("select * from Categories", conn)
    n_triples.extend(dump_node_members(df, "NW", "NW:Categories", "CategoryID", []))
    df = pd.read_sql("select * from Customers", conn)
    n_triples.extend(dump_node_members(df, "NW", "NW:Customers", "CustomerID", []))
    df = pd.read_sql("select * from Employees", conn)
    n_triples.extend(dump_node_members(df, "NW", "NW:Employees", "EmployeeID", []))
    df = pd.read_sql("select * from Shippers", conn)
    n_triples.extend(dump_node_members(df, "NW", "NW:Shippers", "ShipperID", []))

    for t in n_triples:
        print(t)

    # links
    l_triples = []
    df = pd.read_sql("select o.OrderID, od.OrderDetailID from Orders o join OrderDetails od on o.orderID = od.orderID", conn)
    l_triples.extend(dump_triples(df, prefix = "NW", pred = "NW:order_detail"))
    df = pd.read_sql("select od.OrderDetailID, p.ProductID from OrderDetails od join Products p on od.ProductID = p.ProductID", conn)
    l_triples.extend(dump_triples(df, prefix = "NW", pred = "NW:product"))
    df = pd.read_sql("select s.SupplierID, p.ProductID from Suppliers s join Products p on s.SupplierID = p.SupplierID", conn)
    l_triples.extend(dump_triples(df, prefix = "NW", pred = "NW:supplierOf"))
    df = pd.read_sql("select p.ProductID, c.CategoryID from Products p join Categories c on p.CategoryID = c.CategoryID", conn)
    l_triples.extend(dump_triples(df, prefix = "NW", pred = "NW:belongsToCategory"))
    df = pd.read_sql("select o.OrderID, c.CustomerID from Orders o join Customers c on o.CustomerID = c.CustomerID", conn)
    l_triples.extend(dump_triples(df, prefix = "NW", pred = "NW:customer"))
    df = pd.read_sql("select o.OrderID, e.EmployeeID from Orders o join Employees e on o.EmployeeID = e.EmployeeID", conn)
    l_triples.extend(dump_triples(df, prefix = "NW", pred = "NW:employee"))
    df = pd.read_sql("select o.OrderID, s.ShipperID from Shippers s join Orders o on s.ShipperID = o.ShipperID", conn)
    l_triples.extend(dump_triples(df, prefix = "NW", pred = "NW:shipper"))

    for t in l_triples:
        print(t)
    
