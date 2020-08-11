# university-to-do-list automator

Runs on AWS lambda. Deploy with Serverless (`brew install serverless`) and AWS cli.

### Build and Deployment

* In `serverless.yml`, adjust your region and cron rulle to suit your needs.
* Create a `.env` file and add the following values

```
TODOIST_API_TOKEN=...
TIMEZONE_NAME=Australia/Melbourne
```

* Then, `sls deploy` to push to AWS Lambda.

### Testing

After setting up environment variables as above,
```
sls invoke local -f todoistAutomator
```
