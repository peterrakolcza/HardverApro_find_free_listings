![HardverApró](https://cdn.rios.hu/design/ha/logo.png)

# HardverApró - find free listings
This script allows the user to extract the free items from HardverApró and view it in a browser.

## ⚠️Usage
First, install Docker and docker-compose
After that, you can use the following command to start the container
```python
docker-compose up
```

Finally, you can visit the website locally at port 8090
```
http://127.0.0.1:8090
```

(Or you can just run `python app.py` inside the `web` folder and run it without Docker)

## 📝Todo
- list faulty devices
- organize listings into categories
- extend it to more sites
- check if listing is active, otherwise skip
- improve the naming of the listings
