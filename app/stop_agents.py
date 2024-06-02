import socket

import requests

# URL of the DirectoryAgent to get the list of registered agents
directory_address_hostname = socket.gethostname()
directory_address_port = 5000
directory_agent_url = f'http://{directory_address_hostname}:{
    directory_address_port}/GetAgents'


def get_registered_agents(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get agents from {
                  url}. Status code: {response.status_code}")
            return {}
    except requests.RequestException as e:
        print(f"Error getting agents from {url}: {e}")
        return {}


def shutdown_agent(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Successfully stopped agent at {url}")
        else:
            print(f"Failed to stop agent at {
                  url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error stopping agent at {url}: {e}")


if __name__ == "__main__":
    registered_agents = get_registered_agents(directory_agent_url)
    print(f"Registered agents: {registered_agents}")
    for agent_name, agent_address in registered_agents.items():
        base_url = agent_address.split(
            '/')[0] + '//' + agent_address.split('/')[2]
        stop_url = base_url + "/Stop"
        print(f"Shutting down agent {agent_name} at {stop_url}")
        shutdown_agent(stop_url)
    server_stop_url = directory_agent_url.replace('/GetAgents', '/Stop')
    print(f"Shutting down directory agent at {server_stop_url}")
    shutdown_agent(server_stop_url)

    print("Agents shut down successfully")
