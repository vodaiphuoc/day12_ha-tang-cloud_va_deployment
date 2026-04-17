# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. hardcode api key, database url, no config
2. no health check endpoint
3. reload=True => this used in dev only
...

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| config  | hardcode     | config với pandatic/.env file        | tránh bị lộ, dễ dàng thay đổi trong theo depolyment |
| health-check| không có | có endpoint| dễ check container có bị die hay không| 
|Logging|print|dùng logging| log về file, được chia theo info, error, warning, ... |
...

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: image được build sẵn với ngôn ngữ lập trình hoặc 1 chương trình nào đó
2. Working directory: root dir, là directory để thực hiệp các lệnh RUN, COPY, ... của docker
...

### Exercise 2.3: Image size comparison
- Develop:  MB
- Production: [Y] MB
- Difference: [Z]%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://your-app.railway.app
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
[Paste your test outputs]

### Exercise 4.4: Cost guard implementation
[Explain your approach]

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]