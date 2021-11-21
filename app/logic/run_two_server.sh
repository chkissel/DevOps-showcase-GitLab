docker run --name server_one -d -p 5001:5000 --network canny_net server
docker run --name server_two -d -p 5002:5000 --network canny_net server
