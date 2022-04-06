# Webscraper-Project
This webscraper collects data for items on sale at https://www.asos.com/men/sale/cat/?cid=8409&nlid=mw|sale|shop+sale+by+product|sale+view+all using selenium. Data is stored locally as well as on aws s3 and rds. The scraper is also containerised using docker and run on an ec2 instance. Prometheus and grafana are used to monitor the metrics. A CI/CD pipeline is also set up for the docker image so that it is deployed to DockerHub everytime there is a new push on the main branch of the repository. 
# Milestone 1
The first step was to choose a website and build a scraper class with methods that navigate through the website including accepting cookies This was done using xpaths found on the website. The links to different products in the item container were acquired and then stored in a list.
# Milestone 2
The next step was to make the webscraper go to each of these links and acquire details (name, price, product ID). These details were then stored in a dictionary. Furthermore, a UUID4 was generated for each item and images were also collected for each item and stored in a seperate dictionary with the the product ID to track what the image corresponds to.
The image data was also downloaded and stored locally and a json file for the initial dictionary was also made locally which resets everytime the scraper is run.
# Milestone 3
Unit testing methods were also created and checked for the scraper to make sure it was more robust. This was done using pythons's unittest module. Things checked included the scraper navigating to the correct website, cookies should no longer appear after being accepted, a dictionary is made and data is saved in the correct directory. Docstrings were added to explain the code.
# Milestone 4
Code was added so that raw data and image data was then stored in aws s3 using boto3. Code was also added so that tabular data was also uploaded to aws rds. The new data is appended (not replacing) to the old data in postgresql.
# Milestone 5 
Code was refactored and adjusted and was made sure to run smoothly. Code was also added so that the webscraper does not rescrape any products already stored in rds. This was done using a sql query implemented in python that checks that the items product ID is not already within the database.
# Milestone 6
Options were added so that selenium can run in headless mode without issues. A docker image was made for the scraper and then containerised. EC2 was then set up and the docker image was then run on there.
# Milestone 7
A Prometheus container was then set up to monitor the scraper including hardware metrics. This was done by configuring the daemon file for Docker as well as the prometheus.yml file to monitor the metrics of the container in the ec2 instance. A grafana dashboard of the prometheus metrics was also made so that the metrics can be seen more clearly. ![alt text](http://localhost:3000/d/npGD1eynk/docker?orgId=1&from=1649226356859&to=1649247956859)
# Milestone 8
GitHub secrets that contain my Dockerhub details were then added. This was done so that GitHub action will build the Docker image and push it to my Dockerhub account everytime there is a new push to the main branch of the repository. Cronjobs were also added to the ec2 instance which pull the newest version of the scraper everyday from my Dockerhub account and run it

