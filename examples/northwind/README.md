```
sqlite3 NW.sqlitedb < ./northwind-sqlite.sql
python build-rdf.py > NW.ttl

```

```
sh ~/local/shacl-1.4.3/bin/shaclvalidate.sh -datafile ./NW.ttl -shapesfile ./northwind-shacl.ttl
```