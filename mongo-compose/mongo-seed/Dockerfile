FROM mongo

COPY tools-biotools.json /tools-biotools.json
CMD mongoimport --host localhost --db FAIRsoft --collection biotools-tools --type json --file /tools-biotools.json --jsonArray