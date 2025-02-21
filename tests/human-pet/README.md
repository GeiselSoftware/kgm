```
kgm db init
kgm ksd dump ./human-pet.ksd > ./human-pet.shacl.ttl
kgm graph import /human-pet.shacl ./human-pet.shacl.ttl
kgm graph new /human-pet
kgm graph ls
```

