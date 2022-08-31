 sudo docker run -dp 5200:8080 -e SWAGGER_JSON=/tmp/swagger.json  -v /home/user/observatory-api/swagger:/tmp swaggerapi/swagger-ui
