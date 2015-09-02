## HDX Ageing Service
The ageing service is a [`Flask`](http://flask.pocoo.org) powered service to query the age and status of an HDX resource.

## Docker Usage
[![](https://badge.imagelayers.io/luiscape/hdx-monitor-ageing-service:latest.svg)](https://imagelayers.io/?images=luiscape/hdx-monitor-ageing-service:latest 'Get your own badge on imagelayers.io')

This application needs a volume mounted, four environment variables, and a link to a redis instance in order to run successfully. When running, use the following Docker command:

```shell
$ docker run -d \
  -e CKAN_API_KEY=[SYSADMIN_API_KEY] \
  -e CKAN_REMOTE_URL=[CKAN_URL] \
  -e CKAN_PROD_URL=[CKAN_URL] \
  -e CKAN_USER_AGENT=[DESIRED_USER_AGENT] \
  -v ./data:/data \
  --link redis:redis \
  --name age \
  luiscape/hdx-monitor-ageing-service:latest
```
