import json
import requests
import argparse
import os
from time import sleep
from collections import defaultdict

minHealthyServiceInstances = 2
minCpu = 75                         # CPU threshold to be healthy
minMemory = 75

#server = 'localhost:9000'
endpoint = 'servers'

#def apiServer (server,endpoint="servers"):
def apiServer (server,endpoint):
    """
    Takes a server and a query endpoint, connects or handle exception. If successful,
    decodes the retrieved json data and returns it as a python data structure.

    Required Parameters:
        server - API Server to connect to, formatted as IP:PORTt. This is expected to be a string representing the server's hostname or IP address where the API endpoint resides.
        endpoint - API endpoint to call. This argument has a default value of "servers". It's a string that specifies the specific API endpoint you want to interact with on the server.

    Output:
        ['10.58.1.14', '10.58.1.3', '10.58.1.67', '10.58.1.15', ....]
    """
    uri = 'http://' + server + '/' + endpoint
    response = requests.get(uri)
    if response.ok:
        return json.loads(response.content)
    else:
        response.raise_for_status()


def instanceStats (instanceId):
    """
    Retrieves stats for a specific instance, identified by the instance ID, in this case the server IP
    Also marks the instance as healthy or not depending on resource usage (Memory and CPU).

    Required Parameters:
        instanceId - Expects a valid instance id (the server IP) as string type as per the API documentation.

    Output:
        Single output
        {'cpu': '80%', 'memory': '26%', 'service': 'RoleService', 'ip': '10.58.1.10', 'status': 'unhealthy'}
    """
    result = apiServer(server, instanceId)
    # In the current API version, the IP is passed as instance ID, and is not part of the retrieved values, so we update the result and append it.
    result.update({'ip': instanceId})

    # Strip the % sign, spaces, tabs, newline and cr from the beginning and end of the string to convert memory
    # and cpu to a number, compare usage against our threshold and determine if the instance is healthy or not
    if float(result['memory'].strip(' \t\n\r%')) < minMemory and float(result['cpu'].strip(' \t\n\r%')) < minCpu:
        result.update({'status': 'healthy'})
    else:
        result.update({'status': '--unhealthy'})
    return result   # returns the updated result dictionary.


# Retrieves data for a specified service instances. If the service is not specified, retrieves all instances
def serviceStats (service=None):
    """
    Retrieves instances for a specified service, or for all services, and returns it as a list of dictionaries.

    Optional Parameters:
        service - Expects a valid service id with string type per the API documentation.
        If no value is passed, this will defaults to retrieve all services

    Output:
        [{'cpu': '68%', 'memory': '44%', 'service': 'AuthService', 'ip': '10.58.1.147', 'status': 'healthy'},..{}]
    """
    result=[]           # Empty list, this will hold the collected service statistics.
    instanceIds = apiServer(server, endpoint)

    # Grouping Instances by Service
    # Since we don't know the serviceIds in advance, we initialize a defaultdict with a default value of an empty list [] and retrieve/store all instance data
    instances = defaultdict(list)
    for instanceId in instanceIds:
        instance = instanceStats(instanceId)
        instances[instance['service']].append(instance)     #  Group instances by service, produce this: defaultdict(<class 'list'>, {'IdService': [{'cpu': '79%', 'memory': '59%', 'service': 'IdService', 'ip': '10.58.1.14', 'status': 'unhealthy'}]},..)

    # If no service is provided, return stats for all instances in the service collection
    if not service:
        for serviceId in instances:
            result = result + (instances[serviceId])    # Since no service is provided, return stats for all instances in the service collection
    else:
        result = instances[service]                     # Return only the service specified
    return result


# Expects a list of instances, separates them by service and checks if enough instance for each service are healthy.
# Return a dictionary such as { 'service1':'healthy','service2': 'unhealthy'}
def serviceHealth (serviceInstances = dict):
    """
    Scans the provided list of instances and return either an "healthy" or "unhealthy" value for each service,
    depending on how many healthy instances are running.

    Required Parameters:
    serviceInstances - Expects a list of instances, as returned by serviceStats(). List of dictionaries.
    They can belong to multiple services, the check will be carried out separately for each service

    Output:
        {'UserService': 'unhealthy', 'IdService': '--unhealthy', 'AuthService': 'healthy'}
    """
    serviceHealthSummary = {}       # Empty collection for the kv pair
    # We don't know how many services are part of the instance list
    healthyServiceInstances = defaultdict(int)

    for serviceInstance in serviceInstances:
        if serviceInstance['status'] == 'healthy':
            healthyServiceInstances[serviceInstance['service']] += 1
        else:
            if not healthyServiceInstances[serviceInstance['service']]:
                healthyServiceInstances[serviceInstance['service']] = 0

    for service in healthyServiceInstances:
        if healthyServiceInstances[service] >= minHealthyServiceInstances:
            serviceHealthSummary[service] = 'healthy'
            #serviceHealthSummary[service] = 'healthy', healthyServiceInstances[service]
        else:
            serviceHealthSummary[service] = '--unhealthy'
            #serviceHealthSummary[service] = 'unhealthy', healthyServiceInstances[service]
    return serviceHealthSummary


# Get the average resource usage across the instances, number of instances and status of the service
# Returns a dictionary
def serviceStatus (service):
    """
    Calculates an average of the service resource usage and health level and returns it as a dictionary

    Required Parameters:
    service - Expects a valid service ID as per API documentation. String.

    Output:
        {'service': 'IdService', 'cpu': 91.52380952380952, 'memory': 110.47619047619048, 'status': 'healthy', 'instances': 21}
    """
    serviceInstances = serviceStats(service)
    serviceMemory = 0
    serviceCpu = 0
    for instance in serviceInstances:
        # Retrieves mem/cpu usage value from the current instance dictionary, converts the stripped value to an integer for numerical calculations.
        # The value is then added to the serviceMemory variable, which accumulates the total usage across all instances.
        serviceMemory += int(instance['memory'].strip(' \t\n\r%'))
        serviceCpu += int(instance['cpu'].strip(' \t\n\r%'))
    serviceMemory = serviceMemory / len(serviceInstances)           # Calculates the avg memory usage for the service. Divides the total accumulated memory usage (serviceMemory) by the total number of service instances (len(serviceInstances)).
    serviceCpu = serviceCpu / len(serviceInstances)                 # Calculates the avg CPU usage by dividing the total accumulated CPU usage (serviceCpu) by the number of instances
    serviceState = {'service': service, 'cpu': serviceCpu, 'memory': serviceMemory, 'status': serviceHealth(serviceInstances)[service], 'instances': len(serviceInstances)}
    return serviceState


# Output Formatting
def printInstances(instanceList):
    """
    Used for --summary. Expects a list of instances and prints them in a nicely formatted table

    Required Parameters:
    instanceList - Expects a list of instances, as returned by serviceStats(). List of dictionaries.

    Output:
        ------------------------------------------------------------------------
        IP               SERVICE                   CPU      MEMORY   STATUS    |
        ------------------------------------------------------------------------
        10.58.1.121      UserService               76%      77%      --UNHEALTHY
        10.58.1.131      UserService               12%      64%      healthy
    """
    print('------------------------------------------------------------------------')
    print('{:16} {:25} {:8} {:8} {:8}'.format('IP','SERVICE','CPU','MEMORY','STATUS    |'))
    #print('IP','\t\tService','\t\tCPU','\tmemory','\tstatus')
    print('------------------------------------------------------------------------')
    for item in instanceList:
        row = '{:16} {:25} {:8} {:8} {:8}'.format(item['ip'], item['service'], item['cpu'], item['memory'], item['status'])
        #row = '{} {} {} {} {} {} {} {} {}'.format(item['ip'], '\t', item['service'], '\t\t', item['cpu'], '\t', item['memory'], '\t', item['status'])
        print (row)
    print('------------------------------------------------------------------------')

def printServiceStatus(serviceStatus):
    """
    Expects a service status. Prints it in a nicely formatted table

    Required Parameters:
    serviceStatus - Expects a serviceStatus dictionary, as returned by serviceStatus(). Dictionary.
    """
    print('------------------------------------------------------------')
    print('{:25} {:8} {:8} {:8}'.format('SERVICE', 'CPU', 'MEMORY','STATUS'))
    print('------------------------------------------------------------')
    row = '{:25} {:^8.2f} {:^8.2f} {:8}'.format(serviceStatus['service'], serviceStatus['cpu'], serviceStatus['memory'], serviceStatus['status'])
    print (row)

def printServiceHealth(serviceHealthSummary):
    """
    Expects a dictionary containing a key for each service pointing to the service health state.
    Prints it in a nicely formatted table

    Required Parameters:
    serviceHealthSummary - Expects a serviceHealthSummary dictionary, as returned by serviceHealth. Dictionary.

    Output:
        service                   status
        ---------------------------------
        UserService               healthy
        IdService                 healthy
    """
    print('-------------------------------------')
    print('{:25} {:16}'.format('SERVICE','STATUS    |'))
    print('-------------------------------------')
    for service in serviceHealthSummary:
        row = '{:25} {:16}'.format( service, serviceHealthSummary[service]  )
        print (row)
    print('-------------------------------------')


## Instruction Usage
parser = argparse.ArgumentParser(
    description='Small utility to gather and monitor instance resource usage'
    )

group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument(
    'server',
    help='The REST API server:port, e.g. 127.0.0.1:9000',
)

group.add_argument(
    '--summary',
    '-s',
    help='Prints a list of the all the running instances for all services',
    action="store_true",
    required=False
)

group.add_argument(
    '--serviceStats',
    '-ss',
    help='Prints a list of all the instances running the specified service. e.g --serviceStats AuthService',
    required=False
)

parser.add_argument(
    '--healthyInstances',
    '-hi',
    help='Minimum number of instances required for a service to be healthy. Defaults to 2.  e.g --healthyInstances 3 ',
    type=int,
    required=False
)

group.add_argument(
    '--healthCheck',
    '-hc',
    help='Prints a list of all the services with a low number of healthy instances',
    action="store_true",
    required=False
)

group.add_argument(
    '--monitorService',
    '-ms',
    help='Linux TOP style resource monitoring for a specified service. e.g --monitorService AuthService',
    required=False
)

args = parser.parse_args()
server = args.server


# Actions based on user input parameter

if args.healthyInstances:
    minHealthyServiceInstances = args.healthyInstances

# Send the following format as input to printInstances()
#   "[{'cpu': '61%', 'memory': '42%', 'service': 'GeoService', 'ip': '10.58.1.119', 'status': 'healthy'},...]"
if args.summary:
    printInstances(serviceStats())

if args.healthCheck:
    instances = serviceStats()
    printServiceHealth(serviceHealth(instances))

if args.serviceStats:
    printServiceStatus(serviceStatus(args.serviceStats))

if args.monitorService:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        printInstances(serviceStats(args.monitorService))
        sleep(5)