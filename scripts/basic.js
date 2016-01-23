// Description
//  who to pm
//
//  Author:
//  Ramanjit Khakh person@temple.edu

var Houndify = require('houndify').Houndify



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
		console.log("wakafloca flame");		
		var input = 'What is the weather in Philadelphia?';
		var querySpecificRequestInfo = {
		  City: 'new york'
		};
		 
		client.query(input, querySpecificRequestInfo, function(err, res) {
					console.log("respond payload")
					console.log(res);
				
		});
	});

}
