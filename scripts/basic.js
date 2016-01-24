// Description
//  who to pm
//
//  Author:
//  Ramanjit Khakh person@temple.edu

var Houndify = require('houndify').Houndify
var exec = require('child_process').exec;
var cmd = (
	'python ' +
	require('path').join(__dirname, '..', 'houndify_python_sdk-0.1.3', 'houndify.py') +
	' eu4YIoc0quAGGcpph-VuqF1P7Q1viBEJ1gg7c9bPf6I_6H1jOvtmPBvObMJx_m344Htz8uVj1_LOtm4uxiX22g== T6bexd0GJzOELaChLmTu-g=='
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



	robot.respond(/message active/i, function(msg){
		exec(cmd, function(err, stdout, stderr) {
  			if (err) {
  				console.error('Could not access the houndify API.\n\n\n', stdout, '\n\n\n\n' ,err);
  			} else {
  				var payload = JSON.parse(stdout);
  				var choiceData = payload.Disambiguation.ChoiceData;
  				if (choiceData.length > 0) {
  					var transcription = choiceData[0].FixedTranscription;
  					console.log(transcription);
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
