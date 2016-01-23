// Description
//  who to pm
//
//  Author:
//  Ramanjit Khakh person@temple.edu

//var Houndify = require('houndify').Houndify



module.exports = function(robot){
	/*var client = new Houndify({
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
	*/


	var express = require('express');
	var app = express();
	var hound = require('hound').HoundNode;
	
	var Hound = require('hound').Hound;
/* create an express app*/

// Send the request to http text endpoint with authentication headers
	app.get('/textSearchProxy', hound.createTextProxyHandler({ 
	  clientId:  process.env.USER_ID, 
	  clientKey: process.env.USER_KEY
	}));
	var textSearch = new Hound.TextSearch({

  //You need to create an endpoint on your server
  //for handling the authentication and proxying 
  //text search http requests to Hound backend
  //See SDK's server-side method HoundNode.createTextProxyHandler().
  proxy: {
    route: "/textSearchProxy",
    // method: "GET",
    // headers: []
    // ... More proxy options will be added as needed
  },

  
  //Listeners

  //Fires after server responds with Response JSON
  //Info object contains useful information about the completed request
  //See https://houndify.com/reference/HoundServer
  onResponse: function(response, info) {},

  //Fires if error occurs during the request
  onError: function(err, info) {}
});

//see https://houndify.com/reference/RequestInfo
var requestInfo = { 
  UserID: "as124faa12", 
  City: "Toronto", 
  Country: "Canada"
};

var query = "What is the weather like in Toronto?";

//starts streaming of voice search requests to Hound backend



	robot.respond(/message active/i, function(msg){
		textSearch.search(query, requestInfo);
		console.log(textSearch);

		/*console.log("wakafloca flame");		
		var input = 'What time is it in Tokyo?';
		var querySpecificRequestInfo = {
		  City: 'new york'
		};
		 
		client.query(input, querySpecificRequestInfo, function(err, res) {
					console.log("respond payload")
					console.log(res);
				
		});*/


	});

}