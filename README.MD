# university-to-do-list automator

Runs on AWS lambda. Deploy with Serverless (`brew install serverless`) and AWS cli.

## Build and Deployment

* In `serverless.yml`, adjust your region and cron rule to suit your needs.
* Create a `.env` file and add the following values

```
TODOIST_API_TOKEN=...
TIMEZONE_NAME=Australia/Melbourne
DATA_LOCATION=./data
```

* You need data files which contain information about the tasks and projects you will be adding.
* Then, `sls deploy` to push to AWS Lambda.

## Testing

After setting up environment variables as above, and filling out the data files,
```sh
sls invoke local -f todoistAutomator
```
