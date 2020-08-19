
## napari plugins

https://github.com/transformify-plugins/segmentify

https://github.com/marshuang80/cell-segmentation

## Edit linux interface look/feel

## infinite login loop after installing nvidia drivers

```
dconf-editor
```

```
https://askubuntu.com/questions/1231410/cant-log-in-on-ubuntu-20-04

```
It seems to be an issue with the auto-login. One way to fix this is by disabling auto-login from the command prompt:

From the login screen hit <Ctrl> + <Alt> + <F4>
Login through the command prompt input: sudo nano /etc/gdm3/custom.conf
Line number 5 and 6 of custom.conf should be:

AutomaticLoginEnable=true
AutomaticLogin=[username]
where, [username] is the name of the user for auto-login. Change this to:

#AutomaticLoginEnable=true
#AutomaticLogin=[username]
Hit <Ctrl> + S to save, then reboot by hitting <Ctrl> + <Alt> + <F1> and selecting restart from the login menu.
```

## screen share ubuntu and macOS on local network

[[success]

install dconf-editor

```
sudo apt install dconf-editor
```

turn off encryption using interface

```
org/gnome/desktop/remote-access/require-encryption
```

```
# THIS DOES NOT WORK !!!! need to use dconf-editor
#sudo gsettings set org.gnome.Vino require-encryption false
```

## old

this is simple but my desktop mac system is too old

most posts on this don't mention using 'sudo'. Seems there are user and sudo version of gsettings

```
sudo gsettings set org.gnome.Vino require-encryption false
```

https://techsparx.com/linux/ubuntu/remote-desktop.html

https://askubuntu.com/questions/463486/can-no-longer-use-screen-share-to-connect-mac-to-ubuntu-since-upgrading-to-14-04

## can not connect macOS to ubuntu

installing tightvncserver with

https://linuxconfig.org/vnc-server-on-ubuntu-20-04-focal-fossa-linux
