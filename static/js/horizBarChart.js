//Source: http://www.jqueryscript.net/chart-graph/Responsive-Animated-Bar-Chart-with-jQuery-Horizontal-Chart.html

(function ($) {
  "use strict"; //You will be happier

  $.fn.horizBarChart = function( options ) {

    var settings = $.extend({
      // default settings
      selector: '.bar',
      speed: 3000
    }, options);

    // Cycle through all charts on page
	  return this.each(function(){
	    // Start highest number variable as 0
	    // Nowhere to go but up!
  	  var highestNumber = 0;

      // Set highest number and use that as 100%
      // This will always make sure the graph is a decent size and all numbers are relative to each other
    	$(this).find($(settings.selector)).each(function() {
    	var num = $(this).data('number');
        if (num > highestNumber) {
          highestNumber = num;
        }
    	});

      // Time to set the widths
    	$(this).find($(settings.selector)).each(function() {
    		var bar = $(this),
    		    // get all the numbers
    		    num = bar.data('number'),
    		    // math to convert numbers to percentage and round to closest number (no decimal)
    		    percentage = Math.round((num / highestNumber) * 100) + '%';
    		// Time to assign and animate the bar widths
    		$(this).animate({ 'width' : percentage }, settings.speed);
    		$(this).next('.number').animate({ 'left' : percentage }, settings.speed);
    	});
	  });

  }; // horizChart

}(jQuery));
