

    // Script for a modal window / dialog box
// to replace the default confirm window

// Made for practice and personal use in a web app,
// so no support for legacy browsers.

window.onload = (function() {
  
  var triggers        = document.querySelectorAll(".js-confirm"),
      dialogBox       = document.createElement("aside"),
      overlay         = document.createElement("div"),
      resultContainer = document.getElementById("result");
  
      function showDialog(event) {
		
    var target = event.target;
		
		dialogBox.innerHTML = "<p>" + target.getAttribute("data-message") + "</p>" +
		                      "<button id=\"confirm\">" + target.getAttribute("data-confirm-text") + "</button>" +
		                      " <button id=\"cancel\">" + target.getAttribute("data-cancel-text") + "</button>";
		
		
		
		dialogBox.className = "dialog-box";
		dialogBox.id        = "dialog";
		overlay.className   = "overlay";
		overlay.id          = "overlay";
		
		
		// Insert it to the page
		document.body.appendChild( dialogBox );
		document.body.appendChild( overlay );
		
		
		// Give it inline style attributes to position it in the center
		var vertCenter = Math.floor( (window.innerHeight - dialogBox.offsetHeight) / 2 ),
        horCenter  = Math.floor( (window.innerWidth - dialogBox.offsetWidth) / 2 );
		
		dialogBox.style.top  = vertCenter + "px";
		dialogBox.style.left = horCenter + "px";
    
    
    // Dialog box created, so clear the text in the resultContainer
		resultContainer.innerHTML = "";
        resultContainer.className = "result";
		
		
		if ( document.getElementsByTagName("aside").length ) {
			
			var buttons = document.getElementById("dialog").getElementsByTagName("button");
			
			function closeDialogBox() {
				
				document.getElementById("overlay").outerHTML = "";
				document.getElementById("dialog").outerHTML = "";
				
			}
			
			
			for (var i = 0, l = buttons.length; i < l; i++) {
				buttons[i].addEventListener("click", closeDialogBox, false);
			}
			
		}
		
		
	}
	
	
	for (var i = 0, l = triggers.length; i < l; i++) {
		triggers[i].addEventListener("click", showDialog, false);
	}
	
}());
