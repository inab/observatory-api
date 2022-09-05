FROM mongo

COPY tools_biotools.json /tools_biotools.json
CMD mongoimport --host mongodb --db FAIRsoft --collection biotools-tools --type json --file /tools_biotools.json --jsonArray