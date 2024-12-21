# CQRS and Event Sourcing Demo Application with AWS Serverless

This project demonstrates a Command Query Responsibility Segregation (CQRS) and Event Sourcing pattern using AWS Serverless technologies.

The application showcases a user management system with separate read and write models. It utilizes AWS Lambda functions for handling commands and queries, and DynamoDB tables for event storage and data projections.

## Repository Structure

```
.
├── README.md
├── src
│   ├── command_handler.py
│   ├── detail_handler.py
│   ├── list_handler.py
│   └── projection_handler.py
└── template.yaml
```

### Key Files

- `src/command_handler.py`: Handles POST requests to the `/command` endpoint, storing events in the EventsTable.
- `src/detail_handler.py`: Processes GET requests to retrieve user details from the UserDetailTable.
- `src/list_handler.py`: Manages GET requests to list all users from the UserSummaryTable.
- `src/projection_handler.py`: Listens to DynamoDB streams and updates the UserSummaryTable and UserDetailTable based on events.
- `template.yaml`: AWS SAM template defining the serverless infrastructure.

## Usage Instructions

### Installation

Prerequisites:
- AWS CLI configured with appropriate permissions
- AWS SAM CLI installed
- Python 3.12

To deploy the application:

1. Clone the repository
2. Navigate to the project directory
3. Run the following commands:

```bash
sam build
sam deploy --guided
```

Follow the prompts to complete the deployment.

### API Endpoints

1. Create/Update User (Command):
   ```
   POST /command
   Body: {
     "user_id": "user-001",
     "event_type": "USER_CREATED",
     "payload": {
       "name": "Alice",
       "email": "alice@example.com"
     }
   }
   ```

2. List Users:
   ```
   GET /list
   ```

3. Get User Details:
   ```
   GET /detail?user_id=user-001
   ```

### Common Use Cases

1. Creating a new user:
   ```python
   import requests
   import json

   api_url = "https://your-api-gateway-url.amazonaws.com/Prod"
   
   data = {
     "user_id": "user-001",
     "event_type": "USER_CREATED",
     "payload": {
       "name": "Alice",
       "email": "alice@example.com"
     }
   }
   
   response = requests.post(f"{api_url}/command", json=data)
   print(json.loads(response.text))
   ```

   Expected output:
   ```json
   {
     "message": "Event stored",
     "aggregate_id": "user-001",
     "event_type": "USER_CREATED",
     "sequence": "550e8400-e29b-41d4-a716-446655440000"
   }
   ```

2. Retrieving user details:
   ```python
   import requests

   api_url = "https://your-api-gateway-url.amazonaws.com/Prod"
   user_id = "user-001"

   response = requests.get(f"{api_url}/detail?user_id={user_id}")
   print(response.json())
   ```

   Expected output:
   ```json
   {
     "UserID": "user-001",
     "Name": "Alice",
     "Email": "alice@example.com",
     "Balance": 0
   }
   ```

### Troubleshooting

1. Issue: Lambda function timing out
   - Problem: Lambda function execution exceeds the configured timeout.
   - Solution: Increase the `Timeout` value in the `Globals` section of `template.yaml`.

2. Issue: DynamoDB ProvisionedThroughputExceededException
   - Problem: Read/write capacity units are insufficient for the current load.
   - Solution: Increase the `ProvisionedThroughput` values for the affected table in `template.yaml`.

### Debugging

To enable verbose logging:
1. Set the environment variable `LOG_LEVEL` to `DEBUG` for each Lambda function in `template.yaml`.
2. Redeploy the stack using `sam deploy`.
3. View the logs in CloudWatch Logs for each Lambda function.

## Data Flow

The application follows an event-driven architecture with the following data flow:

1. Client sends a command to the `/command` endpoint.
2. `CommandLambda` processes the command and stores an event in the `EventsTable`.
3. `ProjectionLambda` is triggered by the DynamoDB stream from `EventsTable`.
4. `ProjectionLambda` updates the `UserSummaryTable` and `UserDetailTable` based on the event.
5. Clients can query user data using the `/list` and `/detail` endpoints.

```
[Client] -> [CommandLambda] -> [EventsTable] -> [ProjectionLambda] -> [UserSummaryTable]
                                                                   -> [UserDetailTable]
[Client] <- [ListLambda] <- [UserSummaryTable]
[Client] <- [DetailLambda] <- [UserDetailTable]
```

Note: The projection process ensures eventual consistency between the event store and the read models.

## Infrastructure

The application's infrastructure is defined using AWS SAM in the `template.yaml` file. Key resources include:

### DynamoDB Tables
- EventsTable: Stores the event stream with `AggregateID` and `Sequence` as the primary key.
- UserSummaryTable: Stores user summary information for quick listing.
- UserDetailTable: Stores detailed user information.

### Lambda Functions
- CommandLambda: Handles POST /command requests.
- ProjectionLambda: Processes events from EventsTable and updates read models.
- ListLambda: Handles GET /list requests.
- DetailLambda: Handles GET /detail requests.

### API Gateway
- Implicit API Gateway created by SAM to expose Lambda functions as HTTP endpoints.

### IAM Roles
- Each Lambda function has an associated IAM role with necessary permissions to access DynamoDB tables.

The infrastructure is designed to be scalable and follows AWS best practices for serverless applications.