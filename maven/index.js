var cli = require('cli');
var exec = require('child_process').exec;
var fs = require('fs'); 
var knownCameras = require('./knownCameras.json');
var _ = require('underscore');
var q = require('q');

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
function generateVLCStreamCommands(options, cameras) {
  //like srsly kill me
  var vlcCommands = []
  cameras.forEach(function (camera) {
    var defer = q.defer();
    getSerialIDForCamera(camera).then(function startStream(cameraInfo) {
      //console.log(cameraInfo);
      if(cameraInfo && cameraInfo.name) {
        cli.info(cameraInfo.name + ' recognized with serial ' + cameraInfo.id + '.\n\tOpened on Port: ' + (parseInt(options.port) + cameraInfo.port_increment));
        var cmd = "cvlc "+ (options.verbose ? '-vvv' : '');
            cmd += "v4l2://"+camera+":width="+options.width+":height="+options.height+":fps="+options.fps + ' --live-caching 200 ';
            cmd += "--sout '#transcode{vcodec=hv32,venc=x264{preset=ultrafast}vb="+options.bitrate;
            cmd += ",acodec=none}:duplicate{dst=file{dst=" + options.filename + '-' + cameraInfo.name.replace(/ /g, '') + ".mp4},dst=rtp{sdp=rtsp://:";
            cmd += (parseInt(options.port)+cameraInfo.port_increment)+"/}}'";
        cli.info(cmd)
        defer.resolve(cmd);
      }
      else {
        cli.warn('Unknown Camera ' + camera +'. Register in knownCameras.json');
        defer.resolve(undefined);
      }
    });
    vlcCommands.push(defer.promise);
  });
  return q.all(vlcCommands);
}

//We don't use pkill here to avoid killing processess that aren't ours
function killPID(pid) {
  if(pid.length > 0) {
    var command = 'kill ' + pid;
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
  var file = 'do-not-delete-manually.hyperloop';
  if(fs.existsSync(file)) {
    var pids = fs.readFileSync('do-not-delete-manually.hyperloop');
    if(pids && pids.length > 1) {
      pids = pids.toString().split("\n");
      //cli.info('Manually Kiling the following pids: ' + pids);
      for(var index in pids) {
        killPID(pids[index]);
      }
    }
    else {
      cli.info('Could not read pids file (do-not-delete-manually)');
    } 
  }

  return 0;  
}

cli.parse({
  width: ['w', 'Width of video to streams', 'int', 640],
  height: ['h', 'Height of the video streams', 'int', 480],
  bitrate: ['b', 'Requested bitrate from streams', 'int', 4000],
  filename: ['f', 'Filename base to write the streams (test#.mp4)', 'string', 'test'],
  fps: ['fps', 'Frames per second that the camera should attempt to capture', 'int', 45],
  port: ['p', 'Default starting port to broadcast over -- increments by 1 for each camera', 'int', 8554],
  verbose: [false, 'If on, will log out all of VLCs garbage', 'bool', false],
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
      return generateVLCStreamCommands(options, cameras).then(function runCommands(commands) {
        commands.forEach(function (command) {
          exec(command);
        });

        //just use a pipe so i don't have to launch an fs writer
        exec('pgrep -f vlc > do-not-delete-manually.hyperloop', function(err, pids, stderr) {
          if(err) {
             cli.fatal('Could not obtain the VLC pids');
          }
        });

      });
    });
  }
});

