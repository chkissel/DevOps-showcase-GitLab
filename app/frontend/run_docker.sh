docker container run --rm -d -p 80:8080 --name=frontend frontend
# docker container run --rm -d -p 8080:8080 --name=frontend --network canny_net --ip 192.168.0.2 frontend
# docker container run --rm -d -p 8080:8080 --name=frontend --network host frontend
