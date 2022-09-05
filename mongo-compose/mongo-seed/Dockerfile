FROM mongo

COPY tools-biotools.json /tools-biotools.json
CMD mongoimport --host mongodb --db FAIRsoft --collection biotools-tools --type json --file /tools-biotools.json --jsonArray