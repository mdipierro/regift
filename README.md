# what is regift

Regift is a tool that lets you build an Android APK using html+css+js without need for third party tools.
The apps built with regft will also update themselvers automatically from your web site, bypassing the app store.

Regift comprises of three parts:

- the first is a tool (regift build) that allows you to customize a vanilla APK that was pre-built with cordova. This step does not require that you have cordova installed nor that you have Andoird Studio installed. The customized (regifted) app is a particular app that has the ability to download code remotely from a URL that you must specify. Upon startup the customized app will connect to your web server, download this code, cache it locally, then start. This code must be stored in a file called 'package.json', on your server.

- the second is a tool (regift package) that allows you to create a 'package.json' from almost any single page web application.

- the third is a sample app (example2) built with vue.js which you can package and delver to your regifted apps.

### How is regift different from Cordova?

regift ships with an app built wth cordova. It then customize this app to run your singl page web app. yet it does not requre that you have corodova. There is more to regift than the cordova app anyway.

## Example of usage (example1)

```
$ echo <<EOF > config1.yaml
app_name: My First App
description: my first app
author: me
email: me@example.com
url: http://example.com
package_url: http://yourdomain/example1/package.json
EOF
$ regif.py build myapp1 -c confg1.yaml 
```

This will make a signed app ready to distribute app myapp1.apk
This app, at startup will attempt to download a package from http://yourdomain/example1/package.json
You can make an example package.json using the provided example1:

```
$ cd static/examples/example1
$ ../../../regift.py package index.html
```

now copy package.json to your server and the URL http://yourdomain/example1/package.json

## Example of usage (example2)

```
$ echo <<EOF > config2.yaml
app_name: My Second App
description: my second app
author: me
email: me@example.com
url: http://example.com
package_url: http://yourdomain/example2/package.json
EOF
$ regif.py build myapp2 -c confg2.yaml 
```

This will make a signed app ready to distribute app myapp2.apk
This app, at startup will attempt to download a package from http://yourdomain/example1/package.json
You can make an example package.json using the provided example2:

```
$ cd static/examples/example2
$ ../../../regift.py package index.html
```

Now copy package.json to your server and the URL http://yourdomain/example2/package.json so that the apk can find it.

### tips

click on the spinner to force a reload of a package.json from server