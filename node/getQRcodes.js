// Check if "useQRcodes" is true in personalData before calling this!
// because I'm not gonna check!
const spawn = require('child_process').spawn;
const webModel = require('./webModel');
const robotModel = require('./robotModel');
const kill = require('./reallyKillProcess.js');

/*
  getQRcodes will run the zbarcam application to look for QR codes,
  if a QR code is found it will behave in one of two ways:
  1. If the first line is '{' then it will keep accepting lines until
     it receives a '}' and use it as a JSON string.
  2. Otherwise, if it does not start with a '{' it will stop and use
     the single line as the input.
*/
module.exports = function() {
  let killProcess;
  const process = spawn('../scripts/getQRcodes.sh');
  const foundJSON = false;
  const qrJSONstring = '';
  const killOnTimeout = setTimeout(() => {
    // console.log('timeout');
    kill(process.pid);
    robotModel.gettingQRcode = false;
  }, 5000);
  process.stdout.setEncoding('utf8');
  process.stdout.on('data', (data) => {
    const receivedLine = data.split('\n')[0];
    if (receivedLine !== 'Waiting for zbarcam to close . . .') {
      if (receivedLine === '{') {
        const qrJSONstring = JSON.parse(data);
        if (qrJSONstring.mapName) {
          if (
            webModel.mapName === '' &&
            webModel.mapList.indexOf(qrJSONstring.mapName) > -1
          ) {
            webModel.mapName = qrJSONstring.mapName;
          }
        }
        // THESE items will only be triggered ONCE per run via a QR code!
        // to avoid fighting the robot when he is at the "initial" station.
        if (!webModel.hasSetupViaQRcode) {
          if (qrJSONstring.unplugYourself) {
            webModel.hasSetupViaQRcode = true;
            webModel.unplugYourself = qrJSONstring.unplugYourself;
          }
          if (qrJSONstring.ROSstart) {
            webModel.hasSetupViaQRcode = true;
            webModel.ROSstart = qrJSONstring.ROSstart;
          }
        }
      } else {
        webModel.QRcode = receivedLine;
      }
      kill(process.pid);
    }
  });
  // process.stderr.setEncoding('utf8');
  // process.stderr.on('data', function(data) {
  //    console.log('stderr data:' + data);
  // });
  // process.on('error', function(err) {
  //    console.log('getQRcodes Error:' + err);
  // });
  process.on('exit', () => {
    clearTimeout(killOnTimeout);
    robotModel.gettingQRcode = false;
  });
};
