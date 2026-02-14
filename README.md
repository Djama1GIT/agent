# Agent

Agent is a simple LLM microservice. 

## Installation and Setup <sup><sub>(tested on Linux)</sub></sup>

1. Install Docker and Docker Compose if they are not already installed on your system.

2. Clone the project repository:

```bash
git clone https://github.com/Djama1GIT/agent.git
cd agent
```
3. Start the project:

```bash
docker-compose up --build
```

## User Interface
Home page:
http://localhost/

Dashboard:
http://localhost/grafana/ (admin/admin)

## Technologies Used

- Python - A programming language used for the project.
- FastAPI - The Python framework used in the project to implement the REST API.
- REST - An architectural style for designing networked applications, used in the project for API communication between clients and servers.
- Docker - A platform used in the project for creating, deploying, and managing containers, allowing the application to run in an isolated environment.
- Prometheus - An open-source systems monitoring and alerting toolkit that collects and stores metrics as time series data.
- Grafana - A multi-platform open-source analytics and interactive visualization web application for monitoring and observability.
- Loki - A horizontally-scalable, highly-available, multi-tenant log aggregation system inspired by Prometheus.
- Promtail - An agent that ships the contents of local logs to a Loki instance, typically deployed to every machine running applications.

# Contributors

<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%">
        <a href="https://github.com/Djama1GIT">
          <img src="https://avatars.githubusercontent.com/u/89941580?v=4?s=130" height="130px;" alt="Djama1GIT"/>
          <br />
          <sub><b>Djama1GIT</b></sub>
        </a>
      </td>
    </tr>
  </tbody>
</table>
