# what is regift

Regift is a tool that tels you build Android APK using html+css+js without need for addtional third party tools.
The apps build with regft will also update themselvers automatically from your web site, bypassing the stores.

Regift comprises of three parts:

- the first is a tool that allows you to customize a vanilla APK that was pre-build with cordova. This step does not require that you have cordova installed nor that you have Andoird Studio installed. The customized app is a particular app that has the ability to download code from a URL that you must specify. Upon startup the customized app will connect to your web server, download this code, cache it locally, then start. This code must be stored in a file called 'package.json'.

- the second is a tool that allows you to create a 'package.json' from almost any single page web application.



## how does it work?

Regift comprises of about 3 different components:
- the first a ready made Androd app that you can customze and redstribute but does not need recompilation.
- the second is mechanism for packaging almost any simple page web app and 

## How is regft different from Cordova

Regift is based on cordova a cordova app and outputs a cordova app but it is desgned to run 

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