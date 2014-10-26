ctd
===

# Overview

CTD (see the difference) is a web service that allows one to track differences in images.

When developing applications that produce any kind of visual content it is often valuable to track when their output 
changes to rule out incidental changes due bugs, etc. Although this can be done using unit/regression tests checking 
for differences between the current output and some target image, this can become a maintenance burden when the output 
changes frequently for valid reasons. In such situation CTD provides a way to track image differences and notify users of any 
changes and requires minimal setup.

CTD only provides image tracking, so image generation needs to be done outside the system using a CI loop or other means. An 
image to be compared by CTD is submitted to the service along with a name. Next time a new image is submitted CTD will compare 
it with other images bearing the same name and notify users if the image differs from previously submitted one.

Images with the same name in the system are called series. The are no particular restrictions on names except they need to be 
in ASCII, but some markup helps group/classify individual series. A user can set comparison properties for a series, add 
e-mail addresses to send notifications to when a series changes or delete a series. Web page for a series visualizes series 
differences in a step graph. Each image can be viewed and compared to other submitted images from the same series.

Once the system has a large number of series it is preferable to group series. Grouping is done by breaking up series name 
into components with ‘.’ (dot) separating them and treating the name as a path (like a file path) with components being group 
names. Groups are automatically created when a new series name is added to the system. On a web page groups are shown either 
as a tree of items or a gallery with latest images from all descendant series.

CTD also allows comparing between different series or groups. This can be useful for example when comparing generated images 
between different development branches or between different generation methods. For this, series or group names must belong 
to a single class. When a component in series or group name is put inside parenthesis it is treated as a “variable” component. 
Names with the same components except for variable components belong to the same class. For example:
(a).b and (b).b belong to a same class;
(a).b.(c) and (d).b.(e) belong to a same class, but
(a).b, (a).c and (a).b.c all belong to different classes
Inter- group/series comparisons are not done automatically, but are rather available on request from web view. On a series 
page the system will list all other series belonging to the same class and a user can view their difference graphs. Groups in 
the same class can also be compared. In this case the system compares latest images from all descendant series. 

# Installation and usage

The server only runs on a Windows machine. It can be changed if the nvimgdiff program is built for your target system.
- Install Python 2.7+
- -Install PIP (on Windows it needs to be installed through its installer)
- Download CTD
- Copy ctd/default_config.py to config.py and edit it
- Run the server: python runserver.py --config=config. See runserver.py for other possible arguments.

Images are submitted to CTD using a standard HTTP POST method with URL *<server>*/image/post/*<series_name>*. The server 
expects a 'file' form field with an attached image. In Python land one can use provided ctdclient module to upload an image:
```
from ctdclient import upload_image
upload_image(server_url, series_name, path_to_image)
```
Currently the system only accepts PNG, GIF and JPEG images.

# Credits

CTD server is written in [Python 2.7](https://www.python.org/) as a [Flask](http://flask.pocoo.org/) application. It uses 
[nVidia texture tools](https://code.google.com/p/nvidia-texture-tools/) nvimgdiff program for performing the actual image 
comparison. The server also requires [PIP](https://pip.pypa.io/en/latest/index.html) package. 
The web client uses 
- [JQuery](http://jquery.com/)
- [Bootstrap](http://getbootstrap.com/)
- [amCharts](http://www.amcharts.com/)
- [bootstrap-slider](http://www.eyecon.ro/bootstrap-slider/)
- [jQuery treetable](http://ludo.cubicphuse.nl/jquery-treetable/)
- [spin.js](http://fgnass.github.io/spin.js/)
