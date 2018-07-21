# ChargingBreak API

## Dependencies

Install JavaScript dependencies via npm after cloning the repository:

```
npm install
```

## Create API domain

```
sls create_domain
```

## Deploy

Deploy CloudFormation stack

```
sls deploy
```
or
```
make deploy
```

Deploy single function

```
sls deploy function -f <function_name>
```

## Python testing

```
make setup_test
make test
```

## One time only Cognito Config steps
1. Create auth. domain and certificate
1. Assign the domain in the UserPool -> App integration -> Domain name
1. After 20 minutes you need to assign the domain in Route53 with the alias provided on the previous step
1. Assign to UserPool created from CF Stack
1. Configure Identity Providers
1. Configure Attribute Mapping
1. Create "App client" (General settings -> App clients)
1. Create "App client settings" (App integration -> App client settings
  * For Google: Enable Google (callback url is main website)
  * OAuth2.0 (Enable Authorization code grant and Implicit grant)
  * Scopes (email, openid, profile) - set aws... if you want to do user/pass
  
