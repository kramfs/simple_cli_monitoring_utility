# Background
We have mock cloud service provider that features the following characteristics:

1. Offers an API for fetching all running servers. Clients can access `/servers` to get a list of available running instances.

    ````
    $ curl localhost:<port>/servers
    ["10.58.1.121","10.58.1.120","10.58.1.123","10.58.1.122",...]
    ````

2. The same service also allows you to query a given IP (`instanceID`) for simple statistics. Clients can access a specific instance IP (e.g., /10.58.1.10) to get simulated statistics (service name, CPU, memory) for that instance.

    ````
    $ curl localhost:<port>/10.58.1.121
    {"cpu":"61%","service":"UserService","memory":"4%"}
    ````

# Description
This utility was created to interact with the service discovery API. This allows us to efficiently monitor and manage our deployed resources. By querying the API, the utility can retrieve information about the instance service, running instance count per service, their health and performance metrics. This gives us valuable insights into the actual state of our deployed resources, helping us ensure they are functioning as intended and taking appropriate actions if any issues arise.

The tool accepts multiple commands. Depending on which command is run, it should:

1. Print running services to stdout
  `--summary`

2. Print out average CPU/Memory of services of the same type
 `--serviceStats`

3. Flag services which have fewer than 2 healthy instances running
 `--healthyInstances 2 --healthCheck`

4. Have the ability to track and print CPU/Memory of all instances of a given service over
time (until the command is stopped, e.g. ctrl + c).
 `--monitorService IdService`


## Feature Functions
These are notable functions used that handles the heavy lifting workload in retrieving resource information, the function summary, description as well as the required parameters and the expected output.

### apiServer

    Takes a server and a query endpoint, connects or handle exception. If successful, decodes the retrieved json data and returns it as a python data structure.

    Required Parameters:
        server - API Server to connect to, formatted as ip:port. This is expected to be a string representing the server's hostname or IP address where the API endpoint resides.
        endpoint - API endpoint to call. This argument has a default value of "servers". It's a string that specifies the specific API endpoint you want to interact with on the server.

    Output:
        ['10.58.1.14', '10.58.1.3', '10.58.1.67', '10.58.1.15', ....]

````
>>> apiServer(server,endpoint)
['10.58.1.40', '10.58.1.76', '10.58.1.48', '10.58.1.59', '10.58.1.80', '10.58.1.10', '10.58.1.66', '10.58.1.134', '10.58.1.102', '10.58.1.44', '10.58.1.47', '10.58.1.109', '10.58.1.107', '10.58.1.145', '10.58.1.45', '10.58.1.8', '10.58.1.84', '10.58.1.115', '10.58.1.7', '10.58.1.110', '10.58.1.6', '10.58.1.19', '10.58.1.37', '10.58.1.39', '10.58.1.122', '10.58.1.119', '10.58.1.26', '10.58.1.43', '10.58.1.11', '10.58.1.114', '10.58.1.143', '10.58.1.24', '10.58.1.67', '10.58.1.87', '10.58.1.9', '10.58.1.136', '10.58.1.28', '10.58.1.144', '10.58.1.79', '10.58.1.140', '10.58.1.141', '10.58.1.146', '10.58.1.81', '10.58.1.52', '10.58.1.18', '10.58.1.57', '10.58.1.30', '10.58.1.42', '10.58.1.108', '10.58.1.96', '10.58.1.54', '10.58.1.4', '10.58.1.31', '10.58.1.94', '10.58.1.139', '10.58.1.49', '10.58.1.150', '10.58.1.129', '10.58.1.1', '10.58.1.147', '10.58.1.70', '10.58.1.113', '10.58.1.97', '10.58.1.3', '10.58.1.105', '10.58.1.51', '10.58.1.98', '10.58.1.75', '10.58.1.106', '10.58.1.77', '10.58.1.34', '10.58.1.62', '10.58.1.121', '10.58.1.112', '10.58.1.33', '10.58.1.89', '10.58.1.2', '10.58.1.128', '10.58.1.73', '10.58.1.100', '10.58.1.35', '10.58.1.72', '10.58.1.74', '10.58.1.135', '10.58.1.12', '10.58.1.64', '10.58.1.95', '10.58.1.99', '10.58.1.27', '10.58.1.148', '10.58.1.91', '10.58.1.137', '10.58.1.90', '10.58.1.126', '10.58.1.32', '10.58.1.20', '10.58.1.60', '10.58.1.116', '10.58.1.63', '10.58.1.29', '10.58.1.50', '10.58.1.46', '10.58.1.14', '10.58.1.38', '10.58.1.36', '10.58.1.15', '10.58.1.41', '10.58.1.83', '10.58.1.23', '10.58.1.118', '10.58.1.55', '10.58.1.125', '10.58.1.127', '10.58.1.13', '10.58.1.85', '10.58.1.131', '10.58.1.104', '10.58.1.124', '10.58.1.21', '10.58.1.65', '10.58.1.56', '10.58.1.111', '10.58.1.149', '10.58.1.5', '10.58.1.93', '10.58.1.71', '10.58.1.132', '10.58.1.92', '10.58.1.58', '10.58.1.138', '10.58.1.120', '10.58.1.25', '10.58.1.82', '10.58.1.123', '10.58.1.53', '10.58.1.22', '10.58.1.130', '10.58.1.16', '10.58.1.69', '10.58.1.86', '10.58.1.101', '10.58.1.133', '10.58.1.142', '10.58.1.68', '10.58.1.103', '10.58.1.78', '10.58.1.88', '10.58.1.61', '10.58.1.17', '10.58.1.117']
````

## instanceStats

    Retrieves stats for a specific instance, identified by the instance API ID, in this case the server IP. Also marks the instance as healthy or not depending on resource usage (Mem and CPU).

    Required Parameter(s):
        instanceId - Expects a valid instance id (the server IP) as string type as per the API documentation.

    Output:
        {'cpu': '80%', 'memory': '26%', 'service': 'RoleService', 'ip': '10.58.1.10', 'status': 'unhealthy'}

````
>>> instanceStats('10.58.1.14')
{'cpu': '87%', 'memory': '54%', 'service': 'IdService', 'ip': '10.58.1.14', 'status': 'unhealthy'}
````

## serviceStats

    Retrieves instances for a specified service, or for all services, and returns it as a list of dictionaries.

    Optional Parameter(s):
        service - Expects a valid service id with string type per the API documentation.
        If no value is passed, this will defaults to retrieve all services

````
>>> serviceStats()
# Gathers information for all services.
...
>>> serviceStats('IdService')
[{'cpu': '72%', 'memory': '62%', 'service': 'IdService', 'ip': '10.58.1.14', 'status': 'healthy'}, {'cpu': '99%', 'memory': '8%', 'service': 'IdService', 'ip': '10.58.1.125', 'status': 'unhealthy'}, {'cpu': '50%', 'memory': '46%', 'service': 'IdService', 'ip': '10.58.1.117', 'status': 'healthy'}, {'cpu': '21%', 'memory': '26%', 'service': 'IdService', 'ip': '10.58.1.123', 'status': 'healthy'}, {'cpu': '26%', 'memory': '63%', 'service': 'IdService', 'ip': '10.58.1.62', 'status': 'healthy'}, {'cpu': '16%', 'memory': '93%', 'service': 'IdService', 'ip': '10.58.1.116', 'status': 'unhealthy'}, {'cpu': '56%', 'memory': '14%', 'service': 'IdService', 'ip': '10.58.1.51', 'status': 'healthy'}, {'cpu': '29%', 'memory': '1%', 'service': 'IdService', 'ip': '10.58.1.78', 'status': 'healthy'}, {'cpu': '68%', 'memory': '8%', 'service': 'IdService', 'ip': '10.58.1.92', 'status': 'healthy'}, {'cpu': '83%', 'memory': '11%', 'service': 'IdService', 'ip': '10.58.1.71', 'status': 'unhealthy'}, {'cpu': '19%', 'memory': '73%', 'service': 'IdService', 'ip': '10.58.1.120', 'status': 'healthy'}, {'cpu': '0%', 'memory': '52%', 'service': 'IdService', 'ip': '10.58.1.112', 'status': 'healthy'}, {'cpu': '11%', 'memory': '3%', 'service': 'IdService', 'ip': '10.58.1.24', 'status': 'healthy'}, {'cpu': '23%', 'memory': '11%', 'service': 'IdService', 'ip': '10.58.1.86', 'status': 'healthy'}, {'cpu': '15%', 'memory': '46%', 'service': 'IdService', 'ip': '10.58.1.16', 'status': 'healthy'}, {'cpu': '77%', 'memory': '39%', 'service': 'IdService', 'ip': '10.58.1.40', 'status': 'unhealthy'}, {'cpu': '45%', 'memory': '65%', 'service': 'IdService', 'ip': '10.58.1.64', 'status': 'healthy'}, {'cpu': '42%', 'memory': '10%', 'service': 'IdService', 'ip': '10.58.1.96', 'status': 'healthy'}, {'cpu': '46%', 'memory': '55%', 'service': 'IdService', 'ip': '10.58.1.133', 'status': 'healthy'}, {'cpu': '82%', 'memory': '44%', 'service': 'IdService', 'ip': '10.58.1.30', 'status': 'unhealthy'}, {'cpu': '68%', 'memory': '15%', 'service': 'IdService', 'ip': '10.58.1.142', 'status': 'healthy'}]
````


## serviceHealth

    Scans the provided list of instances and return either an "healthy" or "unhealthy" value for each service, depending on how many healthy instances are running.

    Required Parameters:
    serviceInstances - Expects a list of instances, as returned by serviceStats. List of dictionaries. They can belong to multiple services, the check will be carried out separately for each service.


````
>>> serviceHealth([{'cpu': '41%', 'memory': '48%', 'service': 'UserService', 'ip': '10.58.1.52', 'status': 'healthy'}, {'cpu': '80%', 'memory': '55%', 'service': 'IdService', 'ip': '10.58.1.51', 'status': 'unhealthy'}, {'cpu': '60%', 'memory': '54%', 'service': 'AuthService', 'ip': '10.58.1.46', 'status': 'healthy'}, {'cpu': '53%', 'memory': '50%', 'service': 'AuthService', 'ip': '10.58.1.107', 'status': 'healthy'}])

{'UserService': 'unhealthy', 'IdService': 'unhealthy', 'AuthService': 'healthy'}
````


## serviceStatus

    Calculates an average of the service resource usage and health level and returns it as a dictionary

    Required Parameters:
    service - Expects a valid service ID as per API documentation. String.


````
>>> serviceStatus('IdService')
{'service': 'IdService', 'cpu': 47.333333333333336, 'memory': 54.95238095238095, 'status': 'healthy', 'instances': 21}

>>> serviceStatus('AuthService')
{'service': 'AuthService', 'cpu': 54.529411764705884, 'memory': 49.11764705882353, 'status': 'healthy', 'instances': 17}
````

# Build and Run

To standardized the build and application running, we will utilize containers to provide a more controlled and reliable development experience and have the benefit of:

- Reproducible Builds: Guarantee a consistent environment regardless of the developer's machine setup. Everyone on the team gets the same dependencies and configurations, leading to fewer errors and faster debugging.

- Isolation: Applications in containers are isolated from each other and the host system. This prevents conflicts between dependencies and ensures a clean development environment.

- Portability: Containerized applications can be easily moved between different environments (local, development, staging, production) without requiring changes to the code or configuration.

## Requirements:
Before you dive in, make sure the following tools are set up and ready to go, docker and docker compose must handle container creation without a hitch. The local user should also be able to run docker without the need to elevate permission.
- Docker - https://docs.docker.com/engine/install/
- Docker Compose - https://docs.docker.com/compose/install/
- git - https://github.com/git-guides/install-git

## Build

Clone the repo:
````
git clone https://github.com/kramfs/simple_cli_monitoring_utility
````

Enter the cloned repo and you should see the following files and folder
````
$ cd simple_cli_monitoring_utility

$ tree
.
├── compose.yaml
├── dockerfile
├── README.md
├── src
    ├── cpx_server.py
    ├── monitoring.py
    └── requirements.txt

2 directories, 6 files
````

- `compose.yaml` - The compose file has two defined services, the `api` service. This the mock cloud service provider API, with port `80` exposed internally within the container network and also exposed on the host using port `9001`. The other is the `monitoring` service which we can run interactive commands.
- `dockerfile` - For building and creating the container image. We opted to use the slim version of python as our base image.
- `cpx_server.py` - This is our mock cloud service provider API server which will run on the `api` service container. This will be copied to the image.
- `monitoring.py` - Our utility for interacting with the service discovery API. This will be copied to the image.
- `requirements.txt` - Required libraries to be installed as part of the build

To build and create the container:
````
$ docker build . -t monitoring --no-cache
[+] Building 3.1s (10/10) FINISHED                                                                                                                                   docker:default
 => [internal] load build definition from dockerfile                                                                                                                           0.0s
 => => transferring dockerfile: 281B                                                                                                                                           0.0s
 => [internal] load metadata for docker.io/library/python:slim                                                                                                                 0.0s
 => [internal] load .dockerignore                                                                                                                                              0.0s
 => => transferring context: 145B                                                                                                                                              0.0s
 => [1/5] FROM docker.io/library/python:slim                                                                                                                                   0.0s
 => [internal] load build context                                                                                                                                              0.0s
 => => transferring context: 12.77kB                                                                                                                                           0.0s
 => CACHED [2/5] WORKDIR /app                                                                                                                                                  0.0s
 => [3/5] COPY src/requirements.txt ./                                                                                                                                         0.1s
 => [4/5] RUN pip install -r requirements.txt                                                                                                                                  2.8s
 => [5/5] COPY src/ /app                                                                                                                                                       0.0s
 => exporting to image                                                                                                                                                         0.1s
 => => exporting layers                                                                                                                                                        0.1s
 => => writing image sha256:be72abfcc7d975097f590ae7d5dcbf94e375545708e4556b8f9cdab2b3941a61                                                                                   0.0s
 => => naming to docker.io/library/monitoring                                                                                                                                  0.0s
````

If there's no error on the build, we should be able to see our newly created image:
````
$ docker image ls
REPOSITORY                    TAG             IMAGE ID       CREATED        SIZE
monitoring                    latest          11a0d3490542   2 hours ago    143MB
````

Ok looking great so far, let's run it. The docker compose file `compose.yaml` uses the image tagged as monitoring to be present locally:
````
$ docker compose up
[+] Running 3/3
 ✔ Network simple_cli_monitoring_utility_default  Created                                                                                                                       0.2s 
 ✔ Container monitoring                           Created                                                                                                                       0.1s 
 ✔ Container api                                  Created                                                                                                                       0.1s 
Attaching to api, monitoring
monitoring  | Python 3.12.4 (main, Jul 10 2024, 19:07:59) [GCC 12.2.0] on linux
monitoring  | Type "help", "copyright", "credits" or "license" for more information.
````

We should have two running containers now, both are using the same container image tagged as `monitoring`:
````
$ docker compose ps
NAME         IMAGE        COMMAND                  SERVICE      CREATED          STATUS              PORTS
api          monitoring   "python cpx_server.p…"   api          23 minutes ago   Up About a minute   0.0.0.0:9001->80/tcp, :::9001->80/tcp
monitoring   monitoring   "python3"                monitoring   23 minutes ago   Up About a minute
````


# USAGE

To run the app and show the help menu
````
$ docker exec -it monitoring python monitoring.py -h
usage: monitoring.py [-h] [--summary] [--serviceStats SERVICESTATS] [--healthyInstances HEALTHYINSTANCES] [--healthCheck] [--monitorService MONITORSERVICE] server

Small utility to gather and monitor instance resource usage

positional arguments:
  server                The REST API server:port, e.g. 127.0.0.1:9000

options:
  -h, --help            show this help message and exit
  --summary, -s         Prints a list of the all the running instances for all services
  --serviceStats SERVICESTATS, -ss SERVICESTATS
                        Prints a list of all the instances running the specified service. e.g --serviceStats AuthService
  --healthyInstances HEALTHYINSTANCES, -hi HEALTHYINSTANCES
                        Minimum number of instances required for a service to be healthy. Defaults to 2. e.g --healthyInstances 3
  --healthCheck, -hc    Prints a list of all the services with a low number of healthy instances
  --monitorService MONITORSERVICE, -ms MONITORSERVICE
                        Linux TOP style resource monitoring for a specified service. e.g --monitorService AuthService
````

1. To print the running services to stdout, we'll use the `--summary` parameter. We can access the `api` server directly using its name since our `monitoring` container is running in the same network
    ````
    $ docker exec -it monitoring python monitoring.py api --summary
    
    ------------------------------------------------------------------------
    IP               SERVICE                   CPU      MEMORY   STATUS    |
    ------------------------------------------------------------------------
    10.58.1.5        StorageService            17%      66%      healthy 
    10.58.1.99       StorageService            49%      84%      --unhealthy
    10.58.1.73       StorageService            14%      30%      healthy 
    10.58.1.137      StorageService            82%      52%      --unhealthy
    10.58.1.82       StorageService            70%      12%      healthy 
    10.58.1.69       StorageService            78%      68%      --unhealthy
    10.58.1.114      StorageService            62%      41%      healthy 
    10.58.1.53       StorageService            29%      78%      --unhealthy
    10.58.1.4        StorageService            89%      100%     --unhealthy
    10.58.1.15       StorageService            15%      60%      healthy 
    10.58.1.1        StorageService            42%      31%      healthy 
    ````

2. Print out average CPU/Memory of services of the same type, we'll use `--serviceStats`

    ````
    $ docker exec -it monitoring python monitoring.py api --serviceStats StorageService
    ------------------------------------------------------------
    SERVICE                   CPU      MEMORY   STATUS  
    ------------------------------------------------------------
    StorageService             44.94    56.06   healthy 
    ````

3. Flag services which have fewer than 2 healthy instances running, we'll use `--healthyInstances 2 --healthCheck`

    ````
    $ docker exec -it monitoring python monitoring.py api --healthyInstances 2 --healthCheck
    -------------------------------------
    SERVICE                   STATUS    |
    -------------------------------------
    IdService                 healthy
    RoleService               healthy         
    StorageService            healthy         
    AuthService               healthy         
    MLService                 healthy         
    UserService               healthy         
    GeoService                healthy         
    TicketService             healthy         
    TimeService               healthy         
    PermissionsService        healthy         
    ----------------------------------

    # Increase the threshold checking if there are 8 healthy instances
    $ docker exec -it monitoring python monitoring.py api --healthyInstances 8 --healthCheck
    -------------------------------------
    SERVICE                   STATUS    |
    -------------------------------------
    IdService                 --unhealthy     
    RoleService               healthy         
    StorageService            healthy         
    AuthService               healthy         
    MLService                 healthy         
    UserService               --unhealthy     
    GeoService                healthy         
    TicketService             --unhealthy     
    TimeService               --unhealthy     
    PermissionsService        --unhealthy     
    ----------------------------------
    ````

4. Have the ability to track and print CPU/Memory of all instances of a given service over
time (until the command is stopped, e.g. ctrl + c). For this case, we'll use `--monitorService IdService`. It will loop over and run every 5 seconds until the command is stopped.

    ````
    $ docker exec -it monitoring python monitoring.py api -ms IdService  

    ------------------------------------------------------------------------
    IP               SERVICE                   CPU      MEMORY   STATUS    |
    ------------------------------------------------------------------------
    10.58.1.64       IdService                 45%      11%      healthy 
    10.58.1.142      IdService                 7%       38%      healthy 
    10.58.1.133      IdService                 86%      19%      --unhealthy
    10.58.1.62       IdService                 39%      26%      healthy 
    10.58.1.123      IdService                 49%      72%      healthy 
    10.58.1.71       IdService                 42%      76%      --unhealthy
    10.58.1.78       IdService                 88%      51%      --unhealthy
    10.58.1.117      IdService                 50%      99%      --unhealthy
    10.58.1.51       IdService                 22%      45%      healthy 
    10.58.1.14       IdService                 30%      74%      healthy 
    10.58.1.86       IdService                 21%      55%      healthy 
    10.58.1.16       IdService                 25%      69%      healthy 
    10.58.1.92       IdService                 63%      33%      healthy 
    10.58.1.112      IdService                 11%      98%      --unhealthy
    10.58.1.125      IdService                 48%      84%      --unhealthy
    10.58.1.96       IdService                 57%      46%      healthy 
    10.58.1.40       IdService                 98%      93%      --unhealthy
    10.58.1.116      IdService                 86%      63%      --unhealthy
    10.58.1.120      IdService                 73%      25%      healthy 
    10.58.1.30       IdService                 26%      24%      healthy 
    10.58.1.24       IdService                 16%      19%      healthy 
    ------------------------------------------------------------------------
    ````


# Future Improvements:
- Sorting
    - Sort IP's in increasing or decreasing order
    - Sort Service in alphabetical order
    - Sort CPU and/or MEMORY in increasing or decreasing order
    - Sort status from healthy or unhealthy
- Pagination
    - This is to prevent overloading the API which may cause our request from being potentially throttled or timed out if the return payload is large.
- Better display presentation
    - Add color coding to differentiate healthy and unhealthy instances