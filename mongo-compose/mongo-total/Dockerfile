FROM mongo

#ADD https://observatory.openebench.bsc.es/api/tools /tmp/tools.json
COPY tools-total.json /tmp/tools-total.json
RUN jq '.message.tools' /tmp/tools-total.json  > /tmp/init.json
CMD mongoimport --host mongodb --db observatory --collection tools --type json --file /tmp/init.json --jsonArray