# Fetch Rewards Data Engineering: ETL off a SQS Queue

## Overview

This project demonstrates a comprehensive development of an ETL (Extract, Transform, Load) application. The goal is to read Fetch Rewards App JSON data containing user login behavior from an AWS SQS Queue, transform the data by masking personal identifiable information (PII), and then write the transformed data to a Postgres database. The project uses Docker to run all the components locally, simulating the AWS and Postgres environments.

## Objectives

* _Extract_: Read JSON data from an AWS SQS Queue.
* _Transform_: Mask PII fields (device_id and ip) and flatten the JSON data object.
* _Load_: Write the transformed data into a Postgres database.

## Project Setup:

### Prerequisites

	1. Docker
	2. Docker Compose
	3. AWS CLI Local (awscli-local)
	4. Psql (PostgreSQL client)

### Installation

	1. Clone the repository:
`git clone [<repository-url>](https://github.com/harshshah2599/fetch-rewards-etl)`\
`cd fetch-rewards-etl`

	2. Install required packages:
`pip install requirements.txt`

    3. Start Docker containers:
`docker-compose up -d`

## Running the Application:

**Extract, Transform, and Load Messages**

To extract, transform, and load messages from the SQS queue to the Postgres database, run the following command once you are in the project directory:

`python app.py`

This will:

	1. Extract messages from the SQS queue.
	2. Transform the messages by masking PII fields and flattening the data structure.
	3. Load the transformed messages into the Postgres database.


## Verify local setup:

To verify if the ETL application works seamlessly, run the below commands to check the messages fetched from the SQS and the data being loaded into Postgres.

	• Read a message from the queue:
`awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue`

<img width="500" alt="Screenshot 2024-07-08 at 9 47 41 PM" src="https://github.com/harshshah2599/fetch-rewards-etl/assets/114712818/6e617704-530c-4220-8392-7a3f61f83670">


	• Connect to the Postgres database and verify the table:
`psql -d postgres -U postgres -p 5432 -h localhost -W`\
`SELECT * FROM user_logins;`

<img width="500" alt="Screenshot 2024-07-08 at 9 48 23 PM" src="https://github.com/harshshah2599/fetch-rewards-etl/assets/114712818/a010f322-b23d-4ee5-94a8-0c015e26d159">

## View the Data 

To easily compare and understand the data extracted from SQS and loaded into Postgres, I have created functions that allow to directly view the data.

To use these functions, make sure you are inside the project directory and run the following command:

`python view_data.py`

You will be presented with a menu to select whether you want to view the raw data or the transformed data. Simply choose your option, and the corresponding data will be displayed.

## Assumptions and Decisions

	1. Data Masking: PII fields (device_id and ip) are hashed using SHA-256 to ensure that duplicate values can be identified while securing the sensitive information.
	2. Database Schema: The target table `user_logins` is assumed to have been pre-created with the specified schema.
	3. Environment: The application runs locally using Docker to simulate AWS SQS and Postgres services.
	4. App Version Handling: Assumed `app_version` is in the format x.y.z and only the major version (x) is stored.
	5. Date Parsing: Assumed `create_date` is in the YYYY-MM-DD format.

#### Why use SHA256 for data masking? Can data analysts easily find duplicates using this?
SHA-256 is a cryptographic hash function that can be used to mask sensitive information(PII). It generates a fixed-size 256-bit hash that is unique to the input data. Using SHA-256 ensures that the original data cannot be easily recovered, providing a strong layer of security for sensitive information. Data analysts can easily find duplicates using SHA-256. Although the original data is masked and cannot be retrieved directly, the same input value will always produce the same hash output. This means that duplicate values in the original data will result in identical hash values, allowing analysts to identify duplicates without exposing the sensitive information.`

#### How can PII be recovered later on?
To recover the original PII values, the mappings of hashed values to original values can be stored in a secure, access-controlled database. This allows for the reversal of the masking process if necessary, while maintaining security and compliance with privacy regulations.`


## Production Deployment

#### How would you deploy this application in production?

* To deploy this application in production, a combination of containerization and orchestration tools can be used to ensure a robust, scalable, and maintainable environment. Containerization with Docker would be the first step, packaging the application and all its dependencies into a single, consistent unit that can run anywhere. This approach guarantees that the application behaves the same in development, testing, and production environments.

* To manage and scale these containers, Kubernetes which provides automated deployment, scaling, and management of containerized applications can be used. It would ensure high availability and fault tolerance by distributing the containers across a cluster of machines and automatically restarting any containers that fail.

* A CI/CD pipeline would be set up using tools like Jenkins or GitHub Actions. This pipeline would automate the process of testing, building, and deploying the application, ensuring that new features and bug fixes can be delivered quickly and reliably.

* For monitoring and logging, tools like Prometheus for real-time monitoring and alerting, and the ELK Stack (Elasticsearch, Logstash, and Kibana) for logging and visualization. These tools would provide comprehensive observability into the application’s performance and health, allowing for quick identification and resolution of any issues that arise in production.

#### What other components would you want to add to make this production ready?

1. **Error Handling**: Comprehensive error handling and retry mechanisms for robust ETL operations.
The current application does not appropriately handle error or annomalies in the data.
For example, there could be messages which have inconsistent data and may give error such as-
`Missing key 'user' in message: {"user_id": "424cdd21-063a-43a7-b91b-7ca1a833afae", "app_version": "2.3.0", "device_type": "android", "ip": "199.172.111.135", "locale": "RU", "device_id": "593-47-5928"}`
2. **Security**: Secure database connections using SSL to encrypt data in transit, ensuring sensitive information remains protected. Implement IAM roles for AWS resources to enforce fine-grained access control and reduce the risk of unauthorized access.
3. **Data Validation**: Implement data validation checks to ensure that incoming data adheres to expected formats and constraints, preventing corrupted or malicious data from entering the system. These checks can include schema validation, type checking, and range validations.
4. **Monitoring and Logging**: Use tools like Prometheus for real-time monitoring of application performance and resource utilization, enabling proactive issue detection and resolution. Integrate the ELK Stack (Elasticsearch, Logstash, Kibana) for comprehensive logging and visualization, aiding in troubleshooting and maintaining system health.
5. **Configuration Management**: Externalize configuration parameters using environment variables or configuration files to simplify deployment and enhance flexibility. This approach allows for easy updates and management of configurations without changing the application code, supporting different environments and use cases.


## Future Scope for the Application - How can this scale with a growing dataset?

We can use AWS Auto Scaling for SQS and Kubernetes to automatically scale resources based on load, ensuring the application can handle varying levels of traffic efficiently. Partitioning the Postgres database will help manage large datasets more effectively, improving query performance and data organization. Implementing distributed processing with tools like Apache Kafka and Spark will enable real-time data processing and enhance the system’s ability to handle large volumes of data. Additionally, optimizing database queries and using indexing will further improve performance, reducing latency and increasing overall efficiency.


## Conclusion

This project demonstrates the development of an ETL application that reads messages from an SQS queue, transforms the data by masking PII, and loads the transformed data into a Postgres database. The use of Docker ensures a consistent and portable development environment, making it easy to simulate AWS and Postgres services locally.

**For further questions or clarifications, feel free to reach out!**
