# awsume-saml-plugin
Assumes AWS roles with SAML federation.

# IMPORTANT NOTE!
Currently the mainstream awsume application has a bug making this plugin unable to work.
I created a [pull request](https://github.com/trek10inc/awsume/pull/164) to fix this issue, that is not merged yet.
I described in the [installation section](#Installation) how to install the whole setup.

# Usage
```bash
$ # without username and password being specified in ~/.aws/config
$ awsume --with-saml myprofile
Username: Joe
Password: 

Match: arn:aws:iam::111222333444:role/admin,arn:aws:iam::111222333444:saml-provider/myprovider
Assuming role: arn:aws:iam::111222333444:saml-provider/myprovider,arn:aws:iam::111222333444:role/admin
Role credentials will expire 2021-09-10 13:59:16

$ # with username being specified in ~/.aws/config
$ awsume --with-saml myprofile
Password: 

Match: arn:aws:iam::111222333444:role/admin,arn:aws:iam::111222333444:saml-provider/myprovider
Assuming role: arn:aws:iam::111222333444:saml-provider/myprovider,arn:aws:iam::111222333444:role/admin
Role credentials will expire 2021-09-10 13:59:31

$ # with username and password being specified in ~/.aws/config
$ awsume --with-saml myprofile

Match: arn:aws:iam::111222333444:role/admin,arn:aws:iam::111222333444:saml-provider/myprovider
Assuming role: arn:aws:iam::111222333444:saml-provider/myprovider,arn:aws:iam::111222333444:role/admin
Role credentials will expire 2021-09-10 13:59:40

$ # with username and password and mfa_token substitution being used in password and specified in ~/.aws/config
$ awsume --with-saml myprofile --mfa-token 123456

Match: arn:aws:iam::111222333444:role/admin,arn:aws:iam::111222333444:saml-provider/myprovider
Assuming role: arn:aws:iam::111222333444:saml-provider/myprovider,arn:aws:iam::111222333444:role/admin
Role credentials will expire 2021-09-10 13:59:58
```

# Installation (OSX, Linux)
```
mkdir ~/.awsume-installers
cd ~/.awsume-installers
git clone https://github.com/Timboo89/awsume.git
git clone https://github.com/Timboo89/awsume-saml-plugin.git
pip install ./awsume
pip install awsume[saml]
pip install -r ./awsume-saml-plugin/requirements.txt
pip install ./awsume-saml-plugin
# recommendation: also install the console plugin
pip install awsume[console]
pip install awsume[fuzzy]
```

# Installation (Windows)
```
No guide yet.

```

# Additional configuration
For this plugin to be as reusable as possible it needs a configuration file.
As we already have a configuration file when thinking about programmatic access to AWS, we are reusing that.

**~/.aws/config** 
```
[profile myprofile]
role_arn = arn:aws:iam::111222333444:role/admin
principal_arn = arn:aws:iam::111222333444:saml-provider/myprovider
awsume_saml_endpoint = https://sso.mydomain.com/endpoint?RequestBinding=HTTPPost&PartnerId=urn:amazon:webservices
awsume_saml_custom_input_login-type = token
awsume_saml_username = Joe
awsume_saml_password = secret{mfa_token}
```

As you can see there are a couple of extra parameters here.

| Name | required | description |
| --- | --- | --- |
| awsume_saml_endpoint | yes | SSO Endpoint where you normally start your SAML login from when using the browser. |
| awsume_saml_username | no | If not given this plugin will prompt you for it during run. |
| awsume_saml_password | no | If not given this plugin will prompt you for it during run. In some cases you may have an MFA token merged into the password itself. For this case you can use the substitition `{mfa_token}` in conjunction with the `--mfa-token` parameter of awsume. |
| awsume_saml_custom_input_* | no | Not needed for most cases. It my happen, that your saml endpoint has some (hidden or not) input fields. You can specify them here. The prefix `awsume_saml_custom_input_` will be cut of the string.\n E.g. `awsume_saml_custom_input_login-type` becomes `login-type` in the requests payload. |

# What's working
* One-page logins:
  * Login pages were you see all login fields on one page.
  * Currently working for username and password or username and passwords with mfa tokens baked into password-string.
* Adding username and password to aws config with custom parameters
* Adding login endpoint to aws config with custom parameters
* Adding custom https-form fields other than username and password
* Using --mfa-token as input for mfa tokens being merged into password


# What's not implemented (yet)
* Two-page logins:
  * Login page with username and password leading to another page for mfa entry
* One-page logins:
  * Login page with seperate input field for mfa token
  * Defining username / password input names in case they are not containing `(user|email)` or `pass`

# Note of thanks
* I took a trick or two from the official [AWS blog](https://aws.amazon.com/blogs/security/how-to-implement-a-general-solution-for-federated-apicli-access-using-saml-2-0/) to build this more easily.