# university-to-do-list automator

Runs on AWS lambda. Deploy with Serverless (`brew install serverless`) and AWS cli.

### Build and Deployment

1. In `serverless.yml`, adjust your region and cron rulle to suit your needs.
2. Create a `.env` file and add `TODOIST_API_TOKEN=...` (replace the ... with
your own token)
3. Then, `sls deploy` to push to AWS Lambda.

### Testing

After setting up environment variables as above,
```
sls invoke local -f todoistAutomator
```
