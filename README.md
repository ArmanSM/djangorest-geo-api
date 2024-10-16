# djangrest-geo-api
 Simple REST API for servicing GeoJSON. 

# How to Run (Windows)
1. Install Postgres (16.x or earlier) and create a database with the Postgis extension. Note that Postgis version must be version 3.4 or older for compatibility with Django. 3.4 is the default with Postgres 16. Steps below are in psql (postgres shell):
	1. Create db using command: ``` CREATE DATABASE <db_name>; ``
	2. Once connected to it: ``` CREATE EXTENSION postgis; ```
	3. To check that version <= 3.4.x: ``` SELECT PostGIS_full_version(); ```
	4. Note that you should remember the "db_name" and the username and password you set when configuring postgres to put in the .env later to connect to Django to the database


2. Install gdal and other requirements. For windows, use conda to install gdal and Python (other dependencies can be installed using pip in the conda environment). I used gdal 3.6.2. Note that gdal must be version 3.8 or older (as per https://docs.djangoproject.com/en/5.1/ref/contrib/gis/install/geolibs/) 

	1. Install miniconda 3: https://docs.anaconda.com/miniconda/#miniconda-latest-installer-links 
	2. Make environment: ``` conda create --name <env-name> python=3.12.7 ```
	3. Activate the environment: ``` source C:/miniconda3/Scripts/activate <env-name> ```
	4. Install gdal: ```   conda install -c conda-forge gdal==3.6.2 ```
	5. Install other dependencies: ``` pip -r install requirements.txt ```
	6. In settings.py, set the "GDAL_LIBRARY_PATH" to where it is found on your system. For my miniconda environment, it is in  "miniconda3/envs/\<env-name>/Library/bin/gdal.dll"

3. Create a .env file and verify settings.py. Place it in the geoapi/ directory where settings.py can be found.  
Fill in the values.
	- SECRET_KEY=
	- DB_NAME=
	- DB_USER=
	- DB_PASS=
	- The secret key can be generated by running this script in a Python shell: 
	``` 
	from django.core.management.utils import get_random_secret_key
	print(get_random_secret_key()) 
	``` 
	- DB_NAME is the database's name you made in postgres, DB_USER is the username you created in postgres (often 'postgres' by default), DB_PASS is the password you created in postgres. 

	- Make sure the "DATABASES" configurations in settings.py match your database


4. Run the API. First make database migrations, then create a superuser to generate tokens. 
	- ``` python manage.py makemigrations ```
	- ``` python manage.py migrate ```
	- For getting tokens easily for development/testing purposes, enter whatever username and password that's easy to remember when prompted:  
	``` python manage.py createsuperuser ```

	- Run the App: ``` python manage.py runserver ```

5. Generate Token
	1. Open a browser and naviagte to: [http://localhost:8080/api/features/token](http://localhost:8080/api/features/token)
	2. Enter the username and password that you set in createsuperuser and click "post". 
	3. Copy the "access token" and save it to use in Postman or Curl (or other tool) as a Bearer token to make requests

6. Test the Script and the endpoints
	- The script is run as a django command (from the directory with manage.py): 
	``` Python manage.py loadgeojson <Token> ```
		- It can be easier to save the token as a variable and run: ``` Python manage.py loadgeojson $Token ```

	- Get all municipalities endpoint: http://127.0.0.1:8000/api/features/dutch_municipality 
		- Pages can be specified like so: http://127.0.0.1:8000/api/features/dutch_municipality/?page=1 

	- Get municipalities within bounding box: http://127.0.0.1:8000/api/features/dutch_municipality/?in_bbox=5.7,50.9,5.8,51 
		- Order of values in the "in_bbox" query variable: min x, min y, max x, max y
	
	- Get municipality by name: http://127.0.0.1:8000/api/features/dutch_municipality/Stein/
		- Similar for update and delete, but using PUT or DELETE request types. Put requires a geojson in the request.
		- Add one or more municipalities using POST and putting a geojson feature collection in the request body. An example request body is in features/data called "example_simple_municipality.geojson"
