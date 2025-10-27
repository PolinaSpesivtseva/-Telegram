docker run --name tg_analiz_mongo -d --rm \
        -e MONGO_INITDB_ROOT_USERNAME=user \
        -e MONGO_INITDB_ROOT_PASSWORD=5ksXjuYAbveYCfQ8mzbWMvx5i \
        -p 27017:27017 \
        -v ./data:/data/db \
        mongo:latest