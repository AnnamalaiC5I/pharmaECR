# AWS ECS Deployment with GitHub Actions

This repository provides a guide on how to deploy your application to AWS Elastic Container Service (ECS) using GitHub Actions for Continuous Integration and Continuous Deployment (CI/CD). Follow the steps below to set up your ECS deployment.

## Prerequisites

Before getting started, make sure you have the following prerequisites in place:

- An Elastic Container Registry (ECR) image pushed to AWS.
- Basic knowledge of GitHub for source control and GitHub Actions for CI/CD.
- Familiarity with Elastic Container Service (ECS). You can watch a [YouTube video](https://www.youtube.com/watch?v=I9VAMGEjW-Q) for ECS basics, including terms and workflow.

### AWS Roles

Create the necessary AWS roles:

1. **ECSTaskExecution Role**: Create a cluster role with the `AmazonECSTaskExecutionRolePolicy` attached.

## Getting Started with ECS Deployment

### Step 1: Task Definition

1. In the AWS Management Console:
   - Craft a task definition for your ECS deployment.
   - Assign it the ECSTaskExecution role you created.
   - Determine the appropriate task memory and CPU based on your Docker image size.
   - Include the container image URL in the task definition, ensuring it matches the port number specified in your Docker image.

### Step 2: Create an ECS Cluster

1. Create an ECS cluster where your tasks will run. This is the environment where your containers will be managed.

### Step 3: Deploy Your Task

1. Once you've established your ECS cluster, navigate to the 'Tasks' section.
2. Create a new task by selecting the appropriate task definition and instance type.
3. Deploy the task. This action will provide your application with both a public IP and a private IP, making your app accessible.

### Step 4: Security Group Configuration

1. Ensure that the security group assigned to your ECS has the necessary inbound rules to allow traffic on the port specified in your Docker image.
2. If these rules are missing, add the required inbound rules with the correct port number to guarantee proper communication.

## CI/CD Pipelines

In this GitHub repository for CI/CD implementation ([repository link](https://github.com/AnnamalaiC5I/pharmaECR)), follow these steps:

1. Make sure you have all the required files in your repository.
2. Replace the 'task-definition.json' file in the repository with your own JSON task definition file.
3. Add your Access Key ID and Secret Key ID to the GitHub secrets for authentication and access control.
4. Customize the environment variables within the 'aws.yml' file with your specific values (e.g., 'aws_region,' 'ecs_cluster,' 'ecr_repository,' and 'container_name').
5. Select the trigger mechanism that suits your pipeline deployment.

With these steps, you can automate the deployment of your application to AWS ECS using GitHub Actions.

For detailed information, please refer to the [repository](https://github.com/AnnamalaiC5I/pharmaECR).

Feel free to update and expand this README as needed to provide more details or include additional instructions.
