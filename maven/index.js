/**
* Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
* 
* Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
* associated documentation files (the "Software"), to deal in the Software without restriction,
* including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
* and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
* subject to the following conditions:
* 
* The above copyright notice and this permission notice shall be included in all copies or substantial 
* portions of the Software.
* 
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
* LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
* WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/

// We wanted a quick application that could function seperately of all of mars/server just in case.

var cli = require('cli');
var exec = require('child_process').exec;
var fs = require('fs'); 
var knownCameras = require('./knownCameras.json');
var _ = require('underscore');
var q = require('q');

var pidFile = '/do-not-delete-manually.hyperloop';

function getSerialIDForCamera(camera) {
  var defer  = q.defer();
  exec('udevadm info --query=all --name='+camera+' | grep ID_SERIAL_SHORT', function (err, result) {
    if(err) {
      cli.fatal(err);
    }
    if(result.indexOf('ID_SERIAL_SHORT=') > -1) {
      var justId = (result.match(/ID_SERIAL_SHORT=(.+)/))[1];
      defer.resolve(_.findWhere(knownCameras, { id: justId }));
    }
    else {
      defer.resolve(undefined);
    }
  });
  return defer.promise;
}

//I don't like any of this...
function generateGStreamCommands(options, cameras) {
  var gstCommands = [];
  cameras.forEach(function (camera) {
    var defer = q.defer();
    getSerialIDForCamera(camera).then(function startStream(cameraInfo) {
      //console.log(cameraInfo);
      if(cameraInfo && cameraInfo.name) {
        var port = (parseInt(options.port) + cameraInfo.port_increment * 10);
        cli.info(cameraInfo.name + ' recognized with serial ' + cameraInfo.id + '.\n\tOpened on Port: ' + port);
        var cmd =  'splitter. v4l2src device=' + camera  + ' ! \'video/x-raw, width='+options.width+', height='+options.height+', framerate=' + options.fps + '/1\' ! tee name=' + cameraInfo.gst_tee + ' ! queue ';
            cmd += '! omxvp8enc bitrate=' + options.bitrate + ' ! rtpvp8pay pt=96 ! queue ! udpsink host=' + options.ip + ' bind-port=' + port + ' port=' + port + ' loop=false '+ cameraInfo.gst_tee + '. ';
            cmd += '! queue ! omxh264enc bitrate=' + options.bitrate + ' ! mp4mux ! queue ! filesink location=' + options.filename + '-' + cameraInfo.name.replace(/ /g, '') + '.mp4';
        cli.info(cmd)
        defer.resolve(cmd);
      }
      else {
        cli.warn('Unknown Camera ' + camera +'. Register in knownCameras.json');
        defer.resolve(undefined);
      }
    });
    gstCommands.push(defer.promise);
  });
  return q.all(gstCommands);
}

//We don't use pkill here to avoid killing processess that aren't ours
function killPID(pid) {
  if(pid.length > 0) {
    var command = 'kill -2 ' + pid;
    exec(command, function callback(err, result) {
        var result = (err || result || 'success').toString();
        if(result.indexOf('No such process') > -1) {
          result = 'Was already deleted';
        }
        cli.info('Result of [' + command + ']: ' + result);
    });
  } 
}

//Manually reads in the pids file and deletes all pids
function closeOpenStreams() {
  if(fs.existsSync(pidFile)) {
    var pids = fs.readFileSync(pidFile);
    if(pids && pids.length > 1) {
      pids = pids.toString().split("\n");
      //cli.info('Manually Kiling the following pids: ' + pids);
      for(var index in pids) {
        killPID(pids[index]);
      }
    }
    else {
      cli.info('Could not read pids file (' + pidFile + ')');
    } 
  }

  return 0;  
}

cli.parse({
  ip: ['i', 'IP address of the client to receive these streams', 'ip'],
  width: ['w', 'Width of video to streams', 'int', 640],//432],
  height: ['h', 'Height of the video streams', 'int', 360],//240],
  bitrate: ['b', 'Requested bitrate from streams', 'int', 1500000],
  filename: ['f', 'Filename base to write the streams (test#.mp4)', 'string', 'test'],
  fps: ['fps', 'Frames per second that the camera should attempt to capture', 'int', 24],
  port: ['p', 'Default starting port to broadcast over -- increments by 1 for each camera', 'int', 8554],
  verbose: [false, 'If on, will log out all of GStreamer\'s debug information', 'bool', false],
  close: [false, 'When a stream is launched the Processs ID is tracked, if there is an interrupt of communication between client and server, this will explicitly close any opened streams']
});

cli.main(function mainEntryPoint(args, options) {
  
  //if the close option is set, we don't even bother with reading, we try to open
  //up pid file, and read in the pids, afterwards we delete the pid file and 
  //move on
  if(options.close) {
    closeOpenStreams();
  }
  else {
    if (options.ip == null) {
        return cli.fatal('You must run this cli application with a designated Ip address (eg: node index.js -ip 192.168.1.1)');
    }
    //start by grabbing all camera
    fs.readdir('/dev/', function getCameras(err, files) {
      if(err) {
        cli.fatal(err);
      }
      var cameras = [];
      files.forEach(function (file) {
        if(file.indexOf('video') > -1) {
          cameras.push('/dev/' + file);
        }
      });
      cli.info('Found Cameras: ' + cameras);
      return generateGStreamCommands(options, cameras).then(function runCommands(commands) {
        var toExecute = 'sudo gst-launch-1.0 -e ';
        if (options.verbose === true) {
            toExecute += '-v ';
        }
        //provide root t-split to be explicit when viewing the command outside of mars
        toExecute += ' tee name=splitter ';
            
        commands.forEach(function (command) {
            toExecute += command + ' ';
        });
        exec(toExecute);
        cli.info(toExecute);
        //just use a pipe so i don't have to launch an fs writer
        exec('sudo pgrep -f gst-launch-1.0 > ' + pidFile, function(err, pids, stderr) {
          if(err) {
             cli.fatal('Could not obtain the GStreamer pids');
          }
        });

      });
    });
  }
});

