// Description
//  who to pm
//
//  Author:
//  Ramanjit Khakh person@temple.edu

var Houndify = require('houndify').Houndify;
var exec = require('child_process').exec;
var say = require('say');
var cmd = (
	'python ' +
	require('path').join(__dirname, '..', 'houndify_python_sdk-0.1.3', 'houndify.py') +
	' ' + process.env.USER_KEY + ' ' + process.env.USER_ID
);

module.exports = function(robot){
	var client = new Houndify({
	  auth: {
	    clientId: process.env.USER_ID,
	    clientKey: process.env.USER_KEY,
	    userId: 'houndify_try_api_user',
	  },
	  // Global RequestInfo, sent with every request
	  requestInfo: {
	    ClientID: 'Some application name'
	  }
	});



	robot.respond(/on/i, function(msg){
		exec(cmd, function(err, stdout, stderr) {
  			if (err) {
  				console.error('Could not access the houndify API.\n\n\n', stdout, '\n\n\n\n' ,err);
  			} else {
  				//console.log(stdout);
                var payload = JSON.parse(stdout);
  				var choiceData = payload.AllResults[0].WrittenResponseLong;
                console.log(choiceData);
  				if (choiceData.length > 0) {
  					
                    say.speak("Kathy", choiceData);
  				} else {
  					console.log('No choice data available');
  				}
  			}
		});

		/*	var input = 'What is the weather in Philadelphia?';
			var querySpecificRequestInfo = {
			  City: 'new york'
			};
			 
			client.query(input, querySpecificRequestInfo, (err, res) => {
				console.log("respond payload")
				console.log(res);	
			});

		*/
	});

}
