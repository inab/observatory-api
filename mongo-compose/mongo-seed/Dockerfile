FROM mongo

COPY tools-biotools.json /tools-biotools.json
CMD mongoimport --host localhost --db observatory --collection biotools-tools --type json --file /tools-biotools.json --jsonArray