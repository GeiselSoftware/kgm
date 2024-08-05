```
sqlite3 northwind.sqlitedb < ./northwind-sqlite.sql
python build-rdf.py > northwind.data.ttl

```

```
sh ~/local/shacl-1.4.3/bin/shaclvalidate.sh -datafile ./northwind.data.ttl -shapesfile ./northwind.shacl.ttl
```
